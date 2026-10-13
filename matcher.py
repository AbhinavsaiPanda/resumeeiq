
import re
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity


SKILLS = [
    "python", "java", "sql", "mysql", "mongodb",
    "flask", "django", "fastapi", "html", "css",
    "javascript", "react", "node.js", "express.js",
    "pandas", "numpy", "scikit-learn", "machine learning",
    "data analysis", "power bi", "tableau", "excel",
    "git", "github", "rest api", "api development",
    "data structures", "algorithms", "oops",
    "communication", "problem solving", "testing",
    "selenium", "pytest", "aws", "docker"
]


def find_skills(text):
    text = text.lower()
    found = []

    for skill in SKILLS:
        pattern = r"(?<!\w)" + re.escape(skill) + r"(?!\w)"
        if re.search(pattern, text):
            found.append(skill)

    return sorted(set(found))


def analyze_resume(resume_text, job_description):
    resume_text = resume_text.strip()
    job_description = job_description.strip()

    if not resume_text or not job_description:
        raise ValueError("Resume text and job description are required.")

    vectorizer = TfidfVectorizer(stop_words="english")
    vectors = vectorizer.fit_transform(
        [resume_text, job_description]
    )

    similarity = cosine_similarity(vectors[0:1], vectors[1:2])[0][0]
    match_score = round(float(similarity) * 100, 2)

    resume_skills = find_skills(resume_text)
    job_skills = find_skills(job_description)

    matched_skills = [
        skill for skill in job_skills if skill in resume_skills
    ]
    missing_keywords = [
        skill for skill in job_skills if skill not in resume_skills
    ]

    suggestions = []

    if missing_keywords:
        suggestions.append(
            "Review the job requirements and add relevant skills "
            "or experience to your resume only when accurate."
        )

    if not matched_skills:
        suggestions.append(
            "Check whether your resume clearly describes your "
            "relevant technical skills and projects."
        )

    if not suggestions:
        suggestions.append(
            "Your listed skills overlap with the job description. "
            "Review your project achievements and experience for clarity."
        )

    return {
        "match_score": match_score,
        "matched_skills": matched_skills,
        "missing_keywords": missing_keywords,
        "suggestions": suggestions,
    }
