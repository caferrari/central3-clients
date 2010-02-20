<?php

/**
* Classe para carregar dados do webservice do Governo do Tocantins
*
* @version 1
* @author Carlos André Ferrari <carlos@ferrari.eti.br>
* @author Luan Almeida <luanlmd@gmail.com>
*/
class QueryClient
{
	/**
	* Armazena o site que os dados deverão ser pegos
	* @var String
	* @access private
	*/
	private $site = 'teste';

	/**
	* Diretório padrão para cache local de dados
	* @var String
	* @access private
	*/
	private $cache_dir = null;

	/**
	* Instância singleton
	* @var QueryClient
	* @access private
	*/
	private static $instances = array();
	
	/**
	* carrega a instancia do singleton ou cria se não existir
	* @param String	$name instance name, usado somente se deseja adquirir dados de mais de um site
	* @access public
	* @return QueryClient
	*/
	public static function getInstance($name='default')
	{
		if (!isset(self::$instances[$name])) self::$instances[$name] = new self();
		return self::$instances[$name];
	}

	/**
	* Contrutor privado, força singleton
	* @access private
	* @return void
	*/
	private function __construct()
	{
		clearstatcache();
		$this->cache_dir = sys_get_temp_dir() . '/central3/';
		@mkdir ($this->cache_dir);
	}

	/**
	* Usado para mudar o site, o padrão é o de testes
	* @param String	$site sigla do site
	* @access public
	* @return void
	*/
	public function init($site)
	{
		$this->site = $site;
	}

	/**
	* Carrega a url via curl
	* @param String	$url url da query do webservice
	* @access public
	* @return stdObject
	*/
	private function loadUrl($url)
	{
		$cache = $this->cache_dir . md5($url);
		
		// se o arquvio de cache existir
		if (file_exists($cache))
		{
			// Se o tempo de vida do cache estiver aceitavel retorna os dados
			$age = date('U') - filemtime($cache);
			if ($age < 300) return unserialize(file_get_contents($cache));

			// Senão define o horario de criação para agora, para impedir multiplas tentativas de criação do cache
			// e cria o cache novamente
			else touch($cache);
		}
		
		// Tanta carregar um novo recordset
		$ch = curl_init($url);
		curl_setopt ($ch, CURLOPT_RETURNTRANSFER, 1) ;
		$res = curl_exec ($ch);

		// se o webservice retornou o codigo de sucesso, cria um novo cache e retorna a informação!
		if (curl_getinfo($ch, CURLINFO_HTTP_CODE) === 200){
			file_put_contents($cache, $res);
			return unserialize($res);
		}

		// Caso a requisição falhou, muda a data de criacao do cache para agora, e este será o atual
		// até dar o timeout e uma nova tentativa no webservice
		if (file_exists($cache))
		{
			touch($cache);
			return unserialize(file_get_contents($cache));
		}
		
		// Se o cache nao existir e a requisição falhar, uma exception é lançada
		throw new Exception(curl_error($ch));
	}

	/**
	* Executa uma query qualquer no webservice
	* @param String	$acao action do webservice
	* @param String	$pars parametros da requisição
	* @param String	$site caso a busca seja temporariamente em outro site
	* @access public
	* @return stdObject
	*/
	public function query($acao, $pars='', $site=null)
	{
		if ($site===null) $site = $this->site;
		$url = "http://web.secom.to.gov.br/central3/rpc/{$acao}?formato=serial&site={$site}&{$pars}";
		$tmp = $this->loadUrl($url);

		if ($tmp->status===0) throw new Exception($tmp->error_desc);
		return $tmp;
	}

	/**
	* Carrega os dados com base na URL
	* @param String	$uri uri atual do site
	* @access public
	* @return stdObject
	*/
	public function byUri($uri)
	{
		$url = "http://web.secom.to.gov.br/central3/rpc/?formato=serial&site={$this->site}&uri={$uri}";
		$tmp = $this->loadUrl($url);

		if ($tmp->status===0) throw new Exception($tmp->error_desc);
		return $tmp;
	}
}
