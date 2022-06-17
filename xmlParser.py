from mimetypes import init
import xml.etree.ElementTree as ET
from node2 import *

class Crew(ParentNode):  
    def __init__(self, acrewschildren): #pass in acrewchildren for anodes
        #now we add additional attribs for other Crew specific stuff besides Parent class
        self.label = '<crew>'
        self.root = acrewschildren
        self.crew_label = LeafStringNode("crew_label", acrewschildren.find('{medprat}crew_label')) #because ends on a string (the crew label)
        self.demographics = acrewschildren.find('{medprat}demographics')
        asex = self.demographics.find('{medprat}sex')
        self.sex = LeafStringEnumStringNode("sex", asex, ["male", "female"])
        self.contacts = LeafEnumYesNoNode("contacts", self.demographics.find('{medprat}contacts')) #yes or no so we use LeafEnumYesNoNode
        self.arthritis = LeafEnumYesNoNode("arthritis", self.demographics.find('{medprat}arthritis')) 
        #self.eva = LeafEnumYesNoNode("eva", self.demographics.find('{medprat}eva'))
        self.cac = LeafEnumYesNoNode("cac", self.demographics.find('{medprat}cac'))
        self.crowns = LeafEnumYesNoNode("crowns", self.demographics.find('{medprat}crowns'))
        self.pregnancy = LeafEnumYesNoNode("pregnancy", self.demographics.find('{medprat}pregnancy')) #all same method
        
        #-----------------------------
        self.nodes = [self.crew_label, self.sex, self.contacts, self.arthritis, self.cac, self.crowns, self.pregnancy]  #the nodes member where we call the validate() method. N: demographics not here. Rewrites the constructor statement. 

    def printLabel(self):
        print(self.crew_label)    

    def worksheetValidation(self):
        children = []
        children.append(self.root.findall('{medprat}crew_label'))
        children.append(self.root.findall('{medprat}demographics'))
        
        demographics = self.root.findall('{medprat}demographics')
        for itemA in demographics:
            children.append(itemA.findall('{medprat}sex'))
            children.append(itemA.findall('{medprat}contacts'))
            children.append(itemA.findall('{medprat}arthritis'))
            children.append(itemA.findall('{medprat}cac'))
            children.append(itemA.findall('{medprat}crowns'))
            children.append(itemA.findall('{medprat}pregnancy'))

        responseA = ""
        responseB = ""
        error = False
        for child in children:
            if(len(child) > 1):
                error = True
                for element in child:
                    node = LeafNode(element.tag, element)
                    responseA += "Error at line " + node.location + ": duplicate elements found for element \'" + node.label[9:] + "\'\n"
            else:
                responseB = "Worksheet validation successful!"
        if(error):
            return responseA
        else:
            return responseB 

    '''def validateNodes(self):
        print("VALIDATION FOR ", self.crew_label.getValue(), ": ") #get value from crew_label to print out which crew we're looking at
        for node in self.nodes:
            node.validate() #val parent'''

class Contagion(ParentNode):
    def __init__(self, acontagionschildren):
        self.label = '<contagion>'
        self.nodes = []
        self.root = acontagionschildren 
        self.nodes.append(LeafStringNode("condition_name", acontagionschildren.find('{medprat}condition_name')))
        polynomial = acontagionschildren.find('{medprat}polynomial')
        term = polynomial.find('{medprat}term')
        self.nodes.append(LeafEnumNode("degree", term.find('{medprat}degree'),0, 100, .001))
        self.nodes.append(LeafEnumNode("coefficient", term.find('{medprat}coefficient'),0, 100, .001))

    def validateContagionElements(self):
        reviewedItems = []
        foundItems = []
        validated = True
        for node in self.nodes:            
            duplicateFound = False
            if(node.label == "condition_name"):
                return node

    def worksheetValidation(self):
        children = []
        children.append(self.root.findall('{medprat}condition_name'))
        children.append(self.root.findall('{medprat}polynomial'))
        
        polynomial = self.root.findall('{medprat}polynomial')
        for itemA in polynomial:
            children.append(itemA.findall('{medprat}term'))
            term = itemA.findall('{medprat}term')
            for itemB in term:
                children.append(itemB.findall('{medprat}degree'))
                children.append(itemB.findall('{medprat}coefficient'))
        
        responseA = ""
        responseB = ""
        error = False
        for child in children:
            if(len(child) > 1):
                error = True
                for element in child:
                    node = LeafNode(element.tag, element)
                    responseA += "Error at line " + node.location + ": duplicate elements found for element \'" + node.label[9:] + "\'\n"
            else:
                responseB = "Worksheet validation successful!"
        if(error):    
            return responseA
        else:
            return responseB

class Segment(ParentNode):
    def __init__(self, asegmentschildren):
        self.label = '<segment>'
        self.nodes = []
        self.root = asegmentschildren        
        #get direct children of segment
        self.nodes.append(LeafStringNode("segment_name", asegmentschildren.find('{medprat}segment_name')))
        if(asegmentschildren.find('type') is not None):
            self.nodes.append(LeafStringEnumStringNode("type", asegmentschildren.find('{medprat}type'), ["mission", "sas", "eva", "rtdc", "general"]))
        max_ti_exists = asegmentschildren.find('max_ti_percent')
        if(max_ti_exists is not None):
            self.nodes.append(LeafEnumNode('max_ti_percent', asegmentschildren.find('{medprat}max_ti_percent'),0, 100, 0))
        
        #get children of subset
        set = asegmentschildren.find('{medprat}set')
        subset = set.find('{medprat}subset')
        
        crew_labels = subset.find('{medprat}crew_labels')
        if(crew_labels.find('{medprat}all_crew') is not None):
            self.nodes.append(LeafBoolNode('all_crew'))
        if(crew_labels.find('{medprat}crew_label') is not None):
            crew_members = crew_labels.findall('{medprat}crew_label')
            for member in crew_members:
                self.nodes.append(LeafStringNode("crew_label", member))
        
        intervals = subset.find('{medprat}intervals')
        if(intervals is not None):
            for interval in intervals:    
                self.nodes.append(LeafDateTimeNode("start_days", interval.find('{medprat}start_days'), 0, 10**4, 0.00069444))
                self.nodes.append(LeafEnumNode("end_days", interval.find('{medprat}end_days'), 0, 10**4, 0.00069444))
                self.nodes.append(LeafDateTimeSets("interval_set", interval.find('{medprat}start_days'), interval.find('{medprat}end_days')))
                periodic = interval.find('{medprat}periodic') 
                if(periodic is not None): 
                    self.nodes.append(LeafEnumNode("period_days", periodic.find('{medprat}period_days'), 0, 10**4, 0.00069444))
                    self.nodes.append(LeafEnumNode("end_days", periodic.find('{medprat}end_days'), 0, 10**4, 0.00069444))
         
        events = subset.find('{medprat}events') 
        if(events is not None):
            for event in events:
                self.nodes.append(LeafEnumNode("event_days", event.find('{medprat}event_days'), 0, 10**4, 0.00069444))        
                periodic = event.find('{medprat}periodic') 
                if(periodic is not None): 
                    self.nodes.append(LeafEnumNode("period_days", periodic.find('{medprat}period_days'), 0, 10**4, 0.00069444))
                    self.nodes.append(LeafEnumNode("end_days", periodic.find('{medprat}end_days'), 0, 10**4, 0.00069444))

    def isMission(self):
        if(self.nodes[0].value == 'MISSION'):
            return True
        else:
            return False


    def validateSegments(self):
        foundItems = []
        iteration = 0
        for node in self.nodes:
            iteration +- 1
            if(self.isMission()):  
                if(node.label == 'end_days'):
                    foundItems.append(['EOM', node])
            else:
                if(node.label == "start_days" or node.label =="end_days" or node.label == "event_days" or node.label == "period_days"):
                    foundItems.append(['Other', node])
        return foundItems

    def worksheetValidation(self):
        children = []
        children.append(self.root.findall('{medprat}type'))
        children.append(self.root.findall('{medprat}segment_name'))
        children.append(self.root.findall('{medprat}max_ti_percent'))
        children.append(self.root.findall('{medprat}set'))
        
        set = self.root.findall('{medprat}set')
        for itemA in set:
            children.append(itemA.findall('{medprat}subset'))
            subset = itemA.findall('{medprat}subset')
            for itemB in subset:
                children.append(itemB.findall('{medprat}crew_labels'))
                crew_labels = itemB.findall('{medprat}crew_labels')
                for itemC in crew_labels:
                    children.append(itemC.findall('medprat}all_crew'))
                
                children.append(itemB.findall('{medprat}intervals'))
                intervals = itemB.findall('{medprat}intervals')
                for interval in intervals:
                    children.append(interval.findall('{medprat}start_days'))
                    children.append(interval.findall('{medprat}end_days'))
                    children.append(interval.findall('{medprat}periodic'))
                    periodic = interval.findall('{medprat}periodic')
                    for itemD in periodic:
                        children.appand(itemD.findall('{medprat}period_days'))
                        children.append(itemD.findall('{medprat}end_days'))
                
                children.append(itemB.findall('{medprat}events'))
                events = itemB.findall('{medprat}events')
                for event in events:
                    children.append(event.findall('{medprat}event_days'))
                    children.append(event.findall('{medprat}periodic'))
                    periodic = event.findall('{medprat}periodic')
                    for itemE in periodic:
                        children.append(itemE.findall('{medprat}period_days'))
                        children.append(itemE.findall('{medprat}end_days'))
        
        responseA = ""
        responseB = ""
        error = False
        for child in children:
            if(len(child) > 1):
                error = True
                for element in child:
                    node = LeafNode(element.tag, element)
                    responseA += "Error at line " + node.location + ": duplicate elements found for element \'" + node.label[9:] + "\'\n"
            else:
                responseB = "Worksheet validation successful!"
        if(error):
            return responseA
        else:
            return responseB

class Resource(ParentNode):
    def __init__(self, aresourceschildren):
        self.label = '<resource>'
        self.nodes = []
        self.root = aresourceschildren
        self.nodes.append(LeafStringNode("resource_name", aresourceschildren.find('{medprat}resource_name')))
        if(aresourceschildren.find('{medprat}consumable') is not None):
            self.nodes.append(LeafStringEnumStringNode("consumable", aresourceschildren.find('{medprat}consumable'), ["yes", "no"]))
        if(aresourceschildren.find('{medprat}essential') is not None):
            self.nodes.append(LeafStringEnumStringNode("essential", aresourceschildren.find('{medprat}essential'), ["yes", "no"]))
        self.nodes.append(LeafEnumNode("mass_kg", aresourceschildren.find('{medprat}mass_kg'), 0, 200, 10**-6))
        self.nodes.append(LeafEnumNode("volume_ml", aresourceschildren.find('{medprat}volume_ml'), 0, 3*10**5, 10**-7))
        self.nodes.append(LeafEnumNode("parcel_quantity", aresourceschildren.find('{medprat}parcel_quantity'), 0.0001, 5000, 0.0001))
    
    def validateResourceElements(self):
        reviewedItems = []
        foundItems = []
        validated = True
        for node in self.nodes:            
            duplicateFound = False
            if(node.label == "resource_name"):
                return node

    def worksheetValidation(self):
        children = []
        children.append(self.root.findall('{medprat}resource_name'))
        children.append(self.root.findall('{medprat}consumable'))
        children.append(self.root.findall('{medprat}essential'))
        children.append(self.root.findall('{medprat}mass_kg'))
        children.append(self.root.findall('{medprat}volume_ml'))
        children.append(self.root.findall('{medprat}parcel_quantity'))

        responseA = ""
        responseB = ""
        error = False
        for child in children:
            if(len(child) > 1):
                error = True
                for element in child:
                    node = LeafNode(element.tag, element)
                    responseA += "Error at line " + node.location + ": duplicate elements found for element \'" + node.label[9:] + "\'\n"
            else:
                responseB = "Worksheet validation successful!"
        if(error):
            return responseA
        else:
            return responseB 

class MissionResource(ParentNode):
    def __init__(self, amissionresourceschildren):
        self.label = '<mission_resource>'
        self.nodes = []
        self.root = amissionresourceschildren
        self.nodes.append(LeafStringNode("resource_name", amissionresourceschildren.find('{medprat}resource_name')))
        self.nodes.append(LeafStringNode("segment_name", amissionresourceschildren.find('{medprat}segment_name')))
        quantity = amissionresourceschildren.find('{medprat}quantity')
        if(quantity.find('{medprat}max') is not None):
            self.nodes.append(LeafEnumNode("max", quantity.find('{medprat}max'),0,5000,0.0001))
        if(quantity.find('{medprat}min') is not None):
            self.nodes.append(LeafEnumNode("min", quantity.find('{medprat}min'),0,5000,0.0001))
    
    def validateResourceElements(self):
        reviewedItems = []
        foundItems = []
        validated = True
        for node in self.nodes:            
            duplicateFound = False
            if(node.label == "resource_name"):
                return node

    def worksheetValidation(self):
        children = []
        children.append(self.root.findall('{medprat}resource_name'))
        children.append(self.root.findall('{medprat}segment_name'))
        children.append(self.root.findall('{medprat}quantity'))
        quantity = self.root.findall('{medprat}quantity')
        for itemA in quantity:
            children.append(self.root.findall('{medprat}max'))
            children.append(self.root.findall('{medprat}min'))
        
        responseA = ""
        responseB = ""
        error = False
        for child in children:
            if(len(child) > 1):
                error = True
                for element in child:
                    node = LeafNode(element.tag, element)
                    responseA += "Error at line " + node.location + ": duplicate elements found for element \'" + node.label[9:] + "\'\n"
            else:
                responseB = "Worksheet validation successful!"
        if(error):
            return responseA
        else:
            return responseB 
    
class Condition(ParentNode):  
    def __init__(self, acrewschildren): 
        self.label = '<condition>'
        self.root = acrewschildren
        self.condition_name = LeafStringNode("condition_name", acrewschildren.find('{medprat}condition_name')) #because ends on a string (the crew label)
        self.segment_name = LeafStringNode("segment_name", acrewschildren.find('{medprat}segment_name'))
        self.demographics = acrewschildren.find('{medprat}demographics')
        asex = self.demographics.find('{medprat}sex')
        self.sex = LeafStringEnumStringNode("sex", asex, ["male", "female","any"])
        self.contacts = LeafEnumYesNoAnyNode("contacts", self.demographics.find('{medprat}contacts')) #yes or no so we use LeafEnumYesNoNode
        self.arthritis = LeafEnumYesNoAnyNode("arthritis", self.demographics.find('{medprat}arthritis')) 
        self.cac = LeafEnumYesNoAnyNode("cac", self.demographics.find('{medprat}cac'))
        self.crowns = LeafEnumYesNoAnyNode("crowns", self.demographics.find('{medprat}crowns'))
        self.pregnancy = LeafEnumYesNoAnyNode("pregnancy", self.demographics.find('{medprat}pregnancy')) #all same method
        
        apracat= acrewschildren.find('{medprat}pracat')
        self.pracat = LeafStringEnumStringNode("pracat", apracat, ["medical", "environmental","injury/trauma"])
         
        self.nodes = [self.condition_name, self.segment_name, self.sex, self.contacts, self.arthritis, self.cac, self.crowns, self.pregnancy, self.pracat]  #the nodes member where we call the validate() method. N: demographics not here. Rewrites the constructor statement. 
        
        
        self.incidence = acrewschildren.find('{medprat}incidence')
        
        #Top layer incidence data
        self.environmental = self.incidence.find('{medprat}environmental')
        self.sas = self.incidence.find('{medprat}sas') 
        self.eva = self.incidence.find('{medprat}eva') 
        self.fixed = self.incidence.find('{medprat}fixed') 
        self.gamma = self.incidence.find('{medprat}gamma') 
        self.lognormal = self.incidence.find('{medprat}lognormal') 
        
        
        '''if(self.environmental is not None): 
            self.environmental_rate = self.environmental.find('{medprat}environmental_rate')
            self.fixed=self.environmental_rate.find('{medprat}fixed')
            self.gamma=self.environmental_rate.find('{medprat}gamma')
            ff=False
            if(self.fixed is not None): 
                ff=True
                self.rate_per_year=LeafNNDoubleNode("rate_per_year", self.fixed.find('{medprat}rate_per_year'))
                self.nodes.append(self.rate_per_year)
            if(self.gamma is not None): 
                if(ff==True):
                    print("ERROR: *Both* Fixed and Gamma reported under Environmental Rate")
                self.shape=LeafNNDoubleNode("shape",self.gamma.find('{medprat}shape'))
                self.rate_years=LeafNNDoubleNode("rate_years",self.gamma.find('{medprat}rate_years'))
                self.nodes.append(self.shape)
                self.nodes.append(self.rate_years)
            else: 
                print("ERROR: Neither Fixed nor Gamma found under Environmental rate")
                
            self.condition_prob = self.environmental.find('{medprat}condition_prob')
            self.fixedCP=self.condition_prob.find('{medprat}fixed')
            self.beta=self.condition_prob.find('{medprat}beta')
            ff2=False
            
            if(self.fixedCP is not None):
                ff2=True
                self.probability=LeafNNDoubleNode("probability",self.fixedCP.find('{medprat}probability'))
                self.nodes.append(self.probability)
            if(self.beta is not None): 
                if(ff2==True):
                    print("ERROR: *Both* Fixed and Beta reported under Condition Prob")
                self.alpha=LeafNNDoubleNode("alpha",self.beta.find('{medprat}alpha'))
                self.beta=LeafNNDoubleNode("beta",self.beta.find('{medprat}beta'))
                self.nodes.append(self.alpha)
                self.nodes.append(self.beta)
            else: 
                print("Neither found")'''
            
 
        if(self.sas is not None): 
            self.beta = self.sas.find('{medprat}beta')
            self.alpha=LeafNNDoubleNode("alpha",self.beta.find('{medprat}alpha'))
            self.betaPar=LeafNNDoubleNode("beta",self.beta.find('{medprat}beta'))
            self.peak_hours=LeafNNDoubleNode("peak_hours",self.sas.find('{medprat}peak_hours'))
            self.min_hours=LeafNNDoubleNode("min_hours",self.sas.find('{medprat}min_hours'))
            self.max_hours=LeafNNDoubleNode("max_hours",self.sas.find('{medprat}max_hours'))
            self.nodes.append(self.alpha)
            self.nodes.append(self.betaPar)
            self.nodes.append(self.peak_hours)
            self.nodes.append(self.min_hours)
            self.nodes.append(self.max_hours)
            
        if(self.eva is not None): 
            fff=False
            self.fixed = self.eva.find('{medprat}fixed')
            if(self.fixed is not None): 
                self.probability=LeafNNDoubleNode("probability",self.fixed.find('{medprat}probability'))
                self.nodes.append(self.probability)
                
            self.beta = self.eva.find('{medprat}beta')
            if(self.beta is not None): 
                
                self.betaPar=LeafNNDoubleNode("beta",self.beta.find('{medprat}beta'))
                self.alpha=LeafNNDoubleNode("alpha",self.beta.find('{medprat}alpha'))
                self.nodes.append(self.alpha)
                self.nodes.append(self.betaPar)
            
            
        
        #self.pracat=LeafNNDoubleNode("fixed", afixed, ["male", ""])

        
        
        
        
        # self.nodes = [self.condition_name, self.segment_name, self.sex, self.contacts, self.arthritis, self.cac, self.crowns, self.pregnancy, self.pracat, self.rate_per_year, self.shape, self.rate_years]  #the nodes member where we call the validate() method. N: demographics not here. Rewrites the constructor statement. 

    def printLabel(self):
        print(self.condition_name)     

    '''def validateNodes(self): #dataframe for Table Class? 
        print("VALIDATION FOR ", self.condition_name.getValue(), ": ") #get value from crew_label to print out which crew we're looking at
        for node in self.nodes:
            node.validate() #val parent'''

    def worksheetValidation(self):
        children = []
        children.append(self.root.findall('{medprat}condition_name'))
        children.append(self.root.findall('{medprat}segment_name'))
        children.append(self.root.findall('{medprat}demographics'))
        demographics = self.root.findall('{medprat}demographics')
        for itemA in demographics:
            children.append(itemA.findall('{medprat}sex'))
            children.append(itemA.findall('{medprat}contacts'))
            children.append(itemA.findall('{medprat}arthritis'))
            children.append(itemA.findall('{medprat}cac'))
            children.append(itemA.findall('{medprat}crowns'))
            children.append(itemA.findall('{medprat}pregnancy'))

        children.append(self.root.findall('{medprat}pracat'))
        pracat = self.root.findall('{medprat}pracat')
        children.append(self.root.findall('{medprat}incidence'))
        incidence = self.root.findall('{medprat}incidence')
        for itemB in incidence:
            children.append(itemB.findall('{medprat}environmental'))
            children.append(itemB.findall('{medprat}sas'))
            children.append(itemB.findall('{medprat}eva'))
            children.append(itemB.findall('{medprat}fixed'))
            children.append(itemB.findall('{medprat}gamma'))
            children.append(itemB.findall('{medprat}lognormal'))
            environmental = itemB.findall('{medprat}environmental')
            for itemC in environmental:
                children.append(itemC.findall('{medprat}environmenat_rate'))
                environmental_rate = itemC.findall('{medprat}environmental_rate')
                for itemD in environmental_rate:
                    children.append(itemD.findall('{medprat}fixed'))
                    children.append(itemD.findall('{medprat}gamma'))
                    fixed = itemD.findall('{medprat}fixed')
                    for itemE in fixed:
                        children.append(itemE.findall('{medprat}rate_per_year'))
                    gamma = itemD.findall('{medprat}gamma')
                    for itemF in gamma:
                        children.append(itemF.findall('{medprat}shape'))
                        children.append(itemF.findall('{medprat}rate_years'))
                children.append(itemC.findall('{medprat}condition_prob'))
                condition_prob = itemC.findall('{medprat}condition_prob')
                for itemG in condition_prob:
                    children.append(itemG.findall('{medprat}fixed'))
                    children.append(itemG.findall('{medprat}beta'))
                    fixedCP = itemG.findall('{medprat}fixed')
                    for itemH in fixedCP:
                        children.append(itemH.findall('{medprat}probability'))
                    beta = itemG.findall('{medprat}beta')
                    for itemI in beta:
                        children.append(itemI.findall('{medprat}alpha'))
                        children.append(itemI.findall('{medprat}beta'))
            sas = itemB.findall('{medprat}sas')
            for itemK in sas:
                children.append(itemK.findall('{medprat}beta'))
                beta = itemK.findall('{medprat}beta')
                for itemJ in beta:
                    children.append(itemJ.findall('{medprat}alpha'))
                    children.append(itemJ.findall('{medprat}beta'))
                children.append(itemK.findall('{medprat}peak_hours'))
                children.append(itemK.findall('{medprat}min_hours'))
                children.append(itemK.findall('{medprat}max_hours'))
            eva = itemB.findall('{medprat}eva')
            for itemL in eva:
                children.append(itemL.findall('{medprat}fixed'))
                fixed = itemL.findall('{medprat}fixed')
                for itemM in fixed:
                    children.append(itemM.findall('{medprat}probability'))
                children.append(itemL.findall('{medprat}beta'))
                beta = itemL.findall('{medprat}beta')
                for itemN in beta:
                    children.append(itemN.findall('{medprat}beta'))
                    children.append(itemN.findall('{medprat}alpha'))                
        
        responseA = ""
        responseB = ""
        error = False
        for child in children:
            if(len(child) > 1):
                error = True
                for element in child:
                    node = LeafNode(element.tag, element)
                    responseA += "Error at line " + node.location + ": duplicate elements found for element \'" + node.label[9:] + "\'\n"
            else:
                responseB = "Worksheet validation successful!"
        if(error):
            return responseA
        else:
            return responseB 

class Treatment(ParentNode):
    def __init__(self, atreatmentschildren):
        self.label = '<treatment>'
        self.nodes = []
        self.root = atreatmentschildren
        self.nodes.append(LeafStringNode("target_name", atreatmentschildren.find('{medprat}target_name')))
        self.nodes.append(LeafStringNode("source_name", atreatmentschildren.find('{medprat}source_name')))
        
        #get children of cases
        cases = atreatmentschildren.find('{medprat}cases')
        #single - treatment case
        single = cases.find('{medprat}single')
        #if(single is not None):
            #self.getTreatmentCase(single)
        double = cases.find('{medprat}double')
        if(double is not None):
            best = double.find('{medprat}best')
            #if(best is not None):
                #self.getTreatmentCase(best)
            worst = double.find('{medprat}worst')
            #if(worst is not None):
                #self.getTreatmentCase(worst)
        
    def getTreatmentCase(self, atreatmentcase):
        if(atreatmentcase.find('efficacy_percent') is not None):
            self.nodes.append(LeafEnumNode("efficacy_percent", atreatmentcase.find('{medprat}efficacy_percent'),0,100,0))
        if(atreatmentcase.find('necessity_percent') is not None):
            self.nodes.append(LeafEnumNode("necessity_percent", atreatmentcase.find('{medprat}necessity_percent'),0,100,0))
            
        cluster_type = atreatmentcase.find('{medprat}cluster_type')        
        nonalternate = cluster_type.find('{medprat}nonalternate')
        if(nonalternate is not None):
            self.nodes.append(LeafEnumNode("contribution", nonalternate.find('{medprat}contribution'),0,1000,10**-4)) #made up numbers
                #alternate
        alternate = cluster_type.find('{medprat}alternate')
        if(alternate is not None):
            if(alternate.find('equivalence') is not None):
                self.nodes.append(LeafEnumNode("equivalence", alternate.find('{medprat}equivalence'),0,1000,10**-4)) #made up numbers
            if(alternate.find('primacy') is not None):
                self.nodes.append(LeafEnumNode("primacy", alternate.find('{medprat}primacy'), 0, 1000, 10**-4)) #made up numbers
            #dosage
        dosage = atreatmentcase.find('{medprat}dosage')
        self.nodes.append(LeafEnumNode("rate_per_day", dosage.find('{medprat}rate_per_day'),0,100,10**-4))
        if(dosage.find('duration_days') is not None):
            self.nodes.append(LeafEnumNode("duration_days", dosage.find('{medprat}duration_days'),0,1000,0)) #made up numbers
    
    def validateTreatments(self):
        foundItems = []
        for node in self.nodes:
            if(node.label == "target_name" or node.label == "source_name"):
                foundItems.append(node)
        return foundItems

    def worksheetValidation(self):
        children = []
        children.append(self.root.findall('{medprat}target_name'))
        children.append(self.root.findall('{medprat}source_name'))
        children.append(self.root.findall('{medprat}cases'))
        
        cases = self.root.findall('{medprat}cases')
        for itemA in cases:
            children.append(itemA.findall('{medprat}single'))
            children.append(itemA.findall('{medprat}double'))
            double = itemA.findall('{medprat}double')
            for itemB in double:
                children.append(itemB.findall('{medprat}best'))
                crew_labels = itemB.findall('{medprat}worst')
        
        responseA = ""
        responseB = ""
        error = False
        for child in children:
            if(len(child) > 1):
                error = True
                for element in child:
                    node = LeafNode(element.tag, element)
                    responseA += "Error at line " + node.location + ": duplicate elements found for element \'" + node.label[9:] + "\'\n"
            else:
                responseB = "Worksheet validation successful!"
        if(error):    
            return responseA
        else:
            return responseB

class AlternateTreatment(ParentNode):
    def __init__(self, atreatmentschildren):
        self.label = '<alternate_treatment>'
        self.nodes = []
        self.root = atreatmentschildren
        self.nodes.append(LeafStringNode("category_name", atreatmentschildren.find('{medprat}category_name')))
        self.nodes.append(LeafStringNode("resource_name", atreatmentschildren.find('{medprat}resource_name')))
        self.nodes.append(LeafEnumNode("amount_per_category",atreatmentschildren.find('{medprat}amount_per_category'), 0, 100, 0.001)) #made up numbers

    def validateCategories(self):
        foundItems = []
        for node in self.nodes:
            if(node.label == "category_name"):
                foundItems.append(node)
            if(node.label == "resource_name"):
                foundItems.append(node)    
            if(node.label == "amount_per_category"):
                return foundItems

    def worksheetValidation(self):
        children = []
        children.append(self.root.findall('{medprat}category_name'))
        children.append(self.root.findall('{medprat}resource_name'))
        children.append(self.root.findall('{medprat}amount_per_category'))
        
        responseA = ""
        responseB = ""
        error = False
        for child in children:
            if(len(child) > 1):
                error = True
                for element in child:
                    node = LeafNode(element.tag, element)
                    responseA += "Error at line " + node.location + ": duplicate elements found for element \'" + node.label[9:] + "\'\n"
            else:
                responseB = "Worksheet validation successful!"
            
        if(error):
            return responseA
        else:
            return responseB

class Suscept(ParentNode):
    def __init__(self, aSusceptschildren):
        self.label = '<suscept>'
        self.nodes = []
        self.root = aSusceptschildren
        self.nodes.append(LeafStringNode("target", aSusceptschildren.find('{medprat}target')))
        self.nodes.append(LeafStringNode("source", aSusceptschildren.find('{medprat}source')))
        self.nodes.append(LeafEnumNode("incidence_proportion_percent",aSusceptschildren.find('{medprat}incidence_proportion_percent'), 0, 100, 10**-4))

    def validateSuscepts(self):
        foundItems = []
        for node in self.nodes:
            if(node.label == "target"):
                foundItems.append(node)
            if(node.label == "source"):
                foundItems.append(node)    
        return foundItems

    def worksheetValidation(self):
        children = []
        children.append(self.root.findall('{medprat}target'))
        children.append(self.root.findall('{medprat}source'))
        children.append(self.root.findall('{medprat}incidence_proportion_percent'))
        
        responseA = ""
        responseB = ""
        error = False
        for child in children:
            if(len(child) > 1):
                error = True
                for element in child:
                    node = LeafNode(element.tag, element)
                    response += "Error at line " + node.location + ": duplicate elements found for element \'" + node.label[9:] + "\'\n"
            else:
                responseB = "Worksheet validation successful!"
        if(error):
            return responseA
        else:
            return responseB

class Cluster(ParentNode):
    def __init__(self, aClusterschildren):
        self.label = '<simple_treatment>'
        self.nodes = []
        self.root = aClusterschildren
        self.nodes.append(LeafStringNode("condition_name", aClusterschildren.find('{medprat}condition_name')))
        self.nodes.append(LeafStringNode("resource_name", aClusterschildren.find('{medprat}resource_name')))
        if(aClusterschildren.find('{medprat}best_case') != None):
            self.nodes.append(LeafEnumNode("best_case", aClusterschildren.find('{medprat}best_case'),0,100,.001))
        if(aClusterschildren.find('{medprat}worst_case') != None):
            self.nodes.append(LeafEnumNode("worst_case", aClusterschildren.find('{medprat}worst_case'),0,100,.001))
        if(aClusterschildren.find('{medprat}category_name') != None):
            self.nodes.append(LeafStringNode("category_name", aClusterschildren.find('{medprat}category_name')))
    
    def validateClusters(self):
        foundItems = []
        for node in self.nodes:
            if(node.label == "condition_name"):
                foundItems.append(node)
            if(node.label == "resource_name"):
                foundItems.append(node)
        return foundItems

    def worksheetValidation(self):
        children = []
        children.append(self.root.findall('{medprat}condition_name'))
        children.append(self.root.findall('{medprat}resource_name'))
        children.append(self.root.findall('{medprat}best_case'))
        children.append(self.root.findall('{medprat}worst_case'))
        children.append(self.root.findall('{medprat}category_name'))
        
        responseA = ""
        responseB = ""
        error = False
        for child in children:
            error = True
            if(len(child) > 1):
                for element in child:
                    node = LeafNode(element.tag, element)
                    responseA += "Error at line " + node.location + ": duplicate elements found for element \'" + node.label[9:] + "\'\n"
            else:
                responseB = "Worksheet validation successful!"
        if(error):    
            return responseA
        else:
            return responseB
            
#-------------------------MAIN #from pathlab important path

print('Running') #print verbose if needed

pageList = []

#tree = ET.parse('co.xml', parser=LineNumberingParser())
#tree = ET.parse('moon.xml', parser=LineNumberingParser())
#tree = ET.parse('iss6.xml', parser=LineNumberingParser())
#tree = ET.parse('mars.xml', parser=LineNumberingParser())
#tree = ET.parse('mars4.xml', parser=LineNumberingParser())
#tree = ET.parse('gateway_multi.xml', parser=LineNumberingParser())
#tree = ET.parse('contagion_test.xml', parser=LineNumberingParser())
#tree = ET.parse('gateway.xml', parser=LineNumberingParser()) #error imbedded for mission_resource test
tree = ET.parse('gateway2.xml', parser=LineNumberingParser())
root = tree.getroot()

counter = 0
#ET.dump(tree)

#Crew
crewBin = []
for item in root.findall('{medprat}crew'):
    crew = Crew(item)
    crewBin.append(crew)

#Segment
segmentBin = []
for item in root.findall('{medprat}segment'):
    segment = Segment(item)
    segmentBin.append(segment)

#Mission Resource
missionResourceBin = []
for item in root.findall('{medprat}mission_resource'):
    missionResource = MissionResource(item)
    missionResourceBin.append(missionResource)

#Contagion
contagionBin = []
for item in root.findall('{medprat}contagion'):
    contagion = Contagion(item)
    contagionBin.append(contagion)

#Alternative Treatment
alternativeTreatmentBin = []
for item in root.findall('{medprat}alternate_treatment'):
    category = AlternateTreatment(item)
    alternativeTreatmentBin.append(category)

#Treatment
treatmentBin = []
for item in root.findall('{medprat}treatment'):
    treatment = Treatment(item)
    treatmentBin.append(treatment)

#Suscept
susceptBin = []
for item in root.findall('{medprat}suscept'):
    suscept = Suscept(item)
    susceptBin.append(suscept)

#Condition
condBin = []
counter = 0 
for item in root.findall('{medprat}condition'): #CREW1, CREW2, etc.
    condition = Condition(item)
    condBin.append(condition)

#Resource
resourceBin = []
counter = 0 
for item in root.findall('{medprat}resource'): 
    resource = Resource(item)
    resourceBin.append(resource)

#Cluster
clusterBin = []
counter = 0 
for item in root.findall('{medprat}simple_treatment'): 
    cluster = Cluster(item)
    clusterBin.append(cluster)

#---------------------
    
pageList.append(crewBin)
pageList.append(segmentBin)
pageList.append(missionResourceBin)
pageList.append(contagionBin)
pageList.append(alternativeTreatmentBin)
pageList.append(treatmentBin)
pageList.append(susceptBin)
pageList.append(condBin)
pageList.append(resourceBin)
pageList.append(clusterBin)
page = PageNode(pageList)
#page.validateAll()   
#page.validateLeafNodeValues()   
#page.validateParentNode()
page.validatePage()    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
# =============================================================================
# for country in root.findall('country'):
#      rank = country.find('rank').text
#      name = country.get('name')
#      print(name, rank)
# 
# Liechtenstein 1
# Singapore 4
# Panama 68
# =============================================================================
