from ConfigParser import SafeConfigParser
import os

GALAXY_BASE_DIR = os.path.abspath(os.path.dirname(__file__) + '/../../../.')

def getUniverseConfigParser():
    config = SafeConfigParser({'here': GALAXY_BASE_DIR})
    configFn = GALAXY_BASE_DIR + '/universe_wsgi.ini'
    if os.path.exists(configFn):
        config.read(configFn)
    return config

def getFromConfig(config, key, default, section='app:main'):
    try:
        return config.get(section, key)
    except:
        return default

def getUrlPrefix(config):
    prefix = getFromConfig(config, 'prefix', '', 'filter:proxy-prefix')
    filterWith = getFromConfig(config, 'filter-with', '', 'app:main')
    return prefix if filterWith == 'proxy-prefix' else ''

config = getUniverseConfigParser()

if not globals().get('URL_PREFIX'):
    URL_PREFIX = getUrlPrefix(config)

GALAXY_REL_TOOL_CONFIG_FILE = getFromConfig(config, 'tool_config_file', 'config/tool_conf.xml')

def userHasFullAccess(galaxyUserName):
    return True
