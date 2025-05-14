-- resumes table create query

CREATE TABLE resumes (
    id SERIAL PRIMARY KEY,
    Name TEXT,
    designation TEXT,
    total_experience VARCHAR(50),
    skills TEXT[],
    company TEXT,
    project_work TEXT,
    achievements TEXT
);

-- insert query

INSERT INTO resumes (name, designation, total_experience, skills, company, project_work, achievements)
            VALUES ("Name", "Designation", "Experience", "skills_list", "Company", "Project_List", "achievements_list")
