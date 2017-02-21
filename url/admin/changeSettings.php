<?php
session_start();
if (!isset($_SESSION['basic_is_logged_in']) 
    || $_SESSION['basic_is_logged_in'] !== true) {
    header('Location: login.php');
    exit;
}

	
	include '../lib/config.php';
	mysql_connect($cchost,$ccuser,$ccpass);
	@mysql_select_db($ccname) or die( "Unable to select database");
	
	$errors = null;
	$errors = array();
	foreach($_POST AS $key => $value)
	{
		
		
		$$key = $value;
		// first need to make sure this is an allowed field
		
		if($value == ''){	
			switch($key){
				case 'sName':
					$errors[]= "Site Name is required";																	
					break;
				case 'sLocation':
					$errors[]= "Site Location is required";																	
					break;
				case 'length':
					$errors[] = "URL Length needs to be set";
					break;
				case 'analytics':
					$errors[] = "Google Analytics key needs to be set";
					break;
				
			}
		}
		
		
	}
	
	if(!is_numeric($length)){
		$errors[] = "Length needs to be a number";
	} 

	global $errorString;
	if(count($errors) > 0){
		$errorString = '<p>There was an error processing the form.</p>';
		$errorString .= '<ul>';
		foreach($errors as $error){
			$errorString .= "<li>$error</li>";
		}
		$errorString .= '</ul>';
		include 'settings.php';
		
	}
	else{
		$query = "UPDATE settings SET 
				 location = '$sLocation', 
				 bar = '$bar', 
				 analytics = '$analytics', 
				 ads = '$ads', 
				 socialmedia = '$sMedia', 
				 bookmarklet = '$bmarklet', 
				 api = '$api', 
				 name='$sName',
				 length='$length', 
				 ad_html='$ad_html',
				 id='$id_c', 
				 safe='$safe', 
				 chars='$chars', 
				 splash='$splash', 
				 validurl='$valid', 
				 parabox='$parabox', 
				 boxcreate='$boxcreate', 
				 boxvisit='$boxvisit', 
				 pods='$pods', 
				 qr='$qr',
				 top3='$top3',
				 description='$description',
				 recentview='$recentview',
				 recentcreate='$recentcreate'";


		$result = mysql_query($query);
		if(!$result){
			$errorString = '<p>There was an error updating the settings:'.mysql_error().' </p>';
			include 'settings.php';
		}
		else{
			$errorString = '<p>Settings Changed successfully</p>';
			include 'settings.php';
		}
		
	}

		

?>
