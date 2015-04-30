#!/usr/bin/env python
from resource_management import *

# server configurations
config = Script.get_config()

install_dir = config['configurations']['opentsdb-config']['opentsdb.install_dir']
start_cmd = config['configurations']['opentsdb-config']['opentsdb.start_cmd']
log = config['configurations']['opentsdb-config']['opentsdb.log']
create_schema = config['configurations']['opentsdb-config']['opentsdb.create_schema']
download_url = config['configurations']['opentsdb-config']['opentsdb.download_url']

