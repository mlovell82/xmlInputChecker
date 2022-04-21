from mimetypes import init
from types import NoneType
import xml.etree.ElementTree as ET
from node import *

class Segment(ParentNode):
    def __init__(self, asegmentschildren):
        self.nodes = []        
        #get direct children of segment
        self.nodes.append(LeafStringNode("segment_name", asegmentschildren.find('segment_name')))
        if(asegmentschildren.find('type') is not None):
            self.nodes.append(LeafStringEnumStringNode("type", asegmentschildren.find('type'), ["mission", "sas", "eva", "rtdc"]))
        max_ti_exists = asegmentschildren.find('max_ti_percent')
        if(max_ti_exists is not None):
            self.nodes.append(LeafEnumNode('max_ti_percent', asegmentschildren.find('max_ti_percent'),0, 100, 0))
        
        #get children of subset
        set = asegmentschildren.find('set')
        subset = set.find('subset')
        
        crew_labels = subset.find('crew_labels')
        if(crew_labels.find('all_crew') is not None):
            self.nodes.append(LeafBoolNode('all_crew'))
        if(crew_labels.find('crew_label') is not None):
            crew_members = crew_labels.findall('crew_label')
            for member in crew_members:
                self.nodes.append(LeafStringNode("crew_label", member))
        
        intervals = subset.find('intervals')
        if(intervals is not None):
            for interval in intervals:    
                self.nodes.append(LeafEnumNode("start_days", interval.find('start_days'), 0, 100000, .001))
                self.nodes.append(LeafEnumNode("end_days", interval.find('end_days'), 0, 100000, .001))
                periodic = interval.find('periodic') 
                if(periodic is not None): 
                    self.nodes.append(LeafEnumNode("period_days", periodic.find('period_days'), 0, 100000, .001))
                    self.nodes.append(LeafEnumNode("end_days", periodic.find('end_days'), 0, 100000, .001))
         
        events = subset.find('events') 
        if(events is not None):
            for event in events:
                self.nodes.append(LeafEnumNode("event_days", event.find('event_days'), 0, 100000, .001))        
                periodic = event.find('periodic') 
                if(periodic is not None): 
                    self.nodes.append(LeafEnumNode("period_days", periodic.find('period_days'), 0, 100000, .001))
                    self.nodes.append(LeafEnumNode("end_days", periodic.find('end_days'), 0, 100000, .001))
