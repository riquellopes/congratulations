#coding: utf-8
import os
import json
import datetime
import urllib2
import re
from flask import Flask, render_template

"""
	Renomeia função strptime::
"""
to_date = datetime.datetime.strptime

app = Flask(__name__)
app.config.from_object("settings")

class CongratulationsExEnd(Exception):
	pass
	
class Congratulations(object):
	"""Conteiner de agradecimentos::"""
	name_display = ""
	url = ""
	status = ""
	date_end = ""
	date_request = None
	root = os.path.abspath( os.path.dirname(__file__) )
	
	def __new__(cls, *args, **kwargs):
		handle = open('%s/static/js/congratulations.json' % cls.root, 'r')
		values = json.load(handle)
		handle.close()
		for key in values:
			setattr(cls, key, values[key])
		return super(Congratulations, cls).__new__(cls)
		
	def __init__(self, **kwargs):
		try:
			self.name = (str(kwargs['name']).strip())
		except KeyError:
			raise Exception( "O nome do consinscrito, deve ser informado." )
			
		self.name_display = kwargs.get('name_display')
		self.url = kwargs.get('url')
		self.date_end = kwargs.get('date_end')
		
	def search(self):
		"""
			Método que recupera situação do consinscrito::
		"""		
		if not self.date_end is None and ( to_date(self.date_end, '%Y-%m-%d') - datetime.datetime.now() ).days < -1:
			raise CongratulationsExEnd( "Período de resultados encerrado." )
			
		rs = urllib2.urlopen(self.url).read()
		students = ( "".join(re.findall('(?s)<div id="dados">(.*?)</div>', rs)) )
		students = ( "".join(re.findall('(?s)<ul>(.*?)</ul>', (re.split('</h4>', students)[1])  )) ).strip()
		
		self.date_request = datetime.datetime.now().strftime("%Y %B, %d %H:%M")
		self.status = "No accepted"
		if not students:
			self.status = "No processed"
		elif self.name.upper() in students.upper():
			self.status = "Accepted"
	
	@property
	def display_menssage(self):
		"""
			Método que formata as menssagens que serão exibidas::
		"""
		dict_msg = {
				"Accepted":"congratulations your curriculum was <span class='sucess'>accepted</span>",
				"No accepted":"sorry your curriculum wasn't <span class='failure'>accepted</span>",
				"No processed":"your curriculum wasn't <span class='wait'>processed</span>"
		}
		
		try:
			return dict_msg[self.status]
		except KeyError:
			raise Exception( "Status do consinscrito ainda não foi recuperado." )
	
	def save(self):
		"""
			Método que salva as informações em congratulatios.json::
		"""
		try:
			self.search()
			handle = open('%s/static/js/congratulations.json' % self.root, 'w')
			values = json.dumps(self.__dict__)
			handle.write(values)
			handle.close()
			return True
		except:
			pass
			
@app.route("/")
def home():
	"""
		Recupera página principal do sistema::
	"""
	cong = Congratulations(name=app.config['STUDENT_NAME'], 
						   url=app.config['URL_S'], 
						   name_display=app.config['NAME_DISPLAY'], 
						   date_end=app.config['DATE_END'])
	#cong.save()
	return render_template("index.html", cong=cong)