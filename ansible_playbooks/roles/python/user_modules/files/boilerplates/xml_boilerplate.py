#!/usr/bin/env python

# Basename: xml_boilerplate
# Description: Common business logic for Python XML commands
# Version: 1.3
# VersionDate: 29 Jan 2020

# --- XML Commands ---
# Utility:          Parse, Root, Namespace, ToElement
# Element:          Elements, Element, ChildElements
# Value:            ElementText, ElementTag, ElementAttributes, ElementAttribute

from logging_boilerplate import *
import xml.etree.ElementTree as EL
import re

try:
    # Python 2 has both 'str' (bytes) and 'unicode' text
    basestring = basestring
    unicode = unicode
except NameError:
    # Python 3 names the unicode data type 'str'
    basestring = str
    unicode = str

# ------------------------ Classes ------------------------

class XmlManager(object):
    def __init__(self, xml):
        # Initial values or defaults
        self.elementTreeType = type(EL.ElementTree)
        self.elementType = type(EL.Element(None)) # instance not directly exposed
        self.entityType = type(XmlEntity)
        self.xml_path = str(xml)

        self.elementTree = self.Parse(self.xml_path)
        self.parsed = bool(self.elementTree)

        self.rootNamespace = self.Namespace() if (self.parsed) else ""


    def Parse(self, path):
        # logger.debug("(XmlManager:Parse): Init")
        # Read the XML configuration file
        logger.debug("(XmlManager:Parse): parsing {0}...".format(path))
        try:
            elementTree = EL.parse(path)
        except:
            elementTree = None
            logger.error("(XmlManager:Parse): error with parsing")
        return elementTree


    # Returns first element of ElementTree as root; any additional elements are considered comments
    def Root(self, item=None):
        if not item: item = self.elementTree
        entity = self.ToEntity(item.getroot())
        return entity


    def ToEntity(self, item=None):
        if not item: return self.Root()
        if isinstance(item, self.elementTreeType): return self.Root(item)
        if isinstance(item, self.elementType): return XmlEntity(item)
        if isinstance(item, self.entityType): return item
        logger.warning("(XmlManager:ToEntity): unanticipated entity: {0}".format(item))
        logger.warning("(XmlManager:ToEntity): unanticipated type(entity): {0}".format(type(item)))
        return item


    # # Cast to default element if provided a different type
    # def ToEntity(self, element=None):
    #     if not element: return self.Root()
    #     if isinstance(element, self.elementTreeType): return self.Root(element)
    #     if isinstance(element, self.entityType): return element
    #     logger.warning("(XmlManager:ToEntity): unanticipated entity: {0}".format(element))
    #     logger.warning("(XmlManager:ToEntity): unanticipated type(entity): {0}".format(type(element)))
    #     return element


    def Namespace(self, item=None):
        # logger.debug("(XmlManager:Namespace): Init")
        entity = self.ToEntity(item)
        result = re.match(r'\{.*\}', entity.element.tag)
        return result.group(0) if result else ""


    # # Get list of matching elements based on tag filter (XPath)
    # def Elements(self, tag, element=None):
    #     # logger.debug("(XmlManager:Elements): Init")
    #     element = self.ToElement(element)
    #     try:
    #         matches = element.findall(tag)
    #     except:
    #         matches = []
    #     return matches


    # # Get first matching element based on tag filter (XPath)
    # def Element(self, tag, element=None):
    #     # logger.debug("(XmlManager:Elements): Init")
    #     element = self.ToElement(element)
    #     try:
    #         match = element.find(tag)
    #     except:
    #         match = []
    #     return match


    def ParentElement(self, element):
        logger.debug("(XmlManager:ParentElement): Init")
        if isinstance(element, self.entityType):
            return self.Element("..", element)
        else:
            return None


    def ChildElements(self, element):
        # logger.debug("(XmlManager:ChildElements): Init")
        # element = self.ToElement(element)
        # return element.getchildren()
        if isinstance(element, self.entityType):
            # Deprecated in 2.7+
            return element.getchildren()
        else:
            return []


    # Get text content of element
    def ElementText(self, element):
        # logger.debug("(XmlManager:ElementText): Init")
        if isinstance(element, self.entityType):
            return element.text
        else:
            return ""


    # Get a specific element tag
    def ElementTag(self, element):
        # logger.debug("(XmlManager:ElementTag): Init")
        if isinstance(element, self.entityType):
            return element.tag
        else:
            return ""


    # Collection of element attributes; use .keys() on results for attribute names
    def ElementAttributes(self, element=None):
        # logger.debug("(XmlManager:ElementAttributes): Init")
        if isinstance(element, self.entityType):
            return element.attrib
        else:
            return {}


    # Get the value of a specific element attribute
    def ElementAttribute(self, attributeName, element):
        # logger.debug("(XmlManager:ElementAttribute): Init")
        if isinstance(element, self.entityType):
            return element.get(attributeName)
        else:
            return None


    # TODO: create ElementsByAttribute and ElementByAttribute

    # def Elements(self, tag, attributeName="", attributeValue="", element=None, recursive=False):
    #     logger.debug("(XmlManager:Elements): Init")
    #     if not element: element = self.elementTree
    #     logger.debug("(XmlManager:Elements): tag name: {0}".format(tag))
    #     logger.debug("(XmlManager:Elements): attributeName: {0}".format(attributeName))
    #     logger.debug("(XmlManager:Elements): attributeValue: {0}".format(attributeValue))

    #     elementFilter = ".//{0}{1}".format(self.rootNamespace, tag)

    #     if recursive:
    #         matches = element.iterfind(elementFilter)
    #     else:
    #         matches = element.findall(elementFilter)
    #     logger.debug("(XmlManager:Elements): matches: {0}".format(matches))

    #     # Filter matches
    #     results = []
    #     if attributeName != "" and attributeValue != "":
    #         logger.debug("(XmlManager:Elements): filtering element results...")
    #         for element in matches:
    #             if element.get(attributeName) == attributeValue:
    #                 results.append(element)
    #         logger.debug("(XmlManager:Elements): results: {0}".format(results))
        
    #     return results


    # def Element(self, tag, attributeName="", attributeValue="", element=None, recursive=False):
    #     logger.debug("(XmlManager:Element): Init")
    #     # if not element: element = self.elementTree
    #     if not element: element = self.Root()
    #     logger.debug("(XmlManager:Element): tag name: {0}".format(tag))
    #     logger.debug("(XmlManager:Element): attributeName: {0}".format(attributeName))
    #     logger.debug("(XmlManager:Element): attributeValue: {0}".format(attributeValue))

    #     # elementFilter = ".//{0}".format(tag)
    #     elementFilter = ".//{0}{1}".format(self.rootNamespace, tag)
    #     logger.debug("(XmlManager:Element): elementFilter: {0}".format(elementFilter))

    #     if recursive:
    #         matches = element.iterfind(elementFilter)
    #     else:
    #         matches = element.findall(elementFilter)
    #     logger.debug("(XmlManager:Element): matches: {0}".format(matches))

    #     # Filter matches
    #     result = None
    #     if attributeName != "" and attributeValue != "":
    #         logger.debug("(XmlManager:Element): filtering element result...")
    #         for element in matches:
    #             if element.get(attributeName) == attributeValue:
    #                 result = element
    #                 break
    #         logger.debug("(XmlManager:Element): result: {0}".format(result))
        
    #     return result



# Extension methods can only be placed on classes, not built-ins (e.g. str)
# - will need to take in ElementTree, Element, and XmlEntity
# - must return XmlEntity for chain calls
# - Example: <element>.Children()[0].Child("tagName").Tag()
# Currently using Python 2.6 where XPath support is unfeasibly poor; no parent support
class XmlEntity(object):
    def __init__(self, element):
        # Initial values or defaults
        self.type = type(EL.Element(None)) # instance not directly exposed
        self.element = None
        self.exists = False
        # Verify type is correct or fail
        if isinstance(element, self.type)
            self.element = element
            self.exists = True


    def __repr__(self):
        return str(self.element)


    def __str__(self):
        return self.Tag()


    def StripNamespace(self, text):
        if not isinstance(text, str): return ""
        # Trim matching namespace from start of tag
        match = re.match(r'\{.*\}', text)
        if match is None:
            return text # No namespace
        namespace = match.group(0)
        tagName = re.sub(namespace, r'', text)
        return tagName


    def Children(self, tagName=""):
        children = self.element.getchildren()
        results = []
        for c in children:
            child = XmlEntity(c)
            if tagName:
                childTag = self.StripNamespace(child.Tag())
                # Return matching child entity
                if childTag == tagName:
                    results.append(child)
            else:
                results.append(child)
        return results


    def Child(self, tagName):
        children = self.Children()
        for child in children:
            childTag = self.StripNamespace(child.Tag())
            # Return matching child entity
            if childTag == tagName: return child
        return None


    # Get the trimmed text content of an element
    def Text(self):
        if not self.exists: return ""
        return str(self.element.text).strip()


    # Get a specific element tag name
    def Tag(self, withNamespace=False):
        if not self.exists: return ""
        tagName = self.element.tag
        if not withNamespace: tagName = self.StripNamespace(tagName)
        return tagName


    # Collection of element attributes; use .keys() on result for attribute names
    def Attributes(self):
        if not self.exists: return []
        return self.element.attrib


    # Get the value of a specific element attribute
    def Attribute(self, attributeName):
        if not self.exists: return ""
        return self.element.get(attributeName)



# ------------------------ Main program ------------------------

# Initialize the logger
basename = "xml_boilerplate"
log_options = LogOptions(basename)
logger = get_logger(log_options)

if __name__ == "__main__":
    # Returns argparse.Namespace; to pass into function, use **vars(self.args)
    def parse_arguments():
        import argparse
        parser = argparse.ArgumentParser()
        parser.add_argument("--debug", action="store_true")
        return parser.parse_args()
    args = parse_arguments

    # Configure the logger
    log_level = 20                  # logging.INFO
    if args.debug: log_level = 10   # logging.DEBUG
    logger.setLevel(log_level)
    logger.debug("(__main__): args: {0}".format(args))
    logger.debug("(__main__): ------------------------------------------------")

    # -------- XML Test --------
    boilerplate = XmlManager()
    boilerplate.Exit()

    # --- Usage Example ---
    # sudo python /root/.local/lib/python2.7/site-packages/xml_boilerplate.py
