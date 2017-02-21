<?php
	require("lib/config.php");
	require("lib/common.php");
require("lib/header.php");
?>

      <a href="http://<?php echo $config_location; ?>" title="MeeLa - Url Shortner" ><div id="logoland"><?php echo settingsdb(name); ?></div></a>

      <div class="menuland">

      	<a class="btn btn-primary" href="/index.php" >Create New URL</a>

      </div>


 <div class="clear"></div>



<div class="meela_box meelab">

	<div class="stats_tab">
	            
	 <?
			$date = gmdate("Y-m-d");
			$query = "SELECT COUNT(short_url) FROM urls";
			$result = mysql_query($query,DBH) or die(mysql_error());
			$row = mysql_fetch_row($result);
			$rowRes = number_format($row[0]);
			$query2 = "SELECT COUNT(short_url) FROM urls WHERE created = '$date'";

			$query3 = "SELECT COUNT(custom) FROM urls WHERE custom = 'Y'";
			$result3 = mysql_query($query3,DBH) or die(mysql_error());
			$rowcount = mysql_fetch_row($result3);
			$rowcustom = number_format($rowcount[0]);


			$result2 = mysql_query($query2,DBH) or die(mysql_error());
			$todayget = mysql_fetch_row($result2);
			$today = number_format($todayget[0]);
			$hits = mysql_query("SELECT SUM(hits) FROM urls",DBH) or die(mysql_error());
			$hitsGet = mysql_fetch_row($hits);
			$hitsRes = number_format($hitsGet[0]);
			
			if($_POST["showme"] == 0) {
					$showme = 25;
				} else {
					$showme = $_POST["showme"];
			}
		?>           
	            
	            
	<h2 style="text-align:center;">Top <?=$showme?> Most Recent Links</h2>
	<table class="table table-hover">
		<thead>
			<th>Short Url</th>
			<th>Long Url</th>
			<th>Clicks</th>
		</thead>
		<tbody>
			
	        
	        
	<?php
		$table = substr(1, 0, 1);
		
		if ($table) {
		    $result = mysql_query("SELECT id,short_url, url, created, time, hits FROM urls ORDER BY created DESC, time DESC LIMIT ".$showme."",DBH) or die(mysql_error()); 
		    $i = 0;
			while ($row = mysql_fetch_assoc($result)) {
				$id = $row['id'];
		        $short_urlo = $short_url = $row['short_url'];
		        $urlo      = $url       = $row['url'];
		        $created   = date("Y-m-d", $row['created']);
				$time      = $row['time'];
				$hits 	   = $row['hits'];
				$date = $created . ' ' . $time;
		        if (strlen($url) > 40) {
		            $url = substr($url, 0, 40)."...";
		        }
		        if (strlen($short_url) > 16) {
		            $short_url = substr($short_url, 0, 14)."...";
		        }
				$classn = "";
				if( $i % 2 ) $classn = "alt";
		        echo "<tr><td width='150px'><a target='blank' href='http://".settingsdb(location)."/".((!$_SESSION['config']['rewrite']) ? "?" : "")."{$short_url}'>".((!$_SESSION['config']['rewrite']) ? "?" : "")."{$short_url}</a></td><td><small>$url</small></td><!--<td>" . getRelativeTime($date) . "</td> --><td width=\"40px\" id=\"num\">$hits</td></tr>";
				$i++;
		    }
		}

		?>
	        
	        
		</tbody>
	</table>





	</div>  



	<div class="info_stats">

	<h2 style="text-align:center;">Stats</h2>
	<div class="minfo"><a>Show:</a><span><form method="post" action="stats.php">
	<select name="showme" onchange="this.form.submit()">
		<option value="0">--<?=$showme?>--</option>
		<option value="25">25</option>
		<option value="50">50</option>
		<option value="75">75</option>
		<option value="100">100</option>
	</select>
	</form></span></div>

	<div class="minfo" ><a>Links Created Today:</a><span><?=$today?></span></div>

	<div class="minfo"><a>Total Links:</a><span><?=$rowRes?></span></div>
	<div class="minfo"><a>Total Custom URL's:</a><span><?=$rowcustom?></span></div>
	</div>


	<div style="clear:both;"></div>


        

</div>        
        
</body> 
</html> 