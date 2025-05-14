#!/usr/bin/python3

import sys
sys.path.append('../../bot')

from bot_types import AssessmentType, assessment_type_to_string

import psycopg
import csv


class DbConnector:
    def __init__(self, name, user, password, host, port):
        self.driver = psycopg.connect(dbname=name, user=user, password=password, host=host, port=port, autocommit=True)


    def get_stat(self):
        with self.driver.cursor() as cursor:
            cursor.execute(
                "SELECT "
                "Students.student_id, "
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
                "GROUP BY "
                "Students.student_id, Students.group_number, Students.student_name, "
                "Assessments.domain_name, Assessments.assessment_type "
                "ORDER BY Assessments.domain_name, Assessments.assessment_type")
            return cursor.fetchall()


if __name__ == "__main__":
    db = DbConnector("ontologer", "postgres", "aaaaaa", "localhost", 5432)
    stat = db.get_stat()

    field_names = []
    students = dict()
    for record in stat:
        field = f"{record[3]} ({assessment_type_to_string(AssessmentType(record[4]))})"
        if f"{field} -- p" not in field_names:
            field_names = field_names + [f"{field} -- p", f"{field} -- c", f"{field} -- t"]
        if record[0] not in students:
            students[record[0]] = {
                "Фамилия и имя": record[1],
                "Группа": record[2]
            }
        students[record[0]].update({
            f"{field} -- p": record[5] + record[6],
            f"{field} -- c": record[6] + record[8],
            f"{field} -- t": record[9]
        })
    field_names = ["Фамилия и имя", "Группа"] + field_names

    with open("results.csv", 'w', newline='') as csv_file:
        writer = csv.DictWriter(csv_file, fieldnames=field_names, restval=0, dialect='excel')
        writer.writeheader()
        writer.writerows([*students.values()])
