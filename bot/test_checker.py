#!/usr/bin/python3

from ontologies_connector import OntologiesConnector
from ontology_types import RelationType


def check_test_answer(
    ontologies: OntologiesConnector,
    domain: str,
    source: str,
    relationType: RelationType,
    answer: str):
    paths = ontologies.get_path_sequences(domain, source, answer)
    for path in paths:
        relation = path[1]
        if relation.type == relationType:
            return True
    return False
