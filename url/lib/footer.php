<footer>

    <a href="http://<?php echo settingsdb(location); ?>" title="Home">Home</a> | <?php if(!settingsdb(bookmarklet) == 0):?><a href="javascript:void(location.href='http://<?php echo settingsdb(location); ?>/create.php?url='+encodeURIComponent(location.href))" title="<?php echo settingsdb(name); ?> Bookmarklet">Bookmarklet</a> |<?php endif; if(!settingsdb(api) == 0): ?><a href="http://<?php echo settingsdb(location); ?>/api-about.php" title="Developer API">Developer</a> | <?php endif; ?> Copyright &copy; <?=date("Y")?> - <a href="http://wwwmafiashare.net"><?php echo settingsdb(name); ?></a></div>

</footer>


    <!-- Le javascript
    ================================================== -->
    <!-- Placed at the end of the document so the pages load faster -->
    <script src="//ajax.googleapis.com/ajax/libs/jquery/1.8.2/jquery.min.js"></script>
    <script src="http://<?php echo settingsdb(location); ?>/assets/js/jquery.zclip.min.js"></script>

<script>
 var text_input = document.getElementById ('urlbox');
text_input.focus ();
text_input.select ();
</script>
<script>

$(document).ready(function(){

    $("#flashbtn").zclip({
        path:'http://<?php echo settingsdb(location); ?>/assets/ZeroClipboard.swf',
        copy:$('#appendedInputButton').val(),

        afterCopy:function(){
            $('.check').slideDown();
        }
    });

 
});


setTimeout(function(){ 
    $(".check").slideUp("slow"); 
  }, 8000 ); 

</script>



<script type="text/javascript">// <![CDATA[
$(document).ready(function() {
$.ajaxSetup({ cache: false });
$('#urlvisits').load('http://<?php echo settingsdb(location); ?>/stats-api.php?a=totalhits');
$('#urltotal').load('http://<?php echo settingsdb(location); ?>/stats-api.php?a=totalcreated');
$('#urlrecent').load('http://<?php echo settingsdb(location); ?>/stats-api.php?a=recent');
$('#urlrecentview').load('http://<?php echo settingsdb(location); ?>/stats-api.php?a=recentview');


});
// ]]></script>


<script type="text/javascript">

  var _gaq = _gaq || [];
  _gaq.push(['_setAccount', '<?php echo settingsdb(analytics);?>']);
  _gaq.push(['_trackPageview']);

  (function() {
    var ga = document.createElement('script'); ga.type = 'text/javascript'; ga.async = true;
    ga.src = ('https:' == document.location.protocol ? 'https://ssl' : 'http://www') + '.google-analytics.com/ga.js';
    var s = document.getElementsByTagName('script')[0]; s.parentNode.insertBefore(ga, s);
  })();

</script>
  </body>
</html>
