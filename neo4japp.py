# -*- coding: utf-8 -*-
"""
Created on Mon Mar 27 14:52:20 2023

@author: danie
"""

from neo4j import GraphDatabase
import logging
from neo4j.exceptions import ServiceUnavailable

class App:

    def __init__(self, uri, user, password):
        self.driver = GraphDatabase.driver(uri, auth=(user, password))

    def close(self):
        # Don't forget to close the driver connection when you are finished with it
        self.driver.close()
        
    def clear_db(self):
        with self.driver.session(database="neo4j") as session:
            query = (
                "MATCH (n) "
                "DETACH DELETE n")
            session.run(query)
            print('db cleared')  

    def create_protein(self, protein_id):
        with self.driver.session(database="neo4j") as session:
            result = session.execute_write(
                self._create_protein, protein_id)
            for row in result:
                print("Created protein {pr}".format(pr=row['pr']))
                
    @staticmethod
    def _create_protein(tx, protein_id):
        query = (
            """MERGE (pr:Protein {id: $protein_id})
            RETURN pr""")
        result = tx.run(query, protein_id=protein_id)
        try:
            return [{"pr": row["pr"]["id"]}
                    for row in result]
        except ServiceUnavailable as exception:
            logging.error("{query} raised an error: \n {exception}".format(
                query=query, exception=exception))
            raise      
            
    def create_gene(self, protein_id, gene_list):
        with self.driver.session(database="neo4j") as session:
            result = session.execute_write(
            self._create_gene, protein_id, gene_list)
            for row in result:
                print("Linked gene {g} to protein {pr}".format(pr=row['pr'], g=row['g']))
    
    @staticmethod
    def _create_gene(tx, protein_id, gene_list):
        query = (
            """UNWIND $gene_list AS gl 
            MATCH (pr:Protein {id: $protein_id}) 
            MERGE (g:Gene { name: gl.name }) 
            CREATE (pr)-[:FROM_GENE {status: gl.type}]->(g)
            RETURN pr, g""")
        result = tx.run(query, gene_list=gene_list, protein_id=protein_id)
        try:
            return [{"g": row["g"]["name"], "pr": row["pr"]["id"]}
                    for row in result]
        # Capture any errors along with the query and data for traceability
        except ServiceUnavailable as exception:
            logging.error("{query} raised an error: \n {exception}".format(
                query=query, exception=exception))
            raise

    def create_proteinnames(self, protein_id, protein_name_list):
        with self.driver.session(database="neo4j") as session:
            result = session.execute_write(
            self._create_proteinnames, protein_id, protein_name_list)
            for row in result:
                print("Linked name {n} to protein {pr}".format(n=row['n'], pr=row['pr']))
    
    @staticmethod
    def _create_proteinnames(tx, protein_id, protein_name_list):
        query = (
            """UNWIND $protein_name_list AS pnl 
            MATCH (pr:Protein {id: $protein_id}) 
            MERGE (n:Name { name: pnl.name, type: pnl.recalt }) 
            WITH pr, n, pnl 
            CALL apoc.create.relationship(pr, pnl.has, {}, n) YIELD rel 
            RETURN n, pr""")
        result = tx.run(query, protein_name_list=protein_name_list, protein_id=protein_id)
        try:
            return [{"n": row["n"]["name"], "pr": row["pr"]["id"]}
                    for row in result]
        # Capture any errors along with the query and data for traceability
        except ServiceUnavailable as exception:
            logging.error("{query} raised an error: \n {exception}".format(
                query=query, exception=exception))
            raise
                
    def create_references(self, protein_id, reference_list):
        with self.driver.session(database="neo4j") as session:
            result = session.execute_write(
            self._create_references, protein_id, reference_list)
            for row in result:
                print("Linked reference {r} to protein {pr}".format(r=row['r'], pr=row['pr']))
                
    # CREATE (r:Reference { key: rl.key, title: rl.title, type: rl.type,
    #                              date: rl.date, name: rl.name, volume: rl.volume,
    #                              first: rl.first, last: rl.last, DOI: rl.DOI,
    #                              PubMed: rl.PubMed})
    @staticmethod
    def _create_references(tx, protein_id, reference_list):
        query = (
            """MATCH (pr:Protein {id: $protein_id}) 
            CALL apoc.create.nodes(['Reference'], $reference_list) YIELD node
            CREATE (pr) -[:HAS_REFERENCE]-> (node) 
            RETURN node, pr""")
        result = tx.run(query, reference_list=reference_list, protein_id=protein_id)
        try:
            return [{"r": row["node"]["key"], "pr": row["pr"]["id"]}
                    for row in result]
        # Capture any errors along with the query and data for traceability
        except ServiceUnavailable as exception:
            logging.error("{query} raised an error: \n {exception}".format(
                query=query, exception=exception))
            raise
    
    def create_authors(self, author_list):
        with self.driver.session(database="neo4j") as session:
            result = session.execute_write(
            self._create_authors, author_list)
            for row in result:
                print("Linked authors to reference {r}".format(r=row['r']))
    
    @staticmethod
    def _create_authors(tx, author_list):
        query = (
            """UNWIND $author_list AS al 
            MATCH (r:Reference {key: al.ref_key}) 
            MERGE (a:Author { name: al.name}) 
            CREATE (r) -[:HAS_AUTHOR]-> (a) 
            RETURN DISTINCT r""")
        result = tx.run(query, author_list=author_list)
        try:
            return [{"r": row["r"]["key"]}
                    for row in result]
        # Capture any errors along with the query and data for traceability
        except ServiceUnavailable as exception:
            logging.error("{query} raised an error: \n {exception}".format(
                query=query, exception=exception))
            raise

    def create_dbreferences(self, protein_id, dbref_list):
        with self.driver.session(database="neo4j") as session:
            result = session.execute_write(
            self._create_dbreferences, protein_id, dbref_list)
            for row in result:
                print("Linked dbReferences to protein {pr}".format(pr=row['pr']))
    
    @staticmethod
    def _create_dbreferences(tx, protein_id, dbref_list):
        query = (
            # UNWIND $dbref_list AS drl 
            """MATCH (pr:Protein {id: $protein_id}) 
            CALL apoc.create.nodes(['dbReference'], $dbref_list) YIELD node
            CREATE (pr)-[:HAS_DBREFERENCE]->(node) 
            RETURN DISTINCT pr""")
        result = tx.run(query, dbref_list=dbref_list, protein_id=protein_id)
        try:
            return [{"pr": row["pr"]["id"]}
                    for row in result]
        # Capture any errors along with the query and data for traceability
        except ServiceUnavailable as exception:
            logging.error("{query} raised an error: \n {exception}".format(
                query=query, exception=exception))
            raise

    def create_features(self, protein_id, feature_list):
        with self.driver.session(database="neo4j") as session:
            result = session.execute_write(
            self._create_features, protein_id, feature_list)
            for row in result:
                print("Linked feature {f} to protein {pr}".format(f=row['f'], pr=row['pr']))
    
    # optional: if you don't want to fill in "N/A" for missing name and evidence properties, use
    # UNWIND $feature_list AS fl WITH fl WHERE fl.name is NOT NULL AND fl.evidence is NOT NULL
    # and keep the MERGE query. This will leave out incomplete features. Otherwise, you can use 
    # CREATE (f:Feature { name: fl.name, type: fl.type, evidence: fl.evidence}) 
    # but you'll get duplicate nodes.

    @staticmethod
    def _create_features(tx, protein_id, feature_list):
        query = (
            """UNWIND $feature_list AS fl
            MATCH (pr:Protein {id: $protein_id}) 
            MERGE (f:Feature { name: fl.name, type: fl.type, evidence: fl.evidence}) 
            CREATE (pr) -[:HAS_FEATURE {begin: fl.begin, end: fl.end, position: fl.position}]-> (f) 
            RETURN pr, f""")
        result = tx.run(query, protein_id=protein_id, feature_list=feature_list)
        try:
            return [{"pr": row["pr"]["id"], "f": row["f"]["name"]}
                    for row in result]
        # Capture any errors along with the query and data for traceability
        except ServiceUnavailable as exception:
            logging.error("{query} raised an error: \n {exception}".format(
                query=query, exception=exception))
            raise
            
    def create_evidence(self, evidence_list):
        with self.driver.session(database="neo4j") as session:
            result = session.execute_write(
            self._create_evidence, evidence_list)
            for row in result:
                print("Linked evidence {e} to feature {f}".format(e=row['e'], f=row['f']))

    @staticmethod
    def _create_evidence(tx, evidence_list):
        query = (
            """UNWIND $evidence_list AS el 
            MATCH (f:Feature {evidence: el.key}) 
            MERGE (e:Evidence { type: el.type, key: el.key, source: el.sourcetype, 
                               source_id: el.sourceid}) 
            CREATE (f) -[:HAS_EVIDENCE]-> (e) 
            RETURN f, e""")
        result = tx.run(query, evidence_list=evidence_list)
        try:
            return [{"e": row["e"]["key"], "f": row["f"]["name"]}
                    for row in result]
        # Capture any errors along with the query and data for traceability
        except ServiceUnavailable as exception:
            logging.error("{query} raised an error: \n {exception}".format(
                query=query, exception=exception))
            raise        

    def create_keywords(self, protein_id, keyword_list):
        with self.driver.session(database="neo4j") as session:
            result = session.execute_write(
            self._create_keywords, protein_id, keyword_list)
            for row in result:
                print("Linked keyword {k} to protein {pr}".format(k=row['k'], pr=row['pr']))
    
    @staticmethod
    def _create_keywords(tx, protein_id, keyword_list):
        query = (
            """UNWIND $keyword_list AS kl 
            MATCH (pr:Protein {id: $protein_id}) 
            MERGE (k:Keyword { keyword: kl.keyword, id: kl.id}) 
            CREATE (pr) -[:HAS_KEYWORD]-> (k) 
            RETURN pr, k""")
        result = tx.run(query, protein_id=protein_id, keyword_list=keyword_list)
        try:
            return [{"pr": row["pr"]["id"], "k": row["k"]["keyword"]}
                    for row in result]
        # Capture any errors along with the query and data for traceability
        except ServiceUnavailable as exception:
            logging.error("{query} raised an error: \n {exception}".format(
                query=query, exception=exception))
            raise        

    def create_sequence(self, protein_id, sequence_dict):
        with self.driver.session(database="neo4j") as session:
            result = session.execute_write(
            self._create_sequence, protein_id, sequence_dict)
            for row in result:
                print("Linked sequence to protein {pr}".format(pr=row['pr']))
    
    @staticmethod
    def _create_sequence(tx, protein_id, sequence_dict):
        query = (
            """MATCH (pr:Protein {id: $protein_id}) 
            CALL apoc.create.node(['Sequence'], $sequence_dict) YIELD node
            CREATE (pr) -[:HAS_SEQUENCE]-> (node) 
            RETURN pr""")
        result = tx.run(query, protein_id=protein_id, sequence_dict=sequence_dict)
        try:
            return [{"pr": row["pr"]["id"]}
                    for row in result]
        # Capture any errors along with the query and data for traceability
        except ServiceUnavailable as exception:
            logging.error("{query} raised an error: \n {exception}".format(
                query=query, exception=exception))
            raise
            
    def create_organism(self, protein_id, organism_dict):
        with self.driver.session(database="neo4j") as session:
            result = session.execute_write(
            self._create_organism, protein_id, organism_dict)
            for row in result:
                print("Linked organism {o} to protein {pr}".format(o=row['o'],pr=row['pr']))
    
    @staticmethod
    def _create_organism(tx, protein_id, organism_dict):
        query = (
            """UNWIND $organism_dict AS ol 
            MATCH (pr:Protein {id: $protein_id}) 
            MERGE (o:Organism { name: ol.scientificName, taxonomy_id: ol.id}) 
            CREATE (pr) -[:IN_ORGANISM]-> (o) 
            RETURN pr, o""")
        result = tx.run(query, protein_id=protein_id, organism_dict=organism_dict)
        try:
            return [{"pr": row["pr"]["id"], "o": row["o"]["name"]}
                    for row in result]
        # Capture any errors along with the query and data for traceability
        except ServiceUnavailable as exception:
            logging.error("{query} raised an error: \n {exception}".format(
                query=query, exception=exception))
            raise