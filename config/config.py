# config.py
import os

# Flask Default Setting
DEBUG = os.environ.get('DEBUG', 'False') == 'True'