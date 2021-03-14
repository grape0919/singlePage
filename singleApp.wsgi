import os
import sys
sys.path.insert(0, "/var/www/html")
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from app import app as application
