# coding: utf-8
from os import path, environ

PROJECT_ROOT = path.abspath( path.dirname(__file__) )
TEMPLATES_DIR = path.join(PROJECT_ROOT, "templates")

URL_D = "http://www.cce.puc-rio.br/sitecce/website/website.dll/candidatos?cOferec=6103"
URL_S = "http://www.cce.puc-rio.br/sitecce/website/website.dll/candidatos?cOferec=5853"

try:
	from local_settings import *
except ImportError:
	TEST = False
	CONSUMER_SECRET = environ.get('CONSUMER_SECRET')
	CONSUMER_KEY = environ.get('CONSUMER_KEY')
	STUDENT_NAME = environ.get('STUDENT_NAME')