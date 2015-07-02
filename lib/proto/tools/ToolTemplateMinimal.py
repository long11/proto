from proto.tools.GeneralGuiTool import GeneralGuiTool

# This is a template prototyping GUI that comes together with a corresponding
# web page.

class ToolTemplate(GeneralGuiTool):
    @staticmethod
    def getToolName():
        return "Tool not yet in use"

    @staticmethod
    def getInputBoxNames():
        return ['box1','box2'] #Alternatively: [ ('box1','key1'), ('box2','key2') ]

    #@staticmethod
    #def getInputBoxOrder():
    #    return None
    
    @staticmethod    
    def getOptionsBox1(): # Alternatively: getOptionsBoxKey1()
        return ''
        
    @staticmethod    
    def getOptionsBox2(prevChoices):
        return ['']

    #@staticmethod    
    #def getOptionsBox3(prevChoices):
    #    return ['']

    #@staticmethod    
    #def getOptionsBox4(prevChoices):
    #    return ['']

    #@staticmethod
    #def getDemoSelections():
    #    return ['testChoice1','..']
        
    @staticmethod    
    def execute(choices, galaxyFn=None, username=''):
        print 'Executing...'

    @staticmethod
    def validateAndReturnErrors(choices):
        return None
        
    #@staticmethod
    #def isPublic():
    #    return False
    #
    #@staticmethod
    #def isRedirectTool():
    #    return False
    #
    #@staticmethod
    #def getRedirectURL(choices):
    #    return ''
    #
    #@staticmethod
    #def getToolDescription():
    #    return ''

    #@staticmethod
    #def isDebugMode():
    #    return False
    #
    #@staticmethod    
    #def getOutputFormat(choices):
    #    return 'html'