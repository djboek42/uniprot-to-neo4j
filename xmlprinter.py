# Short file to easily print content of the xml file and see which properties
# are stored at which levels

import xml.etree.ElementTree as ET

filename = r"C:\Users\danie\OneDrive\Documents\weavechallenge\Q9Y261.xml"
tree = ET.parse(filename)
root = tree.getroot()
entry = root[0]
uniprot = entry.tag.split('entry')[0]

def explore_xml(branch,i):
    """Recursive function that will print tags, attributes and text from every branch"""
    print("-"*i, branch.tag[28:], branch.attrib, branch.text)
    if len(branch) > 0:
        i+=1
        for child in branch:
            explore_xml(child,i)

# Print the entry, here I specified to only print the first 15 items.
# can also do for subclass in entry.findall(uniprot+'reference') for example, to print only references
for subclass in entry[:15]:
    explore_xml(subclass,0)
    print("-"*50)