import sys
import tempfile
import urllib
from json import JSONDecoder
import os
import hashlib
import io

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
			content = open(cache).read()
			return JSONDecoder().decode(content)			
		
		res = urllib.urlopen(url)
		if (res.getcode() == 200):
			content = res.read()
 
			file = open(cache, 'w')
			file.write(content)
			file.close();
			
			return JSONDecoder().decode(content)
			
		return False

	def query(self, acao, pars=''):
		url = "http://web.secom.to.gov.br/central3/rpc/%s?formato=json&site=%s&%s" % (acao, self.site, pars)
		dic = self.loadUrl(url)
		if dic['status'] == 0:
			return False
		return dic
		
	def byUri(self, uri):
		url = "http://web.secom.to.gov.br/central3/rpc/?formato=json&site=%s&uri=%s" % (self.site, uri)
		dic = self.loadUrl(url)
		if dic['status'] == 0:
			return False
		return dic

if __name__ == "__main__":		
	a1 = QueryClient().getInstance()
	print (a1.query('noticia.listar'))
