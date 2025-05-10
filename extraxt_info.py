import os
import re

def extract_info(text_file_path):
    
    info = {}
    
    with open(text_file_path, 'r', encoding='utf8') as file:
        text = file.read()
        
    lines = [line.strip() for line in text.split("\n") if line.strip()]
    
    name_match = next((re.search(r'^Name\s*:\s*(.+)', line) for line in lines if re.search(r'^Name\s*:\s*(.+)', line)), None)
    if name_match:
        info["Name"] = name_match.group(1).strip()
    else:
        probable_names = [line for line in lines[:5] if line.istitle() or len(line.split()) <= 4]
        info["Name"] = probable_names[0] if probable_names else lines[0]

    # DESIGNATION
    exp_start = -1
    for i, line in enumerate(lines):
        if re.match(r"^(experience|work experience|PROFESSIONAL EXPERIENCE)\s*$", line, re.IGNORECASE):
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
        des_match = next((re.search(r"(working as|currently a|serving as|I am a|Role)\s+([A-Za-z\s,&]+)", line, re.IGNORECASE) for line in lines), None)
        if des_match:
            info["Designation"] = des_match.group(2).strip()

    # SKILLS
    skills_found = False
    skills = []

    for i, line in enumerate(lines):
        match = re.match(r"^(skills|technical skills|technical)\s*[:\-]*\s*(.*)$", line, re.IGNORECASE)
        if match:
            skills_text = match.group(2).strip()
        # Collect next few lines just in case more skills are listed
            for next_line in lines[i+1:i+5]:
                if next_line.strip() == "" or re.match(r"^[A-Z][A-Za-z\s]{2,}$", next_line):  # heading or empty
                    break
                skills_text += " " + next_line.strip()
            skills = re.split(r"[,•]", skills_text)
            info["Skills"] = [s.strip() for s in skills if len(s.strip()) > 1]
            skills_found = True
            break

    if not skills_found:
        info["Skills"] = []


    # EXPERIENCE DURATION
    exp_match = next((re.search(r"(\d+(\.\d+)?\s*\+?\s*(years|year|months))", line, re.IGNORECASE) for line in lines), None)
    info["Total Experience"] = exp_match.group(0) if exp_match else ""

    # COMPANY
    company_block = ""
    for i, line in enumerate(lines):
        if re.match(r"^(experience|work experience|intern|professional experience)\s*$", line, re.IGNORECASE):
            company_block = "\n".join(lines[i+1:i+6])
            break
    info["Company"] = company_block.strip() if company_block else ""

    # PROJECTS
    project_block = ""
    for i, line in enumerate(lines):
        if re.match(r"^(projects?|project work)\s*$", line, re.IGNORECASE):
            project_block = "\n".join(lines[i+1:i+10])
            break

    if project_block:
        titles = re.findall(r"(?m)^(?![\s•\-])[\w\s&():/]{0,100}$", project_block)
        info["Projects"] = [t.strip() for t in titles if t.strip()]
    else:
        fallback = next((re.search(r"(?i)(projects?.{0,300})", line) for line in lines if "project" in line.lower()), None)
        info["Projects"] = fallback.group(1).strip() if fallback else ""

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

info = extract_info("output/extracted_text.txt")
for key, value in info.items():
    print(f"{key}: {value}\n")
