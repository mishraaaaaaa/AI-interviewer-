import streamlit as st
from interviewer import get_skills, generate_question, evaluate_answer, generate_report, extract_text_from_resume, extract_name_from_resume
import time
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

def send_resume_email(resume_file, candidate_name):
    # Email configuration from environment variables
    # Set SENDER_EMAIL and SENDER_PASSWORD in your environment
    # For Gmail: Use your Gmail address and app password (not regular password)
    sender_email = os.getenv('SENDER_EMAIL')
    sender_password = os.getenv('SENDER_PASSWORD')
    receiver_email = "mishradiwakar132004@gmail.com"
    
    if not sender_email or not sender_password:
        print("Email credentials not set. Skipping email send.")
        return False
    
    # Create message
    msg = MIMEMultipart()
    msg['From'] = sender_email
    msg['To'] = receiver_email
    msg['Subject'] = f"New Resume Upload: {candidate_name}"
    
    body = f"Resume uploaded by {candidate_name}"
    msg.attach(MIMEText(body, 'plain'))
    
    # Attach resume
    attachment = MIMEBase('application', 'octet-stream')
    attachment.set_payload(resume_file.getvalue())
    encoders.encode_base64(attachment)
    attachment.add_header('Content-Disposition', f"attachment; filename={resume_file.name}")
    msg.attach(attachment)
    
    # Send email
    try:
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(sender_email, sender_password)
        text = msg.as_string()
        server.sendmail(sender_email, receiver_email, text)
        server.quit()
        return True
    except Exception as e:
        print(f"Email sending failed: {e}")
        return False

st.set_page_config(
    page_title="AI Interview Simulator",
    page_icon="🤖",
    layout="wide"
)

# ---------- SESSION STATE ----------

if "interview_started" not in st.session_state:
    st.session_state.interview_started = False

if "questions" not in st.session_state:
    st.session_state.questions = []

if "report_generated" not in st.session_state:
    st.session_state.report_generated = False

if "candidate_name" not in st.session_state:
    st.session_state.candidate_name = None

# ---------- MODERN UI CSS ----------

st.markdown("""
<style>

/* Background */

.stApp{
background-image: linear-gradient(rgba(0,0,0,0.82), rgba(0,0,0,0.85)),
url("https://images.unsplash.com/photo-1551836022-d5d88e9218df");

background-size: cover;
background-position: center;
background-attachment: fixed;
color:white;
}

/* Title */

.title{
font-size:60px;
font-weight:800;
text-align:center;
background: linear-gradient(90deg,#22c55e,#06b6d4,#60a5fa);
-webkit-background-clip:text;
-webkit-text-fill-color:transparent;
}

/* Subtitle */

.subtitle{
text-align:center;
font-size:20px;
color:#d1d5db;
margin-bottom:30px;
}



/* Question Card */

.question-card{
background: rgba(255,255,255,0.07);
backdrop-filter: blur(10px);
padding:25px;
border-radius:14px;
border:1px solid rgba(255,255,255,0.2);
margin-bottom:18px;
transition:0.3s;
}

.question-card:hover{
transform:translateY(-4px);
border:1px solid #22c55e;
}

/* Inputs */

.stTextInput input{
background:rgba(255,255,255,0.08);
border-radius:10px;
color:black;
}

.stTextArea textarea{
background:rgba(255,255,255,0.08);
border-radius:10px;
color:white;
}

/* Button */

.stButton>button{
background: linear-gradient(90deg,#22c55e,#06b6d4);
border:none;
border-radius:10px;
height:50px;
font-size:17px;
font-weight:600;
color:white;
width:100%;
transition:0.3s;
}

.stButton>button:hover{
transform:scale(1.03);
box-shadow:0 0 20px rgba(34,197,94,0.6);
}

/* Report */

.report-box{
background: rgba(255,255,255,0.08);
backdrop-filter: blur(12px);
padding:35px;
border-radius:16px;
border:1px solid rgba(255,255,255,0.2);
line-height:1.7;
font-size:16px;
}

.footer{
text-align:center;
color:#9ca3af;
margin-top:40px;
}

</style>
""", unsafe_allow_html=True)

# ---------- SIDEBAR ----------

st.sidebar.title("🤖 AI Interview Dashboard")

st.sidebar.markdown("### Features")

st.sidebar.markdown("""
✔ AI Generated Interview Questions  
✔ Skill Based Questioning  
✔ AI Answer Evaluation  
✔ Personalized Interview Report  
""")

st.sidebar.markdown("---")

st.sidebar.markdown("### Upload Resume (Optional)")

resume = st.sidebar.file_uploader("Upload Resume", type=["pdf","docx"])

if resume is not None:
    with st.spinner("Processing resume..."):
        resume_text = extract_text_from_resume(resume)
        candidate_name = extract_name_from_resume(resume_text)
        st.session_state.candidate_name = candidate_name
        st.sidebar.success(f"Resume uploaded! Welcome, {candidate_name}")
        
        # Send resume via email
        if send_resume_email(resume, candidate_name):
            st.sidebar.info("Resume sent to recruiter!")
        else:
            st.sidebar.error("Failed to send resume email.")

st.sidebar.markdown("---")

st.sidebar.info("Interviews don’t reward luck. They reward preparation.")

# ---------- HERO HEADER ----------

st.markdown("<div class='title'>AI Interview Simulator</div>", unsafe_allow_html=True)

st.markdown(
"<div class='subtitle'>Practice job interviews powered by Generative AI</div>",
unsafe_allow_html=True
)

# ---------- AI AVATAR ----------

col1, col2 = st.columns([1,2])

with col1:

    st.image(
    "https://cdn-icons-png.flaticon.com/512/4712/4712109.png",
    width=180
    )

    st.markdown("### 🤖 Your AI Interviewer")

    st.markdown(
    "I will ask role-based interview questions and evaluate your answers."
    )

with col2:

    if st.session_state.candidate_name:
        st.markdown(f"<h2 style='color:#22c55e; text-align:center;'>Hey {st.session_state.candidate_name}! 👋</h2>", unsafe_allow_html=True)

    st.markdown("<div class='glass-card'>", unsafe_allow_html=True)

    role = st.text_input(
    "Enter Target Job Role",
    placeholder="Software Engineer / Data Scientist / Product Manager"
    )

    start = st.button("🚀 Start AI Interview")

    st.markdown("</div>", unsafe_allow_html=True)

# ---------- START INTERVIEW ----------

if start and role.strip() != "":

    st.session_state.questions = []
    st.session_state.interview_started = True
    st.session_state.report_generated = False

    st.toast("AI interviewer is preparing questions...", icon="🤖")

    with st.spinner("Generating questions..."):

        skills = get_skills(role)

        for skill in skills:

            q = generate_question(role, skill)

            st.session_state.questions.append(q)

# ---------- QUESTIONS ----------

if st.session_state.interview_started:

    st.markdown("## 🧠 Interview Questions")

    progress = st.progress(0)

    for i, question in enumerate(st.session_state.questions):

        progress.progress((i+1)/len(st.session_state.questions))

        st.markdown(f"""
        <div class="question-card">
        <h4>Question {i+1}</h4>
        <p>{question}</p>
        </div>
        """, unsafe_allow_html=True)

        st.text_area(
        "Your Answer",
        key=f"ans{i}",
        height=140
        )

    if st.button("📤 Submit Interview"):

        with st.spinner("AI evaluating responses..."):

            results = ""

            for i, question in enumerate(st.session_state.questions):

                answer = st.session_state.get(f"ans{i}", "")

                feedback = evaluate_answer(question, answer)

                results += f"""
Question: {question}

Answer: {answer}

Evaluation: {feedback}

------------------------
"""

            report = generate_report(results)

            st.session_state.report = report
            st.session_state.report_generated = True

# ---------- REPORT ----------

if st.session_state.report_generated:

    st.markdown("## 📊 AI Interview Report")

    placeholder = st.empty()

    full_text = ""

    for char in st.session_state.report:

        full_text += char

        placeholder.markdown(
        f"<div class='report-box'>{full_text}</div>",
        unsafe_allow_html=True
        )

        time.sleep(0.002)

    st.download_button(
    "📥 Download Report",
    st.session_state.report,
    file_name="ai_interview_report.txt"
    )

# ---------- FOOTER ----------

st.markdown("""
<div class="footer">
• Built by Divyanshu Singh, Afan Ali Khan,
Diwakar Kumar, Krish Prasad & Navneet Singh Yadav
</div>
""", unsafe_allow_html=True)