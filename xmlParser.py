from mimetypes import init
import xml.etree.ElementTree as ET
from decimal import *

class LeafNode:  
  def __init__(self, alabel, anode):
        self.label = alabel
        self.value = anode.text
        self.location = str(anode._start_line_number)

  def setValue(self, avalue):
    self.value = avalue

  def getValue(self):
    return self.value
    
  def getLabel(self):
    return self.label

class ParentNode:
  nodes = []
  def __init__(self, anodes):
    self.nodes = anodes

  

  def validateNodes(self):
    errorFound = False
    singleNodeResult = ""
    totalMessage = ""

    if(self.worksheetValidation() != "Worksheet validation successful!"):
      errorFound = True
      totalMessage += self.worksheetValidation()
    
    parentLabels = []
    for node in self.nodes:
      #check for field min, max, or step violations
      singleNodeResult = node.validateLessVerbose()
      if(singleNodeResult != "Field validation successful!"):
        errorFound = True
        totalMessage += singleNodeResult
      
    if(errorFound):
      return totalMessage
    else:
      return singleNodeResult

class PageNode:
  page = []
  def __init__(self, aparentNodes):
    self.page = aparentNodes
  
  def validateAll(self):
    #print("FIELD LEVEL VALIDATION:")
    self.validateLeafNodeValues()
    print(" ")
    #print("TABLE LEVEL VALIDATION:")
    self.validateParentNode()
    print(" ")
    #print("DATABASE LEVEL VALIDATION:")
    self.validatePage()

  def validatePage(self):
    #Duplicate and omitted worksheet types are reported
    for parentNodeList in self.page:    
      self.checkForDuplicateParentNodes(parentNodeList)
    self.checkForMissingParentNodes()

    #For alternative treatment nodes, resource names are reported if they do not appear in the condition node
    self.checkResourceNamesInAlternateTreatmentsAndResources()

    #For contagion nodes, condition names are reported if they do not appear in condition nodes
    self.checkConditionNamesInContagionsAndConditions()

    #For the susceptibility nodes, condition names are reported if they do not appear in the condition node
    self.checkConditionNamesInSusceptsAndConditions()

    #For the treatment nodes, nodes are reported that do not appear in other nodes (if the necessary nodes are in the set)
    self.checkResourceNamesInTreatmentsAndResources() #resource names that do not appear in the resource nodes
    self.checkConditionNamesInTreatmentsAndConditions() #condition names that do not appear in the condition nodes
    self.checkCategoryNameResourceNameComboInTreatmentsAndAlternateTreatments() #combination of category name and resource name in the same row that do not appear in the alternate treatment nodes
    
    #For the cluster nodes, nodes are reported if they do not appear in other parent nodes (if the necessary nodes are in the set)
    self.checkSourceNamesInClustersAndResources()
    self.checkTargetNamesInClustersAndConditions()

    #For mission resource nodes, check that resource/segment time/crew label combinations are unique
    if(self.checkResourceCrewSegmentTimeInMissionResources() != "validated"):
      print(self.checkResourceCrewSegmentTimeInMissionResources())
  
  def validateParentNode(self):
    items = []
    contagionItems = []
    categoryItems = []
    treatmentItems = []
    clusterItems = []
    susceptItems = []
    eom = 0
    for parentNodeList in self.page:
      for parentNode in parentNodeList:  
        #check 1:  look for duplicate resources
        if(parentNode.label =='<resource>'):
          newItem = parentNode.validateResourceElements()
          for item in items:
            if(item.value == newItem.value):
              print("<resource> Error at line " + newItem.location + ":  " + newItem.value + " is listed multiple times")  
          items.append(newItem)

        #check 2:  look for duplicate contagion condition names
        if(parentNode.label == '<contagion>'):
          newItem = parentNode.validateContagionElements()
          for item in contagionItems:
            if(item == newItem.value):
              print("<contagion> Error at line " + newItem.location + ": " + newItem.value + " is listed multiple times")
          contagionItems.append(newItem.value)  

        #check 3: look for duplicate category_name/resource_name combinations in alternate treatments (formerly category)
        if(parentNode.label == '<alternate_treatment>'):
          newItem = parentNode.validateCategories()
          for item in categoryItems:
            if(item[0].value == newItem[0].value and item[1].value == newItem[1].value):
              print("<alternate_treatment> Error at line " + newItem[0].location + ": " + newItem[0].value + " and " + newItem[1].value + " are listed multiple times")
          categoryItems.append(newItem)

        #check 4: look for first or last times after EOM time are reported in segments (formerly activity)
        if(parentNode.label == '<segment>'):
          newItems = parentNode.validateSegments()
          other = 0
          for item in newItems:
            if(item[0] == "EOM"):
              eom = float(item[1].value)
          for item in newItems:
            other = float(item[1].value)
            if(eom < other):
              print("<segment> Error at line " + item[1].location + ": " + item[1].value + " is later than " + str(eom))
                          
        #check 5: look for duplicate target name / source name combinations in treatments
        if(parentNode.label == '<treatment>'):
          newItem = parentNode.validateTreatments()
          for item in treatmentItems:
            if(item[0].value == newItem[0].value and item[1].value == newItem[1].value):
              print("<treatment> Error at line " + newItem[0].location + ": " + newItem[0].value + " and " + newItem[1].value + " are listed multiple times")
          treatmentItems.append(newItem)
          
        #check 6: look for duplicate target name / source name combinations in clusters aka simple_treatment
        if(parentNode.label == '<simple_treatment>'):
          newItem = parentNode.validateClusters()
          for item in clusterItems:
            if(item[0].value == newItem[0].value and item[1].value == newItem[1].value):
              print("<simple_treatment> Error at line " + newItem[0].location + ": " + newItem[0].value + " and " + newItem[1].value + " are listed multiple times")
          clusterItems.append(newItem)

        #check 7: look for duplicate target condition name / source condition name in suscepts
        if(parentNode.label == '<suscept>'):
          newItem = parentNode.validateSuscepts()
          for item in susceptItems:
            if(item[0].value == newItem[0].value and item[1].value == newItem[1].value):
              print("<suscept> Error at line " + newItem[0].location + ": " + newItem[0].value + " and " + newItem[1].value + " are listed multiple times")
          susceptItems.append(newItem)  
        
  def checkForDuplicateParentNodes(self, parentNodeList):
    reviewedItems = []
    for parentNode in parentNodeList:
      for item in reviewedItems:
        if(item[0].label == parentNode[0].label):
          print("Duplicate node found at line " + item[0].location + " there are multiple instances of ")

  def checkForMissingParentNodes(self):
    reviewedItems = ['<crew>', '<segment>', '<contagion>', '<condition>', '<resource>', '<treatment>', '<suscept>', '<mission_resource>', '<alternate_treatment>', '<simple_treatment>']
    for item in reviewedItems:
      itemFound = False
      for parentNodeList in self.page:
        if(len(parentNodeList) > 0):
          if(item == parentNodeList[0].label):
            itemFound = True
      if(itemFound == False):
        print("Missing " + item + " in this file")

  def checkResourceNamesInAlternateTreatmentsAndResources(self):
    alternatateTreatmentResource = []
    resource = []

    for parentNodeList in self.page:        
      for parentNode in parentNodeList:
        if(parentNode.label == '<alternate_treatment>'):
          alternatateTreatmentResource.append(parentNode.nodes[1].value)
        if(parentNode.label == '<resource>'):
          resource.append(parentNode.nodes[0].value)
    
    for resource in alternatateTreatmentResource:
      isFound = False
      for aresource in resource:
        if(aresource == resource):
          isFound = True
      if(isFound == False):
        print('<alternate_treatment> resource_name ' + resource + ' is missing from the <resource> elements')

  def checkConditionNamesInContagionsAndConditions(self):
    contagionConditionNames = []
    conditionConditionNames = []
    for parentNodeList in self.page:        
      for parentNode in parentNodeList:
        if(parentNode.label == '<contagion>'):
          contagionConditionNames.append(parentNode.nodes[0].value)
        if(parentNode.label == '<condition>'):
          conditionConditionNames.append(parentNode.nodes[0].value)
    for conditionNameA in contagionConditionNames:
      isFound = False
      for conditionNameB in conditionConditionNames:
        if(conditionNameA == conditionNameB):
          isFound = True
      if(isFound == False):
        print('<contagion> condition_name ' + conditionNameA + ' is missing from the <condition> elements')
  
  def checkConditionNamesInSusceptsAndConditions(self):
    susceptTargets = []
    conditionConditionNames = []
    for parentNodeList in self.page:        
      for parentNode in parentNodeList:
        if(parentNode.label == '<suscept>'):
          susceptTargets.append(parentNode.nodes[0].value)
        if(parentNode.label == '<condition>'):
          conditionConditionNames.append(parentNode.nodes[0].value)
    for conditionNameA in susceptTargets:
      isFound = False
      for conditionNameB in conditionConditionNames:
        if(conditionNameA == conditionNameB):
          isFound = True
      if(isFound == False):
        print('<suscept> target ' + conditionNameA + ' is missing from the <condition> elements')

  def checkResourceNamesInTreatmentsAndResources(self):
    treatmentResource = []
    resource = []

    for parentNodeList in self.page:        
      for parentNode in parentNodeList:
        if(parentNode.label == '<treatment>'):
          treatmentResource.append(parentNode.nodes[1].value)
        if(parentNode.label == '<resource>'):
          resource.append(parentNode.nodes[0].value)
    
    for resource in treatmentResource:
      isFound = False
      for aresource in resource:
        if(aresource == resource):
          isFound = True
      if(isFound == False):
        print('<treatment> resource_name ' + resource + ' is missing from the <resource> elements')

  def checkConditionNamesInTreatmentsAndConditions(self):
    treatmentTargetNames = []
    conditionConditionNames = []
    for parentNodeList in self.page:        
      for parentNode in parentNodeList:
        if(parentNode.label == '<treatment>'):
          treatmentTargetNames.append(parentNode.nodes[0].value)
        if(parentNode.label == '<condition>'):
          conditionConditionNames.append(parentNode.nodes[0].value)
    for conditionNameA in treatmentTargetNames:
      isFound = False
      for conditionNameB in conditionConditionNames:
        if(conditionNameA == conditionNameB):
          isFound = True
      if(isFound == False):
        print('<treatment> target_name ' + conditionNameA + ' is missing from the <condition> elements')

  def checkCategoryNameResourceNameComboInTreatmentsAndAlternateTreatments(self):
    #target_name source_name
    #category_name resource_name
    treatmentNames = []
    alternateTreatmentNames = []
    for parentNodeList in self.page:        
      for parentNode in parentNodeList:
        if(parentNode.label == '<treatment>'):
          treatmentNames.append(parentNode.nodes[0].value + " & " + parentNode.nodes[1].value)
        if(parentNode.label == '<alternate_treatment>'):
          alternateTreatmentNames.append(parentNode.nodes[0].value + " & " + parentNode.nodes[1].value)
    for conditionNameA in alternateTreatmentNames:
      isFound = False
      for conditionNameB in treatmentNames:
        if(conditionNameA == conditionNameB):
          isFound = True
      if(isFound == False):
        print('<alternate_treatment> category_name & resource_name combination ' + conditionNameA + ' is missing from the <treatment> elements')

  def checkSourceNamesInClustersAndResources(self):
    clusterSourceNames = []
    resourceResourceNames = []
    treatmentResourceNames = []
    for parentNodeList in self.page:        
      for parentNode in parentNodeList:
        if(parentNode.label == '<simple_treatment>'):
          clusterSourceNames.append(parentNode.nodes[1].value)
        if(parentNode.label == '<resource>'):
          resourceResourceNames.append(parentNode.nodes[0].value)
        if(parentNode.label == '<treatment>'):
          treatmentResourceNames.append(parentNode.nodes[1].value)
    for treatmentResourceName in treatmentResourceNames:
      isFound = False
      for resourceName in resourceResourceNames:
        if(resourceName == treatmentResourceName):
          isFound = True
      if(isFound == False):
        print('<treatment> resource_name ' + treatmentResourceName + ' is missing from the <resource> elements')
      isFound = False
      for clusterResourceName in clusterSourceNames:
        if(clusterResourceName == treatmentResourceName):
          isFound = True
      if(isFound == False):
        print('<treatment> resource_name ' + treatmentResourceName + ' is missing from the <cluster> elements')

  def checkTargetNamesInClustersAndConditions(self):
    clusterSourceNames = []
    conditionResourceNames = []
    treatmentResourceNames = []
    for parentNodeList in self.page:        
      for parentNode in parentNodeList:
        if(parentNode.label == '<simple_treatment>'):
          clusterSourceNames.append(parentNode.nodes[0].value)
        if(parentNode.label == '<condition>'):
          conditionResourceNames.append(parentNode.nodes[0].value)
        if(parentNode.label == '<treatment>'):
          treatmentResourceNames.append(parentNode.nodes[0].value)
    for treatmentResourceName in treatmentResourceNames:
      isFound = False
      for resourceName in conditionResourceNames:
        if(resourceName == treatmentResourceName):
          isFound = True
      if(isFound == False):
        print('<treatment> target_name ' + treatmentResourceName + ' is missing from the <condition> elements')
      isFound = False
      for clusterResourceName in clusterSourceNames:
        if(clusterResourceName == treatmentResourceName):
          isFound = True
      if(isFound == False):
        print('<treatment> target_name ' + treatmentResourceName + ' is missing from the <cluster> elements')
##################################################
  def checkResourceCrewSegmentTimeInMissionResources(self):
    missionResourceListA = []
    missionResourceListB = []
    segmentList = []
    #Get each mission resource element and append them to 2 lists
    for parentList in self.page:
      for parent in parentList:
        if(parent.label == "<mission_resource>"):
          missionResourceListA.append(parent)
          missionResourceListB = missionResourceListA
        if(parent.label == "<segment>"):
          segmentList.append(parent)
    
    #Find any mission resources that have the same value for resource_name   
    incrementA = 0   
    for  missionA in missionResourceListA:
      incrementB = 0
      for missionB in missionResourceListB:
        if(missionB.nodes[0].value == missionA.nodes[0].value and incrementA != incrementB):
          #Find corresponding segments for both mission resources
          segmentA = []
          segmentB = []
          for segment in segmentList:
            if(segment.nodes[0].value == missionA.nodes[1].value):
              segmentA = segment
            if(segment.nodes[0].value == missionB.nodes[1].value):
              segmentB = segment
          
          #Check for matching crew_labels
          crewLabelsMatch = False
          for nodeA in segmentA.nodes:
            for nodeB in segmentB.nodes:
              if(((nodeA.label == 'crew_label' and nodeB.label == 'crew_label') or (nodeA.label == 'all_crew' and nodeB.label == 'all_crew')) and nodeA.value == nodeB.value):
                crewLabelsMatch = True
          
          #Check segment list for matching segment times
          for nodeA in segmentA.nodes:
            if(nodeA.label == 'interval_set'):
              for nodeB in segmentB.nodes:
                if(nodeB.label == 'interval_set'):
                  if(nodeB.start < nodeA.end and nodeB.start >= nodeA.start):
                    if(crewLabelsMatch):
                      return '<segment> Error at line ' + nodeB.location + ": segment intervals must not overlap with matching crew_labels for mission_resource elements with matching resources"
                  elif(nodeA.start < nodeB.end and nodeA.start >= nodeB.start):
                    if(crewLabelsMatch):
                      return '<segment> Error at line ' + nodeB.location + ": segment intervals must not overlap with matching crew_labels for mission_resource elements with matching resources"
        incrementB += 1
      incrementA += 1
    return "validated"
 ####################################################                  
  
  def validateLeafNodeValues(self):
    errorFound = False
    singleNodeResult = ""
    totalMessage = ""
    for parentNodeList in self.page:
      for parentNode in parentNodeList:
        singleNodeResult = parentNode.validateNodes()
        if(singleNodeResult != "Field validation successful!"):
          errorFound = True
          totalMessage += singleNodeResult
    if(errorFound):
      print("error source 1")
      print(totalMessage)
    else:
      print(singleNodeResult)


class LeafStringNode(LeafNode):
    constraint = {
      "min": 1,
      "max": 256
    }

    def validate(self):
      if(len(self.value) < self.constraint["min"] or len(self.value) > self.constraint["max"]):
        print(self.label + " must be no more than 256 characters and not blank!")
      else:
        print("validation successful!")

    def validateLessVerbose(self):
      if(len(self.value) < self.constraint["min"] or len(self.value) > self.constraint["max"]):
        return "Error at line " + self.location + " for " + self.label + ": must be no more than 256 characters and not blank!\n"
      else:
        return "Field validation successful!"

class LeafDateTimeNode(LeafNode):
    def __init__(self, alabel, anode, amin, amax, astep):
      self.label = alabel
      self.value = anode.text
      self.location = str(anode._start_line_number)
      self.constraint = {
      "min": amin,
      "max": amax,
      "step": astep
    }

    def validate(self):
      valuePrecision = Decimal(self.value)
      constraintPrecision = Decimal(str(self.constraint['step']))
      if(self != ""):
        if(float(self.value) < self.constraint['min']):
          print(self.label + " must be greater than or equal to " + str(self.constraint["min"]))
        elif(float(self.value) > self.constraint['max']):
          print(self.label + " must be less than or equal to " + str(self.constraint['max']))
        elif(valuePrecision.as_tuple().exponent % constraintPrecision.as_tuple().exponent != 0):
          return "Error at line " + self.location + " The value entered for " + self.label + " cannot have a decimal that is not a multiple of " + str(self.constraint['step']) + "\n"
        else:
          print("Field validation successful!")

    def validateLessVerbose(self):
      valuePrecision = Decimal(self.value)
      constraintPrecision = Decimal(str(self.constraint['step']))
      if(self != ""):
        if(float(self.value) < self.constraint['min']):
          return "Error at line " + self.location + " for " + self.label + ": must be greater than or equal to " + str(self.constraint["min"]) + "\n"
        elif(float(self.value) > self.constraint['max']):
          return "Error at line " + self.location + " for " + self.label + ": must be less than or equal to " + str(self.constraint['max']) + "\n"
        elif(valuePrecision.as_tuple().exponent % constraintPrecision.as_tuple().exponent != 0):
          return "Error at line " + self.location + " The value entered for " + self.label + " cannot have a decimal that is not a multiple of " + str(self.constraint['step']) + "\n"
        else:
          return "Field validation successful!"

class LeafDateTimeSets(LeafNode):
    def __init__(self, alabel, anodeA, anodeB):
      self.label = alabel
      self.start = anodeA.text
      self.end = anodeB.text
      self.location = str(anodeA._start_line_number)
    def validateLessVerbose(self):      
      return "Field validation successful!"

class LeafEnumNode(LeafNode):
    def __init__(self, alabel, anode, amin, amax, astep):
      self.label = alabel
      self.value = anode.text
      self.location = str(anode._start_line_number)
      self.constraint = {
      "min": amin,
      "max": amax,
      "step": astep
    }

    def validate(self):
      valuePrecision = Decimal(self.value)
      constraintPrecision = Decimal(str(self.constraint['step']))
      if(self != ""):
        if(float(self.value) < self.constraint['min']):
          print(self.label + " must be greater than or equal to " + str(self.constraint["min"]))
        elif(float(self.value) > self.constraint['max']):
          print(self.label + " must be less than or equal to " + str(self.constraint['max']))
        elif(valuePrecision.as_tuple().exponent < constraintPrecision.as_tuple().exponent):
          print('The value entered for ' + self.label + ' cannot be more precise than ' + str(self.constraint['step']))
        else:
          print("Field validation successful!")

    def validateLessVerbose(self):
      valuePrecision = Decimal(self.value)
      constraintPrecision = Decimal(str(self.constraint['step']))
      if(self != ""):
        if(float(self.value) < self.constraint['min']):
          return "Error at line " + self.location + " for " + self.label + ": must be greater than or equal to " + str(self.constraint["min"]) + "\n"
        elif(float(self.value) > self.constraint['max']):
          return "Error at line " + self.location + " for " + self.label + ": must be less than or equal to " + str(self.constraint['max']) + "\n"
        elif(valuePrecision.as_tuple().exponent < constraintPrecision.as_tuple().exponent):
          return "Error at line " + self.location + " The value entered for " + self.label + " cannot be more precise than " + str(self.constraint['step']) + "\n"
        else:
          return "Field validation successful!"

class LeafEnum01Node(LeafNode):
    constraint = {
      'min': '0',
      'max': '1'
    }   

    def validate(self):
      if(self.value != self.constraint['min'] and self.value != self.constraint['max']):
        print(self.label + " must equal ", self.constraint['min'], " or ", self.constraint['max'])
      else:
        print(self.label + " Field validation successful!")

    def validateLessVerbose(self):
      if(self.value != self.constraint['min'] and self.value != self.constraint['max']):
        return "Error at line " + self.location + " for " + self.label + ": must equal ", self.constraint['min'], " or ", self.constraint['max'] + "\n"
      else:
        return "Field validation successful!"

class LeafNNDoubleNode(LeafNode):
    constraint = {
      'min': 0,
      'max': 1000000000000  #@@@
    }   

    def validate(self): #each LeafNode should have its own validate() method
      if(Decimal(self.value) < self.constraint['min'] or Decimal(self.value) > self.constraint['max']):
        print(self.label, " must be between ", self.constraint['min'], " and ", self.constraint['max'])
      else:
        print(self.label, "Field validation successful!")

    def validateLessVerbose(self):
      if(Decimal(self.value) < self.constraint['min'] or Decimal(self.value) > self.constraint['max']):
        return "Error at line " + self.location + " for " + self.label + ": must be between" , self.constraint['min'], " and ", self.constraint['max']
      else:
        return "Field validation successful!"
        
    #-------    
        
class LeafEnumYesNoNode(LeafNode):
    constraint = {
      'min': 'no',
      'max': 'yes'
    } 

    def validate(self):
      if(self.value != self.constraint['min'] and self.value != self.constraint['max']):
        print(self.label, " must equal ", self.constraint['min'], " or ", self.constraint['max'])
      else:
        print(self.label, "Field validation successful!")

    def validateLessVerbose(self):
      if(self.value != self.constraint['min'] and self.value != self.constraint['max']):
        return self.label, " must equal ", self.constraint['min'], " or ", self.constraint['max']
      else:
        return "Field validation successful!"
        

        
class LeafEnumYesNoAnyNode(LeafNode):
    constraint = {
      'min': 'no',
      'max': 'yes',
      'any': 'any'
    } 

    def validate(self):
      if(self.value != self.constraint['min'] and self.value != self.constraint['max'] and self.value != self.constraint['any']):
        print(self.label, " must equal ", self.constraint['min'],",", self.constraint['max'], ", or", self.constraint['any'])
      else:
        print(self.label, " validation successful!")

    def validateLessVerbose(self):
      if(self.value != self.constraint['min'] and self.value != self.constraint['max'] and self.value != self.constraint['any']):
        return self.label, " must equal ", self.constraint['min'],",", self.constraint['max'], ", or", self.constraint['any']
      else:
        return "Field validation successful!"


class LeafStringEnumStringNode(LeafNode):
    def __init__(self, alabel, avalue, aconstraints):
      self.label = alabel
      self.value = avalue.text
      self.location = str(avalue._start_line_number)
      self.constraints = aconstraints

    def validate(self):
      found = False
      moreToGo = 0
      allowableValues = ""
      for constraint in self.constraints:
        if(self.getValue() == constraint):
          found = True
        allowableValues += constraint
        if(moreToGo < (len(self.constraints) -1)):
          allowableValues += ", "
      if(found != True):
        print("Acceptable values are " + allowableValues)
      else:
            print("validation successful!")

    def validateLessVerbose(self):
      found = False
      moreToGo = 0
      allowableValues = ""
      for constraint in self.constraints:
        if(self.getValue() == constraint):
          found = True
        allowableValues += constraint
        if(moreToGo < (len(self.constraints) -1)):
          allowableValues += ", "
      if(found != True):
        return "Error at line " + self.location + " Acceptable values are " + allowableValues + "\n"
      else:
            return "Field validation successful!"

class LeafBoolNode(LeafNode):
  def __init__(self, alabel):
    self.label = alabel
    self.value = True

  def validateLessVerbose(self):
    return "Field validation successful!"

class LineNumberingParser(ET.XMLParser):
    def _start_list(self, *args, **kwargs):
        # Here we assume the default XML parser which is expat
        # and copy its element position attributes into output Elements
        element = super(self.__class__, self)._start_list(*args, **kwargs)
        element._start_line_number = self.parser.CurrentLineNumber
        element._start_column_number = self.parser.CurrentColumnNumber
        element._start_byte_index = self.parser.CurrentByteIndex
        return element

    def _end(self, *args, **kwargs):
        element = super(self.__class__, self)._end(*args, **kwargs)
        element._end_line_number = self.parser.CurrentLineNumber
        element._end_column_number = self.parser.CurrentColumnNumber
        element._end_byte_index = self.parser.CurrentByteIndex
        return element  

