#!/usr/bin/python2.6
# -*- coding: utf-8 -*-#
import sys, tempfile, urllib, os, hashlib, time
from json import JSONDecoder

class QueryClient:
	"""Classe para carregar dados do webservice do Governo do Tocantins"""
	
	__instance = {}
	
	def __init__(self):
		self.site = 'teste'
		self.cache_dir = tempfile.gettempdir() + "/central3/"
	
	def getInstance(self, instance = "default"):
		
		if QueryClient.__instance.has_key(instance) == False:
			QueryClient.__instance[instance] = QueryClient()

		return QueryClient.__instance[instance]
		
	def init(self, site = "default"):
		self.site = site
	
	def loadUrl(self, url):
		cache = self.cache_dir + hashlib.md5(url).hexdigest()
		
		if os.path.isfile(cache):
			# Se o tempo de vida do cache estiver aceitavel retorna os dados
			age = time.time() - os.stat(cache).st_mtime
			if age <= 300:
				content = open(cache).read()
				return JSONDecoder().decode(content)
			
			# Senão define o horario de criação para agora, para impedir multiplas tentativas de criação do cache
			# e cria o cache novamente
			else:
				os.utime(cache, None)
		
		# Tanta carregar um novo recordset
		try:
			res = urllib.urlopen(url)
			# se o webservice retornou o codigo de sucesso, cria um novo cache e retorna a informação!
			if (res.getcode() == 200):
				content = res.read()
 
				file = open(cache, 'w')
				file.write(content)
				file.close();
			
				return JSONDecoder().decode(content)
		finally:
			pass
		
		# Caso a requisição falhou, muda a data de criacao do cache para agora, e este será o atual
		# até dar o timeout e uma nova tentativa no webservice
		if os.path.isfile(cache):	
			os.utime(cache, None)
			content = open(cache).read()
			return JSONDecoder().decode(content)
		
		# Se o cache nao existir e a requisição falhar, uma exception é lançada	
		raise Exception('Erro ao obter arquivo')

	def query(self, acao, pars=''):
		url = "http://web.secom.to.gov.br/central3/rpc/%s?formato=json&site=%s&%s" % (acao, self.site, pars)
		dic = self.loadUrl(url)
		if dic['status'] == 0:
			raise Exception(dic['error_desc'])
		return dic
		
	def byUri(self, uri):
		url = "http://web.secom.to.gov.br/central3/rpc/?formato=json&site=%s&uri=%s" % (self.site, uri)
		dic = self.loadUrl(url)
		if dic['status'] == 0:
			raise Exception(dic['error_desc'])
		return dic

if __name__ == "__main__":		
	a1 = QueryClient().getInstance()
	print (a1.query('noticia.listar'))
