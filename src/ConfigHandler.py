import json

class ConfigHandler(object):
    
    def __init__(self, config_file_path):
        self.config =''
        with open(config_file_path) as f:
            self.config = json.load(f)


    def get_json(self):
      print(self.config)