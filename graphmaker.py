# Based on example code to load some data to Neo4j
# This code is based on the example code from the Neo4j Python Driver
# https://neo4j.com/docs/api/python-driver/current/

import xml.etree.ElementTree as ET
from neo4japp import App


# Load in data, get the entry section with all relevant data
filename = r"C:\Users\danie\OneDrive\Documents\weavechallenge\Q9Y261.xml"
tree = ET.parse(filename)
root = tree.getroot()
entry = root[0]

# Finding the xmlns
uniprot = entry.tag.split('entry')[0]

# Extract the first accession number as the protein_id
protein_id = entry.find(uniprot+'accession').text

# Get all names for the protein and create the names for the relationships
proteins = entry.find(uniprot+'protein')
protein_name_list = []
for child in proteins:
    for branch in child:
        proteindata = {'recalt' : child.tag[28:], 'name': branch.text}
        proteindata['has'] = "HAS_"+branch.tag[28:-4].upper()+'_'+'NAME'  # relationship name
        protein_name_list.append(proteindata)
        
# If we only want the recommended names, use:
    
# recprotein = entry.find(uniprot+'protein').find(uniprot+'recommendedName')
# protein_name_list = []
# for child in recprotein:
#     proteindata = {'name' : child.text}
#     proteindata['has'] = "HAS_"+child.tag[28:-4].upper()+'_'+'NAME'  # relationship name
#     protein_name_list.append(proteindata)

# Extract gene data from the entry
genes = entry.find(uniprot+'gene')
gene_list = []
for gene in genes:
    genedata = {'name' : gene.text, 'type': gene.attrib['type']}
    gene_list.append(genedata)

# Extract organism with its scientific, common and reference id
organism = entry.find(uniprot+'organism')
organism_dict = {}
for name in organism.findall(uniprot+'name'):
    organism_dict[name.attrib['type']+'Name'] =  name.text
ref = organism.find(uniprot+'dbReference')
organism_dict['id'] = ref.attrib['id']

# Extract references
# We make a separate list of authors that will be linked to the references through the key
references = entry.findall(uniprot+'reference')
reference_list = []
author_list = []       
for ref in references:
    refdata = {}
    refdata['key'] = ref.attrib['key']
    citation = ref.find(uniprot+'citation')
    refdata.update(citation.attrib)
    title = citation.find(uniprot+'title')
    refdata['title'] = title.text
    reference_list.append(refdata)
    authorlist = citation.find(uniprot+'authorList')
    for author in authorlist:
        authors = {'name': author.attrib['name'], 'ref_key' : ref.attrib['key']}
        author_list.append(authors)
    dbref = citation.findall(uniprot+'dbReference')
    for db in dbref:
        refdata[db.attrib['type']] = db.attrib['id']
    scope = ref.find(uniprot+'scope')
    refdata['scope'] = scope.text

# Extract features. For missing values, we enter 'N/A'
features = entry.findall(uniprot+'feature')
feature_list = []
for feature in features:
    featdata = {'type' : feature.attrib['type']}
    if 'description' in feature.attrib:
        featdata['name'] = feature.attrib['description']
    else:
        featdata['name'] = 'N/A'
    if 'evidence' in feature.attrib:
        featdata['evidence'] = feature.attrib['evidence']
    else:
        featdata['evidence'] = 'N/A'
    for pos in feature[0]:
        featdata[pos.tag[28:]] = pos.attrib['position']
    feature_list.append(featdata)

# Extract evidence, enter 'N/A' for missing source type and source data
evidences = entry.findall(uniprot+'evidence')
evidence_list =[]
for evidence in evidences:
    evidata = {'type': evidence.attrib['type'], 'key': evidence.attrib['key']}
    if len(evidence)>0:
        for source in evidence[0]:
            evidata['sourcetype'] = source.attrib['type']
            evidata['sourceid'] = source.attrib['id']
    else:   
        evidata['sourcetype'] = 'N/A'
        evidata['sourceid'] = 'N/A'
    evidence_list.append(evidata)

# Extract dbReferences and their properties
dbReferences = entry.findall(uniprot+'dbReference')
dbref_list = []
for dbref in dbReferences:
    dbdata = dbref.attrib
    if len(dbref) > 0:
        for prop in dbref:
            if prop.tag[28:] == 'property':
                dbdata[prop.attrib['type']] = prop.attrib['value']
            else: dbdata[prop.tag[28:]+'_id'] = prop.attrib['id']
    dbref_list.append(dbdata)

# Extract keywords
keywords = entry.findall(uniprot+'keyword')
keyword_list = []
for keyword in keywords:
    keydata = {'id' : keyword.attrib['id'], 'keyword' : keyword.text}
    keyword_list.append(keydata)

# Extract the sequence of the protein
sequence = entry.find(uniprot+'sequence')
sequence_dict = sequence.attrib
sequence_dict['sequence'] = sequence.text


if __name__ == "__main__":
    uri = "bolt://localhost:7687"
    password = "Very-Strong-Password"
    user = "neo4j"
    app = App(uri, user, password)
    app.clear_db()
    app.create_protein(protein_id)
    app.create_proteinnames(protein_id, protein_name_list)
    app.create_gene(protein_id,gene_list)
    app.create_organism(protein_id, organism_dict)
    app.create_references(protein_id, reference_list)
    app.create_authors(author_list)
    app.create_dbreferences(protein_id, dbref_list)
    app.create_keywords(protein_id, keyword_list)
    app.create_features(protein_id, feature_list)
    app.create_evidence(evidence_list)
    app.create_sequence(protein_id, sequence_dict)
    app.close()
