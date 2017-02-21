<?php
session_start();
require("../lib/config.php");
$errorMessage = '';
if (isset($_POST['txtUserId']) && isset($_POST['txtPassword'])) {
if ($_POST['txtUserId'] === $adminuser && $_POST['txtPassword'] === $adminpassword) { 
$_SESSION['basic_is_logged_in'] = true;

header('Location: index.php');
exit;
} else {
$errorMessage = 'Sorry, wrong user id / password';
}
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

<style>
.login {
	width: 430px; 
	margin: 0 auto;
}

h1 {
	margin: 100px 0 20px;
}
</style>

  </head>

  <body>


		<center><h1>Admin Panel</h1></center> 
		<?php
if ($errorMessage != '') {
?>
<p align="center"><strong><font color="#990000"><?php echo $errorMessage; ?></font></strong></p>
<?php
}
?> 
        
  


<div class="login">
      <form method="post" name="frmLogin" class="well form-inline">
        <input name="txtUserId" type="text" class="input-medium" placeholder="username">
        <input name="txtPassword" type="password" class="input-medium" placeholder="Password">
        <button name="btnLogin" type="submit" class="btn">Sign in</button>
      </form>
</div>


</body>
</html>