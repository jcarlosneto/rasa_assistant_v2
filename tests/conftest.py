import os
import sys

RAIZ = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.join(RAIZ, "rasa"))
sys.path.insert(0, os.path.join(RAIZ, "web_interface"))
