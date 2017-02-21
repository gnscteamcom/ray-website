<?php
	function validateName($name){
		//if it's NOT valid
		if(strlen($name) < 4)
			return false;
		//if it's valid
		else
			return true;
	}
	function validateEmail($email){
		return ereg("^[a-zA-Z0-9]+[a-zA-Z0-9_-]+@[a-zA-Z0-9]+[a-zA-Z0-9.-]+[a-zA-Z0-9]+.[a-z]{2,4}$", $email);
	}
	
	function validateMessage($message){
		//if it's NOT valid
		if(strlen($message) < 10)
			return false;
		//if it's valid
		else
			return true;
	}
	
	function validateAddress($address){
		//if it's NOT valid
		if(strlen($address) < 5)
			return false;
		//if it's valid
		else
			return true;
	}
	
	function validateCity($city){
		return ereg("^[a-z,A-Z]+$", $city);
	}
	
	function validateZip($zip){
		//if it's NOT valid
		if(strlen($zip) < 4)
			return false;
		//if it's valid
		else
			return true;
	}
	
	function validateMobile($mobile){
		//if it's NOT valid
		if(strlen($mobile) < 11)
			return false;
		//if it's valid
		else
			return true;
	}
?>

