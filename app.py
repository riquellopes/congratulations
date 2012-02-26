#coding: utf-8
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
	
	def __init__(self, **kwargs):
		try:
			self.name = (kwargs['name'].strip())
		except KeyError:
			raise Exception( "O nome do consinscrito, deve ser informado." )
			
		self.status = ""
		self.date_request = None
		self.name_display = kwargs.get('name_display')
		self.url = kwargs.get('url')
		self.date_end = kwargs.get('date_end') if kwargs.get('date_end') is None else to_date(kwargs.get('date_end'), '%Y-%m-%d')
		
	def search(self):
		"""
			Método que recupera situação do consinscrito::
		"""			
		if not self.date_end is None and ( self.date_end - datetime.datetime.now() ).days <= 0:
			raise CongratulationsExEnd( "Período de resultados encerrado." )
			
		rs = urllib2.urlopen(self.url).read()
		students = ( "".join(re.findall('(?s)<div id="dados">(.*?)</div>', rs)) )
		students = ( "".join(re.findall('(?s)<ul>(.*?)</ul>', (re.split('</h4>', students)[1])  )) ).strip()
		
		self.date_request = datetime.datetime.now()
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
			return ("<h2>Mr <span class='name'>%(name_display)s</span>, %(default_msg)s.</h2><a href='%(link)s' class=\"label label-info\">PucRio</a><br /><span class=\"label label-info\">Last update: <i>%(date)s</i></span>\
					" % {'name_display':self.name_display, 'default_msg':dict_msg[self.status], 
				   		 'link':self.url, 'date':datetime.datetime.now().strftime("%Y %B, %d %H:%M")} ).strip()
		except KeyError:
			raise Exception( "Status do consinscrito ainda não foi recuperado." )

@app.before_request
def process():
	"""
		Processa informações sobre consinscrito::
	"""
	try:
		cong = Congratulations(name=app.config['STUDENT_NAME'], url=app.config['URL_S'], name_display='@riquellopes', date_end=app.config['DATE_END'])
		cong.search()
		html = open( '%s/index.html' % app.config['TEMPLATES_DIR'], 'w' )
		html.write( render_template("index_cache.html", cong=cong) )
		html.close()
	except CongratulationsExEnd:
		pass
		
@app.route("/")
def home():
	"""
		Recupera página principal do sistema::
	"""
	return render_template("index.html")