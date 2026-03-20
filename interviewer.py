from groq import Groq
import os
from dotenv import load_dotenv
import pdfplumber
import docx
import time
time.sleep(0.7)

# Load environment variables
load_dotenv()

# Create Groq client
import streamlit as st

api_key = os.getenv("GROQ_API_KEY") or st.secrets["GROQ_API_KEY"]

client = Groq(api_key=api_key)

# -------------------------
# LLM CALL FUNCTION
# -------------------------

def ask_llm(prompt):
    try:
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {"role": "system", "content": "You are a professional technical interviewer."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.3,
            max_tokens=400
        )

        return response.choices[0].message.content

    except Exception as e:
        return f"Error generating AI response: {str(e)}"


# -------------------------
# SKILL EXTRACTION
# -------------------------

def get_skills(role):

    prompt = f"""
You are a senior technical recruiter and industry hiring expert.

Your task is to identify the MOST IMPORTANT technical skills required for the job role below.

Job Role: {role}

Rules:
- List exactly 5 skills.
- Only technical skills.
- No explanations.
- Return them as comma-separated values.

Example format:
Python, Data Structures, SQL, Machine Learning, Statistics
"""

    response = ask_llm(prompt)

    skills = response.replace("\n", ",").split(",")
    skills = [s.strip(" .0123456789") for s in skills if s.strip()]
    return skills[:5]


# -------------------------
# QUESTION GENERATION
# -------------------------

def generate_question(role, skill):

    prompt = f"""
You are a senior technical interviewer at a top technology company.

Generate ONE realistic interview question.

Role: {role}
Skill being tested: {skill}

Requirements:
- Medium difficulty
- Prefer scenario or problem-solving questions
- Avoid simple definitions
- Sound like a real interviewer

Return ONLY the question.
"""

    return ask_llm(prompt)


# -------------------------
# ANSWER EVALUATION
# -------------------------

def evaluate_answer(question, answer):

    if not answer.strip():
        return "Score: 0\nFeedback: No answer provided."

    prompt = f"""
You are a strict technical interviewer evaluating a candidate.

Question:
{question}

Candidate Answer:
{answer}

Evaluate the answer critically.

Scoring Guidelines:
10 = Excellent, precise, expert-level understanding
7–9 = Good understanding with minor gaps
4–6 = Partial understanding
1–3 = Poor understanding
0 = Completely incorrect or irrelevant

Return your evaluation STRICTLY in this format:

Score: <number out of 10>

Feedback:
- One sentence explaining what was correct
- One sentence explaining what was missing
- One suggestion to improve the answer
"""

    return ask_llm(prompt)


# -------------------------
# REPORT GENERATION
# -------------------------

def generate_report(results):

    prompt = f"""
You are a senior hiring manager reviewing an AI interview evaluation.

Candidate Results:
{results}

Generate a professional interview report.

Structure the report as:

Overall Performance:
A short summary of the candidate's interview quality.

Strengths:
Bullet points describing strong areas.

Weak Areas:
Bullet points describing knowledge gaps.

Hiring Recommendation:
Choose one:
- Strong Hire
- Hire
- Borderline
- No Hire

Keep the report professional and concise.
"""

    return ask_llm(prompt)


# -------------------------
# RESUME TEXT EXTRACTION
# -------------------------

def extract_text_from_resume(file):

    if file.name.endswith(".pdf"):

        text = ""

        with pdfplumber.open(file) as pdf:
            for page in pdf.pages:
                page_text = page.extract_text()
                if page_text:
                    text += page_text

        return text

    elif file.name.endswith(".docx"):

        doc = docx.Document(file)
        text = ""

        for para in doc.paragraphs:
            text += para.text

        return text

    return ""


# -------------------------
# NAME EXTRACTION
# -------------------------

def extract_name_from_resume(text):

    prompt = f"""
    Extract the candidate's full name.
    The name usually appears at the top of the resume.
    Return only the full name.

Rules:
- Return ONLY the name
- Do not include titles like Mr, Ms, Dr
- Do not include explanations

Resume Text:
{text}
"""

    return ask_llm(prompt)