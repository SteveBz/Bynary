import configparser


class GaiaLoginConf:
    def __init__(self, config_file):
        config = configparser.ConfigParser()
        config.read(config_file)
        self.user = config['login']['user']
        self.password = config['login']['password']
