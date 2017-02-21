<?php
session_start();
if (!isset($_SESSION['basic_is_logged_in']) 
    || $_SESSION['basic_is_logged_in'] !== true) {
    header('Location: login.php');
    exit;
}

?>
<!DOCTYPE html>
<html lang="en">
  <head>
    <meta charset="utf-8">
    <title>Url Shorten | Admin</title>
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <meta name="description" content="">
    <meta name="author" content="">

    <!-- Le styles -->
    <link href="assets/css/bootstrap.css" rel="stylesheet">

    <!-- Le HTML5 shim, for IE6-8 support of HTML5 elements -->
    <!--[if lt IE 9]>
      <script src="http://html5shim.googlecode.com/svn/trunk/html5.js"></script>
    <![endif]-->
	<?php
		$cur_page = htmlspecialchars($_GET["page"]);
		$search = htmlspecialchars($_GET["search"]);
		$cur_page = ($cur_page? $cur_page : 1);
		
		
		include '../lib/config.php';
	?>

<style>


.main {
	margin: 30px auto;
}


.none {
	display: none;
}

.table {
	float: left;
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
#outer-body{
	position:relative;
	
}
#loading {
	display:none;
	position:absolute;
	top:200px;
	left:360px;
	width:100px;
	height:100px;
	
}

</style>
<script src="https://ajax.googleapis.com/ajax/libs/jquery/1.7.2/jquery.min.js"></script>
<script>
	
	function srch(str,page){
		if (str.length==0)
		{ 
		  $("#body-container").hide();
		  $("#loading").show();	
		  $.get("fill-info.php?page="+page, function(data){
				$("#stat_box").html(data.stats);
				$("#index-body").html(data.table);
				$("#pager").html(data.pager); 
				$("#loading").hide();	
				$("#body-container").show();
			}, 'json');
		}
		else{
				$("#body-container").hide();
				$("#loading").show();	
				$.get("fill-info.php?search="+str+"&page="+page, function(data){
					$("#stat_box").html(data.stats);
					$("#index-body").html(data.table);
					$("#pager").html(data.pager); 
					$("#loading").hide();	
					$("#body-container").show();
				}, 'json');
				
		}
		return;
	}
	function delete_entry(id,page){
		var c = confirm("Are you sure you wish to delete this entry?");
		if(c){
			window.open('delete-entry.php?id='+id+'&page='+page,'_self');
		}
	}
	$(document).ready( function(){
		
		 srch('<?=$search?>',<?=$cur_page?>);
		 $('#search').val('<?=$search?>');
	});
	
</script>
 </head>

 <body>



<?php include('header.php'); ?>


<div id="outer-body">
	<img id="loading" src="./assets/img/loading.gif" alt="loading..."/>
	<div id="body-container">
		<div id="stat_box">
		
		</div>
		
		<div class="row">
			<div class="width">
			  <table class="table table-bordered table-striped">
				
				<thead>
				  <tr>
					<th>ID</th>
					<th>Name</th>
					<th>URL</th>
					<th>Date/Time</th>
					<th>Hits</th>
					<th></th>
				  </tr>
				</thead>
				<tbody id="index-body">
				
				 
			
				</tbody>
			  </table>
			</div>
			
			  <div id="pager" class="pagination">
				
			  </div>
			</div>
			
			
			
	</div>
</div>		
		


</div> <!--| main END |-->




    <!-- Le javascript
    ================================================== -->
    <!-- Placed at the end of the document so the pages load faster -->
  
	<script src="assets/js/bootstrap.min.js"></script>
    <script src="assets/js/bootstrap-button.js"></script>

<script>
	$(document).ready(function() {
	  $("#u").load("http://updates.codecanopy.com/CC_URLS.php");
	});
</script>


  </body>
</html>
