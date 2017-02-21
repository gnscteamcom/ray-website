<?php
	ob_start();
	error_reporting(0);
	require("lib/config.php");
	require("lib/common.php");
	require("lib/geoiploc.php");
	if( isset($_SERVER['QUERY_STRING']) ){
		$i = $_SERVER['QUERY_STRING'];
	}else{
		$i = $_SERVER['REQUEST_URI'];
		$i = str_replace("/","",$i);
	}
	$suffix = $i{0};
	$result = mysql_query("SELECT id,url FROM urls WHERE short_url = '$i'",DBH) or die(mysql_error());	
	if (mysql_num_rows($result) > 0) {
		$row = mysql_fetch_assoc($result);
		$id = $row['id'];
		$url = $row['url'];
		mysql_query("UPDATE urls SET hits=hits+1 WHERE id = '{$id}'",DBH);
		

	$time_s = date('G:i:s');
	$date_s = date('d-m-Y');
	$ip_s = $_SERVER["REMOTE_ADDR"];
	$reff_s = $_SERVER["HTTP_REFERER"];
	$lang_s = $_SERVER['HTTP_ACCEPT_LANGUAGE'];
	$selected_key = getCountryFromIP($ip_s, "code");

	$result_stats = mysql_query("INSERT INTO stats (urlid, ip, locfrom, country, language, time, cdate) VALUES ('$id', '$ip_s', '$reff_s', '$selected_key', '$lang_s', '$time_s', '$date_s')",DBH) or die(mysql_error()); 

	

if(settingsdb(bar) == 1) {	

		$meela_urllow = stripslashes(str_replace(",", "%2C", $url));
		$meela_urllow = strtolower($meela_urllow);
		if ((strpos($meela_urllow, "youtube")))
		{
			header('HTTP/1.1 301 Moved Permanently');
			header("Location: ".stripslashes(str_replace(",", "%2C", $url)));
		}

		if ((strpos($meela_urllow, "facebook")))
		{
			header('HTTP/1.1 301 Moved Permanently');
			header("Location: ".stripslashes(str_replace(",", "%2C", $url)));
		}

		if ((strpos($meela_urllow, "google")))
		{
			header('HTTP/1.1 301 Moved Permanently');
			header("Location: ".stripslashes(str_replace(",", "%2C", $url)));
		}


		/*  Meta  */
		$tags = get_meta_tags(stripslashes(str_replace(",", "%2C", $url)));
		/*  Title  */
		function getTitle($Url){
		    $str = file_get_contents($Url);
		    if(strlen($str)>0){
		        preg_match("/\<title\>(.*)\<\/title\>/",$str,$title);
		        return $title[1];
		    }
		}
		if (getTitle(stripslashes(str_replace(",", "%2C", $url))) == "") {
			$titletag = "<title>". $i ." | URL Made on <?php echo settingsdb(name); ?></title>";
		} else {
			$titletag = "<title>". getTitle(stripslashes(str_replace(",", "%2C", $url))) ."| ".settingsdb(name)."</title>";
		}
} ?>
<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.01 Transitional//EN" "http://www.w3.org/TR/html4/loose.dtd">
<html xmlns:fb="http://ogp.me/ns/fb#">
<head>
<meta http-equiv="Content-Type" content="text/html; charset=UTF-8">
<meta name="description" content="<?php echo $tags['description']; ?>">
<?php

if(settingsdb(splash) == 1 && settingsdb(bar) == 0) { echo '<META HTTP-EQUIV="refresh" CONTENT="5; URL='.stripslashes(str_replace(",", "%2C", $url)).'">'; }

echo $titletag; ?>

<link rel="stylesheet" href="http://<?php echo settingsdb(location); ?>/assets/css/bar.css" /> 

<!--[if gte IE 9]>
  <style type="text/css">
    .gradient {
       filter: none;
    }
  </style>
<![endif]-->

</head>
<body>

<?php if(settingsdb(bar) == 1) { ?>
<div id="fb-root"></div>
<script>(function(d, s, id) {
var js, fjs = d.getElementsByTagName(s)[0];
if (d.getElementById(id)) return;
js = d.createElement(s); js.id = id;
js.src = "//connect.facebook.net/en_GB/all.js#xfbml=1&appId=292875815726";
fjs.parentNode.insertBefore(js, fjs);
}(document, 'script', 'facebook-jssdk'));</script>

<div id="bar">

<div id="meela_shareimg"><img src="http://<?php echo settingsdb(location); ?>/assets/img/like-us.png" name="Like us!" /></div>
<div id="meela_share"><fb:like href="http://<?php echo settingsdb(location); ?>" send="true" layout="button_count" width="450" show_faces="false" font="arial"></fb:like></div>


<a id="close" href="<?php echo stripslashes(str_replace(",", "%2C", $url)); ?>">Not working?</a>
<a id="textadf" href="http://mee.la/buynow">Buy Meela Script</a>
</div>

<?php }  if(settingsdb(splash) == 1 && settingsdb(bar) == 0) { } else { ?>
		  <iframe id='meela_frame' <?php if(settingsdb(bar) == 1 && settingsdb(splash) == 1) { ?>style='display:none;' src="" <?php }  elseif(settingsdb(bar) == 1 && $settingsdb(splash) == 0) { echo 'src=" '.stripslashes(str_replace(",", "%2C", $url)).'"'; } ?> width="100%" height="100%" frameborder="0"></iframe> 

<?php }  if(settingsdb(splash) == 1) { ?>

<style>
#PreLoad {
width: 960px;
text-align: center;
overflow: auto;
margin: 50px auto;
color: #3D9AC3;
font-family: HelveticaNeue-Light, "Helvetica Neue Light", "Helvetica Neue", sans-serif;
font-size: 25px;
}
.clear {
clear: both;
height: 80px;
width: 100%;
}

#loadgif {
width: 160px;
height: 160px;
padding: 10px;
margin: 0 auto;
}
</style>
<div class="clear"></div>
<div id="loadgif"><img width="160" height="160" src="/assets/img/loading.gif"></div>
<div style="font-size: 25px;" id="PreLoad">You are about to visit: <br/><br/> <?php echo stripslashes(str_replace(",", "%2C", $url)); ?></div>

<?php } if (!settingsdb(analytics) == "") { ?>

<script type="text/javascript">
	var _gaq = _gaq || [];
	_gaq.push(['_setAccount', '<?php echo settingsdb(analytics); ?>']);
	_gaq.push(['_trackPageview']);

	(function() {
	var ga = document.createElement('script'); ga.type = 'text/javascript'; ga.async = true;
	ga.src = ('https:' == document.location.protocol ? 'https://ssl' : 'http://www') + '.google-analytics.com/ga.js';
	var s = document.getElementsByTagName('script')[0]; s.parentNode.insertBefore(ga, s);
	})();
</script>
<script>_gaq.push(['_setCustomVar', 1, 'URL Visitors', '<?php echo $i; ?>', 1 ]); </script>	

<?php }  if(settingsdb(splash) == 1) { ?>

<script src="https://ajax.googleapis.com/ajax/libs/jquery/1.7.2/jquery.min.js"></script>

<script>
$(document).ready(function(){ 
	$('#meela_frame').delay(5000).queue(function( nxt ) {
		$("#meela_frame").fadeIn();
		$("#meela_frame").attr("src", "<?php echo stripslashes(str_replace(",", "%2C", $url)); ?>");
		$("#PreLoad").fadeOut();      
			nxt();
	});
});	
</script>
<?php } ?>
</body>
</html>



		<?php


	if(settingsdb(splash) == 0 && settingsdb(bar) == 0) {
		header('HTTP/1.1 301 Moved Permanently');
		header("Location: ".stripslashes(str_replace(",", "%2C", $url)));
	}


		exit;
	}

	header('HTTP/1.1 301 Moved Permanently');
	header("Location: http://".settingsdb(location));
	exit;
?>