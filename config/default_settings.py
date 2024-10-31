# -*- coding: utf-8 -*-
import os
from os.path import dirname, join

# configure file based session
SESSION_TYPE = "filesystem"
SESSION_FILE_DIR = join(dirname(__file__), "cache")

# configure flask app for local development
CLIENT_ID = os.environ.get('CLIENT_ID', '144A806DFDBB49EAB3323FB6B2D0678E')
CLIENT_SECRET = os.environ.get('CLIENT_SECRET', '9Nf2GfzRNhH_tc8Zv64_BmSHO5tG4m_a6B6la671U7Bisx85')
STATE = 'ABC'
ENV = "development"