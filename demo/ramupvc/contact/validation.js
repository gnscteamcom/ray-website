/***************************/
//@Author: Adrian "yEnS" Mato Gondelle & Ivan Guardado Castro
//@website: www.yensdesign.com
//@email: yensamg@gmail.com
//@license: Feel free to use it, but keep this credits please!					
/***************************/

$(document).ready(function(){
	//global vars
	var form = $("#customForm");
	var name = $("#name");
	var nameInfo = $("#nameInfo");
	var email = $("#email");
	var emailInfo = $("#emailInfo");
	var address = $("#address");
	var addressInfo = $("#addressInfo");
	var city = $("#city");
	var cityInfo = $("#cityInfo");
	var zip = $("#zip");
	var zipInfo = $("#zipInfo");
	var mobile = $("#mobile");
	var mobileInfo = $("#mobileInfo");
	var message = $("#message");
	
	//On blur
	name.blur(validateName);
	email.blur(validateEmail);
	address.blur(validateAddress);
	city.blur(validateCity);
	zip.blur(validateZip);
	mobile.blur(validateMobile);
	//On key press
	name.blur(validateName);
	email.blur(validateEmail);
	address.blur(validateAddress);
	city.blur(validateCity);
	zip.blur(validateZip);
	mobile.blur(validateMobile);
	//On Submitting
	form.submit(function(){
		if(validateName() & validateEmail() & validateAddress() & validateCity() & validateZip() & validateMobile() & validateMessage())
			return true
		else
			return false;
	});
	
	//validation functions
	function validateEmail(){
		//testing regular expression
		var a = $("#email").val();
		var filter = /^[a-zA-Z0-9]+[a-zA-Z0-9_.-]+[a-zA-Z0-9_-]+@[a-zA-Z0-9]+[a-zA-Z0-9.-]+[a-zA-Z0-9]+.[a-z]{2,4}$/;
		//if it's valid email
		if(filter.test(a)){
			email.removeClass("error");
			emailInfo.text("Valid E-mail please, you will need it to log in!");
			emailInfo.removeClass("error");
			return true;
		}
		//if it's NOT valid
		else{
			email.addClass("error");
			emailInfo.text("Invalid E-mail!");
			emailInfo.addClass("error");
			return false;
		}
	}
	function validateName(){
		//if it's NOT valid
		if(name.val().length < 4){
			name.addClass("error");
			nameInfo.text("We want names with more than 3 letters!");
			nameInfo.addClass("error");
			return false;
		}
		//if it's valid
		else{
			name.removeClass("error");
			nameInfo.text("What's your name?");
			nameInfo.removeClass("error");
			return true;
		}
	}
	
	function validateAddress(){
		//if it's NOT valid
		if(address.val().length < 5){
			address.addClass("error");
			addressInfo.text("We need your address!");
			addressInfo.addClass("error");
			return false;
		}
		//if it's valid
		else{
			address.removeClass("error");
			addressInfo.text("What's your address?");
			addressInfo.removeClass("error");
			return true;
		}
	}
	
	function validateCity(){
		//if it's NOT valid
		var b = $("#city").val();
		var filter2 = /^[a-z,A-Z]{3,}$/;
		//if it's valid city
		if(filter2.test(b)){
			city.removeClass("error");
			cityInfo.text("Valid City!");
			cityInfo.removeClass("error");
			return true;
		}
		//if it's NOT valid
		else{
			city.addClass("error");
			cityInfo.text("Invalid City!");
			cityInfo.addClass("error");
			return false;
		}
	}
	
	function validateZip(){
		var c = $("#zip").val();
		var filter3 = /^[0-9]{4,5}$/;
		//if it's valid zip
		if(filter3.test(c)){
			zip.removeClass("error");
			zipInfo.text("Valid ZIP Code");
			zipInfo.removeClass("error");
			return true;
		}
		//if it's NOT valid
		else{
			zip.addClass("error");
			zipInfo.text("Invalid ZIP Code");
			zipInfo.addClass("error");
			return false;
		}
	}
	
	function validateMobile(){
		var f = $("#mobile").val();
		var filter6 = /^[0-9]{11,14}$/;
		//if it's valid mobile
		if(filter6.test(f)){
			mobile.removeClass("error");
			mobileInfo.text("Valid Phone Number");
			mobileInfo.removeClass("error");
			return true;
		}
		//if it's NOT valid
		else{
			mobile.addClass("error");
			mobileInfo.text("Invalid Phone Number!");
			mobileInfo.addClass("error");
			return false;
		}
	}
	
	function validateMessage(){
		//it's NOT valid
		if(message.val().length < 10){
			message.addClass("error");
			return false;
		}
		//it's valid
		else{			
			message.removeClass("error");
			return true;
		}
	}
});