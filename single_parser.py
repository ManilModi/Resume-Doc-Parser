import os
import pymupdf
import re
import psycopg2

FILE_PATH = "CVs/upal_cv.pdf"
OUTPUT_FOLDER = "output"

os.makedirs(OUTPUT_FOLDER, exist_ok=True)

def extract_text_from_pdf(path):
    try:
        doc = pymupdf.open(path)
        text = ""
        for page in doc:
            text += page.get_text() + "\n"
        return text
    except Exception as e:
        print(f"Failed to read PDF {path}: {e}")
        return None

def parse_document(file_path):
    filename = os.path.basename(file_path)

    if filename.endswith(".pdf") or filename.endswith(".docx"):
        text = extract_text_from_pdf(file_path)
    else:
        print(f"Unsupported file type: {filename}")
        return None

    if text:
        output_filename = f"{os.path.splitext(filename)[0]}_output.txt"
        out_path = os.path.join(OUTPUT_FOLDER, output_filename)

        with open(out_path, "w", encoding="utf8") as out:
            out.write(text)
        print(f"Text saved to: {out_path}")
        return text
    else:
        return None

def extract_info(text):
    
    info = {}
        
    lines = [line.strip() for line in text.split("\n") if line.strip()]
    
    #NAME
    
    name_match = next((re.search(r'^Name\s*:\s*(.+)', line) for line in lines if re.search(r'^Name\s*:\s*(.+)', line)), None)
    if name_match:
        info["Name"] = name_match.group(1).strip()
    else:
        probable_names = [line for line in lines[:5] if line.istitle() or len(line.split()) <= 4]
        try:
            info["Name"] = probable_names[0] if probable_names else lines[0]
        except Exception as e:
            print(f"Resume contains image data {e}")

    # DESIGNATION
    exp_start = -1
    for i, line in enumerate(lines):
        if re.match(r"^(experience|work experience|PROFESSIONAL EXPERIENCE|Role|working experience)\s*$", line, re.IGNORECASE):
            exp_start = i + 1
            break

    if exp_start != -1:
        experience_block = "\n".join(lines[exp_start:exp_start + 5])
        short_exp = " ".join(lines[exp_start:exp_start + 2]).strip()
        info["Designation"] = short_exp

        designation_keywords = ["developer", "engineer", "analyst", "manager", "consultant", "architect", "lead"]
        for line in lines[exp_start:exp_start + 10]:
            for keyword in designation_keywords:
                if keyword.lower() in line.lower():
                    info["Designation"] = line.strip()
                    break
    else:
        des_match = next((re.search(r"(ROLE|working as|currently a|serving as|I am a)\s*[:\-]?\s*([A-Za-z\s,&]+)", line, re.IGNORECASE) 
        for line in lines), None)
        if des_match:
            info["Designation"] = des_match.group(2).strip()

    # SKILLS
    
    skills_found = False
    skills = []

    for i, line in enumerate(lines):
        match = re.match(r"^(skills|technical skills|key COMPETENCIES)\s*[:\-]*\s*$", line.strip(), re.IGNORECASE)
        if match:
            collected_lines = []
            for next_line in lines[i+1:]:
                next_line = next_line.strip()
                if re.match(r"^(PROJECT|EXPERIENCE|SUMMARY|ACHIEVEMENTS|CERTIFICATES?)\b", next_line, re.IGNORECASE):
                    break
                if next_line != "":
                    collected_lines.append(next_line)
            combined_text = ' '.join(collected_lines)
            skills = re.split(r"[,•\n]", combined_text)
            info["Skills"] = [s.strip() for s in skills if len(s.strip()) > 1]
            skills_found = True
            break

    if not skills_found:
        info["Skills"] = []



    # EXPERIENCE DURATION
    pattern = re.compile(r"(\d+(\.\d+)?\s*\+?\s*(years?|yrs?|months?))", re.IGNORECASE)
    exp_match = next((match for line in lines if (match := pattern.search(line))), None)
    info["Total Experience"] = exp_match.group(0) if exp_match else ""

    # COMPANY
    company_block = ""
    for i, line in enumerate(lines):
        if re.match(r"^(experience|work experience|intern|professional experience|working experience)\s*$", line, re.IGNORECASE):
            company_block = "\n".join(lines[i+1:i+6])
            break
    info["Company"] = company_block.strip() if company_block else ""

    # PROJECTS
    project_block = ""

    project_lines = []
    capture = False

    for line in lines:
        if re.match(r"^\d+\.\s+[\w\s()/-]+$", line.strip()) or re.match(r"^(projects?|project work|project|technical projects|projects detail|projects).*?$", line.strip(), re.IGNORECASE):


            capture = True
            project_lines.append(line.strip())
            continue

        if capture and (re.match(r"^[A-Z\s]{3,}$", line.strip()) or re.match(r"^[\w\s]+:$", line.strip())):
            break

        if capture:
            project_lines.append(line.strip())

    if project_lines:
        projects_text = " ".join(project_lines)
    

        split_projects = re.split(r"\n(?=\d+\.\s)", projects_text)
        info["Projects"] = [proj.strip() for proj in split_projects if proj.strip()]
    else:
        info["Projects"] = []


    # ACHIEVEMENTS
    achievements_line = next((line for line in lines if re.search(r"(achievements|certification|awards)", line, re.IGNORECASE)), "")
    if achievements_line:
        achievements_text = achievements_line
        idx = lines.index(achievements_line)
        achievements_text += " " + " ".join(lines[idx+1:idx+5])
        info["Achievements"] = re.sub(r'\n+', ' ', achievements_text.strip())
    else:
        info["Achievements"] = ""

    return info

# Run
text = parse_document(FILE_PATH)

if text:
    info = extract_info(text)
    for key, value in info.items():
        print(f"{key}: {value}\n")


