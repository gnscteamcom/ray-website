<?php
session_start();
if (!isset($_SESSION['basic_is_logged_in']) 
    || $_SESSION['basic_is_logged_in'] !== true) {
    header('Location: login.php');
    exit;
}

?>
<?php
		include '../lib/config.php';
		
		mysql_connect($cchost,$ccuser,$ccpass);
		@mysql_select_db($ccname) or die( "Unable to select database");
		
		$query="SELECT * FROM settings";
		$result = mysql_query($query);
		mysql_close();
		
		$t_sLocation = mysql_result($result,0,"location");
		$sLocation = ($sLocation ? $sLocation : ($t_sLocation? $t_sLocation : ''));
		
		$t_sName = mysql_result($result,0,"name");
		$sName = ($sName ? $sName : ($t_sName? $t_sName : ''));
		
		$t_bar = mysql_result($result,0,"bar");
		$bar = ($bar ? $bar : ($t_bar? $t_bar : 0));
		
		$t_analytics = mysql_result($result,0,"analytics");
		$analytics = ($analytics? $analytics : ($t_analytics? $t_analytics : 0));
		
		$t_ads = mysql_result($result,0,"ads");
		$ads = ($ads? $ads : ($t_ads? $t_ads : 0));
		
		
		$t_ad_html = mysql_result($result,0,"ad_html");
		$ad_html = ($ad_html? $ad_html : ($t_ad_html? $t_ad_html: ''));
		
		$t_api = mysql_result($result,0,"api");
		$api = ($api? $api : ($t_api? $t_api : 0));
		
		$t_sMedia = mysql_result($result,0,"socialmedia");
		$sMedia = ($sMedia? $sMedia : ( $t_sMedia? $t_sMedia: 0));
		
		
    $t_qr = mysql_result($result,0,"qr");
    $qr = ($qr? $qr : ( $t_qr? $t_qr: 0));
    
    $t_bmarklet = mysql_result($result,0,"bookmarklet");
		$bmarklet = ($bmarklet? $bmarklet : ($t_bmarklet? $t_bmarklet: 0 ));
		
		
		$t_randomc = mysql_result($result,0,"chars");
		$randomc = ($randomc ? $randomc : ($t_randomc? $t_randomc: 0 ));

    $t_length = mysql_result($result,0,"length");
    $length = ($length ? $length : ($t_length? $t_length: 0 ));
	
    $t_safe = mysql_result($result,0,"safe");
    $safe = ($safe ? $safe : ($t_safe? $t_safe: 0 ));

    $t_splash = mysql_result($result,0,"splash");
    $splash = ($splash ? $splash : ($t_splash? $t_splash: 0 ));

    $t_valid = mysql_result($result,0,"validurl");
    $valid = ($valid ? $valid : ($t_valid? $t_valid: 0 ));



    $t_top3 = mysql_result($result,0,"top3");     
    $top3 = ($top3 ? $top3 : ($t_top3? $t_top3: 0 ));
  
    $t_description = mysql_result($result,0,"description");
    $description = ($description ? $description : ($t_description? $t_description: 0 ));

    $t_recentview = mysql_result($result,0,"recentview");
    $recentview = ($recentview ? $recentview : ($t_recentview? $t_recentview: 0 ));

    $t_recentcreate = mysql_result($result,0,"recentcreate");
    $recentcreate = ($recentcreate ? $recentcreate : ($t_recentcreate? $t_recentcreate: 0 ));   
	?>

<!DOCTYPE html>
<html lang="en">
  <head>
    <meta charset="utf-8">
    <title><?=$sName?> | Admin - Settings</title>
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

.ad_html {
  width: 500px;
}

</style>
	<script>
		function set_ads(i){
			var a = document.getElementById('ads');
			a.value = i;
		}
		function set_sMedia(i){
			var a= document.getElementById('sMedia');
			a.value = i;
		}
		function set_bar(i){
			var a= document.getElementById('bar');
			a.value = i;
		}
		function bMark(i){
			var a= document.getElementById('bmarklet');
			a.value = i;
		}
		function set_api(i){
			var a= document.getElementById('api');
			a.value = i;
		}
    function set_splash(i){
      var a= document.getElementById('splash');
      a.value = i;
    }
    function set_valid(i){
      var a= document.getElementById('valid');
      a.value = i;
    }

    function set_qrs(i){
      var a= document.getElementById('qr');
      a.value = i;
    }


    function set_top3(i){
      var a= document.getElementById('top3');
      a.value = i;
    }
    function set_description(i){
      var a= document.getElementById('description');
      a.value = i;
    }
    function set_recentview(i){
      var a= document.getElementById('recentview');
      a.value = i;
    }

    function set_recentcreate(i){
      var a= document.getElementById('recentcreate');
      a.value = i;
    }
	</script>
  </head>

  <body>



<?php include('header.php'); ?>

<div>




 <form class="form-horizontal"  method="post" action="changeSettings.php">
        <fieldset>
		   <?=$errorString?>		
		  <input id="sMedia" name="sMedia" type="hidden" value="<?=$sMedia?>">
      <input id="qr" name="qr" type="hidden" value="<?=$qr?>">
		  <input id="ads" name="ads" type="hidden" value="<?=$ads?>">
		  <input id="bar" name="bar" type="hidden" value="<?=$bar?>">
      <input id="splash" name="splash" type="hidden" value="<?=$splash?>">
      <input id="valid" name="valid" type="hidden" value="<?=$valid?>">
		  <input id="bmarklet" name="bmarklet" type="hidden" value="<?=$bmarklet?>">
		  <input id="api" name="api" type="hidden" value="<?=$api?>">
      <input id="top3" name="top3" type="hidden" value="<?=$top3?>">
      <input id="description" name="description" type="hidden" value="<?=$description?>">
      <input id="recentview" name="recentview" type="hidden" value="<?=$recentview?>">
      <input id="recentcreate" name="recentcreate" type="hidden" value="<?=$recentcreate?>">

            <ul id="myTab" class="nav nav-tabs">
              <li class="active"><a href="#extras" data-toggle="tab">Extras</a></li>
              <li><a href="#design" data-toggle="tab">Design</a></li>
              <li><a href="#ad" data-toggle="tab">Ads</a></li>
              <li><a href="#core" data-toggle="tab">Core</a></li>
            </ul>
            <div id="myTabContent" class="tab-content">
              <div class="tab-pane fade in active" id="extras">

                        <div class="control-group">
                          <label class="control-label" for="input01">Social Media Share <a href="#" data-rel="tooltip" tabindex="99" title="Sharing options once you crate your url."><i class="icon-question-sign"></i></a></label>
                          <div class="controls">
                          <div class="power btn-group"  data-toggle="buttons-radio">
                              <a class="btn btn-success <? echo ($sMedia==1 ?  'active' : '' );?> " href="#" onclick="set_sMedia(1)" >On</a><!--| btn-success |-->
                              <a class="btn btn-danger <? echo ($sMedia!=1 ?  'active' : '' );?> " href="#" onclick="set_sMedia(0)">Off</a><!--| disabled btn-danger |-->
                          </div>
                          </div>
                        </div>      
                        

                        <div class="control-group">
                          <label class="control-label" for="input01">QR Code Share <a href="#" data-rel="tooltip" tabindex="99" title="Sharing options once you crate your url."><i class="icon-question-sign"></i></a></label>
                          <div class="controls">
                          <div class="power btn-group"  data-toggle="buttons-radio">
                              <a class="btn btn-success <? echo ($qr==1 ?  'active' : '' );?> " href="#" onclick="set_qrs(1)" >On</a><!--| btn-success |-->
                              <a class="btn btn-danger <? echo ($qr!=1 ?  'active' : '' );?> " href="#" onclick="set_qrs(0)">Off</a><!--| disabled btn-danger |-->
                          </div>
                          </div>
                        </div>   


                        <div class="control-group">
                          <label class="control-label" for="input01">iFrame Bar <a href="#" data-rel="tooltip" tabindex="99" title="This bar will apear above the site on a shortened url."><i class="icon-question-sign"></i></a></label>
                          <div class="controls">
                          <div class="power btn-group"  data-toggle="buttons-radio">
                              <a class="btn btn-success <? echo ($bar==1 ?  'active' : '' ); ?>" href="#" onclick="set_bar(1)">On</a><!--| btn-success |-->
                              <a class="btn btn-danger  <? echo($bar!=1 ? 'active' : '' ); ?>" href="#" onclick="set_bar(0)">Off</a><!--| disabled btn-danger |-->
                          </div>
                          </div>
                        </div>
                            

                        <div class="control-group">
                          <label class="control-label" for="input01">Splash Page <a href="#" data-rel="tooltip" tabindex="99" title="Loading screen which apears before loading shortened URL."><i class="icon-question-sign"></i></a></label>
                          <div class="controls">
                          <div class="power btn-group"  data-toggle="buttons-radio">
                              <a class="btn btn-success <? echo ($splash==1 ?  'active' : '' ); ?>" href="#" onclick="set_splash(1)">On</a><!--| btn-success |-->
                              <a class="btn btn-danger  <? echo($splash!=1 ? 'active' : '' ); ?>" href="#" onclick="set_splash(0)">Off</a><!--| disabled btn-danger |-->
                          </div>
                          </div>
                        </div>


                        <div class="control-group">
                          <label class="control-label" for="input01">Bookmarklet</label>
                          <div class="controls">
                          <div class="power btn-group"  data-toggle="buttons-radio">
                              <a class="btn btn-success <? echo ($bmarklet==1 ?  'active' : '' ); ?>" href="#" onclick="bMark(1)">On</a><!--| btn-success |-->
                              <a class="btn btn-danger <? echo ($bmarklet!=1 ?  'active' : '' ); ?>" href="#" onclick="bMark(0)">Off</a><!--| disabled btn-danger |-->
                          </div>
                          </div>
                        </div>

                        <div class="control-group">
                          <label class="control-label" for="input01">URL Validation</label>
                          <div class="controls">
                          <div class="power btn-group"  data-toggle="buttons-radio">
                              <a class="btn btn-success <? echo ($valid==1 ?  'active' : '' ); ?>" href="#" onclick="set_valid(1)">On</a><!--| btn-success |-->
                              <a class="btn btn-danger <? echo ($valid!=1 ?  'active' : '' ); ?>" href="#" onclick="set_valid(0)">Off</a><!--| disabled btn-danger |-->
                          </div>
                          </div>
                        </div>                        

                        <div class="control-group">
                          <label class="control-label" for="input01">API</label>
                          <div class="controls">
                          <div class="power btn-group"  data-toggle="buttons-radio">
                              <a class="btn btn-success <? echo ($api==1 ?  'active' : '' ); ?>" href="#" onclick="set_api(1)" >On</a><!--| btn-success |-->
                              <a class="btn btn-danger <? echo ($api!=1 ? 'active' : '' ); ?>" href="#" onclick="set_api(0)" >Off</a><!--| disabled btn-danger |-->
                          </div>
                          </div>
                        </div>          

              </div> <!-- EXTRAS -->
              <div class="tab-pane fade" id="ad">

                  <div class="control-group">
                    <label class="control-label" for="input01">Ads <a href="#" data-rel="tooltip" tabindex="99" title="This ad will apear on the homepage under the url shorten function."><i class="icon-question-sign"></i></a></label>
                    <div class="controls">
                    <div class="power btn-group"  data-toggle="buttons-radio">
                        <a class="btn btn-success <? echo ($ads==1 ?  'active' : '' );?>" href="#" onclick="set_ads(1);" >On</a><!--| btn-success |-->
                        <a class="btn btn-danger <? echo ($ads!=1 ?  'active' : '' );?>" href="#" onclick="set_ads(0);">Off</a><!--| disabled btn-danger |-->
                    </div>
                    </div>
                  </div>      
                  
                  <div class="control-group">
                    <label class="control-label" for="textarea">Ad HTML</label>
                    <div class="controls">
                      <textarea class="input-xlarge ad_html" name="ad_html" id="textarea" rows="3" ><?=$ad_html?></textarea>
                    </div>
                  </div>

              </div><!-- AD -->
              <div class="tab-pane fade" id="design">

                        <div class="control-group">
                          <label class="control-label" for="input01">Top 3</label>
                          <div class="controls">
                          <div class="power btn-group"  data-toggle="buttons-radio">
                              <a class="btn btn-success <? echo ($top3==1 ?  'active' : '' ); ?>" href="#" onclick="set_top3(1)">On</a><!--| btn-success |-->
                              <a class="btn btn-danger <? echo ($top3!=1 ?  'active' : '' ); ?>" href="#" onclick="set_top3(0)">Off</a><!--| disabled btn-danger |-->
                          </div>
                          </div>
                        </div>


                        <div class="control-group">
                          <label class="control-label" for="input01">Description</label>
                          <div class="controls">
                          <div class="power btn-group"  data-toggle="buttons-radio">
                              <a class="btn btn-success <? echo ($description==1 ?  'active' : '' ); ?>" href="#" onclick="set_description(1)">On</a><!--| btn-success |-->
                              <a class="btn btn-danger <? echo ($description!=1 ?  'active' : '' ); ?>" href="#" onclick="set_description(0)">Off</a><!--| disabled btn-danger |-->
                          </div>
                          </div>
                        </div>


                        <div class="control-group">
                          <label class="control-label" for="input01">Recently Viewed</label>
                          <div class="controls">
                          <div class="power btn-group"  data-toggle="buttons-radio">
                              <a class="btn btn-success <? echo ($recentview==1 ?  'active' : '' ); ?>" href="#" onclick="set_recentview(1)">On</a><!--| btn-success |-->
                              <a class="btn btn-danger <? echo ($recentview!=1 ?  'active' : '' ); ?>" href="#" onclick="set_recentview(0)">Off</a><!--| disabled btn-danger |-->
                          </div>
                          </div>
                        </div>

                        <div class="control-group">
                          <label class="control-label" for="input01">Recently Created</label>
                          <div class="controls">
                          <div class="power btn-group"  data-toggle="buttons-radio">
                              <a class="btn btn-success <? echo ($recentcreate==1 ?  'active' : '' ); ?>" href="#" onclick="set_recentcreate(1)">On</a><!--| btn-success |-->
                              <a class="btn btn-danger <? echo ($recentcreate!=1 ?  'active' : '' ); ?>" href="#" onclick="set_recentcreate(0)">Off</a><!--| disabled btn-danger |-->
                          </div>
                          </div>
                        </div>                        



              </div><!-- DESIGN -->

              <div class="tab-pane fade" id="core">

                      <div class="control-group">
                        <label class="control-label" for="input01">Site Name</label>
                        <div class="controls">
                          <input type="text" class="input-xlarge" name="sName" value="<?=$sName?>">
                        </div>
                      </div>
                      
                      
                       <div class="control-group">
                        <label class="control-label" for="input01">Site Location <a href="#" data-rel="tooltip" tabindex="99" title="e.g extra.codecanopy.com (without http://)"><i class="icon-question-sign"></i></a></label>
                        <div class="controls">
                          <input type="text" class="input-xlarge" name="sLocation" value="<?=$sLocation?>">
                        </div>
                      </div>
                      
                      <div class="control-group">
                        <label class="control-label" for="input01">Url length</label>
                        <div class="controls">
                          <input type="text" class="input-xlarge span2" name="length" value="<?=$length?>">
                        </div>
                      </div>

                      <div class="control-group">
                        <label class="control-label" for="input01">Random URL Generator Characters</label>
                        <div class="controls">
                          <input type="text" class="input-xlarge span2" name="randomc" value="<?=$randomc?>">
                        </div>
                      </div>          
                      
                      
                      <div class="control-group">
                        <label class="control-label" for="input01">Google Analytics <a href="#" data-rel="tooltip" tabindex="99" title="Google Analytics ID e.g UA-24574253-1"><i class="icon-question-sign"></i></a></label>
                        <div class="controls">
                          <input type="text" class="input-xlarge" name="analytics" value="<?=$analytics?>">
                        </div>
                      </div>


                      <div class="control-group">
                        <label class="control-label" for="input01">Safe Browsing <a href="#" data-rel="tooltip" tabindex="99" title="Google Safe browsing apikey required to activate."><i class="icon-question-sign"></i></a></label>
                        <div class="controls">
                          <input type="text" class="input-xlarge" name="safe" value="<?=$safe?>">
                        </div>
                      </div>
          
              </div><!-- CORE -->

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
    <script src="assets/js/bootstrap-tooltip.js"></script>
	    
    <script>
	   $('[data-rel="tooltip"]').tooltip();


    $(document).ready(function() {
      $("#u").load("CC_URLS.php");
    });


    </script>


  </body>
</html>
