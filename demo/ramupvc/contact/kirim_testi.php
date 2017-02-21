<?php
include("koneksi_ramupvc.php");
$koneksi=mysql_connect($host, $username, $password) or die ("cannot enter to mysql!");
mysql_select_db($database) or die ("cannot select database!");

//Mendefinisikan variabel
$name=$_POST['name'];
$email=$_POST['email'];
$address=$_POST['address'];
$city=$_POST['city'];
$zip=$_POST['zip'];
$mobile=$_POST['mobile'];
$message=$_POST['message'];
$polaemail='^.+@.+..+$';

if(!$name || !$email || !$address || !$city || !$zip || !$mobile || !$message) 
{
	echo('<script type="text/javascript">');
	echo('alert("Failed to send comment")');
	echo('</script>');
}
else if(!eregi($polaemail,$email)) 
{
	echo(window.alert("Your email is invalid"));
}
else
{
	
	$add=mysql_query("insert into $table (name,address,city,zip,mobile,email,message) values ('$name','$address','$city','$zip','$mobile','$email','$message')")
    or die("Could not insert data because ".mysql_error());

    echo('<script type="text/javascript">');
	echo('window.location="index.php"');
	echo('</script>');
}
?>