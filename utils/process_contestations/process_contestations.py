#!/usr/bin/python3

import sys
sys.path.append('../../bot')

from bot_types import ContestationType, contestation_type_to_string

import psycopg
from argparse import ArgumentParser
import json


class DbConnector:
    def __init__(self, name, user, password, host, port):
        self.driver = psycopg.connect(dbname=name, user=user, password=password, host=host, port=port, autocommit=True)


    def proccess_disputed(self, task_id):
        with self.driver.cursor() as cursor:
            cursor.execute(
                "UPDATE Contestations SET contestation_type=%s WHERE task_id=%s",
                (ContestationType.Disputed.value, task_id))
            cursor.execute(
                "UPDATE Tasks SET task_challenged=TRUE WHERE task_id=%s",
                (task_id,))
            

    def proccess_rejected(self, task_id):
        with self.driver.cursor() as cursor:
            cursor.execute(
                "UPDATE Contestations SET contestation_type=%s WHERE task_id=%s",
                (ContestationType.Rejected.value, task_id))
            cursor.execute(
                "UPDATE Tasks SET task_challenged=FALSE WHERE task_id=%s",
                (task_id,))


def process_contestations(db, disputed_list, rejected_list):
    for disputed in disputed_list:
        db.proccess_disputed(disputed)
    for rejected in rejected_list:
        db.proccess_rejected(rejected)


if __name__ == "__main__":
    parser = ArgumentParser(description="Script to process contestations")
    parser.add_argument("-j", "--json", help="JSON file with tasks")
    args = parser.parse_args()

    db = DbConnector("ontologer", "postgres", "aaaaaa", "localhost", 5432)
    with open(args.json) as file:
        tasks = json.load(file)
        process_contestations(
            db,
            tasks[ContestationType.Disputed.value],
            tasks[ContestationType.Rejected.value])
