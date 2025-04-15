import os
import yaml
from collections import defaultdict
from deepmerge import always_merger

class DotNotationDict:
    """A helper class to enable dot notation access for dictionaries."""
    def __init__(self, data):
        for key, value in data.items():
            if isinstance(value, dict):
                value = DotNotationDict(value)
            self.__dict__[key] = value

    def __getattr__(self, name):
        raise AttributeError(f"'DotNotationDict' object has no attribute '{name}'")

class Config:
    def __init__(self, config_file='config.yaml', config_dir='conf.d'):
        self.__config_files = []

        if (os.path.isfile(config_file)):
            self.__config_files.append(config_file)
        
        if (os.path.isdir(config_dir)):
            self.__config_files += [os.path.join(config_dir, f) for f in os.listdir(config_dir)]

        self.__config = self.__load_config()

    def __load_config(self):
        config = defaultdict(dict)

        for f in self.__config_files:
            print(f"Loading configuration from {f}")
            try:
                with open(f, 'r') as file:
                    if config_data := yaml.safe_load(file):
                        config = always_merger.merge(config, config_data)
            except FileNotFoundError:
                raise Exception(f"Configuration file '{self.__config_file}' not found.")
            except yaml.YAMLError as e:
                raise Exception(f"Error parsing YAML file: {e}")
        
        return DotNotationDict(config)

    def __getattr__(self, name):
        return getattr(self.__config, name)

config = Config()