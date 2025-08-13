# Career Connector – AI-Powered Career Guidance Platform :

Career Connector is an AI-powered web application designed to help MBA students and job seekers discover the best career path based on their skills.
The platform has two main modules – Student and Recruiter – enabling seamless interaction between candidates and hiring professionals.
-Features :

1) Student Section:
AI-Powered Career Recommendations – Suggests the most suitable specialization and job role based on skills.

2) Recruiter Section:
Secure Recruiter Login with password encryption.
Job Posting & Candidate Management – Recruiters can post jobs, view candidates, and shortlist them.
Integrated Student-Company Interaction – Easy connection between talent and opportunities.

3) Technical Highlights:
Hybrid Rules + Machine Learning model for career recommendations.
Backend with Streamlit UI and secure tokens for smooth user experience
Separate backend workflows for Student and Recruiter integrated into a single platform.

-Tech Stack:
Component            Technology                                                    

Frontend          Streamlit                                                     
Backend           Python (FastAPI initially, later migrated fully to Streamlit) 
Machine Learning   Pandas                                                                                       
Database          sqlite3                                             
Security          Password hashing & encryption                                 
Version Control   Git & GitHub                                                  

-Project Structure:
CC-app

career_connector.db
JobData.csv
main.py
.gitignore
requirements.txt

- Installation & Setup :
1️) Clone the Repository like the follows:

git clone https://github.com/Avi846/Career-connector.git
cd career-connector

2) Create Virtual Environment & Install Dependencies

3) Run the Application like follows inside terminal:
   streamlit run main.py

