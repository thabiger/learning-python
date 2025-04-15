import os
import yaml
from collections import defaultdict
from deepmerge import always_merger
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import threading

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

        self.__config_file = config_file
        self.__config_dir = config_dir
        
        self.load_config()
        self.__start_watcher()

    def load_config(self):
        config = defaultdict(dict)

        for f in self.__collect_config_files():
            print(f"Loading configuration from {f}")
            try:
                with open(f, 'r') as file:
                    if config_data := yaml.safe_load(file):
                        config = always_merger.merge(config, config_data)
            except FileNotFoundError:
                raise Exception(f"Configuration file '{self.__config_file}' not found.")
            except yaml.YAMLError as e:
                raise Exception(f"Error parsing YAML file: {e}")
        
        self.__config = DotNotationDict(config)

    def __collect_config_files(self):
        config_files = []

        if (os.path.isfile(self.__config_file)):
            config_files.append(self.__config_file)
        
        if (os.path.isdir(self.__config_dir)):
            config_files += [os.path.join(self.__config_dir, f) for f in os.listdir(self.__config_dir)]

        return config_files

    def __getattr__(self, name):
        return getattr(self.__config, name)

    def __start_watcher(self):
        """Start a file watcher to monitor changes in configuration files."""
        event_handler = self._ConfigFileChangeHandler(self)
        observer = Observer()

        # Watch the main configuration file and the configuration directory for changes
        observer.schedule(event_handler, path=self.__config_file, recursive=False)
        observer.schedule(event_handler, path=self.__config_dir, recursive=True)

        # Run the observer in a separate thread
        observer_thread = threading.Thread(target=observer.start, daemon=True)
        observer_thread.start()

    class _ConfigFileChangeHandler(FileSystemEventHandler):
        """Handles file system events for configuration files."""
        def __init__(self, config_instance):
            self.config_instance = config_instance

        def on_modified(self, event):
            if event.src_path and event.event_type in ['modified', 'created', 'deleted']:
                print(f"Configuration file '{event.src_path}' changed. Reloading...")
                self.config_instance.load_config()

config = Config()