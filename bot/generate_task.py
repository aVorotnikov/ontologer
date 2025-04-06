#!/usr/bin/python3

from ontologies_connector import OntologiesConnector
from argparse import ArgumentParser
from ontology_types import RelationType

import random


ATTEMPTS_TO_GENERATE_TEST_TASK = 3
MAX_LENGTH_FOR_TEST_TASK = 3
MAX_VARIANTS = 4


class FreeChoiceTask:
    def __init__(self, source, destination, difficulty, domain):
        self.source = source
        self.destination = destination
        self.difficulty = difficulty
        self.domain = domain


def generate_free_choice_task(connector: OntologiesConnector, domain, difficulty = 1):
    sequence = connector.get_random_sequence(domain, difficulty)
    if len(sequence) == 0:
        raise RuntimeError(f"Failed to generate task: no such sequence for '{domain}'")
    return FreeChoiceTask(sequence[0].name, sequence[-1].name, difficulty, domain)


def generate_free_choice_task_text(task: FreeChoiceTask):
    return f'Как связаны понятия "{task.source}" и "{task.destination}"?'


class TestTask:
    def __init__(self, source, relation, options, domain):
        self.source = source
        self.relation = relation
        self.options = options
        self.domain = domain


def _generate_test_task(connector: OntologiesConnector, domain):
    term = connector.get_random_term(domain).name
    if term is None:
        raise RuntimeError(f"Failed to generate task: no terms in '{domain}'")
    vicinity = connector.get_vicinity(domain, term)
    random.shuffle(vicinity)
    if len(vicinity) == 0:
        raise RuntimeError(f"Failed to generate task: no vicinity in '{domain}' for '{term}'")
    options = set()
    path = vicinity[0]
    relation = path[1].type
    options.add(path[-1].name)
    for path in vicinity:
        name = path[-1].name
        if name != term:
            options.add(path[-1].name)
            if len(options) == MAX_VARIANTS:
                options_list = list(options)
                random.shuffle(options_list)
                return TestTask(term, relation, options_list, domain)
    for length in range(2, MAX_LENGTH_FOR_TEST_TASK + 1):
        vicinity = connector.get_vicinity(domain, term, length)
        random.shuffle(vicinity)
        for path in vicinity:
            name = path[-1].name
            if name != term:
                options.add(path[-1].name)
                if len(options) == MAX_VARIANTS:
                    options_list = list(options)
                    random.shuffle(options_list)
                    return TestTask(term, relation, options_list, domain)
    options_list = list(options)
    random.shuffle(options_list)
    return TestTask(term, relation, options_list, domain)


def generate_test_task(connector: OntologiesConnector, domain):
    for i in range(ATTEMPTS_TO_GENERATE_TEST_TASK):
        try:
            return _generate_test_task(connector, domain)
        except:
            pass
    raise RuntimeError(f"Failed to generate task for '{domain}'")


def generate_test_task_text(task: TestTask):
    relType = task.relation
    if RelationType.Inheritance == relType:
        relation = "наследования"
    elif RelationType.Realization == relType:
        relation = "реализации"
    elif RelationType.Dependency == relType:
        relation = "зависимости"
    elif RelationType.Aggregation == relType:
        relation = "агрегации"
    elif RelationType.Composition == relType:
        relation = "композиции"
    elif RelationType.Instance == relType:
        relation = "инстанцирования"
    elif RelationType.Manifest == relType:
        relation = "манифестации"
    elif RelationType.Input == relType:
        relation = "входа алгоритма"
    elif RelationType.Output == relType:
        relation = "выхода алгоритма"
    elif RelationType.Association == relType:
        relation = "ассоциации"
    else:
        raise TypeError(f"Unknown relation: {relType}")
    return f'Какое понятие связано с понятием "{task.source}" отношением {relation}?'


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

    task = generate_free_choice_task(connector, args.domain)
    print(
        f"Source: {task.source}. Destination: {task.destination}. "
        f"Difficulty: {task.difficulty}. Domain: {task.domain}")
    print(f"Task text representation: {generate_free_choice_task_text(task)}")

    task = generate_test_task(connector, args.domain)
    print(
        f"Term: {task.source}. Relation: {task.relation}. "
        f"Options: {task.options}. Domain: {task.domain}")
    print(f"Task text representation: {generate_test_task_text(task)}")
