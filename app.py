import os

import streamlit as st
import mysql.connector
from PyPDF2 import PdfReader
from groq import Groq

# ================= GROQ CLIENT =================
client = Groq(
    api_key=os.getenv("GROQ_API_KEY")
)

# ================= DATABASE CONNECTION =================
def db():
    return mysql.connector.connect(
        host="mysql",
        user="root",
        password="sujalroot45",
        database="notes_db"
    )

# ================= PAGE CONFIG =================
st.set_page_config(
    page_title="AI Notes Generator",
    page_icon="📘",
    layout="centered"
)

# ================= TITLE =================
st.title("📘 AI Notes Generator")

# ================= SIDEBAR =================
menu = st.sidebar.selectbox(
    "Menu",
    ["Login", "Register"]
)

# ================= REGISTER =================
if menu == "Register":

    st.subheader("Create Account")

    u = st.text_input("Username", key="reg_user")

    p = st.text_input(
        "Password",
        type="password",
        key="reg_pass"
    )

    if st.button("Register"):

        if u == "" or p == "":
            st.warning("Please fill all fields")

        else:

            d = db()
            c = d.cursor()

            # Create users table
            c.execute("""
                CREATE TABLE IF NOT EXISTS users(
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    username VARCHAR(50),
                    password VARCHAR(50)
                )
            """)

            # Check existing user
            c.execute(
                "SELECT * FROM users WHERE username=%s",
                (u,)
            )

            existing = c.fetchone()

            if existing:

                st.error("Username already exists")

            else:

                c.execute(
                    "INSERT INTO users(username,password) VALUES(%s,%s)",
                    (u, p)
                )

                d.commit()

                st.success("Registered Successfully")

            d.close()

# ================= LOGIN =================
if menu == "Login":

    st.subheader("Login")

    u = st.text_input(
        "Username",
        key="login_user"
    )

    p = st.text_input(
        "Password",
        type="password",
        key="login_pass"
    )

    if st.button("Login"):

        d = db()
        c = d.cursor()

        c.execute(
            "SELECT * FROM users WHERE username=%s AND password=%s",
            (u, p)
        )

        user = c.fetchone()

        d.close()

        if user:

            st.session_state["u"] = u

            st.success("Logged In Successfully")

        else:

            st.error("Invalid Username or Password")

# ================= MAIN APP =================
if "u" in st.session_state:

    st.sidebar.success(
        f"Logged in as {st.session_state['u']}"
    )

    # Logout
    if st.sidebar.button("Logout"):

        del st.session_state["u"]

        st.rerun()

    st.subheader(
        f"Welcome {st.session_state['u']} 👋"
    )

    # ================= PDF UPLOAD =================
    f = st.file_uploader(
        "Upload PDF",
        type=["pdf"]
    )

    if f:

        reader = PdfReader(f)

        text = ""

        for page in reader.pages:

            page_text = page.extract_text()

            if page_text:
                text += page_text

        st.success("PDF Uploaded Successfully")

        # ================= GENERATE NOTES =================
        if st.button("Generate Notes"):

            with st.spinner("Generating Notes..."):

                try:

                    res = client.chat.completions.create(
                        model="llama-3.1-8b-instant",
                        messages=[
                            {
                                "role": "system",
                                "content": "You are a helpful notes generator."
                            },
                            {
                                "role": "user",
                                "content": f"""
                                Create short and easy notes from this text.

                                Text:
                                {text[:4000]}
                                """
                            }
                        ],
                        temperature=0.5,
                        max_tokens=1024
                    )

                    out = res.choices[0].message.content

                    # ================= SAVE NOTES TO DATABASE =================
                    d = db()

                    c = d.cursor()

                    c.execute(
                        """
                        INSERT INTO notes(username, filename, notes)
                        VALUES(%s,%s,%s)
                        """,
                        (
                            st.session_state["u"],
                            f.name,
                            out
                        )
                    )

                    d.commit()

                    d.close()

                    # ================= SHOW NOTES =================
                    st.subheader("📝 Generated Notes")

                    st.write(out)

                    # ================= DOWNLOAD BUTTON =================
                    st.download_button(
                        label="Download Notes",
                        data=out,
                        file_name="notes.txt",
                        mime="text/plain"
                    )

                    st.success("Notes Saved Successfully")

                except Exception as e:

                    st.error(f"Error: {e}")

    # ================= NOTES HISTORY =================
    st.divider()

    st.subheader("📂 Notes History")

    try:

        d = db()

        c = d.cursor()

        c.execute(
            """
            SELECT filename, notes
            FROM notes
            WHERE username=%s
            ORDER BY id DESC
            """,
            (st.session_state["u"],)
        )

        data = c.fetchall()

        d.close()

        if data:

            for file_name, notes in data:

                with st.expander(f"📄 {file_name}"):

                    st.write(notes)

        else:

            st.info("No notes history found")

    except Exception as e:

        st.error(f"History Error: {e}")