# How to run

1. [Neo4j Desktop](https://neo4j.com/download/) is used to run this code. Install it and create a new project. Create a local DBMS within the project, set your password to Very-Strong-Password (or change the password set in the .py file) and install the APOC plugin.
2. Start the DBMS
3. Run graphmaker.py
4. Open the DBMS in Neo4j and view the result. You can choose which nodes to show.

The full graph:
![graph](https://github.com/djboek42/uniprot-to-neo4j/assets/78880986/f89fda70-bcf2-4f52-b565-23d1a67ae763)

Some selections, the following showing just the protein's features and their evidence:

![graphpfe](https://github.com/djboek42/uniprot-to-neo4j/assets/78880986/8624c6d7-0203-4e2d-906c-3f0fc4bb871e)

Showing the protein name, its organism and the protein's keywords

![graphpnok](https://github.com/djboek42/uniprot-to-neo4j/assets/78880986/93ef7af3-e7b0-4925-a05c-14bd1b39defa)
