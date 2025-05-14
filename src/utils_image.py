from unstructured.partition.pdf import partition_pdf
import os
import re
import pandas as pd

def fix_malformed_headers(text):
    def normalize_headers(match):
        return match.group(0).replace(" ", "")
    
    pattern = r'\b(?:[A-Z]\s+){1,5}[A-Z]\b'
    return re.sub(pattern, normalize_headers, text)

def image_resume_parsing(pdf_path):
    elements = partition_pdf(
        filename=pdf_path,
        extract_images_in_pdf=True,
        ocr_languages="eng",
        strategy="hi_res"
    )

    full_text = "\n".join([str(element) for element in elements])

    full_text = full_text.replace(")", "S")

    full_text = fix_malformed_headers(full_text)

    print(full_text)

    output_dir = "output"
    os.makedirs(output_dir, exist_ok=True)

    base_filename = os.path.basename(pdf_path)
    output_filename = os.path.splitext(base_filename)[0] + "_output.txt"
    output_path = os.path.join(output_dir, output_filename)

    with open(output_path, "w", encoding="utf-8") as f:
        f.write(full_text)

    print(f"Text extracted and saved to: {output_path}")
    return full_text


def extract_info(text, filename):
    
    info = {}
        
    lines = [line.strip() for line in text.split("\n") if line.strip()]
    
    #NAME
    
    name_pattern = re.compile(
    r"""
    (?:[¢•\-\s]*)?
    (?:Full\s*Name|Name|Personal\s*Information)\s*[:\-]?\s*
    (?P<name>
        (?:Mr|Mrs|Ms|Miss|Dr|Er)?\.?\s*
        [A-Z][a-z]+(?:\s+[A-Z][a-z]+){1,3}
        (?:\s*\(.*?\))?
    )
    """,
    re.IGNORECASE | re.VERBOSE
)



    matches = [match.group().strip() for line in lines for match in name_pattern.finditer(line)]

    if matches:
        info["Name"] = matches[0]

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

    
    df = pd.DataFrame([info])
    
    os.makedirs("info_json", exist_ok=True)
    base_filename = os.path.splitext(os.path.basename(filename))[0]
    json_path = os.path.join("info_json", f"{base_filename}.json")
    df.to_json(json_path, orient="records", indent=4)

    print(f"Info saved to CSV: {json_path}")
    
    return info