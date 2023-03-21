# weave-challenge

To start, run neo4j in Docker. I use Windows so my command is:

> docker run --publish=7474:7474 --publish=7687:7687 --volume=C:%HOMEPATH%/neo4j/data:/data neo4j:latest
> docker run -p 7474:7474 -p 7687:7687 -v %CD%/data:/data -v %CD%/plugins:/plugins --name neo4j-apoc -e NEO4J_apoc_export_file_enabled=true -e NEO4J_apoc_import_file_enabled=true -e NEO4J_apoc_import_file_use__neo4j__config=true -e NEO4J_PLUGINS=\[\"apoc\"\] neo4j:latest
