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
	
	include '../lib/config.php';
	$user=$config['db_username'];
	$password=$config['db_password'];
	$database=$config['db_name'];
	mysql_connect($cchost,$ccuser,$ccpass);
	@mysql_select_db($ccname) or die( "Unable to select database");
	
	$query = "DELETE FROM urls WHERE id=$id";
	$result = mysql_query($query);
	mysql_close();
	header("Location: index.php?page=$page");
	
?>
