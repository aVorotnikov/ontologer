#!/usr/bin/python3

import sys
sys.path.append('../../bot')

from bot_types import AssessmentType, assessment_type_to_string

import psycopg


class DbConnector:
    def __init__(self, name, user, password, host, port):
        self.driver = psycopg.connect(dbname=name, user=user, password=password, host=host, port=port, autocommit=True)


    def get_stat(self):
        with self.driver.cursor() as cursor:
            cursor.execute(
                "SELECT "
                "Students.student_name, "
                "Students.group_number, "
                "Assessments.domain_name, "
                "Assessments.assessment_type, "
                "COUNT(*) FILTER (WHERE task_passed AND NOT task_challenged), "
                "COUNT(*) FILTER (WHERE task_passed AND task_challenged), "
                "COUNT(*) FILTER (WHERE NOT task_passed AND NOT task_challenged), "
                "COUNT(*) FILTER (WHERE NOT task_passed AND task_challenged), "
                "COUNT(*) "
                "FROM Tasks "
                "LEFT JOIN Assessments ON Tasks.assessment_id=Assessments.assessment_id "
                "LEFT JOIN Students ON Assessments.student_id=Students.student_id "
                "GROUP BY Students.group_number, Students.student_name, Assessments.domain_name, Assessments.assessment_type")
            return cursor.fetchall()


if __name__ == "__main__":
    db = DbConnector("ontologer", "postgres", "aaaaaa", "localhost", 5432)
    print(db.get_stat())
