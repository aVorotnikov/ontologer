#!/usr/bin/python3

from ontologies_connector import OntologiesConnector
from argparse import ArgumentParser


class Task:
    def __init__(self, source, destination, difficulty, domain):
        self.source = source
        self.destination = destination
        self.difficulty = difficulty
        self.domain = domain


def generate_task(connector: OntologiesConnector, domain, difficulty = 1):
    sequence = connector.get_random_sequence(domain, difficulty)
    if len(sequence) == 0:
        raise RuntimeError(f"Failed to generate task: no such sequence for '{domain}'")
    return Task(sequence[0].name, sequence[-1].name, difficulty, domain)


def generate_task_text(task: Task):
    return f'Как связаны понятия "{task.source}" и "{task.destination}"?'


if __name__ == "__main__":
    parser = ArgumentParser(description="Script to upload ontology to database")
    parser.add_argument("-i", "--ip", help="Database IP", default="localhost") 
    parser.add_argument("-p", "--port", help="Database port", default=7687) 
    parser.add_argument("-u", "--user", help="Database user", default="neo4j") 
    parser.add_argument("-w", "--password", help="Database password", required=True) 
    parser.add_argument("-d", "--domain", help="Domain", required=True)

    args = parser.parse_args()

    uri = f"neo4j://{args.ip}:{args.port}"
    auth = (args.user, args.password)
    connector = OntologiesConnector(uri, auth)
    task = generate_task(connector, args.domain)
    print(
        f"Source: {task.source}. Destination: {task.destination}. "
        f"Difficulty: {task.difficulty}. Domain: {task.domain}")
    print(f"Task text representation: {generate_task_text(task)}")
