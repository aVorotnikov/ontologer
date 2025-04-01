#!/usr/bin/python3

from enum import Enum


class AssessmentType(Enum):
    Test = "test"
    FreeChoice = "free_choice"


def assessement_type_to_string(type: AssessmentType):
    if type == AssessmentType.Test:
        return "Тест"
    if type == AssessmentType.FreeChoice:
        return "Задание со свободным ответом"
    return "Неизвестно"


def string_to_assessment_type(str):
    if str == assessement_type_to_string(AssessmentType.Test):
        return AssessmentType.Test
    if str == assessement_type_to_string(AssessmentType.FreeChoice):
        return AssessmentType.FreeChoice
    raise ValueError(f"Unknown assessment: {str}")


class ContestationType(Enum):
    Unprocessed = "unprocessed"
    Rejected = "rejected"
    Disputed = "disputed"


def contestation_type_to_string(type: ContestationType):
    if type == ContestationType.Unprocessed:
        return "Необработано"
    if type == ContestationType.Rejected:
        return "Отклонено"
    if type == ContestationType.Disputed:
        return "Оспорено"
    return "Неизвестно"
