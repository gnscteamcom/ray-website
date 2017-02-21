<?php 
	require("lib/config.php");
	require("lib/common.php");
	require("lib/header.php");
	?>
    


<a href="http://<?php echo $config_location; ?>" title="MeeLa - Url Shortner" ><div id="logoland"><?php echo settingsdb(name); ?></div></a>
<div class="menuland">
    <a class="btn btn-primary" href="/index.php" >Create New URL</a>
</div>

<div class="clear"></div>

<div class="meela_box meelab">


    <h2>Developer API</h2>
    <h3>Random</h3>
    <p><strong>API:</strong> http://mee.la/api.php?url=http://faceflow.com/<br /></p>
    <p><strong>Responce:</strong> http://mee.la/2755</p>
    <br />

    <h3>Custom</h3>
    <p><strong>API:</strong> http://mee.la/api.php?url=http://faceflow.com/&amp;custom=videochat<br /></p>
    <p><strong>Responce:</strong> http://mee.la/videochat</p>

</div>
      
<?php require("lib/footer.php"); ?>
