#!/usr/bin/python3

from enum import Enum


class AssessmentType(Enum):
    Test = "test"
    FreeChoice = "free_choice"


class ContestationType(Enum):
    Unprocessed = "unprocessed"
    Rejected = "rejected"
    Disputed = "disputed"
