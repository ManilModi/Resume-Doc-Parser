import psycopg2
from constants import HOST, DATABASE, USER, PASSWORD

def insert_into_postgresql(info):
    conn = None
    try:
        conn = psycopg2.connect(
            host=HOST,
            database=DATABASE,
            user=USER,
            password=PASSWORD
        )
        cursor = conn.cursor()

        insert_query = """
            INSERT INTO resumes (name, designation, total_experience, skills, company, project_work, achievements)
            VALUES (%s, %s, %s, %s, %s, ARRAY[%s], ARRAY[%s])
            """


        name = info["Name"]
        designation = info["Designation"]
        total_experience = info["Total Experience"]
        skills = info["Skills"]
        company = info["Company"]
        project_work = info["Projects"]
        achievements = info["Achievements"]

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


