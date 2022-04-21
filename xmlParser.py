from mimetypes import init
import xml.etree.ElementTree as ET
from crew import *
from segment import *
from node import *

'''import sys
with open(sys.argv[1], 'r') as f:
    tree3 = ET.parse(f)'''

#Future topics to research
#2. Obtaining the xml file from the command line

tree = ET.parse('crew.xml')
tree2 = ET.parse('segment.xml')
root = tree.getroot()
root2 = tree2.getroot()
crewBin = []
segmentBin = []
for item in root.findall('crew'):
    crew = Crew(item)
    print("Validation for Crew:")
    crew.validateNodes()
    crewBin.append(crew)

for item in root2.findall('segment'):
    segment = Segment(item)
    print("Validation for Segments:")
    segment.validateNodes()
    segmentBin.append(segment)
