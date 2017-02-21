<?php 

$basename = str_replace(".php","",basename($_SERVER['REQUEST_URI']));


?>

<div class="main container">

<div id="u"></div>
  <div class="navbar">
    <div class="navbar-inner">
      <div class="container">
      
        <a class="brand" href="#">Admin Panel</a>
        <div class="nav-collapse">
          <ul class="nav">
            <li <?php if ($basename == "index") { echo 'class="active"';} ?>><a href="index.php">Urls</a></li>
            <li <?php if ($basename == "stats") { echo 'class="active"';} ?>><a href="stats.php">Stats</a></li>
            <li <?php if ($basename == "settings") { echo 'class="active"';} ?>><a href="settings.php">Settings</a></li>
            <li><a href="http://codecanopy.com">Help</a></li>
          </ul>
              
          <?php if ($basename == "index"):?>
          <form class="navbar-search pull-left" action="">
            <input type="text" class="search-query span2" placeholder="Search">
          </form>
          <?php endif; ?>

          <ul class="nav pull-right">
            <li><a href="logout.php">Logout</a></li>
          </ul>
        </div><!-- /.nav-collapse -->
      </div>
    </div><!-- /navbar-inner -->
  </div><!-- /navbar -->
