#!/usr/bin/python3

from ontology_types import *
import pymorphy2
from enum import Enum


class MorphyCase(Enum):
    nomn = "nomn" # именительный
    gent = "gent" # родительный
    datv = "datv" # дательный
    accs = "accs" # винительный
    ablt = "ablt" # творительный
    loct = "loct" # предложный
    voct = "voct" # звательный
    gen2 = "gen2" # второй родительный (частичный)
    acc2 = "acc2" # второй винительный
    loc2 = "loc2" # второй предложный (местный)


def __morph_string_with_case(string, case: MorphyCase):
    if 0 != len(string):
        string = string[0].lower() + string[1:]

    words = string.split(' ')
    morph = pymorphy2.MorphAnalyzer()

    for i in range(len(words)):
        parsing = morph.parse(words[i])[0]
        tag = parsing.tag
        if 'nomn' in tag and ('NOUN' in tag or 'ADJF' in tag or 'PRTF' in tag or 'NPRO' in tag):
            words[i] = parsing.inflect({case.value}).word

    return ' '.join(words)


def __construct_sequence_not_reverse(node1: Node, relation: Relation, node2: Node):
    relType = relation.type
    if RelationType.Inheritance == relType:
        return f"{node1.name} является частным случаем {__morph_string_with_case(node2.name, MorphyCase.gent)}."
    elif RelationType.Realization == relType:
        return f"{node1.name} является частным случаем {__morph_string_with_case(node2.name, MorphyCase.gent)}."
    elif RelationType.Dependency == relType:
        return f"{node1.name} зависит от {__morph_string_with_case(node2.name, MorphyCase.gent)}."
    elif RelationType.Aggregation == relType:
        return f"{node1.name} является частью {__morph_string_with_case(node2.name, MorphyCase.gent)}."
    elif RelationType.Composition == relType:
        return f"{node1.name} является частью {__morph_string_with_case(node2.name, MorphyCase.gent)}."
    elif RelationType.Instance == relType:
        return f"{node1.name} является частным случаем {__morph_string_with_case(node2.name, MorphyCase.gent)}."
    elif RelationType.Manifest == relType:
        return f"{node1.name} является воплощением {__morph_string_with_case(node2.name, MorphyCase.gent)}."
    elif RelationType.Input == relType:
        return f"{node1.name} является входом {__morph_string_with_case(node2.name, MorphyCase.gent)}."
    elif RelationType.Output == relType:
        return f"{node1.name} имеет выход {node2.name}."
    elif RelationType.Association == relType:
        return f"{node1.name} {relation.predicate} {node2.name}"
    raise TypeError(f"Unknown relation: {relType}")


def __construct_sequence_reverse(node1: Node, relation: Relation, node2: Node):
    relType = relation.type
    if RelationType.Inheritance == relType:
        return f"{node1.name} является обобщением {__morph_string_with_case(node2.name, MorphyCase.gent)}."
    elif RelationType.Realization == relType:
        return f"{node1.name} является обобщением {__morph_string_with_case(node2.name, MorphyCase.gent)}."
    elif RelationType.Dependency == relType:
        return f"{node2.name} зависит от {__morph_string_with_case(node1.name, MorphyCase.gent)}."
    elif RelationType.Aggregation == relType:
        return f"{node1.name} содержит {__morph_string_with_case(node2.name, MorphyCase.accs)}."
    elif RelationType.Composition == relType:
        return f"{node1.name} содержит {__morph_string_with_case(node2.name, MorphyCase.accs)}."
    elif RelationType.Instance == relType:
        return f"{node1.name} является экземляром типа {node2.name}."
    elif RelationType.Manifest == relType:
        return f"{node1.name} воплощает {__morph_string_with_case(node2.name, MorphyCase.accs)}."
    elif RelationType.Input == relType:
        return f"{node1.name} имеет вход {__morph_string_with_case(node2.name, MorphyCase.gent)}."
    elif RelationType.Output == relType:
        return f"{node1.name} является выходом {__morph_string_with_case(node2.name, MorphyCase.gent)}."
    elif RelationType.Association == relType:
        return f"{node1.name} {relation.predicateInv} {node2.name}"
    raise TypeError(f"Unknown relation: {relType}")


def construct_sequence(node1: Node, relation: Relation, node2: Node):
    if not relation.reverse:
        return __construct_sequence_not_reverse(node1, relation, node2)
    return __construct_sequence_reverse(node1, relation, node2)


if __name__ == "__main__":
    print("#1: ", construct_sequence(
        Node("Элемент множества", []),
        Relation(RelationType.Aggregation, pole1=Pole(multiplicity="*")),
        Node("Множество", [])))
    print("#2: ", construct_sequence(
        Node("Множество", []),
        Relation(RelationType.Aggregation, pole1=Pole(multiplicity="*"), reverse=True),
        Node("Элемент множества", []),))
