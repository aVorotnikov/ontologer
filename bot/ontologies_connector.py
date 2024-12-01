#!/usr/bin/python3

from neo4j import GraphDatabase, RoutingControl
from argparse import ArgumentParser
import random
import ontology_types


RO_CONTROL = RoutingControl.READ


class OntologiesConnector:
    def __init__(self, uri, auth):
        self.driver = GraphDatabase.driver(uri, auth=auth)


    def _get_sequences_records(self, domain, length):
        request = "MATCH (c0:Class {domain: $domain})"
        for i in range(1, length + 1):
            request += f"-[r{i}]-(c{i}:Class {{domain: $domain}})"
        request += " RETURN c0"
        for i in range(1, length + 1):
            request += f", r{i}, c{i}"

        return self.driver.execute_query(
            request, domain=domain, database_="neo4j", routing_=RO_CONTROL
        )[0]


    def _get_path_sequences_records(self, domain, start_name, end_name, length):
        request = "MATCH (c0:Class {domain: $domain, name: $start_name})"
        for i in range(1, length):
            request += f"-[r{i}]-(c{i}:Class {{domain: $domain}})"
        request += f"-[r{length}]-(c{length}:Class {{domain: $domain, name: $end_name}})"
        request += " RETURN c0"
        for i in range(1, length + 1):
            request += f", r{i}, c{i}"

        return self.driver.execute_query(
            request, domain=domain, start_name=start_name, end_name=end_name,
            database_="neo4j", routing_=RO_CONTROL
        )[0]


    @staticmethod
    def _get_node(class_record):
        modifiers = []
        for modifier in class_record["modifiers"]:
            modifiers.append(ontology_types.NodeModifier(modifier))
        return ontology_types.Node(class_record["name"], modifiers)


    @staticmethod
    def _get_relation(relation_record):
        pole1 = ontology_types.Pole(
            relation_record["pName1"],
            relation_record["pMultiplicity1"],
            relation_record["pOthers1"])
        pole2 = ontology_types.Pole(
            relation_record["pName2"],
            relation_record["pMultiplicity2"],
            relation_record["pOthers2"])
        return ontology_types.Relation(
            ontology_types.RelationType(relation_record.type),
            relation_record["predicate"],
            relation_record["predicateInv"],
            pole1,
            pole2)


    @staticmethod
    def _record_to_sequence(record):
        if 0 == len(record):
            return []
        sequence = []
        node = record["c0"]
        sequence.append(OntologiesConnector._get_node(node))
        prev_id = node.element_id
        for i in range(1, len(record) // 2 + 1):
            relation = record[f"r{i}"]
            relation_result = OntologiesConnector._get_relation(relation)
            relation_result.reverse = (relation.end_node.element_id == prev_id)
            sequence.append(relation_result)
            node = record[f"c{i}"]
            sequence.append(OntologiesConnector._get_node(node))
            prev_id = node.element_id
        return sequence


    def get_random_sequence(self, domain, length = 1):
        records = self._get_sequences_records(domain, length)
        if len(records) == 0:
            return []
        record = records[random.randrange(len(records))]
        return OntologiesConnector._record_to_sequence(record)


    def get_path_sequences(self, domain, start_name, end_name, length = 1):
        records = self._get_path_sequences_records(domain, start_name, end_name, length)
        res = []
        if len(records) == 0:
            return res
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
    print(connector.get_random_sequence(args.domain))
    print(connector.get_path_sequences(args.domain, "Множество", "Элемент множества"))
