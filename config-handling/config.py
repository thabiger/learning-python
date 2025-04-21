import os
import yaml
import threading
import time
from collections import defaultdict
from deepmerge import always_merger
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from queue import Queue

class DotNotationDict:
    """A helper class to enable dot notation access for dictionaries."""
    def __init__(self, data):
        for key, value in data.items():
            if isinstance(value, dict):
                value = DotNotationDict(value)
            self.__dict__[key] = value

    def __getattr__(self, name):
        raise AttributeError(f"'DotNotationDict' object has no attribute '{name}'")

def watcher_action(func):
    """Decorator to register a watcher action."""
    def wrapper(*args, watcher, aggregate_by=None, interval=0.1, **kwargs):
        
        events = {}
        
        while True:
            time.sleep(interval)

            while not watcher.queue.empty():
                event = watcher.queue.get()        
                
                if aggregate_by:
                    events[getattr(event, aggregate_by)] = event
                else:
                    events[os.urandom(8).hex()] = event
            
            while events:
                _, event = events.popitem()

                if event == "STOP":
                    watcher.stop()

                print(f"Consumer {watcher.id} received event: {event}")
                # Perform an action related with the particular consumer instance
                func(*args, event, **kwargs)

    return wrapper

class Watcher:

    def __init__(self, id, kind, action, **kwargs):

        self.__id = id
        self.__queue = Queue()

        if kind not in {"internal", "external"}:
            raise ValueError(f"Invalid type: {kind}. Allowed values are 'internal' and 'external'.")
        else:
            self.__kind = kind

        self.__thread = threading.Thread(target=action, kwargs={'watcher': self, **kwargs})
        self.__thread.start()

    @property
    def id(self):
        return self.__id

    @property
    def queue(self):
        return self.__queue

    @property
    def kind(self):
        return self.__kind

    def stop(self):
        """Stop the watcher thread gracefully."""
        self.__thread.join()
        print(f"Watcher {self.id} stopped.")

class Config:

    def __init__(self, config_file='config.yaml', config_dir='conf.d', process_interval=5):

        self.__config_file = config_file
        self.__config_dir = config_dir
        self.__watchers = [] # List of registred watchers

        self.load_config()
        self.__start_source_config_watcher()
        self.create_watcher(self.load_action, id="config-source", kind="internal", aggregate_by="event_type", interval=5)

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

    @watcher_action
    def load_action(self, event):
        print(f"Configuration changed: {event}")
        self.load_config()
        # Notify all watchers about the configuration change
        for watcher in self.get_watchers("kind", "external"):
            watcher.queue.put(event)

    def __collect_config_files(self):
        config_files = []

        if (os.path.isfile(self.__config_file)):
            config_files.append(self.__config_file)
        
        if (os.path.isdir(self.__config_dir)):
            config_files += [os.path.join(self.__config_dir, f) for f in os.listdir(self.__config_dir)]

        return config_files

    def __getattr__(self, name):
        return getattr(self.__config, name)

    def __start_source_config_watcher(self):
        """Start a file watcher to monitor changes in configuration files."""
        event_handler = self._ConfigFileChangeHandler(self)
        self.__observer = Observer()

        # Watch the main configuration file and the configuration directory for changes
        self.__observer.schedule(event_handler, path=self.__config_file, recursive=False)
        self.__observer.schedule(event_handler, path=self.__config_dir, recursive=True)

        # Run the observer in a separate thread
        observer_thread = threading.Thread(target=self.__observer.start, daemon=True)
        observer_thread.start()

    class _ConfigFileChangeHandler(FileSystemEventHandler):
        """Handles file system events for configuration files."""
        def __init__(self, config_instance):
            self.config_instance = config_instance

        def on_modified(self, event):
            if event.src_path and event.event_type in ['modified', 'created', 'deleted']:
                self.config_instance.get_watcher("config-source").queue.put(event)

    def create_watcher(self, action, kind="external", id=None, **kwargs):
        """Create a new watcher and return its id."""
        
        if id and id in [ c.id for c in self.__watchers ]:
            raise Exception(f"Consumer with id '{id}' already registered.")
        
        if id is None:
            id = os.urandom(8).hex()

        watcher = Watcher(id, kind, action, **kwargs)
        self.__watchers.append(watcher)
        return watcher

    def get_watcher(self, id):
        """Get a watcher by its id."""
        for watcher in self.__watchers:
            if watcher.id == id:
                return watcher
        raise Exception(f"Consumer with id '{id}' not found.")
    
    def get_watchers(self, attr, value):
        return [ watcher for watcher in self.__watchers if getattr(watcher, attr) == value ]

    def stop(self):
        """Stop all watchers."""
        for watcher in self.__watchers:
            watcher.stop()
        self.__observer.stop()
        self.__observer.join()
        print("All watchers stopped.")
    
config = Config()