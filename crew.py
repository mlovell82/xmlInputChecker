from mimetypes import init
import xml.etree.ElementTree as ET
from node_class import *

class Crew(ParentNode):
    def __init__(self, acrewschildren):
        self.crew_label = LeafStringNode("crew_label", acrewschildren.find('crew_label'))
        self.demographics = acrewschildren.find('demographics')
        self.sex = LeafStringEnumStringNode("sex", self.demographics.find('sex'), ["Male", "Female"])
        self.contacts = LeafEnum01Node("contacts", self.demographics.find('contacts'))
        self.eva = LeafEnum01Node("eva", self.demographics.find('eva'))
        self.cac = LeafEnum01Node("cac", self.demographics.find('cac'))
        self.pregnancy = LeafEnum01Node("pregnancy", self.demographics.find('pregnancy'))
        self.nodes = [self.crew_label, self.sex, self.contacts, self.eva, self.cac, self.pregnancy]

    def printLabel(self):
        print(self.crew_label)     

    def validateNodes(self):
        print("VALIDATION FOR ", self.crew_label.getValue(), ": ")
        for node in self.nodes:
            node.validate()






