#!/usr/bin/python3

from free_choice_checker.construct_sequence import construct_sequence
from llm_connector import LlmConnector
from ontologies_connector import OntologiesConnector


MIN_LENGTH_TO_CHECK = 1
MAX_LENGTH_TO_CHECK = 3


def generate_answer(sequence):
    sentences = []
    for i in range(0, len(sequence) - 1, 2):
        sentences.append(construct_sequence(sequence[i], sequence[i + 1], sequence[i + 2]))
    return ". ".join(sentences)


def compare_statements(llm: LlmConnector, statement1: str, statement2: str):
    request = f'Ответь односложно: "Да" или "Нет". Эквиваленты ли 2 утверждения "{statement1}" и "{statement2}"?'
    response = llm.generate_response(request)
    return response.lower().startswith("да")


def check_free_choice_answer(
    ontologies: OntologiesConnector,
    llm: LlmConnector,
    domain: str,
    source: str,
    destination: str,
    answer: str):
    for length in range(MIN_LENGTH_TO_CHECK, MAX_LENGTH_TO_CHECK):
        sequences = ontologies.get_path_sequences(domain, source, destination, length)
        for sequence in  sequences:
            reference = generate_answer(sequence)
            if (compare_statements(llm, answer, reference)):
                return True
    return False
