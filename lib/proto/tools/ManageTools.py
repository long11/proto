from proto.tools.GeneralGuiTool import GeneralGuiTool, MultiGeneralGuiTool
from proto.config.Config import GALAXY_BASE_DIR, GALAXY_REL_TOOL_CONFIG_FILE, URL_PREFIX
import os, re, shelve, shutil, sys, traceback
from importlib import import_module
from collections import OrderedDict
#import xml.etree.ElementTree as ET
from cgi import escape
from urllib import quote

SOURCE_CODE_BASE_DIR = GALAXY_BASE_DIR + '/lib'
#HB_TOOL_DIR = GALAXY_BASE_DIR + '/tools/hyperbrowser/new-xml/'
#PROTO_TOOL_DIR = HB_SOURCE_CODE_BASE_DIR + '/quick/webtools/'
PROTO_TOOL_DIR = GALAXY_BASE_DIR + '/lib/proto/tools/'
TOOL_SHELVE = GALAXY_BASE_DIR + '/database/proto-tool-cache.shelve'
TOOL_CONF = GALAXY_BASE_DIR + '/' + GALAXY_REL_TOOL_CONFIG_FILE
GALAXY_TOOL_XML_PATH = GALAXY_BASE_DIR + '/tools/'
TOOL_XML_REL_PATH = 'hyperbrowser/'



class GalaxyToolConfig:

    tool_xml_template = '''<tool id="%s" name="%s" version="1.0.0"
  tool_type="hyperbrowser_generic" proto_tool_module="%s" proto_tool_class="%s">
  <description>%s</description>
</tool>\n'''

    def __init__(self, tool_conf_fn=TOOL_CONF):
        self.tool_conf_fn = tool_conf_fn
        with open(self.tool_conf_fn, 'r') as tcf:
            self.tool_conf_data = tcf.read()
        
    def getSections(self):
        self.sectionPos = {}
        section_names = []
        for m in re.finditer(r'<section ([^>]+)>', self.tool_conf_data):
            attrib = {}
            for a in re.findall(r'([^ =]+)="([^"]+)"', m.group(1)):
                attrib[a[0]] = a[1]
            self.sectionPos[attrib['name']] = m.end(0)
            section_names.append(attrib['name'])
        return section_names
    
    def addTool(self, section_name, tool_file):
        self.getSections()
        tool_tag = '\n\t<tool file="%s" />' % (tool_file,)
        pos = self.sectionPos[section_name]
        self.tool_conf_data = self.tool_conf_data[:pos] + tool_tag + self.tool_conf_data[pos:]
        return self.tool_conf_data

    def write(self):
        shutil.copy(self.tool_conf_fn, self.tool_conf_fn + '.bak')
        with open(self.tool_conf_fn, 'w') as f:
            f.write(self.tool_conf_data)
        
    def createToolXml(self, tool_fn, tool_id, tool_name, tool_module, tool_cls, tool_descr):
        tool_xml = self.tool_xml_template % (tool_id, tool_name, tool_module, tool_cls, tool_descr)
        return tool_xml


def getProtoToolList(except_class_names=[]):
    except_class_names.append('ToolTemplate')
    tools = {}
    tool_classes = []
    pys = []
    for d in os.walk(PROTO_TOOL_DIR):
        if d[0].find('.svn') == -1:
            pys += [os.path.join(d[0], f) for f in d[2] if f.endswith('.py') and not any(f.startswith(x) for x in ['.', '#'])]
    
    #print 'Num py', len(pys)        
    for fn in pys:
        with open(fn) as f:
            for line in f:
                m = re.match(r'class +(\w+) *\((\w+)\)', line)
                if m:
                    class_name = m.group(1)
                    if class_name not in except_class_names:
                        module_name = os.path.splitext(os.path.relpath(fn, SOURCE_CODE_BASE_DIR))[0].replace(os.path.sep, '.')
                        #print module_name
                        try:
                            module = import_module(module_name)
                            prototype_cls = getattr(module, class_name)
                            if issubclass(prototype_cls, GeneralGuiTool) and not issubclass(prototype_cls, MultiGeneralGuiTool) and hasattr(prototype_cls, 'getToolName'):
                                prototype = prototype_cls('hb_no_tool_id_yet')
                                toolModule = module_name.split('.')[2:]
                                if class_name != toolModule[-1]:
                                    toolSelectionName = '.'.join(toolModule) + ' [' + class_name + ']'
                                else:
                                    toolSelectionName = '.'.join(toolModule)

                                tools[toolSelectionName] = (fn, m.group(2), prototype_cls, module_name)
                                tool_classes.append(prototype_cls)
                        except Exception as e:
                            traceback.print_exc()
                        #break
    #print 'Num protopy', len(tools)
    return tools, tool_classes



class ExploreToolsTool(MultiGeneralGuiTool):

    @staticmethod
    def getToolName():
        return "ProTo tool explorer"

    @staticmethod
    def getToolSelectionName():
        return "-----  Select tool -----"

    @staticmethod
    def isBatchTool():
        return False

    @staticmethod
    def useSubToolPrefix():
        return True
    
    @classmethod
    def getSubToolClasses(cls):
        tool_shelve = shelve.open(TOOL_SHELVE, 'r')
        installed_classes = [tool_shelve.get(t)[1] for t in tool_shelve.keys() if os.path.exists(os.path.join(SOURCE_CODE_BASE_DIR, tool_shelve.get(t)[0].replace('.', os.path.sep)) + '.py') ]                
        tool_shelve.close()
        tool_list = getProtoToolList(installed_classes)[1]
        return sorted(tool_list, key=lambda c: c.__module__)



    #@classmethod
    #def getOptionsBoxInstalled(cls):
    #    cls.existing_tools = cls.get_existing_tool_xml_list()
    #    tool_shelve = shelve.open(TOOL_SHELVE, 'r')
    #    cls.installed_classes = [tool_shelve.get(t)[1] for t in tool_shelve.keys()]
    #    tool_shelve.close()
    #    return sorted(cls.installed_classes)
    #
    #
    #@classmethod
    #def getOptionsBoxProtoTools(cls, choices):
    #    proto_tools = sorted(cls.get_proto_tool_list().keys())
    #    return None
    #
    #@classmethod
    #def getOptionsBoxOrphanTools(cls, choices):
    #    orphans = [t for t in cls.get_proto_tool_list().keys() if t not in cls.installed_classes]
    #    return sorted(orphans)
    
    #@classmethod
    #def get_existing_tool_xml_list(cls):
    #    tools = {}
    #    xmls = [x for x in os.listdir(HB_TOOL_DIR) if x.endswith('.xml')]
    #    for fn in xmls:
    #        tree = ET.parse(HB_TOOL_DIR + fn)
    #        root = tree.getroot()
    #        if root.tag == 'tool' and root.attrib.get('tool_type') == 'hyperbrowser_generic':
    #            tool_id = root.attrib['id']
    #            tools[tool_id] = root.attrib
    #    return tools



class InstallToolsTool(GeneralGuiTool):
    prototype = None

    @classmethod
    def _getToolList(cls):
        tool_shelve = shelve.open(TOOL_SHELVE, 'r')
        tool_IDs = set(tool_shelve.keys())
        installed_classes = [tool_shelve.get(t)[1] for t in tool_IDs]
        tool_shelve.close()
        return getProtoToolList(installed_classes)[0]

    @classmethod
    def _getProtoType(cls, tool):
        try:
            prototype = cls._getToolList()[tool][2]()
        except:
            prototype = None
        return prototype


    @staticmethod
    def getToolName():
        return "ProTo tool installer"

    @staticmethod
    def getInputBoxNames():
        return [('Select tool', 'tool'), ('Tool ID', 'toolID'), ('Tool name', 'name'), ('Tool description', 'description'), ('Tool XML file', 'toolXMLPath'), ('Select section', 'section')]

    @staticmethod
    def getResetBoxes():
        return [1]

    @staticmethod
    def isBatchTool():
        return False

#    @staticmethod
#    def isHistoryTool():
#        return False

    @staticmethod
    def useSubToolPrefix():
        return True

    @classmethod
    def getOptionsBoxTool(cls):
        tool_list = cls._getToolList()
        return ['-- Select tool --'] + sorted(tool_list)

    @classmethod
    def getOptionsBoxToolID(cls, prevchoices):
        if prevchoices.tool is None or prevchoices.tool.startswith('--'):
            return ''
        tool_list = cls._getToolList()
        return 'ProTo_' + tool_list[prevchoices.tool][2].__name__

    @classmethod
    def getOptionsBoxName(cls, prevchoices):
        prototype = cls._getProtoType(prevchoices.tool)
        if prototype is not None:
            return prototype.getToolName()

    @classmethod
    def getOptionsBoxDescription(cls, prevchoices):
        return ''

    @classmethod
    def getOptionsBoxToolXMLPath(cls, prevchoices):
        prototype = cls._getProtoType(prevchoices.tool)
        if prototype is not None:
            package = prototype.__module__.split('.')
            package_dir = '/'.join(package[2:-1]) + '/' if len(package) > 3 else ''
            return 'proto/' + package_dir + prototype.__class__.__name__ + '.xml'

    @classmethod
    def getOptionsBoxSection(cls, prevchoices):
        toolConf = GalaxyToolConfig()
        return toolConf.getSections()
        
    #@classmethod
    #def getOptionsBoxInfo(cls, prevchoices):
    #    txt = ''
    #    if prevchoices.tool and prevchoices.section:
    #        txt = 'Install %s into %s' % (prevchoices.tool, prevchoices.section)
    #    tool_cls = prevchoices.tool
    #    prototype = cls.prototype
    #    #tool_file = TOOL_XML_REL_PATH + tool_cls + '.xml'
    #    tool_file = prevchoices.toolXMLPath
    #    xml = cls.toolConf.addTool(prevchoices.section, tool_file)
    #    tool_xml = cls.toolConf.createToolXml(tool_file, prevchoices.toolID, prevchoices.name, prototype.__module__, prototype.__class__.__name__, prevchoices.description)
    #    return 'rawstr', '<pre>' + escape(xml) + '</pre>' + '<pre>' + escape(tool_xml) + '</pre>'

    @classmethod
    def validateAndReturnErrors(cls, choices):
        if not choices.toolID or len(choices.toolID) < 6 or not re.match(r'^[a-zA-Z0-9_]+$', choices.toolID):
            return 'Tool ID must be at least 6 characters and not contain special chars'
        return None
        
    @classmethod
    def execute(cls, choices, galaxyFn=None, username=''):
        txt = ''
        if choices.tool and choices.section:
            txt = 'Install %s into %s' % (choices.tool, choices.section)
        tool_cls = choices.tool
        prototype = cls._getProtoType(choices.tool)
        tool_file = choices.toolXMLPath
        toolConf = GalaxyToolConfig()
        xml = toolConf.addTool(choices.section, tool_file)
        tool_xml = toolConf.createToolXml(tool_file, choices.toolID, choices.name, prototype.__module__, prototype.__class__.__name__, choices.description)
        
        abs_tool_xml_path = GALAXY_TOOL_XML_PATH + choices.toolXMLPath
        try:
            os.makedirs(os.path.dirname(abs_tool_xml_path))
        except:
            pass
        with open(abs_tool_xml_path, 'w') as tf:
            tf.write(tool_xml)
        
        toolConf.write()
        
        print '<pre>' + escape(xml) + '</pre>' + '<pre>' + escape(tool_xml) + '</pre>'
        

        
class GenerateToolsTool(GeneralGuiTool):

    @staticmethod
    def getToolName():
        return "ProTo tool generator"

    @staticmethod
    def isBatchTool():
        return False

    @staticmethod
    def getInputBoxNames():
        return [('Package name', 'packageName'),
                ('Module name', 'moduleName'),
                ('Tool name', 'toolName'),
                ('Use template with inline documentation', 'template')]

    #@staticmethod
    #def getResetBoxes():
    #    return ['moduleName']
    
    @staticmethod
    def getOptionsBoxPackageName():
        return ''
    
    @staticmethod
    def getOptionsBoxModuleName(prevchoices):
        return 'ChangeMeTool'
    
    @staticmethod
    def getOptionsBoxToolName(prevchoices):
        return 'Title of tool'

    @staticmethod
    def getOptionsBoxTemplate(prevchoices):
        return ['Yes', 'No']
    
    @staticmethod
    def execute(choices, galaxyFn=None, username=''):
        packagePath = choices.packageName.split('.')
        packageDir = PROTO_TOOL_DIR + '/'.join(packagePath)
        if not os.path.exists(packageDir):
            os.makedirs(packageDir)

        for i in range(len(packagePath)):
            init_py = PROTO_TOOL_DIR + '/'.join(packagePath[0:i+1]) + '/__init__.py'
            if not os.path.exists(init_py):
                print 'creating ', init_py
                open(init_py, 'a').close()
            
        pyname = packageDir + '/' + choices.moduleName + '.py'
        
        if choices.template == 'Yes':
            templatefn = PROTO_TOOL_DIR + 'ToolTemplate.py'
        else:
            templatefn = PROTO_TOOL_DIR + 'ToolTemplateMinimal.py'
        
        with open(templatefn) as t:
            template = t.read()
        
        #template = re.sub(r'ToolTemplate', choices.moduleName, template)
        template = template.replace('ToolTemplate', choices.moduleName)
        template = template.replace('Tool not yet in use', choices.toolName)

        with open(pyname, 'w') as p:
            p.write(template)
        explore_id = quote(choices.moduleName + ': ' + choices.toolName)
        print 'Tool generated: <a href="%s/proto/?tool_id=proto_ExploreToolsTool&sub_class_id=%s">%s: %s</a>' % (URL_PREFIX, explore_id, choices.moduleName, choices.toolName)
        print 'Tool source path: ', pyname
        
