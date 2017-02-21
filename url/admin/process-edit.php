<?php
session_start();
if (!isset($_SESSION['basic_is_logged_in']) 
    || $_SESSION['basic_is_logged_in'] !== true) {
    header('Location: login.php');
    exit;
}

?>
<?php

	$id = htmlspecialchars($_GET["id"]);
	$page = htmlspecialchars($_GET["page"]);
	
	$sUrl = $_POST['sUrl'];
	$lUrl = $_POST['lUrl'];
	$errors = null;
	$errors = array();
	
	if($sUrl == ''){
		$errors[] = "Short Url cannot be blank";
		
	}
	
	if($lUrl == ''){
		$errors[] = "Long Url cannot be blank";
		
	}
	if(filter_var($lUrl, FILTER_VALIDATE_URL) === FALSE){
		$errors[] = "Long Url needs to be a valid Url";
	}
	
	
	
	global $errorString;
	if(count($errors) > 0){
		$errorString = '<p>There was an error processing the form.</p>';
		$errorString .= '<ul>';
		foreach($errors as $error){
			$errorString .= "<li>$error</li>";
		}
		$errorString .= '</ul>';
		include 'edit-entry.php';
		
	}
	else{
		include '../lib/config.php';
		mysql_connect($cchost,$ccuser,$ccpass);
		@mysql_select_db($ccname) or die( "Unable to select database");
		
		$query = "UPDATE urls SET short_url='$sUrl', url='$lUrl'  WHERE id=$id";
		$result = mysql_query($query);
		mysql_close();
		header("Location: index.php?page=$page");
	}

?>
