#!/usr/bin/python3

import psycopg


class DbConnector:
    def __init__(self, name, user, password, host, port):
        self.driver = psycopg.connect(dbname=name, user=user, password=password, host=host, port=port, autocommit=True)


    def insert_domains(self, domains):
        with self.driver.cursor() as cursor:
            for domain in domains:
                cursor.execute('INSERT INTO Domains (domain_name) VALUES (%s) ON CONFLICT DO NOTHING', (domain,))
