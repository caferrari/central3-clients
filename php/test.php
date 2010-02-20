<?php

include 'QueryClient.php';

$qc = QueryClient::getInstance();
$qc->init('teste');

$rs = $qc->query('noticia.listar');

echo '<pre>';
print_r($rs);
echo '</pre>';
