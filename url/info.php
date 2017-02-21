<?php 
	require("lib/config.php");
	require("lib/common.php");
	?>
    
    
<?php

$i = $_GET['short'];

$result = mysql_query("SELECT * FROM urls WHERE short_url = '$i'",DBH) or die(mysql_error());		
		$row = mysql_fetch_array($result);
		$url = $row[2];
		$created = $row[3];
		$hits = $row[5];
		$short_url = $i;
		$id_s = $row[0];

$result_s_c = mysql_query("SELECT COUNT(DISTINCT ip) FROM stats WHERE urlid = '$id_s'",DBH) or die(mysql_error());	
$row_s_c = mysql_fetch_array($result_s_c);

$result_s_c_u = mysql_query("SELECT DISTINCT locfrom FROM stats WHERE urlid = '$id_s'",DBH) or die(mysql_error());	
$row_s_c_u = mysql_fetch_array($result_s_c_u);

$result_s = mysql_query("SELECT * FROM stats WHERE urlid = '$id_s'",DBH) or die(mysql_error());		
		$row_s = mysql_fetch_array($result_s);
		$urlfrom_s = $row_s[3];
		$date_s = $row_s[7];
		$time_s = $row_s[8];
		$count_s = mysql_num_rows($result_s);

		$date_s = date('d-m-Y');
$result_today = mysql_query("SELECT * FROM stats WHERE urlid = '$id_s' AND cdate = '$date_s'",DBH) or die(mysql_error());		
		$count_today = mysql_num_rows($result_today);

$result_today_u = mysql_query("SELECT COUNT(DISTINCT ip) FROM stats WHERE urlid = '$id_s' AND cdate = '$date_s'",DBH) or die(mysql_error());	
		$row_today_u = mysql_fetch_array($result_today_u);

if($count_s==0 && $hits==0)
{ echo "no results to show"; }


while($array=mysql_fetch_array($result_s))
	 { 		

		while($array_u=mysql_fetch_array($result_s_c_u))
			{ 	
				$result_u = mysql_query("SELECT * FROM stats WHERE locfrom = '$array_u[0]' AND urlid = '$id_s'",DBH) or die(mysql_error());	
				$count_u = mysql_num_rows($result_u);
				if ($array_u[0] == "") {
					$url_name = "Direct Traffic";
				} else {
					$url_name = $array_u[0];
				}
				
				$source_urls .= "<tr><td style='width:500px !important;'><a href='".$url_name."'>".substr($url_name, 0, 100)."</a></td><td class='tm'>".$count_u."</td></tr>"; 
			}

	}




?>


<?php
require("lib/header.php");
?>   
 
    <a href="http://<?php echo settingsdb(location); ?>" title="<?php echo settingsdb(name); ?> - Url Shortner" ><div id="logoland"><?php echo settingsdb(name); ?></div></a>

      <div class="menuland">

      	<a class="btn btn-primary" href="/index.php" >Create New URL</a>

      </div>


 <div class="clear"></div>



    <div class="meela_box meelab">





<h2 class="tl" style="overflow:auto;"><strong>URL: </strong><?php echo $url; ?></h2>

<hr/>

<h1 style="text-align:left; width:400px; float: left; margin-left: 20px;">http://<?php echo settingsdb(location); ?>/<?php echo $short_url; ?></h1>
<h2 style="text-align:right; width: 300px; float: right; margin-right: 20px;">Created: <?php echo $created; ?></h2>

 <div class="clear"></div>
<hr/>

<div class="info">


<div class="minfo"><a>Hits</a><span><?php echo $hits; ?></span></div>

<div class="minfo"><a>Unique Hits</a><span><?php echo $row_s_c[0]; ?></span></div>

<div class="minfo"><a>Hits Today</a><span><?php echo $count_today; ?></span></div>
<div class="minfo"><a>Unique Hits Today</a><span><?php echo $row_today_u[0]; ?></span></div>


</div>



<section class="stats_map"><span>Visitor Map</span>
  <div id="chart_div_map" style="width: 420px; height: 300px;"></div>
</section>


<div class="clearfix"></div>



 <table class="table table-striped stats_table">
 	            <colgroup>
              <col class="span6">
              <col class="span1">
            </colgroup>

              <thead>
                <tr>
                  <th>Referral Location</th>
                  <th class="tm">Visits</th>
                </tr>
              </thead>
              <tbody>
              	<?php echo $source_urls; ?>
              </tbody>
            </table>

</div>

   <script type="text/javascript" src="https://www.google.com/jsapi"></script>
    <script type='text/javascript'>
     google.load('visualization', '1', {'packages': ['geochart']});
     google.setOnLoadCallback(drawRegionsMap);

      function drawRegionsMap() {
        var data = google.visualization.arrayToDataTable([
          ['Country', 'Visits Today'],

<?php


    $table_map = substr(1, 0, 1);
  
  if ($table_map) {
      $result_map = mysql_query("SELECT DISTINCT country FROM stats WHERE urlid='$id_s'",DBH) or die(mysql_error());
      $i = 0;
    while ($row_map  = mysql_fetch_assoc($result_map)) {

          $country_map = $row_map['country'];
          $result2_map = mysql_query("SELECT COUNT(country) FROM stats WHERE country='$country_map' AND urlid='$id_s'",DBH) or die(mysql_error());
          $todayget_map = mysql_fetch_row($result2_map);
          $count_map = $todayget_map[0];
          echo "['".$country_map."', ".$count_map."], ";
 	
      }
  }

?>

        ]);

        var options = {};

        var chart = new google.visualization.GeoChart(document.getElementById('chart_div_map'));
        chart.draw(data, options);
    };
    </script>



<?php require("lib/footer.php"); ?>

      