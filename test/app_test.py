# coding: utf-8
import datetime
import unittest
from mock import Mock, patch
from nose.tools import assert_equals, assert_true, assert_raises, assert_false
from app import Congratulations, CongratulationsExEnd, app

class MockUrllib(Mock):
	
	def __init__(self, file_test):
		self.file_test = file_test
			
	def read(self):
		handle = open(self.file_test)
		html = "".join( handle )
		return html

class MockCongratulations(Congratulations):
	pass
	
class CongratulationsTest(unittest.TestCase):

	def test_class_Congratulations_existe(self):
		assert_true(isinstance(Congratulations, object))
	
	def test_objeto_recebe_nome_do_consinscrito(self):
		"""
			Caso instâcia seja criada, o nome do consinscrito deve ser passado para pesquisa::
		"""
		c = Congratulations(name='leandro')
		assert_equals((c.name.upper()), 'LEANDRO')
	
	def test_caso_nome_nao_seja_passado_deve_haver_um_exception(self):
		"""
			Caso o nome do consinscrito não seja passso, sistema deve levantar um exception::
		"""
		assert_raises(Exception, Congratulations)
	
	@patch('app.urllib2.urlopen')
	def test_jonas_brother_no_accepted(self, sr):
		"""
			Consinscrito Jonas Brother não teve seu perfil aprovado::
		"""
		sr.return_value = MockUrllib('teste_dentista.html')
		c = Congratulations(name='Jonas Brother', url=app.config['URL_D'])
		c.search()
		assert_equals(c.status.lower(), "no accepted")
	
	@patch('app.urllib2.urlopen')
	def test_leandro_accepted(self, sr):
		"""
			Consinscrito Leandro teve seu perfil aprovado::
		"""
		sr.return_value = MockUrllib('teste_dentista.html')
		c = Congratulations(name='Leandro', url=app.config['URL_D'])
		c.search()
		assert_equals(c.status.lower(), "accepted")
	
	@patch('app.urllib2.urlopen')
	def test_jarbas_no_processed(self, sr):
		"""
			Consinscrito Jarbas ainda não teve seu perfil processado::
		"""
		sr.return_value = MockUrllib('teste.html')
		c = Congratulations(name='Jarbas', url=app.config['URL_S'])
		c.search()
		assert_equals(c.status.lower(), "no processed")
		
	@patch('app.urllib2.urlopen')
	def test_menssage_tela_jarbas(self, sr):
		"""
			Caso situação do Jarbas ainda não tem cido processada, sistema gera mensagem::
		"""
		sr.return_value = MockUrllib('teste.html')
		c = Congratulations(name='Jarbas', url=app.config['URL_S'], name_display='@riquellopes')
		c.search()
		msg = ("<h2>Mr <span class='name'>@riquellopes</span>, your curriculum wasn't <span class='wait'>processed</span>.</h2><a href='%(link)s' class=\"label label-info\">PucRio</a><br /><span class=\"label label-info\">Last update: <i>%(date)s</i></span>\
			   " % {'link':app.config['URL_S'], 'date':datetime.datetime.now().strftime("%Y %B, %d %H:%M")} ).strip()
		assert_equals(c.display_menssage.lower(), msg.lower())
	
	@patch('app.urllib2.urlopen')
	def test_menssagem_tela_jonas(self, sr):
		"""
			Caso situação do Jonas já tenha cido processada, sistema gera mensagem::
		"""
		sr.return_value = MockUrllib('teste_dentista.html')
		c = Congratulations(name='Jonas Brother', url=app.config['URL_D'], name_display='@brother')
		c.search()
		msg = ("<h2>Mr <span class='name'>@brother</span>, sorry your curriculum wasn't <span class='failure'>accepted</span>.</h2><a href='%(link)s' class=\"label label-info\">PucRio</a><br /><span class=\"label label-info\">Last update: <i>%(date)s</i></span>\
			   " % {'link':app.config['URL_D'], 'date':datetime.datetime.now().strftime("%Y %B, %d %H:%M")} ).strip()
		assert_equals(c.display_menssage.lower(), msg.lower())
	
	@patch('app.urllib2.urlopen')
	def test_messagem_tela_leandro(self, sr):
		"""
			Caso situação do Leandro já tenha cido processada, sistema gera mensagem::
		"""
		sr.return_value = MockUrllib('teste_dentista.html')
		c = Congratulations(name='Leandro', url=app.config['URL_D'], name_display='@leandro')
		c.search()
		msg = ("<h2>Mr <span class='name'>@leandro</span>, congratulations your curriculum was <span class='sucess'>accepted</span>.</h2><a href='%(link)s' class=\"label label-info\">PucRio</a><br /><span class=\"label label-info\">Last update: <i>%(date)s</i></span>\
			   " % {'link':app.config['URL_D'], 'date':datetime.datetime.now().strftime("%Y %B, %d %H:%M")} ).strip()
		assert_equals(c.display_menssage.lower(), msg.lower())
	
	def test_caso_search_nao_seja_chamado(self):
		"""
			Caso método search não seja chamado antes do display_menssage, deve haver um exception::
		"""
		c = Congratulations(name='Leandro', url=app.config['URL_D'], name_display='@leandro')
		try:
			c.display_menssage
		except Exception, e:
			assert_true(True)
	
	@patch('app.urllib2.urlopen')
	def test_periodo(self, sr):
		"""
			Caso período de liberação de resultado já tenha encerrado, search deve levantar exception::
		"""	
		sr.return_value = MockUrllib('teste_dentista.html')
		c = Congratulations(name='Leandro', url=app.config['URL_D'], name_display='@leandro', date_end='2012-02-26')
		assert_raises(CongratulationsExEnd, c.search)
		
class ViewTest(unittest.TestCase):
	
	def setUp(self):
		self.app = app.test_client()
	
	@patch('app.Congratulations')
	def test_home(self, cg):
		"""
			Título na página home deve ser Congratulatios app::
		"""
		rs = self.app.get("/")
		assert_true('<title>Congratulations APP</title>' in str(rs.data) )
	
	def test_process(self):
		"""
			Toda vez que o index for acessado, sistema deve atualizar as informações do arquivo index.html::
		"""
		self.app.get('/')
		handle = open(app.config['TEMPLATES_DIR']+"/index.html")
		html = "".join( handle )
		handle.close()
		assert_true('Last update: <i>%s</i>' % (datetime.datetime.now().strftime("%Y %B, %d %H:%M")) in str(html))
	
	@patch('app.Congratulations')
	@patch('app.render_template')
	def test_process_end(self, cg, rt):
		"""
			Caso periodo de resultados tenha encerrado, arquivo index não deve ser mais atualizado::
		"""
		cg.side_effect = CongratulationsExEnd("")
		rt.return_value = MockUrllib('teste_msg.html')
		rs = self.app.get('/')
		assert_false('Last update: <i>%s</i>' % (datetime.datetime.now().strftime("%Y %B, %d %H:%M")) in str(rs.data) )