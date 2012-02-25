#coding: utf-8
import datetime
import urllib2
import re
from flask import Flask, render_template

app = Flask(__name__)
app.config.from_object("settings")

class Congratulations(object):
	
	def __init__(self, **kwargs):
		try:
			self.name = (kwargs['name'].strip())
		except KeyError:
			raise Exception( "O nome do consinscrito, deve ser informado." )
			
		self.status = ""
		self.date_request = None
		self.name_display = kwargs.get('name_display')
		self.url = kwargs.get('url')
		
	def search(self):
		"""
			Método que recupera situação do consinscrito::
		"""
		rs = urllib2.urlopen(self.url).read()
		students = ( "".join(re.findall('(?s)<div id="dados">(.*?)</div>', rs)) )
		students = ( "".join(re.findall('(?s)<ul>(.*?)</ul>', (re.split('</h4>', students)[1])  )) ).strip()
		
		self.date_request = datetime.datetime.now()
		self.status = "No accepted"
		if not students:
			self.status = "No processed"
		elif self.name in students:
			self.status = "Accepted"
	
	@property
	def display_menssage(self):
		"""
			Método que formata as menssagens que serão exibidas::
		"""
		dict_msg = {
				"Accepted":"congratulations your curriculum was accepted",
				"No accepted":"sorry your curriculum don't accepted",
				"No processed":"your curriculum don't processed"
		}
		
		try:
			return ("Mr <span class='name'>%(name_display)s</span>, %(default_msg)s.<br /><a href='%(link)s'>PucRio</a><br />Last update:<em>%(date)s</em>\
					" % {'name_display':self.name_display, 'default_msg':dict_msg[self.status], 
				   		 'link':self.url, 'date':datetime.datetime.now().strftime("%d %B, %Y")} ).strip()
		except KeyError:
			raise Exception( "Status do consinscrito ainda não foi recuperado." )

@app.route("/")
def home():
	"""
		Recupera página principal do sistema::
	"""
	return render_template("index.html")
