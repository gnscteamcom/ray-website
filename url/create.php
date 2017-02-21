<?php
	require("lib/config.php");
	require("lib/common.php");

	$error = false;
	$url   = trim(urldecode(@$_REQUEST['url']));
	if (strstr($url, "http://") == $url) {
	} elseif (strstr($url, "https://") == $url) {
	} else {
	$url = "http://".trim(urldecode(@$_REQUEST['url']));
	}
	$custom   = trim(urldecode(@$_REQUEST['custom']));
	if( empty($url) || $url == "http://" || $url == "https://"  || strlen($url) < 8 || stristr($url,$config_location) ){
		$error = true;
	}else{
		if( !isValidUrl($url) ){ $error = true; }
	}
	require("lib/header.php");



	if (!empty($url) && !$error) {
if (!settingsdb(safe) == '') {
	
$m_url = 'https://sb-ssl.google.com/safebrowsing/api/lookup?client=api&apikey='.settingsdb(safe).'&appver=1.0&pver=3.0&url='.$url;

$curl_handle=curl_init();
curl_setopt($curl_handle,CURLOPT_URL,$m_url);
curl_setopt($curl_handle,CURLOPT_CONNECTTIMEOUT,2);
curl_setopt($curl_handle,CURLOPT_RETURNTRANSFER,1);
$buffer = curl_exec($curl_handle);
curl_close($curl_handle);

}

$buffer = "";

if (empty($buffer))
{
    $length = strlen($url);
	$short_url = shortenit($url,$custom);
	$surl = $short_url;
	$short_url    = "http://".settingsdb(location)."/".((!$_SESSION['config']['rewrite']) ? "?" : "").$short_url;
	$short_length = strlen($short_url);

?>
	<a href="http://<?php echo $config_location; ?>" title="MeeLa - Url Shortner" ><div id="logo"><?php echo settingsdb(name); ?></div></a> 
	<h2>Your new URL has been created!</h2> 

	<div id='bluebox' class='tbox'>

		<div id="content-short-url">

	<div class="alert alert-info check">
		<center>The URL has been coppied to your clipboard.</center>
	</div>
			<div class="input-append">
			  <input id="appendedInputButton" size="16" type="text" onclick="select_all(this)" class="sturl_field span5" value="<?=$short_url?>" ><a class="btn btn-primary btn-large"><span id="flashbtn">Copy Me!</span></a>
			</div>

		</div> 


	<style type="text/css">.check { display:none; }</style>

		<div class="<?php if(!settingsdb(socialmedia) == 0 && !settingsdb(qr) == 0 ) { echo "meelab"; } elseif(!settingsdb(qr) == 0) { echo "meelabqr"; } elseif(!settingsdb(socialmedia) == 0 ) { echo "meelab"; } else { echo "none"; } ?>">
		<div class="<?php if(!settingsdb(qr) == 0 && settingsdb(socialmedia) == 0) { echo "qro"; } elseif(!settingsdb(qr) == 0 && !settingsdb(socialmedia) == 0) { echo "qr"; } else { echo "none";} ?>"><img src="https://chart.googleapis.com/chart?chs=200x200&cht=qr&chl=<?php echo $short_url; ?>" /></div>


			<div class="socialmedia <?php if(settingsdb(socialmedia) == 0 ) { echo "none"; } ?>">
				<?php if(!settingsdb(socialmedia) == 0 && !settingsdb(qr) == 0 ) { echo "<h2>Share Me</h2>"; } ?>
				<a href="http://www.facebook.com/sharer.php?u=<?=$short_url?>" target="_blank">
				<div class="facebook <?php if(!settingsdb(socialmedia) == 0 && settingsdb(qr) == 0 ) { echo "share_btns"; } else { echo "share_btn"; } ?>">
					Facebook
				</div></a>
				<a href="https://twitter.com/share?url=<?=$short_url?>" target="_blank">
				<div class="twitter <?php if(!settingsdb(socialmedia) == 0 && settingsdb(qr) == 0 ) { echo "share_btns"; } else { echo "share_btn"; } ?>">
					Twitter
				</div></a>

			</div>
			<div class="clearfix"></div>
		</div>	

	</div>

<?
}
else
{
    echo "<h2>This URL has been flagged by our system as ";
    print $buffer;
    echo ". <br/>We are unable to shorten this URL.</h2>";
}


	}else {
	    echo "<h2>A valid URL was not entered, please try again.</h2>";
	}
?>
	</div>



<?php
	require("lib/footer.php");
?>
