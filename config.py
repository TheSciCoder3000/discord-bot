from configparser import ConfigParser

config = ConfigParser()
config.read('config.ini')
config_data = config['GENERAL']

token = config_data['token']
test_guild = config_data['test_guild']
tropa_guild = config_data['tropa_guild']
research_guild = config_data['research_guild']