# 🧠 Resume Doc Parser

A Python-based resume parser that processes resumes in PDF format, extracts key information using text extraction and regex techniques, and stores the data in a PostgreSQL database.

---

## 📌 Objective

Automatically extract structured information from resumes including:
- Name
- Designation
- Skills
- Total Experience
- Current Company
- Project Descriptions
- Achievements

---

## 🛠 Tech Stack

- **Python**: Scripting and data processing
- **PyMuPDF (fitz)**: PDF text extraction
- **psycopg2**: PostgreSQL connector for Python
- **PostgreSQL**: Database for storing structured resume data
- **Regular Expressions (`re`)**: For identifying and extracting patterns from text

---

## 📂 File Handling & Text Extraction

### Supported File Types
- `.pdf` and `.docx`  
> ⚠️ `.doc` files are deprecated and **not supported**


## 🔍 Information Extraction using Regex
Fields Extracted:
- Name: Captures Name: or the first non-empty line

- Designation: Matches known titles or keywords like "currently a", "working as"

- Skills: Extracts from sections titled "Skills", "Technical Skills", etc.

- Experience: Matches time durations like "3+ years", "18 months", etc.

- Company: Pulled from "Experience", "Intern", or "Professional Experience" sections

- Projects: Looks for sections titled "Projects", "Technical Projects"

- Achievements: Detects sections like "Achievements", "Awards", or "Certifications"


## 🏁 Getting Started

1. Clone the repo
   ```bash 
     git clone https://github.com/ManilModi/Resume-Doc-Parser.git
     cd Resume-Doc-Parser
     ```
2. Run the script
   ```bash
    python db_conn.py

   ```
