#!/usr/bin/python

import time
from config import config, watcher_action

@watcher_action
def exec_on_config_change(event):
    print("Configuration changed(%s), executing appropriate actions in the app..." % event)

config.create_watcher(action=exec_on_config_change, id="app_consumer_1")

while True:
    print(config.example_key)
    time.sleep (1)

