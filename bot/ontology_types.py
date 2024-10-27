#!/usr/bin/python3

from enum import Enum


class NodeModifier(Enum):
    Abstract = "abstract"
    Object = "object"
    Algorithm = "algorithm"


class Node:
    def __init__(self, name, modifiers = []):
        self.name = name
        self.modifiers = modifiers


class RelationType(Enum):
    Association = "Association"
    Inheritance = "Inheritance"
    Realization = "Realization"
    Dependency = "Dependency"
    Aggregation = "Aggregation"
    Composition = "Composition"
    Instance = "Instance"
    Manifest = "Manifest"
    Input = "Input"
    Output = "Output"


class Pole:
    def __init__(self, name = "", multiplicity = "", others = ""):
        self.name = name
        self.multiplicity = multiplicity
        self.others = others


class Relation:
    def __init__(self, type: RelationType, predicate = "", predicateInv = "", pole1 = Pole(), pole2: Pole = Pole(), reverse=False):
        self.type = type
        self.predicate = predicate
        self.predicateInv = predicateInv
        self.pole1 = pole1
        self.pole2 = pole2
        self.reverse = reverse
