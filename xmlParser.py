from mimetypes import init
import xml.etree.ElementTree as ET
from crew_class import *
from node_class import *

'''import sys
with open(sys.argv[1], 'r') as f:
    tree3 = ET.parse(f)'''

#Future topics to research
#2. Obtaining the xml file from the command line
#4. Calling the input checker from a c++ project with xml files

tree = ET.parse('crew.xml')
root = tree.getroot()
#print(root)
tree2 = ET.parse('segment.xml')
root2 = tree2.getroot()
crewBin = []
for item in root.findall('crew'):
    crew2 = Crew(item)
    crew2.validateNodes()
    crewBin.append(crew2)




"""
Here are possible classes for the project
  Activity
  Category
  Cluster
  Condition
  Contagion
  Crew
  Database
  DefaultField
  EnumField
  Field
  FieldRange
  Node
  RangeField
  RangeFields
  Resource
  StringEnumField
  StringField
  Suscept
  Treatment
  Validation
  Workbook
Here are some possible module scripts
  ImportExport
  Resize
  
"""
print("test")
