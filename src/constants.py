# constants.py

MODEL_NAME = "all-MiniLM-L6-v2"

TARGET_HEADERS = {
    "Skills": "skills",
    "Projects": "projects",
    "Experience": "work experience",
    "Certifications": "certifications and courses",
    "Education": "educational background",
    "Designation": "designation",
    "Company": "company or organization",
    "Achievements": "key achievements or awards",
    "Personal Details": "personal information such as name, email, phone number, address"
}

DESIGNATION_KEYWORDS = [
    "developer", "engineer", "analyst", "manager", "consultant", "architect", "lead"
]

#DATABASE

HOST = "localhost"
DATABASE = "resume_parser"
USER = "postgres"
PASSWORD = "root"