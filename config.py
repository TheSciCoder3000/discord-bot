from configparser import ConfigParser
import os

env_config = ConfigParser()
env_config.read('env.ini')
mode = env_config['Env']['mode']

repl = False if mode == 'dev' else True

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