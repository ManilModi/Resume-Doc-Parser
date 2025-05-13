from sentence_transformers import SentenceTransformer, util
import fitz
import os
from image_parsing import image_resume_parsing
import re
from single_parser import extract_info

pdf_path = "CVs/Mruga shah.pdf"
output_folder = "segment_output"
os.makedirs(output_folder, exist_ok=True)

has_image=False

model = SentenceTransformer('all-MiniLM-L6-v2')

target_headers = {
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


header_embeddings = {
    k: model.encode(v, convert_to_tensor=True)
    for k, v in target_headers.items()
}

def extract_sections_with_embeddings(pdf_path):
    has_images = False

    if pdf_path.endswith(".pdf") or pdf_path.endswith(".docx"):
        doc = fitz.open(pdf_path)
        all_lines = []

        for page_num in range(len(doc)):
            page = doc[page_num]
            image_list = page.get_images(full=True)

            if image_list:
                has_images = True
                print(f"Page {page_num + 1} has {len(image_list)} image(s).")
                text = image_resume_parsing(pdf_path)
                return text, has_images

        for page in doc:
            all_lines += [line.strip() for line in page.get_text().splitlines() if line.strip()]

        sections = {}
        current_section = "Other"

        for line in all_lines:
            line_embedding = model.encode(line, convert_to_tensor=True)
            scores = {
                section: util.cos_sim(line_embedding, emb).item()
                for section, emb in header_embeddings.items()
            }

            best_match, best_score = max(scores.items(), key=lambda x: x[1])
            if best_score > 0.65:
                current_section = best_match
                if current_section not in sections:
                    sections[current_section] = []
                continue

            sections.setdefault(current_section, []).append(line)

        return {k: "\n".join(v).strip() for k, v in sections.items() if v}, has_images
    else:
        print(f"Unsupported file type: {pdf_path}")
        return {}, has_images


def segment_text_file(pdf_path):
    sections, has_image = extract_sections_with_embeddings(pdf_path)

    if has_image:
        return image_resume_parsing(pdf_path), has_image

    all_section_content = ""
    for heading, content in sections.items():
        all_section_content += f"------{heading}------------\n{content}\n\n"

    combined_output_path = os.path.join(output_folder, f"{os.path.splitext(os.path.basename(pdf_path))[0]}_combined_sections.txt")

    with open(combined_output_path, "w", encoding="utf-8") as f:
        f.write(all_section_content)
    print(f"All header sections saved in '{combined_output_path}' file.")
    
    return all_section_content, has_image

    


def extract_info_from_segmented_text(segmented_text):
    info = {}

    sections = re.split(r"-{6,}(.*?)\-{6,}", segmented_text)

    section_dict = {}
    for i in range(1, len(sections), 2):
        header = sections[i].strip().lower()
        content = sections[i+1].strip()
        section_dict[header] = content

    
    # NAME
    name = ""
    other = section_dict.get("other", "").strip()

    if other:
        first_line = next((line.strip() for line in other.splitlines() if line.strip()), "")
        name_match = re.search(r"\b([A-Z][a-z]+(?:\s[A-Z][a-z]+){0,3})\b", first_line)
        if name_match:
            name = name_match.group(1)
    else:
        lines = [line.strip() for line in segmented_text.splitlines() if line.strip()]
        first_lines = " ".join(lines[:3])
        name_match = re.search(r"\b([A-Z][a-z]+(?:\s[A-Z][a-z]+){0,3})\b", first_lines)
        if name_match:
            name = name_match.group(1)

    if name:
        info["Name"] = name


    # Designation
    experience = section_dict.get("experience", "") or section_dict.get("work experience", "")
    if experience:
        designation_keywords = ["developer", "engineer", "analyst", "manager", "consultant", "architect", "lead"]
        for line in experience.splitlines():
            for keyword in designation_keywords:
                if keyword.lower() in line.lower():
                    info["Designation"] = line.strip()
                    break
            if "Designation" in info:
                break

    # Skills
    skills = section_dict.get("skills", "")
    skills_list = re.split(r"[,•\n]", skills)
    info["Skills"] = [s.strip() for s in skills_list if len(s.strip()) > 1]

    # Company
    company_lines = experience.splitlines()[:5]
    info["Company"] = next((line for line in company_lines if re.search(r'\b(Inc|Ltd|Technologies|Solutions|Company|Corp|Pvt|LLC|Infosys|Wipro|TCS|Google|Microsoft)\b', line, re.IGNORECASE)), "")

    # Projects
    projects = section_dict.get("projects", "")
    split_projects = re.split(r"\n(?=\d+\.\s)", projects)
    info["Projects"] = [proj.strip() for proj in split_projects if proj.strip()]

    # Achievements, Certifications, Courses, Awards
    achievement_keywords = [
        "achievements", 
        "key achievements or awards", 
        "certifications", 
        "certification", 
        "courses", 
        "awards"
    ]

    achievements_text = ""
    for key in achievement_keywords:
        if key in section_dict:
            achievements_text = section_dict[key]
            break

    info["Achievements"] = achievements_text.strip()

    
    # Total Experience
    exp_match = re.search(r"(\d+(\.\d+)?\s*\+?\s*(years?|yrs?|months?))", experience, re.IGNORECASE)
    info["Total Experience"] = exp_match.group(0) if exp_match else ""

    return info

text, has_image = segment_text_file(pdf_path)

if has_image:
    info = extract_info(text)
else:
    info = extract_info_from_segmented_text(text)

print("\nExtracted Resume Info:")
for k, v in info.items():
    print(f"{k}: {v}")
