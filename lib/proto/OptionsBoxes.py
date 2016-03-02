

class BaseOptionsBox(object):

    @staticmethod    
    def isTypeOf(opts):
        return False

    def getValue(self):
        return self.defaultValue if self.value is None else self.value
    
    def getOptions(self):
        return self.options

    def getType(self):
        return self.type

    def process(self, proto, paramId, paramValue):
        self.value = paramValue
        return self.getValue()

    @classmethod    
    def construct(cls, opts):
        return cls(opts)



class TextOptionsBox(BaseOptionsBox):
    
    def __init__(self, text, rows=1, readonly=False):
        self.defaultValue = text
        self.rows = rows
        self.readonly = readonly
        self.options = (text, rows, readonly)
        self.type = 'text_readonly' if readonly else 'text'

    @staticmethod    
    def isTypeOf(opts):
        if isinstance(opts, basestring):
            return True
        if isinstance(opts, tuple):
            if len(opts) in [2, 3] and (isinstance(opts[0], basestring)):
                return True
        return False
    
    @classmethod    
    def construct(cls, opts):
        return cls(*opts) if isinstance(opts, tuple) else cls(opts)



class PasswordOptionsBox(BaseOptionsBox):
    type = '__password__'
    
    def __init__(self, options='__password__'):
        self.defaultValue = ''
        self.options = options
        
    @classmethod
    def isTypeOf(cls, opts):
        return isinstance(opts, basestring) and opts == cls.type



class HiddenOptionsBox(BaseOptionsBox):
    type = '__hidden__'
    
    def __init__(self, value):
        self.defaultValue = value
        self.options = (self.type, value)
        
    @classmethod
    def isTypeOf(cls, opts):
        return isinstance(opts, tuple) and opts[0] == cls.type

    @classmethod    
    def construct(cls, opts):
        return cls(opts[1])



class CheckOptionsBox(BaseOptionsBox):
    type = 'checkbox'
    
    def __init__(self, value):
        self.defaultValue = value
        self.options = bool(value)
        
    @staticmethod
    def isTypeOf(opts):
        return isinstance(opts, bool)

    def process(self, proto, paramId, paramValue):
        self.value = True if paramValue == "True" else self.options if proto.use_default else False
        return self.getValue()


    
OptionsBoxClassList = [CheckOptionsBox, HiddenOptionsBox, PasswordOptionsBox, TextOptionsBox]
