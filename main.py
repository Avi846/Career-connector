import streamlit as st
import pandas as pd
import sqlite3
import jwt
import datetime
from passlib.hash import bcrypt
import os

# ========== CONFIGURATION ==========
DB_PATH = 'career_connector.db'
JWT_SECRET = ''  # In production, use a secure env var
JWT_ALGORITHM = 'HS256'
JOBDATA_PATH = os.path.join(os.path.dirname(__file__), 'Career_connector_app', 'JobData.csv')

# ========== DATABASE SETUP ==========
def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db()
    c = conn.cursor()
    # Recruiters
    c.execute('''CREATE TABLE IF NOT EXISTS recruiters (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        email TEXT UNIQUE NOT NULL,
        password TEXT NOT NULL,
        company TEXT NOT NULL
    )''')
    # Jobs
    c.execute('''CREATE TABLE IF NOT EXISTS jobs (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT NOT NULL,
        description TEXT NOT NULL,
        skills TEXT NOT NULL,
        salary TEXT NOT NULL,
        location TEXT NOT NULL,
        eligibility TEXT NOT NULL,
        recruiter_email TEXT NOT NULL
    )''')
    conn.commit()
    conn.close()

init_db()

# ========== AUTH HELPERS ==========
def hash_password(password):
    return bcrypt.hash(password)

def verify_password(password, hashed):
    return bcrypt.verify(password, hashed)

def create_jwt(payload):
    payload['exp'] = datetime.datetime.utcnow() + datetime.timedelta(hours=6)
    return jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)

def decode_jwt(token):
    try:
        return jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
    except jwt.ExpiredSignatureError:
        return None
    except jwt.InvalidTokenError:
        return None

# ========== JOB DATA LOADING ==========
def load_jobdata():
    try:
        return pd.read_csv(JOBDATA_PATH)
    except Exception:
        return pd.DataFrame()

jobdata_df = load_jobdata()

# ========== STREAMLIT UI ==========
st.set_page_config(page_title="Career Connector App", layout="wide")
st.title("Career Connector App")
tabs = st.tabs(["Recruiter", "Student"])

# ========== RECRUITER TAB ==========
with tabs[0]:
    st.header("Recruiter Portal")
    menu = st.radio("Select Option", ["Signup", "Login", "Post Job", "My Jobs"])

    if menu == "Signup":
        st.subheader("Create a Recruiter Account")
        name = st.text_input("Name", key="r_name")
        email = st.text_input("Email", key="r_email")
        password = st.text_input("Password", type="password", key="r_pass")
        company = st.text_input("Company", key="r_company")
        if st.button("Sign Up"):
            if not name or not email or not password or not company:
                st.warning("Please fill in all fields.")
            else:
                conn = get_db()
                c = conn.cursor()
                c.execute("SELECT * FROM recruiters WHERE email=?", (email,))
                if c.fetchone():
                    st.error("Email already exists.")
                else:
                    hashed = hash_password(password)
                    c.execute("INSERT INTO recruiters (name, email, password, company) VALUES (?, ?, ?, ?)", (name, email, hashed, company))
                    conn.commit()
                    st.success("Recruiter created successfully!")
                conn.close()

    elif menu == "Login":
        st.subheader("Recruiter Login")
        email = st.text_input("Email", key="login_email")
        password = st.text_input("Password", type="password", key="login_pass")
        if st.button("Login"):
            conn = get_db()
            c = conn.cursor()
            c.execute("SELECT * FROM recruiters WHERE email=?", (email,))
            user = c.fetchone()
            conn.close()
            if not user or not verify_password(password, user['password']):
                st.error("Invalid credentials.")
            else:
                token = create_jwt({"email": user['email'], "name": user['name']})
                st.session_state['recruiter_token'] = token
                st.success("Login successful!")
                st.info("You can now post jobs and view your jobs.")

    elif menu == "Post Job":
        token = st.session_state.get('recruiter_token')
        user = decode_jwt(token) if token else None
        if not user:
            st.warning("Please login as a recruiter to post jobs.")
        else:
            st.subheader("Post a Job")
            title = st.text_input("Job Title", key="job_title")
            description = st.text_area("Job Description", key="job_desc")
            skills = st.text_input("Skills Required (comma separated)", key="job_skills")
            salary = st.text_input("Salary Offered", key="job_salary")
            location = st.text_input("Job Location", key="job_location")
            eligibility = st.text_area("Eligibility Criteria", key="job_eligibility")
            if st.button("Post Job"):
                if not title or not description or not skills or not salary or not location or not eligibility:
                    st.warning("Please fill in all fields.")
                else:
                    conn = get_db()
                    c = conn.cursor()
                    c.execute("INSERT INTO jobs (title, description, skills, salary, location, eligibility, recruiter_email) VALUES (?, ?, ?, ?, ?, ?, ?)",
                        (title, description, skills, salary, location, eligibility, user['email']))
                    conn.commit()
                    conn.close()
                    st.success("Job posted successfully!")

    elif menu == "My Jobs":
        token = st.session_state.get('recruiter_token')
        user = decode_jwt(token) if token else None
        if not user:
            st.warning("Please login as a recruiter to view your jobs.")
        else:
            st.subheader("Your Posted Jobs")
            conn = get_db()
            c = conn.cursor()
            c.execute("SELECT * FROM jobs WHERE recruiter_email=?", (user['email'],))
            jobs = c.fetchall()
            conn.close()
            if not jobs:
                st.info("No jobs posted yet.")
            else:
                for job in jobs:
                    st.markdown(f"""
*Title:* {job['title']}  
*Location:* {job['location']}  
*Salary:* {job['salary']}  
*Skills:* {job['skills']}  
*Eligibility:* {job['eligibility']}  
---
""")

# ========== STUDENT TAB ==========
with tabs[1]:
    st.header("Student Portal")
    st.write("Get job recommendations based on your skills!")
    st.subheader("Enter Your Skills (comma separated)")
    student_skills = st.text_input("Skills", key="student_skills")
    if st.button("Get Recommendations"):
        if not student_skills:
            st.warning("Please enter at least one skill.")
        else:
            skills_list = [s.strip().lower() for s in student_skills.split(",") if s.strip()]
            if jobdata_df.empty:
                st.error("JobData.csv not found or empty.")
            else:
                # Simple skill matching: count overlap
                jobdata_df['SkillMatch'] = jobdata_df['Skills'].apply(lambda x: len(set([s.strip().lower() for s in str(x).split(',')]) & set(skills_list)))
                top_jobs = jobdata_df[jobdata_df['SkillMatch'] > 0].sort_values(by='SkillMatch', ascending=False).head(5)
                if top_jobs.empty:
                    st.info("No matching jobs found. Try different or more skills.")
                else:
                    st.success("Top Recommended Jobs:")
                    for _, row in top_jobs.iterrows():
                        st.markdown(f"""
*Domain:* {row['Domain']}  
*Job Role:* {row['Job Role']}  
*Skills Required:* {row['Skills']}  
*Personality:* {row['Personality']}  
---
""")
    st.divider()
    st.subheader("Browse All Jobs (Recruiter Posted)")
    conn = get_db()
    c = conn.cursor()
    c.execute("SELECT * FROM jobs")
    jobs = c.fetchall()
    conn.close()
    if not jobs:
        st.info("No jobs posted by recruiters yet.")
    else:
        for job in jobs:
            st.markdown(f"""
*Title:* {job['title']}  
*Location:* {job['location']}  
*Salary:* {job['salary']}  
*Skills:* {job['skills']}  
*Eligibility:* {job['eligibility']}  
*Posted by:* {job['recruiter_email']}  
---
""")
