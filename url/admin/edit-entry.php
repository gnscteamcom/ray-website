<?php
session_start();
if (!isset($_SESSION['basic_is_logged_in']) 
    || $_SESSION['basic_is_logged_in'] !== true) {
    header('Location: login.php');
    exit;
}

?>
<?php
		
		$t_id = htmlspecialchars($_GET["id"]);
		$t_page = htmlspecialchars($_GET["page"]);
		$id = ($id? $id : $t_id);
		$page = ($page? $page: $t_page);
		include '../lib/config.php';
		
		mysql_connect($cchost,$ccuser,$ccpass);
		@mysql_select_db($ccname) or die( "Unable to select database");
		
		$query="SELECT * FROM urls WHERE id=$id";
		$result = mysql_query($query);
		
		$t_sUrl= mysql_result($result,0,"short_url");
		$t_lUrl= mysql_result($result,0,"url");
		
		$sUrl = ($sUrl? $sUrl : $t_sUrl ); 
		$lUrl = ($lUrl? $lUrl : $t_lUrl ); 
		mysql_close();
?>

<!DOCTYPE html>
<html lang="en">
  <head>
    <meta charset="utf-8">
    <title>Notify Basic | Admin - Settings</title>
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


h2 {
	margin: 10px 160px;
}



</style>

  </head>

  <body>



<div class="main container">


  <p>&nbsp;</p>
  <div class="navbar">
    <div class="navbar-inner">
      <div class="container">
      
        <a class="brand" href="#">Admin Panel</a>
        <div class="nav-collapse">
          <ul class="nav">
            <li><a href="#">Urls</a></li>
            <li class="active"><a href="#">Settings</a></li>
            <li><a href="#">Help</a></li>
          </ul>
          
           <form class="navbar-search pull-left" action="">
            <input type="text" class="search-query span2" placeholder="Search">
          </form>
          
          <ul class="nav pull-right">

            <li><a href="logout.php">Logout</a></li>
            
          </ul>
        </div><!-- /.nav-collapse -->
      </div>
    </div><!-- /navbar-inner -->
  </div><!-- /navbar -->


<div>



<h2>Edit URL</h2>


 <form class="form-horizontal" action="process-edit.php?<? echo "id=$id&page=$page"; ?>" method="post">
        <fieldset>
			<?=$errorString?>
		      <div class="control-group">
            <label class="control-label" for="input01">Short Url</label>
            <div class="controls">
              <input type="text" class="input-xlarge" id="input01" name="sUrl" value=<?=$sUrl?>>
            </div>
          </div>
          
          
           <div class="control-group">
            <label class="control-label" for="input01">Long Url</label>
            <div class="controls">
              <input type="text" class="input-xlarge" id="input01" name="lUrl" value=<?=$lUrl?>>
            </div>
          </div>
 
           <div class="form-actions">
            <button type="submit" class="btn btn-primary">Save changes</button>
            <button class="btn">Cancel</button>
          </div>
        </fieldset>
      </form>
         
          
     


</div>



</div> <!--| main END |-->




    <!-- Le javascript
    ================================================== -->
    <!-- Placed at the end of the document so the pages load faster -->
    <script src="https://ajax.googleapis.com/ajax/libs/jquery/1.7.2/jquery.min.js"></script>
	<script src="assets/js/bootstrap.min.js"></script>
    <script src="assets/js/bootstrap-button.js"></script>
	    
    <script>
	
    </script>


  </body>
</html>
