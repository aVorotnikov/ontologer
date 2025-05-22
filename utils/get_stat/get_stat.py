#!/usr/bin/python3

import sys
sys.path.append('../../bot')

from bot_types import AssessmentType, assessment_type_to_string, ContestationType, contestation_type_to_string

import matplotlib.pyplot as plt
import numpy as np
import psycopg


class DbConnector:
    def __init__(self, name, user, password, host, port):
        self.driver = psycopg.connect(dbname=name, user=user, password=password, host=host, port=port, autocommit=True)


    def get_tasks_number(self):
        with self.driver.cursor() as cursor:
            cursor.execute(
                "SELECT " 
                "COUNT(*) FILTER (WHERE task_passed AND NOT task_challenged), "
                "COUNT(*) FILTER (WHERE task_passed AND task_challenged), "
                "COUNT(*) FILTER (WHERE NOT task_passed AND NOT task_challenged), "
                "COUNT(*) FILTER (WHERE NOT task_passed AND task_challenged), "
                "COUNT(*) "
                "FROM Tasks "
                "LEFT JOIN Assessments ON Tasks.assessment_id=Assessments.assessment_id "
                "LEFT JOIN Students ON Assessments.student_id=Students.student_id "
                "WHERE Students.group_number != 'Нет подходящей'")
            return cursor.fetchone()


    def get_tasks_domains(self):
        with self.driver.cursor() as cursor:
            cursor.execute(
                "SELECT "
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
                "WHERE Students.group_number != 'Нет подходящей' "
                "GROUP BY Assessments.domain_name, Assessments.assessment_type")
            return cursor.fetchall()


    def get_contestations_number(self):
        with self.driver.cursor() as cursor:
            cursor.execute(
                "SELECT COUNT(*) "
                "FROM Contestations "
                "LEFT JOIN Tasks ON Contestations.task_id=Tasks.task_id "
                "LEFT JOIN Assessments ON Tasks.assessment_id=Assessments.assessment_id "
                "LEFT JOIN Students ON Assessments.student_id=Students.student_id "
                "WHERE Students.group_number != 'Нет подходящей'")
            return cursor.fetchone()[0]


    def get_contestations_types(self):
        with self.driver.cursor() as cursor:
            cursor.execute(
                "SELECT "
                "Contestations.contestation_type, "
                "COUNT(*) "
                "FROM Contestations "
                "LEFT JOIN Tasks ON Contestations.task_id=Tasks.task_id "
                "LEFT JOIN Assessments ON Tasks.assessment_id=Assessments.assessment_id "
                "LEFT JOIN Students ON Assessments.student_id=Students.student_id "
                "WHERE Students.group_number != 'Нет подходящей' "
                "GROUP BY Contestations.contestation_type")
            return cursor.fetchall()


    def get_contestations_domains(self):
        with self.driver.cursor() as cursor:
            cursor.execute(
                "SELECT "
                "Assessments.domain_name, "
                "COUNT(*) "
                "FROM Contestations "
                "LEFT JOIN Tasks ON Contestations.task_id=Tasks.task_id "
                "LEFT JOIN Assessments ON Tasks.assessment_id=Assessments.assessment_id "
                "LEFT JOIN Students ON Assessments.student_id=Students.student_id "
                "WHERE Students.group_number != 'Нет подходящей' "
                "GROUP BY Assessments.domain_name")
            return cursor.fetchall()


    def get_contestations_task_types(self):
        with self.driver.cursor() as cursor:
            cursor.execute(
                "SELECT "
                "Assessments.assessment_type, "
                "COUNT(*) "
                "FROM Contestations "
                "LEFT JOIN Tasks ON Contestations.task_id=Tasks.task_id "
                "LEFT JOIN Assessments ON Tasks.assessment_id=Assessments.assessment_id "
                "LEFT JOIN Students ON Assessments.student_id=Students.student_id "
                "WHERE Students.group_number != 'Нет подходящей' "
                "GROUP BY Assessments.assessment_type")
            return cursor.fetchall()


def create_tasks_stat_hist(db: DbConnector):
    stat = db.get_tasks_domains()
    if len(stat) == 0:
        return

    labels = []
    val1 = []
    val2 = []
    val3 = []
    val4 = []
    for column in stat:
        labels.append(f"{column[0]}\n({assessment_type_to_string(AssessmentType(column[1]))})")
        val1.append(column[2])
        val2.append(column[3])
        val3.append(column[4])
        val4.append(column[5])

    fig, ax = plt.subplots()
    fig.set_size_inches(18.5, 10.5)
    width = 0.2
    x = np.arange(len(labels))

    rects = ax.bar(x - 3 * width / 2, val1, width, label='Зачтены', color='g')
    ax.bar_label(rects, padding=3)
    rects = ax.bar(x - 1 * width / 2, val2, width, label='Зачтены, оспорены', color='y')
    ax.bar_label(rects, padding=3)
    rects = ax.bar(x + 1 * width / 2, val3, width, label='Незачтены', color='r')
    ax.bar_label(rects, padding=3)
    rects = ax.bar(x + 3 * width / 2, val4, width, label='Незачтены, оспорены', color='b')
    ax.bar_label(rects, padding=3)

    ax.grid(axis='y')
    ax.set_xticks(x)
    ax.set_xticklabels(labels, rotation=19)
    ax.legend()
    fig.suptitle(f"Результаты оценивания заданий")
    fig.savefig("task_results.png", dpi=100)


def get_contestations_types(db: DbConnector):
    stat = db.get_contestations_types()
    if len(stat) == 0:
        return

    labels = [contestation_type_to_string(ContestationType(row[0])) for row in stat]
    values = [row[1] for row in stat]

    fig, ax = plt.subplots()
    ax.pie(values, labels=labels, autopct='%1.1f%%')
    fig.suptitle(f"Результаты оспаривания заданий")
    fig.savefig("contestations_types.png")

    for i in range(len(stat)):
        print(f"\t{labels[i]}: {values[i]}")


def get_contestations_domains(db: DbConnector):
    stat = db.get_contestations_domains()
    if len(stat) == 0:
        return

    labels = [row[0] for row in stat]
    values = [row[1] for row in stat]

    fig, ax = plt.subplots()
    ax.pie(values, labels=labels, autopct='%1.1f%%')
    fig.suptitle(f"Количество оспариваний по главам")
    fig.savefig("contestations_domains.png")

    for i in range(len(stat)):
        print(f"\t{labels[i]}: {values[i]}")


def get_contestations_task_types(db: DbConnector):
    stat = db.get_contestations_task_types()
    if len(stat) == 0:
        return

    labels = [assessment_type_to_string(AssessmentType(row[0])) for row in stat]
    values = [row[1] for row in stat]

    fig, ax = plt.subplots()
    ax.pie(values, labels=labels, autopct='%1.1f%%')
    fig.suptitle(f"Количество оспариваний по типам заданий")
    fig.savefig("contestations_task_types.png")

    for i in range(len(stat)):
        print(f"\t{labels[i]}: {values[i]}")


def get_successful_contestations_reasons():
    stat = {
        "Ошибка в онтологиях": 1,
        "Ошибка языковой модели": 2
    }

    fig, ax = plt.subplots()
    ax.pie(stat.values(), labels=stat.keys(), autopct='%1.1f%%')
    fig.suptitle(f"Причины неправильной оценки заданий")
    fig.savefig("successful_contestations_reasons.png")


if __name__ == "__main__":
    db = DbConnector("ontologer", "postgres", "aaaaaa", "localhost", 5432)
    task_stat = db.get_tasks_number()
    print("Количество заданий:")
    print(f"\tЗачтены, неоспорены: {task_stat[0]}")
    print(f"\tЗачтены, оспорены: {task_stat[1]}")
    print(f"\tНезачтены, неоспорены: {task_stat[2]}")
    print(f"\tНезачтены, оспорены: {task_stat[3]}")
    print(f"\tВсего: {task_stat[4]}")
    create_tasks_stat_hist(db)
    print(f"Количество оспариваний: {db.get_contestations_number()}")
    get_contestations_types(db)
    get_contestations_domains(db)
    get_contestations_task_types(db)
    get_successful_contestations_reasons()
