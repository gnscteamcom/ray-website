<?php

	if (file_exists("lib/config.php")) {
		require("lib/config.php");
		require("lib/common.php");
	} else {
		header('Location: install.php'); exit();
	}


	if ($_SESSION['config']['rewrite'] == false && strlen($_SERVER['QUERY_STRING']) > 1) {

	echo $_SERVER['QUERY_STRING'];

		$result = mysql_query("SELECT id,url FROM urls WHERE short_url = '{$_SERVER['QUERY_STRING']}'",DBH) or die(mysql_error());	

		if (mysql_num_rows($result) > 0) {

			header("Location: forward.php?".$_SERVER['QUERY_STRING']);

			exit;

		}

	}

	require("lib/header.php");


?>

      <a href="http://<?php echo settingsdb(location); ?>" title="<?php echo settingsdb(name); ?> - Url Shortner" ><div id="logo"><?php echo settingsdb(name); ?></div></a>
 <h1>Use this URL shortener service to shorten your long URLs!</h1>

<? include("lib/urlcreatebox.php"); ?>	


<div class="clear"></div>



<?php
if(settingsdb(ads) == 1) {
	echo "<div class=\"meelab ad\">".settingsdb(ad_html)."</div>";
}


if(settingsdb(top3) == 1) {
  echo '<div class="span3 meelab home_stats">
      <span>Total Urls:</span>
      <p id="urltotal">^_^</p>
    </div>
    <div class="span3 meelab home_stats">
      <span>Total Url Visits:</span>
      <p id="urlvisits">^_^</p>
    </div>
    <div class="span3 meelab home_stats">
      <span>Random Fun Link:</span>
      <a target="blank" href="http://mee.la/lol">http://mee.la/lol</a>
    </div>

 <div class="clearfix"></div>';
}


if(settingsdb(description) == 1) {
  echo '<div class="meela_box meelab">
      <h2>What is MeeLa?</h2>
      <p>Welcome to Mee.La! Are you sick of sharing long URL\'s to your friends? Would you like to rickroll a friend without him having any idea about the link you\'re referring him to? Then you\'ve come to the right place! Enter any URL in the above field, and we will give you a short and unique mee.la URL that you can share. Gone are the days where you need to email people long complicated links, you can just MeeLa it and tell them the simple link which is easy to remember.</p>
    </div>
';
}


if(settingsdb(recentview) == 1) {
  echo '    <div class="meela_box meelab">
      <h2>Recently Viewed URL\'s</h2>

                <div id="urlrecentview"></div>

    </div>';
}


if(settingsdb(recentcreate) == 1) {
  echo '  <div class="meela_box meelab">
      <h2>Recently Created URL\'s</h2>

                <div id="urlrecent"></div>

    </div>';
}

 ?>


    











</div> <!-- /container -->

<?php require("lib/footer.php"); ?>