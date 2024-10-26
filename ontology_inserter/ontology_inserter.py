#!/usr/bin/python3

from neo4j import GraphDatabase
from argparse import ArgumentParser
import json


def delete_domain(driver, domain):
    driver.execute_query(
        "MATCH (c1:Class {domain: $domain})-[r]->(c2:Class {domain: $domain}) DELETE r",
        domain=domain, database_="neo4j"
    )
    driver.execute_query(
        "MATCH (c:Class {domain: $domain}) DELETE c",
        domain=domain, database_="neo4j"
    )


def insert_node(driver, domain, node):
    driver.execute_query(
        "CREATE (c:Class {domain: $domain, name: $name, modifiers: $modifiers})",
        domain=domain, name=node["name"], modifiers=node["modifiers"], database_="neo4j"
    )


def insert_relation(driver, domain, relation):
    driver.execute_query(
        'MATCH (c1:Class {domain: $domain, name: $name1}) '
        'MATCH (c2:Class {domain: $domain, name: $name2}) '
        f'CREATE (c1)-[:{relation["type"]}]->(c2)',
        domain=domain, name1=relation["name1"], name2=relation["name2"], database_="neo4j"
    )


if __name__ == "__main__":
    parser = ArgumentParser(description="Script to upload ontology to database")
    parser.add_argument("-i", "--ip", help="Database IP", default="localhost") 
    parser.add_argument("-p", "--port", help="Database port", default=7687) 
    parser.add_argument("-u", "--user", help="Database user", default="neo4j") 
    parser.add_argument("-w", "--password", help="Database password", required=True) 
    parser.add_argument("-j", "--json", help="File with ontology", required=True)

    args = parser.parse_args()

    with open(args.json) as file:
        jsonDict = json.load(file)
    domain = jsonDict["domain"]
    print(f"Domain: {domain}")

    uri = f"neo4j://{args.ip}:{args.port}"
    auth = (args.user, args.password)

    with GraphDatabase.driver(uri, auth=auth) as driver:
        delete_domain(driver, domain)
        for node in jsonDict["nodes"]:
            insert_node(driver, domain, node)
        for relation in jsonDict["relations"]:
            insert_relation(driver, domain, relation)
