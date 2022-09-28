from configparser import ConfigParser
import os

repl = False

def getConfig(configKey):
    if repl:
        return os.environ[configKey]
    else:
        config = ConfigParser()
        config.read('config.ini')
        config_data = config['GENERAL']
        return config_data[configKey]



token = getConfig('token')
test_guild = getConfig('test_guild')
tropa_guild = getConfig('tropa_guild')
research_guild = getConfig('research_guild')