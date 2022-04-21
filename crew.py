from mimetypes import init
import xml.etree.ElementTree as ET
from node import *

class Crew(ParentNode):
    def __init__(self, acrewschildren):
        self.nodes = []
        self.nodes.append(LeafStringNode("crew_label", acrewschildren.find('crew_label')))
        
        #get children of demographics
        self.demographics = acrewschildren.find('demographics')
        self.nodes.append(LeafStringEnumStringNode("sex", self.demographics.find('sex'), ["MALE", "FEMALE"]))
        self.nodes.append(LeafEnum01Node("contacts", self.demographics.find('contacts')))
        self.nodes.append(LeafEnum01Node("crowns", self.demographics.find('crowns')))
        self.nodes.append(LeafEnum01Node("eva", self.demographics.find('eva')))
        self.nodes.append(LeafEnum01Node("cac", self.demographics.find('cac')))
        self.nodes.append(LeafEnum01Node("pregnancy", self.demographics.find('pregnancy')))     
