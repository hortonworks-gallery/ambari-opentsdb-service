#!/usr/bin/env python
from resource_management import *

config = Script.get_config()

opentsdb_piddir = config['configurations']['opentsdb']['opentsdb_piddir']
opentsdb_pidfile = format("{opentsdb_piddir}/opentsdb.pid")