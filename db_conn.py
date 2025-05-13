
import psycopg2
from segment_parsing import segment_text_file, extract_info_from_segmented_text
from single_parser import extract_info


FILE_PATH = "CVs/Govind_Rathod_Android-2.pdf"
OUTPUT_FOLDER = "segment_output"


text, has_image = segment_text_file(FILE_PATH)

if has_image:
    info = extract_info(text)
else:
    info = extract_info_from_segmented_text(text)

def insert_into_postgresql(info):
    conn = None  # Ensure conn is defined even if connection fails
    try:
        conn = psycopg2.connect(
            host="localhost",
            database="resume_parser",
            user="postgres",
            password="root"
        )
        cursor = conn.cursor()

        insert_query = """
            INSERT INTO resumes (name, designation, total_experience, skills, company, project_work, achievements)
            VALUES (%s, %s, %s, %s, %s, ARRAY[%s], ARRAY[%s])
            """


        name = info.get("Name")
        designation = info.get("Designation")
        total_experience = info.get("Total Experience")
        skills = info.get("Skills", [])
        company = info.get("Company")
        project_work = info.get("Projects")
        achievements = info.get("Achievements")

        cursor.execute(insert_query, (
            name, designation, total_experience, skills, company, project_work, achievements
        ))

        conn.commit()
        print("Data inserted successfully.")
    except Exception as e:
        print(f"Error inserting data: {e}")
    finally:
        if conn:
            cursor.close()
            conn.close()


insert_into_postgresql(info)

