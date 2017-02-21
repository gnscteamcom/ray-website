<?php
	ob_start();
	require("lib/config.php");
	require("lib/common.php");
	$error = false;
	$url   = trim(urldecode(@$_REQUEST['url']));
	$custom   = trim(urldecode(@$_REQUEST['custom']));

	
	if( empty($url) || $url == "http://" || $url == "https://"  || strlen($url) < 8  ){
		$error = true;
	}else{
		if( !isValidUrl($url) ){ $error = true; }
	}
	if (!empty($url) && !$error) {
		$short_url = shortenit($url,$custom);
		$short_url    = "http://".$config_location."/".((!$_SESSION['config']['rewrite']) ? "?" : "").$short_url;
	    $short_length = strlen($short_url);
		echo $short_url;
	}else {
	    echo 'Error';
	}
?>