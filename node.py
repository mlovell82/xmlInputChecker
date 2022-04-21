from mimetypes import init
import xml.etree.ElementTree as ET

class LeafNode:  
  def __init__(self, alabel, anode):
        self.label = alabel
        self.value = anode.text

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
    for node in self.nodes:
      node.validate()
    print(" ")

class LeafStringNode(LeafNode):
    constraint = {
      "min": 1,
      "max": 250
    }

    def validate(self):
      if(len(self.value) < self.constraint["min"] or len(self.value) > self.constraint["max"]):
        print(self.label + " must be greater than 0 characters and less than 255 characters!")
      else:
        print(self.label + " validation successful!")

class LeafEnumNode(LeafNode):
    def __init__(self, alabel, anode, amin, amax, astep):
      self.label = alabel
      self.value = anode.text
      self.constraint = {
      "min": amin,
      "max": amax,
      "step": astep
    }

    def validate(self):
      if(self != ""):
        if(float(self.value) < self.constraint['min']):
          print(self.label + " must be greater than or equal to " + str(self.constraint["min"]))
        elif(float(self.value) > self.constraint['max']):
          print(self.label + " must be less than or equal to " + str(self.constraint['max']))
        else:
          print(self.label + " validation successful!")

class LeafEnum01Node(LeafNode):
    constraint = {
      'min': '0',
      'max': '1'
    }   

    def validate(self):
      if(self.value != self.constraint['min'] and self.value != self.constraint['max']):
        print(self.label + " must equal ", self.constraint['min'], " or ", self.constraint['max'])
      else:
        print(self.label + " validation successful!")

class LeafStringEnumStringNode(LeafNode):
    def __init__(self, alabel, avalue, aconstraints):
      self.label = alabel
      self.value = avalue.text
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
            print(self.getLabel() + " validation successful!")

class LeafBoolNode(LeafNode):
  def __init__(self, alabel):
    self.label = alabel
    self.value = True

  def validate(self):
    print(self.getLabel() + " validation successful!")

  
