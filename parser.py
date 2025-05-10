import os
import pymupdf


FOLDER_PATH = "CVs"
OUTPUT_FOLDER = "output"

os.makedirs(OUTPUT_FOLDER, exist_ok=True)


def extract_text_from_pdf(path):
    doc = pymupdf.open(path)
    text = ""
    for page in doc:
        text += page.get_text() + "\n"
    return text


def parse_document():
    for filename in os.listdir(FOLDER_PATH):
        file_path = os.path.join(FOLDER_PATH, filename)

        if filename.endswith(".pdf") or filename.endswith(".docx"):
            try:
                text = extract_text_from_pdf(file_path)
            except Exception as e:
                print(f"Failed to read PDF {filename}: {e}")
                continue

        else:
            print(f"Unsupported file type: {filename}")
            continue

        output_filename = f"{os.path.splitext(filename)[0]}_output.txt"
        out_path = os.path.join(OUTPUT_FOLDER, output_filename)

        with open(out_path, "w", encoding="utf8") as out:
            out.write(text)

parse_document()

