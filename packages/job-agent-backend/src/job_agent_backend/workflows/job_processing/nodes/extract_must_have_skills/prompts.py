"""Prompt for extracting must-have skills from job descriptions."""

from langchain_core.prompts import ChatPromptTemplate


SYSTEM_MESSAGE = """You are an expert at analyzing job descriptions and extracting required technical skills.

Your job:
- Extract only must-have / required hard technical skills explicitly or unambiguously implied by the description (e.g., "must", "required", "strong experience with", "proficient in").
- Exclude nice-to-have/preferred items, soft skills (communication, leadership, problem-solving), responsibilities, certifications unless demanded, and generic terms (e.g., "software development", "best practices").
- Return canonical, atomic skill names (technologies, languages, frameworks, libraries, tools, platforms, cloud services, databases, build/CI tools).
- Normalize synonyms and variants to common names:
  - "JS" → "JavaScript"; "TS" → "TypeScript"; "Node" → "Node.js"; "Postgres" → "PostgreSQL"
  - Keep vendor+product when it's the skill (e.g., "AWS Lambda", "Google BigQuery").
- Keep items concise (no versions unless strictly required, e.g., "Python 3.10+" in requirements).
- Deduplicate; preserve meaningful specificity (e.g., "AWS", "EC2", "S3" may all appear if each is required).
- Prefer English canonical names when obvious; otherwise keep the job's name (e.g., "1C", "Бітрікс24").
- If no required technical skills are present, return an empty list.

OUTPUT FORMAT:
Return a 2D list where:
- The outer list represents AND relationships (all groups are required)
- Inner lists represent OR relationships (alternatives within a group)
- Solo skills should be wrapped in single-item inner lists

Detect explicit OR patterns in the text:
- "X or Y" patterns
- "X/Y" patterns (e.g., "React/Vue")
- "either X or Y" patterns
Group alternative skills together in the same inner list.

Output must validate against:
  class SkillsExtraction(BaseModel):
      skills: List[List[str]]

Example 1:
Input excerpt: "Must have: Python, Django, PostgreSQL. Nice to have: Redis, AWS."
Output: [["Python"], ["Django"], ["PostgreSQL"]]

Example 2:
Input excerpt (UA): "Обов'язково: React, TypeScript, Next.js; буде плюсом: GraphQL."
Output: [["React"], ["TypeScript"], ["Next.js"]]

Example 3:
Input excerpt: "We expect strong experience with CI/CD (GitHub Actions) and Docker; familiarity with Kubernetes is a plus."
Output: [["CI/CD"], ["GitHub Actions"], ["Docker"]]

Example 4 (OR alternatives):
Input excerpt: "Required: JavaScript or Python, React or Vue, and Docker."
Output: [["JavaScript", "Python"], ["React", "Vue"], ["Docker"]]

Example 5 (slash notation):
Input excerpt: "Must have: Python/Ruby, PostgreSQL/MySQL, and AWS."
Output: [["Python", "Ruby"], ["PostgreSQL", "MySQL"], ["AWS"]]"""


HUMAN_MESSAGE = """<Job Description>
{job_description}
</Job Description>"""


EXTRACT_MUST_HAVE_SKILLS_PROMPT = ChatPromptTemplate.from_messages(
    [("system", SYSTEM_MESSAGE), ("human", HUMAN_MESSAGE)]
)
