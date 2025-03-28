DROP TABLE IF EXISTS Groups CASCADE;
CREATE TABLE Groups (
    group_number TEXT PRIMARY KEY
);
INSERT INTO Groups (group_number) VALUES ('unknown');

DROP TABLE IF EXISTS Students CASCADE;
CREATE TABLE Students (
    student_login TEXT PRIMARY KEY,
    student_name TEXT,
    group_number TEXT REFERENCES Groups(group_number)
);

DROP TABLE IF EXISTS AssessmentTypes CASCADE;
CREATE TABLE AssessmentTypes (
    assessement_type TEXT PRIMARY KEY
);
INSERT INTO AssessmentTypes (assessement_type) VALUES ('test'), ('free_choice');

DROP TABLE IF EXISTS Domains CASCADE;
CREATE TABLE Domains (
    domain_label TEXT PRIMARY KEY,
    domain_name TEXT NOT NULL
);
INSERT INTO Domains (domain_label, domain_name) VALUES ('set_theory', 'Наивная теория множеств');

DROP TABLE IF EXISTS Assessments CASCADE;
CREATE TABLE Assessments (
    assessment_id TEXT PRIMARY KEY,
    student_login TEXT REFERENCES Students(student_login),
    assessement_type TEXT REFERENCES AssessmentTypes(assessement_type),
    domain_label TEXT REFERENCES Domains(domain_label),
    assessment_start TIMESTAMP NOT NULL
);

DROP TABLE IF EXISTS Tasks CASCADE;
CREATE TABLE Tasks (
    task_id SERIAL PRIMARY KEY,
    assessment_id TEXT REFERENCES Assessments(assessment_id),
    task_number INTEGER NOT NULL,
    task_question TEXT NOT NULL,
    task_start TIMESTAMP NOT NULL,
    task_end TIMESTAMP NOT NULL,
    task_passed BOOLEAN NOT NULL,
    task_challenged BOOLEAN NOT NULL,
    task_info JSON NOT NULL
);

DROP TABLE IF EXISTS ContestationTypes CASCADE;
CREATE TABLE ContestationTypes (
    contestation_type TEXT PRIMARY KEY
);
INSERT INTO ContestationTypes (contestation_type) VALUES ('unprocessed'), ('rejected'), ('disputed');

DROP TABLE IF EXISTS Contestations CASCADE;
CREATE TABLE Contestations (
    taskId SERIAL PRIMARY KEY REFERENCES Tasks(task_id),
    contestation_type TEXT REFERENCES ContestationTypes(contestation_type)
);
