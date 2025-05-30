DROP TABLE IF EXISTS Groups CASCADE;
CREATE TABLE Groups (
    group_number TEXT PRIMARY KEY
);
INSERT INTO Groups (group_number) VALUES ('Нет подходящей');

DROP TABLE IF EXISTS Students CASCADE;
CREATE TABLE Students (
    student_id BIGINT PRIMARY KEY,
    student_login TEXT,
    student_name TEXT NOT NULL,
    group_number TEXT REFERENCES Groups(group_number)
);

DROP TABLE IF EXISTS AssessmentTypes CASCADE;
CREATE TABLE AssessmentTypes (
    assessment_type TEXT PRIMARY KEY
);
INSERT INTO AssessmentTypes (assessment_type) VALUES ('test'), ('free_choice');

DROP TABLE IF EXISTS Domains CASCADE;
CREATE TABLE Domains (
    domain_name TEXT PRIMARY KEY
);

DROP TABLE IF EXISTS Assessments CASCADE;
CREATE TABLE Assessments (
    assessment_id SERIAL PRIMARY KEY,
    student_id BIGINT REFERENCES Students(student_id),
    assessment_type TEXT REFERENCES AssessmentTypes(assessment_type),
    domain_name TEXT REFERENCES Domains(domain_name),
    assessment_start TIMESTAMP NOT NULL
);

DROP TABLE IF EXISTS Tasks CASCADE;
CREATE TABLE Tasks (
    task_id SERIAL PRIMARY KEY,
    assessment_id INTEGER REFERENCES Assessments(assessment_id),
    task_number INTEGER NOT NULL,
    task_question TEXT NOT NULL,
    task_start TIMESTAMP NOT NULL,
    task_end TIMESTAMP NOT NULL,
    task_passed BOOLEAN NOT NULL,
    task_challenged BOOLEAN NOT NULL,
    task_info JSONB NOT NULL,
    UNIQUE (assessment_id, task_number)
);

DROP TABLE IF EXISTS ContestationTypes CASCADE;
CREATE TABLE ContestationTypes (
    contestation_type TEXT PRIMARY KEY
);
INSERT INTO ContestationTypes (contestation_type) VALUES ('unprocessed'), ('rejected'), ('disputed');

DROP TABLE IF EXISTS Contestations CASCADE;
CREATE TABLE Contestations (
    task_id SERIAL PRIMARY KEY REFERENCES Tasks(task_id),
    contestation_type TEXT REFERENCES ContestationTypes(contestation_type)
);
