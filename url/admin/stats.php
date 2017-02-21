<?php
session_start();
if (!isset($_SESSION['basic_is_logged_in']) 
    || $_SESSION['basic_is_logged_in'] !== true) {
    header('Location: login.php');
    exit;
}

?>
<?php
		include '../lib/config.php';
    include '../lib/common.php';
    $date = gmdate("d-m-Y");
	?>

<!DOCTYPE html>
<html lang="en">
  <head>
    <meta charset="utf-8">
    <title><?=$sName?> | Admin - Settings</title>
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <meta name="description" content="">
    <meta name="author" content="">

    <!-- Le styles -->
    <link href="assets/css/bootstrap.css" rel="stylesheet">

    <!-- Le HTML5 shim, for IE6-8 support of HTML5 elements -->
    <!--[if lt IE 9]>
      <script src="http://html5shim.googlecode.com/svn/trunk/html5.js"></script>
    <![endif]-->
		
<style>


.main {
	margin: 30px auto;
}


.none {
	display: none;
}

hr {
  margin: 7px !important;
}

.pull-right {
	margin-right: 10px !important;
}

.width {
	width: 960px;
	margin-left: 20px;
}

.pagination {
	text-align:center;
}

.databox {
	margin: 10ox 0;
	height: 80px;
	
}

.ad_html {
  width: 500px;
}

.meela, .meela2 {
  border: 1px solid #c6c6c6;
  -webkit-border-radius: 5px;
  -moz-border-radius: 5px;
  border-radius: 5px;
  padding: 10px;
  margin: 10px;
}

.meela span{
  font-size: 16px;
  height: 20px;
  margin-left: 15px;
}

.meela p{
  font-size: 50px;
  text-align: center;
  height: 40px;
  line-height: 45px;
}

.minipod {
  width: 278px;
  float: left;
}

.fiftypod {
  width: 438px;
  float: left;
}



</style>
	<script>
		function set_ads(i){
			var a = document.getElementById('ads');
			a.value = i;
		}
		function set_sMedia(i){
			var a= document.getElementById('sMedia');
			a.value = i;
		}
		function set_bar(i){
			var a= document.getElementById('bar');
			a.value = i;
		}
		function bMark(i){
			var a= document.getElementById('bmarklet');
			a.value = i;
		}
		function set_api(i){
			var a= document.getElementById('api');
			a.value = i;
		}
	</script>
  </head>

  <body>

<?php include('header.php'); ?>





<div>


<section class="meela minipod"><span>Total Urls</span><hr/><p id="urltotal">^_^</p></section>
<section class="meela minipod"><span>Total URL vists</span><hr/><p id="urlvisits">^_^</p></section>
<section class="meela minipod"><span>Created Today</span><hr/><p id="urltotaltoday">^_^</p></section>

<div class="clearfix"></div>

<section class="meela"><span>Shortened URL's</span><hr/>
  <div id="chart_div_urls"></div>
</section>

<div class="clearfix"></div>

<section class="meela fiftypod"><span>URL Visitor Map (<?php echo $date; ?>)</span><hr/>
  <div id="chart_div_map" style="width: 420px; height: 300px;"></div>
</section>



<section class="meela fiftypod"><span>Custom Vs Random</span><hr/>
  <div id="chart_div" style="width: 420px; height: 300px;"></div>
</section>

<div class="clearfix"></div>
<section class="meela">
<center><h2>Recently Visited URLS</h2></center><hr/>
  <table class="table table-striped">
    <thead>
      <tr>
        <th>Short URL</th>
        <th>Visit Oragin</th>
        <th>Hits</th>
        <th>Created</th>
      </tr>
    </thead>
    <tbody id="urlrecentview">


  </table>
</section>

<div class="clearfix"></div>

<section class="meela">
<center><h2>Recently Created URLS</h2></center><hr/>
  <table class="table table-striped">
    <thead>
      <tr>
        <th>Short URL</th>
        <th>Original URL</th>
        <th>Created</th>
        <th>Hits</th>
      </tr>
    </thead>
    <tbody id="urlrecent">


  </table>
</section>


</div>



</div> <!--| main END |-->




    <!-- Le javascript
    ================================================== -->
    <!-- Placed at the end of the document so the pages load faster -->
    <script src="https://ajax.googleapis.com/ajax/libs/jquery/1.7.2/jquery.min.js"></script>
  	<script src="assets/js/bootstrap.min.js"></script>
    <script src="assets/js/bootstrap-button.js"></script>
    <script src="assets/js/bootstrap-tooltip.js"></script>
	  
        <!--Load the AJAX API-->
    <script type="text/javascript" src="https://www.google.com/jsapi"></script>
    <script type="text/javascript">

      // Load the Visualization API and the piechart package.
      google.load('visualization', '1.0', {'packages':['corechart']});

      // Set a callback to run when the Google Visualization API is loaded.
      google.setOnLoadCallback(drawChart);

      // Callback that creates and populates a data table,
      // instantiates the pie chart, passes in the data and
      // draws it.
      function drawChart() {

        // Create the data table.
        var data = new google.visualization.DataTable();
        data.addColumn('string', 'Topping');
        data.addColumn('number', 'Slices');
        data.addRows([
  <?php

          $result3 = mysql_query("SELECT COUNT(custom) FROM urls WHERE custom='Y'",DBH) or die(mysql_error());
          $count3 = mysql_fetch_row($result3);
          echo "['Custom', ".$count3[0]."],";

          $result4 = mysql_query("SELECT COUNT(custom) FROM urls WHERE custom='N'",DBH) or die(mysql_error());
          $count4 = mysql_fetch_row($result4);
          echo "['Random', ".$count4[0]."] ";

?>

        ]);

        // Set chart options
        var options = {'width':420, 'height':300};

        // Instantiate and draw our chart, passing in some options.
        var chart = new google.visualization.PieChart(document.getElementById('chart_div'));
        chart.draw(data, options);
      }
    </script>


    <script type="text/javascript">
      google.load("visualization", "1", {packages:["corechart"]});
      google.setOnLoadCallback(drawChart);
      function drawChart() {
        var data = google.visualization.arrayToDataTable([
          ['Day',  'Visits', 'Created'],


<?php 

$m= date("m");
$de= date("d");
$y= date("Y");
for($i=0; $i<=15; $i++){
$monthback =  date('Y-m-d',mktime(0,0,0,$m,($de-$i),$y)); 
$monthcreatedate =  date('l dS F Y',mktime(0,0,0,$m,($de-$i),$y)); 
$countresult = mysql_query("SELECT * FROM urls WHERE created='$monthback'",DBH) or die(mysql_error());
$monthdaycreate = mysql_num_rows($countresult);

$monthbackvisit =  date('d-m-Y',mktime(0,0,0,$m,($de-$i),$y)); 
$countresulvisit = mysql_query("SELECT * FROM stats WHERE cdate='$monthbackvisit'",DBH) or die(mysql_error());
$monthdaycreatevisit = mysql_num_rows($countresulvisit);


echo "['".$monthcreatedate."', ".$monthdaycreatevisit.", ".$monthdaycreate."], ";
}

?>


        ]);

        var options = {

          hAxis: {title: 'Days'}
        };

        var chart = new google.visualization.AreaChart(document.getElementById('chart_div_urls'));
        chart.draw(data, options);
      }
    </script>

    <script type='text/javascript'>
     google.load('visualization', '1', {'packages': ['geochart']});
     google.setOnLoadCallback(drawRegionsMap);

      function drawRegionsMap() {
        var data = google.visualization.arrayToDataTable([
          ['Country', 'Visits Today'],

<?php


    $table = substr(1, 0, 1);
    $date = gmdate("d-m-Y");
  
  if ($table) {
      $result = mysql_query("SELECT DISTINCT country FROM stats WHERE cdate='$date'",DBH) or die(mysql_error());
      $i = 0;
    while ($row  = mysql_fetch_assoc($result)) {

          $country = $row['country'];
          $result2 = mysql_query("SELECT COUNT(country) FROM stats WHERE country='$country'",DBH) or die(mysql_error());
          $todayget = mysql_fetch_row($result2);
          $count = $todayget[0];
          echo "['".$country."', ".$count."], ";
 
      }
  }

?>

        ]);

        var options = {};

        var chart = new google.visualization.GeoChart(document.getElementById('chart_div_map'));
        chart.draw(data, options);
    };
    </script>



<script type="text/javascript">// <![CDATA[
$(document).ready(function() {
$.ajaxSetup({ cache: false });
$('#urlvisits').load('astats.php?a=totalhits');
$('#urltotal').load('astats.php?a=totalcreated');
$('#urltotaltoday').load('astats.php?a=urltotaltoday');
$('#urlrecent').load('astats.php?a=recent');
$('#urlrecentview').load('astats.php?a=recentview');
$("#u").load("http://updates.codecanopy.com/CC_URLS.php");


});
// ]]></script>

    <script>
	   $('[data-rel="tooltip"]').tooltip();
    </script>


  </body>
</html>
