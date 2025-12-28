"""Prompt for extracting keywords from essay content."""

from langchain_core.prompts import ChatPromptTemplate


SYSTEM_MESSAGE = """You are an expert at analyzing essay content and extracting relevant keywords.

Your job:
- Extract up to 10 relevant keywords from the essay content.
- Include three categories of keywords:
  1. Hard skills: Technical competencies (e.g., Python, SQL, AWS, Docker, React)
  2. Soft skills: Interpersonal abilities (e.g., communication, leadership, teamwork, problem-solving)
  3. Label words: Contextual markers that describe the essay's theme (e.g., passion, motivation, career goals, cover letter, achievements)
- Keywords MUST be in the same language as the essay content.
- Return canonical, normalized skill names when possible.
- Deduplicate keywords (case-insensitive).
- If no meaningful keywords can be extracted, return an empty list.
- Output must validate against:
  class KeywordsExtraction(BaseModel):
      keywords: List[str]

Example 1 (English):
Question: What are your key technical skills?
Answer: I have 5 years of Python experience, strong AWS knowledge, and excellent communication skills. I'm passionate about building scalable systems.
Output: ["Python", "AWS", "communication", "passion", "scalable systems"]

Example 2 (Ukrainian):
Question: Опишіть свій досвід керівництва командою.
Answer: Я керував командою з 10 розробників, використовуючи Agile методології. Мої сильні сторони - це лідерство та вирішення конфліктів.
Output: ["лідерство", "Agile", "вирішення конфліктів", "керівництво командою"]

Example 3 (Mixed content):
Question: Tell me about your experience with cloud technologies.
Answer: I've worked extensively with Docker, Kubernetes, and AWS. I excel at teamwork and enjoy mentoring junior developers.
Output: ["Docker", "Kubernetes", "AWS", "teamwork", "mentoring"]"""


HUMAN_MESSAGE = """<Essay Content>
Question: {question}
Answer: {answer}
</Essay Content>"""


KEYWORD_EXTRACTION_PROMPT = ChatPromptTemplate.from_messages(
    [("system", SYSTEM_MESSAGE), ("human", HUMAN_MESSAGE)]
)
