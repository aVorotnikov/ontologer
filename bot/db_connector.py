#!/usr/bin/python3

import psycopg
from bot_types import *
import json

import datetime


class DbConnector:
    def __init__(self, name, user, password, host, port):
        self.driver = psycopg.connect(dbname=name, user=user, password=password, host=host, port=port, autocommit=True)


    def get_student(self, login):
        with self.driver.cursor() as cursor:
            cursor.execute("SELECT student_login, student_name, group_number from Students WHERE student_login=%s", (login,))
            return cursor.fetchall()


    def insert_domains(self, domains):
        with self.driver.cursor() as cursor:
            for domain in domains:
                cursor.execute("INSERT INTO Domains (domain_name) VALUES (%s) ON CONFLICT DO NOTHING", (domain,))


    def get_groups(self):
        with self.driver.cursor() as cursor:
            cursor.execute("SELECT group_number from Groups")
            return [record[0] for record in cursor.fetchall()]


    def insert_student(self, login, name, group):
        groups = self.get_groups()
        if group not in groups:
            group = "Нет подходящей"
        with self.driver.cursor() as cursor:
            cursor.execute("INSERT INTO Students "
                "(student_login, student_name, group_number) VALUES (%s, %s, %s) "
                "ON CONFLICT (student_login) DO UPDATE "
                "SET student_name=excluded.student_name, group_number=excluded.group_number",
                (login, name, group))


    def insert_assessment(self, login, type: AssessmentType, domain):
        with self.driver.cursor() as cursor:
            cursor.execute("INSERT INTO Assessments "
                "(student_login, assessment_type, domain_name, assessment_start) "
                "VALUES (%s, %s, %s, CURRENT_TIMESTAMP) "
                "RETURNING assessment_id",
                (login, type.value, domain))
            return cursor.fetchone()[0]


    def insert_task(self, assessment_id, task_number, task_question, task_start: datetime.datetime.now(), task_passed, task_info):
        with self.driver.cursor() as cursor:
            cursor.execute("INSERT INTO Tasks "
                "(assessment_id, task_number, task_question, task_start, task_end, task_passed, task_challenged, task_info) "
                "VALUES (%s, %s, %s, %s, CURRENT_TIMESTAMP, %s, FALSE, %s) "
                "RETURNING task_id",
                (assessment_id, task_number, task_question, task_start, task_passed, json.dumps(task_info)))
            return cursor.fetchone()[0]


    def get_assessments(self, login):
        with self.driver.cursor() as cursor:
            cursor.execute(
                "SELECT assessment_id, assessment_start, domain_name, assessment_type "
                "FROM Assessments "
                "WHERE student_login=%s",
                (login,))
            return cursor.fetchall()


    def get_tasks(self, assessment_id, login):
        with self.driver.cursor() as cursor:
            cursor.execute(
                "SELECT task_number, task_start, task_end, task_passed, task_challenged "
                "FROM Tasks "
                "LEFT JOIN Assessments ON Tasks.assessment_id=Assessments.assessment_id "
                "LEFT JOIN Contestations ON Tasks.task_id=Contestations.task_id "
                "WHERE Tasks.assessment_id=%s AND Assessments.student_login=%s AND Contestations.task_id IS NULL",
                (assessment_id, login))
            return cursor.fetchall()


    def insert_contestation(self, assessment_id, task_number, login):
        with self.driver.cursor() as cursor:
            cursor.execute(
                "INSERT INTO Contestations (task_id, contestation_type) "
                "VALUES ("
                " (SELECT task_id "
                " FROM Tasks "
                " LEFT JOIN Assessments ON Tasks.assessment_id=Assessments.assessment_id "
                " WHERE Tasks.assessment_id=%s AND Tasks.task_number=%s AND Assessments.student_login=%s), "
                "'unprocessed') "
                "ON CONFLICT DO NOTHING",
                (assessment_id, task_number, login))


    def get_stat(self, login):
        with self.driver.cursor() as cursor:
            cursor.execute(
                "SELECT "
                "Assessments.assessment_type, "
                "COUNT(*) FILTER (WHERE task_passed), "
                "COUNT(*) FILTER (WHERE task_challenged), "
                "COUNT(*) "
                "FROM Tasks "
                "LEFT JOIN Assessments ON Tasks.assessment_id=Assessments.assessment_id "
                "WHERE Assessments.student_login=%s "
                "GROUP BY Assessments.assessment_type",
                (login,))
            return cursor.fetchall()


    def get_stat_domains(self, login):
        with self.driver.cursor() as cursor:
            cursor.execute(
                "SELECT "
                "Assessments.domain_name, "
                "Assessments.assessment_type, "
                "COUNT(*) FILTER (WHERE task_passed), "
                "COUNT(*) FILTER (WHERE task_challenged), "
                "COUNT(*) "
                "FROM Tasks "
                "LEFT JOIN Assessments ON Tasks.assessment_id=Assessments.assessment_id "
                "WHERE Assessments.student_login=%s "
                "GROUP BY Assessments.domain_name, Assessments.assessment_type",
                (login,))
            return cursor.fetchall()


if __name__ == "__main__":
    db = DbConnector("ontologer", "postgres", "aaaaaa", "localhost", 5432)
    db.insert_domains(["Наивная теория множеств"])
    print("Users: {}".format(db.get_student("ivanov")))
    db.insert_student("ivanov", "Иванов", "5040102/30201")
    assessment_id = db.insert_assessment("ivanov", AssessmentType.FreeChoice, "Наивная теория множеств")
    print(f"Assessment {assessment_id}")
    print("Task {}".format(db.insert_task(assessment_id, 1, "Пупу?", datetime.datetime.now(), True, {"a": 214, "b": "c"})))
    print("Assessments: {}".format(db.get_assessments("ivanov")))
    print("Tasks: {}".format(db.get_tasks(assessment_id, "ivanov")))
    print("Tasks (incorrect login): {}".format(db.get_tasks(assessment_id, "notivanov")))
    print("Stat: {}".format(db.get_stat("ivanov")))
    print("Stat domains: {}".format(db.get_stat_domains("ivanov")))
    db.insert_contestation(assessment_id, 1, "ivanov")
