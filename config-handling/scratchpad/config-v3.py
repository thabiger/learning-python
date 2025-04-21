import os
import yaml
import threading
import time
from dataclasses import dataclass
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

@dataclass
class ConsumerModel:
    id: str
    queue: Queue

class Config:
    def __init__(self, config_file='config.yaml', config_dir='conf.d', process_interval=5):

        self.__config_file = config_file
        self.__config_dir = config_dir
        self.__process_interval = process_interval  # Interval to process events (in seconds)
        self.__config_change_event_queue = Queue()  # Queue to store file change events
        self.__consumers = []                       # List of registred consumers
        self.__stop_event = threading.Event()       # Event to stop threads in a graceful manner

        self.load_config()
        self.__start_watcher()
        self.__start_event_processor()

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
                self.config_instance._Config__config_change_event_queue.put(event.src_path)

    def __start_event_processor(self):
        """Start a thread to process events from the queue at regular intervals."""
        def process_events():
            while not self.__stop_event.is_set():
                time.sleep(self.__process_interval)  # Wait for the defined interval
                if not self.__config_change_event_queue.empty():
                    self.__process_config_change_event_queue()

        processor_thread = threading.Thread(target=process_events, daemon=True)
        processor_thread.start()

    def __process_config_change_event_queue(self):
        """Process all events in the queue as a batch."""
        processed_items = set()

        while not self.__config_change_event_queue.empty():
            event_path = self.__config_change_event_queue.get()
            processed_items.add(event_path)

        if processed_items:
            print(f"Reloading config due to changes in: {', '.join(processed_items)}")
            self.load_config()
            # Notify all consumers about the configuration change
            for consumer in self.__consumers:
                consumer.queue.put("Config updated")

    def register_consumer(self, id=None):
        """Register a new consumer and return its queue."""
        
        if id and id in [ c.id for c in self.__consumers ]:
            raise Exception(f"Consumer with id '{id}' already registered.")
        
        if id is None:
            id = os.urandom(8).hex()

        consumer = ConsumerModel(id, Queue())
        self.__consumers.append(consumer)
        return consumer

    def stop(self):
        self.__observer.stop()
        self.__observer.join()
        self.__stop_event.set()

config = Config()

def watcher_action(func):
    """Decorator to register a watcher action."""
    def wrapper(consumer, *args, **kwargs):
        while True:
            event = consumer.queue.get()  # Wait for a notification
            if event == "STOP":
                break
            print(f"Consumer {consumer.id} received event: {event}")
            # Perform an action related with the particular consumer instance
            func(event, *args, **kwargs)
    return wrapper

class Watcher:

    def __init__(self, action, id=None):

        instance = config.register_consumer(id)

        self.__thread = threading.Thread(target=action, args=(instance,))
        self.__thread.start()

    def stop(self):
        """Stop the consumer thread gracefully."""
        self.__instance.queue.put("STOP")   # Send a "STOP" signal to the queue
        self.__thread.join()                # Wait for the thread to finish
        print(f"Consumer {self.__instance.id} stopped.")