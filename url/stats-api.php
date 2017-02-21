<?php
		require("lib/config.php");
		require("lib/common.php");
$a = $_GET['a'];
if ($a == "totalcreated") {
	$countresult = mysql_query("SELECT * FROM urls",DBH) or die(mysql_error());
	echo number_format(mysql_num_rows($countresult));
} elseif ($a == "totalhits") {
	$query_h= "SELECT SUM(hits) AS total from urls";
	$result_h=  mysql_query($query_h, DBH);
	echo number_format(mysql_result($result_h,0,"total"));
} elseif ($a == "recent") {


		$table = substr(1, 0, 1);
		echo "            <table class='table table-striped'>
              <thead>
                <tr>
                  <th>Short URL</th>
                  <th>Original URL</th>
                  <th>Created</th>
                  <th>Hits</th>
                </tr>
              </thead>
              <tbody>";
	
	if ($table) {
	    $result = mysql_query("SELECT * FROM urls ORDER BY created DESC, time DESC LIMIT 10",DBH) or die(mysql_error()); 
	    $i = 0;
		while ($row = mysql_fetch_assoc($result)) {
			$id = $row['id'];
	        $short_urlo = $short_url = $row['short_url'];
	        $urlo      = $url       = $row['url'];
	        //$created   = date("Y-m-d", $row['created']);
			$time      = $row['time'];
			$hits 	   = $row['hits'];
			$create = $row['created'];
			$date = gmdate("Y-m-d");

			if ($create == $date) {
				$created = getRelativeTime($time);
			} else {
				$created = getRelativeTime($create);
			}


	        if (strlen($url) > 60) {
	            $url = substr($url, 0, 60)."...";
	        }
	        if (strlen($short_url) > 16) {
	            $short_url = substr($short_url, 0, 20)."...";
	        }
			$classn = "";
			if( $i % 2 ) $classn = "alt";
	        echo "<tr><td width=\"100px\"><a target='_blank' href='http://".$config_location."/".((!$_SESSION['config']['rewrite']) ? "?" : "")."{$short_url}'>".((!$_SESSION['config']['rewrite']) ? "?" : "")."{$short_url}</a></td><td><small>$url</small></td><td>" . $created . " ago</td><td width=\"40px\" id=\"num\">$hits</td></tr>";
			$i++;
	    }
	    echo "</tbody></table>";
	}




} elseif ($a == "recentview") {


		$table = substr(1, 0, 1);
			echo "<table class='table table-striped'>
              <thead>
                <tr>
                  <th>Short URL</th>
                  <th>Visited From</th>
                  <th>Hits</th>
                </tr>
              </thead>
              <tbody>";		
	
	if ($table) {
	    $result = mysql_query("SELECT * FROM stats ORDER BY cdate DESC, time DESC LIMIT 10",DBH) or die(mysql_error());
	    $i = 0;
		while ($row  = mysql_fetch_assoc($result)) {
	        $urlo_id = $row['urlid'];
	        $country = $row['country'];
	        $countryl = strtolower($country);
	        if ($row['locfrom'] == "") {
	        	 $locfrom = "Direct Visit";
	        } else {
	        	 $locfrom = $row['locfrom'];
	        }
	       
			$result2 = mysql_query("SELECT * FROM urls WHERE id='$urlo_id'",DBH) or die(mysql_error()); 
			$row2 = mysql_fetch_assoc($result2);

			$short_url = $row2['short_url'];
			$hits 	   = $row2['hits'];

			$short_url_S = "http://".$config_location."/".((!$_SESSION['config']['rewrite']) ? "?" : "")."{$short_url}";

			if (strlen($short_url_S) > 20) {
	            $short_url_S = substr($short_url_S, 0, 20)."...";
	        }
	        if (strlen($locfrom) > 60) {
	            $locfrom = substr($locfrom, 0, 60)."...";
	        }
			$classn = "";
			if( $i % 2 ) $classn = "alt";
	        echo "<tr><td width=\"150px\"><a target='_blank' href='http://".$config_location."/".((!$_SESSION['config']['rewrite']) ? "?" : "")."{$short_url}'>$short_url_S</a></td><td><a target='_blank' href='".$locfrom."''>$locfrom<a/></td><td><small>$hits</small></td></tr>";
			$i++;
	    }
	    echo "</tbody></table>";
	}




}



 ?>
