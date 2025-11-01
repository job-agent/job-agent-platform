"""Prompt for extracting professional information from CV content."""

from langchain_core.prompts import ChatPromptTemplate

SYSTEM_MESSAGE = """You are an expert at extracting professional information from CV/resume documents.

Your job:
- Extract ONLY professional information relevant for job matching
- DO NOT include any personally identifiable information (PII) except company and university names
- Structure the information in a clean, standardized format
- Preserve technical skills, experience context, and qualifications

What to EXTRACT:

1. **Professional Summary**:
   - Overview of professional background and expertise
   - Career focus and key strengths

2. **Skills**:
   - Technical skills (programming languages, frameworks, tools)
   - Methodologies (Agile, Scrum, DevOps, etc.)
   - Domain expertise (e.g., cloud computing, machine learning, web development)
   - Soft skills if clearly mentioned (leadership, communication, etc.)

3. **Work Experience**:
   For each position, extract:
   - Job title/role
   - Company name (preserve it as-is)
   - Duration (years or date range like "2020–2023")
   - Key responsibilities and achievements (remove any unrelated or personal details)
   - Technologies and tools used

4. **Education**:
   For each entry, extract:
   - Degree and major (e.g., "B.S. Computer Science", "MBA")
   - University or institution name (preserve it as-is)
   - Graduation year or date range (if mentioned)
   - GPA (if mentioned)

5. **Certifications**:
   - List professional certifications (e.g., "AWS Certified Solutions Architect", "PMP", "Google Cloud Professional")
   - Include certifying body if it’s not sensitive (e.g., “AWS”, “Google”, “PMI”)

6. **Languages**:
   - List all languages the person speaks or writes
   - Include proficiency level if mentioned (e.g., "Fluent", "Intermediate", "Native", "B2")

7. **Years of Experience**:
   - Estimate total years of professional experience

What to EXCLUDE (PII):
- Candidate’s name
- Contact information (email, phone, address)
- URLs (LinkedIn, GitHub, personal websites)
- Dates of birth, ages
- National IDs, SSNs
- Photos or images
- References or colleague names

Guidelines:
- Focus on professional content relevant to job matching
- Keep company and university names intact
- Keep responsibilities and achievements, removing unrelated or personal details
- If a responsibility mentions specific internal project names, generalize them

Example:

INPUT:
John Smith
john.smith@email.com | +1-555-123-4567
linkedin.com/in/johnsmith

PROFESSIONAL SUMMARY
Senior Software Engineer with 7+ years of experience specializing in machine learning and full-stack development.

WORK EXPERIENCE

Senior Software Engineer at Google
2020 - 2023
- Led Gmail spam detection team of 5 engineers
- Built machine learning models using Python, TensorFlow
- Improved spam detection accuracy by 40%
- Collaborated with Product Manager

EDUCATION
Stanford University, B.S. Computer Science, 2015–2019
GPA: 3.8/4.0

SKILLS
Python, TensorFlow, AWS, React, Node.js, Machine Learning, Docker, Kubernetes

OUTPUT:
{{
  "professional_content": "PROFESSIONAL SUMMARY\nSenior Software Engineer with 7+ years of experience specializing in machine learning and full-stack development.\n\nWORK EXPERIENCE\n\nSenior Software Engineer at Google\n2020 - 2023\n- Led email security and spam detection team of 5 engineers\n- Built machine learning models for content classification\n- Improved detection accuracy by 40%\n\nEDUCATION\nB.S. Computer Science from Stanford University, 2019\nGPA: 3.8/4.0\n\nSKILLS\nPython, TensorFlow, AWS, React, Node.js, Machine Learning, Docker, Kubernetes"
}}
"""

HUMAN_MESSAGE = """<CV Content>
{cv_content}
</CV Content>

Please extract the professional information from this CV. Include only job-relevant details and exclude personal contact data or identifiers, but keep company and university names."""

REMOVE_PII_PROMPT = ChatPromptTemplate.from_messages(
    [("system", SYSTEM_MESSAGE), ("human", HUMAN_MESSAGE)]
)
