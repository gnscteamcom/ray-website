<?php

error_reporting(0);

    $updates = simplexml_load_file('http://updates.codecanopy.com/CC_URLS.xml');
    $currentv = "2.0";

    if ($updates->update[0]->version == $currentv && $updates->update[0]->updatecheck == 1) {} else {
    	$up = 1;
    }

	if ($updates->update[0]->updatecheck == 1) {
    	$desc = ' You are currently on v'.$currentv.' The lastest version is v'.$updates->update[0]->version;
    }   else  {
    	$desc = $updates->update[0]->desc;
    }

    if ($updates->update[0]->link == '') {} else {
    	$link = '<a href="'.$updates->update[0]->link.'" target="blank" style="margin-left: 30px;" class="badge badge-'.$updates->update[0]->type.'">'.$updates->update[0]->linktext.'</a>';
    }

   if ($up == 1):
?>

<div class="alert alert-<?php echo $updates->update[0]->type; ?>">
	<strong><?php echo $updates->update[0]->bold; ?> </strong><?php echo $desc.$link; ?>
</div>



<?php  endif; ?>