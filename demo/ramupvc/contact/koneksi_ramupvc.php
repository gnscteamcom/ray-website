<?php
//koneksi dengan database mysql
//koneksi_ramupvc.php
$host="localhost";
$username="rayrina1_test";
$password="011235";
$database="rayrina1_test";
$table="messages";
$koneksi=mysql_connect($host, $username, $password) or die ("cannot enter to mysql!");
mysql_select_db($database) or die ("cannot select database!");
?>