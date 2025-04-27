#!/usr/bin/python3

import sys
sys.path.append('../bot')

from ontologies_connector import OntologiesConnector
from free_choice_checker.construct_sequence import construct_sequence

from argparse import ArgumentParser


def get_all_sequences(connector, domain, length = 1):
    records = connector._get_sequences_records(domain, length)
    if len(records) == 0:
        return []
    res = []
    for record in records:
        res.append(OntologiesConnector._record_to_sequence(record))
    return res


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
    sequences = get_all_sequences(connector, args.domain)
    print(f"Number of relations: {len(sequences)}")
    sentences = [construct_sequence(s[0], s[1], s[2]) for s in sequences]

    with open(f'{args.domain}.txt', 'w') as f:
        for sentence in sentences:
            f.write(f"{sentence}\n")
