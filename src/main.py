from ConfigHandler import ConfigHandler

if __name__ == '__main__':
    config_handler = ConfigHandler('./config.json')
    config_handler.get_json()