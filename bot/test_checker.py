#!/usr/bin/python3

from ontologies_connector import OntologiesConnector
from ontology_types import Relation, RelationType


def check_test_answer(
    ontologies: OntologiesConnector,
    domain: str,
    source: str,
    relation: Relation,
    answer: str):
    paths = ontologies.get_path_sequences(domain, source, answer)

    if relation.type == RelationType.Association:
        for path in paths:
            pathRelation = path[1]
            if relation.type == pathRelation.type and (relation.predicate == pathRelation.predicate or relation.predicate == pathRelation.predicateInv):
                return True
            return False

    for path in paths:
        pathRelation = path[1]
        if relation.type == pathRelation.type:
            return True
    return False
