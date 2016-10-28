<?php

// configure
$from = 'Demo contact form <demo@domain.com>'; //the email address that will be in the From field of the email. Important: To avoid being marked as spam, use email on your domain
$sendTo = 'entertainmentmaple@gmail.com'; //the email address that will receive the email with the output of the form. Can be your personal address or can be same as the address as in $from variable. Make sure this email exists.
$subject = 'New message from contact form'; //the subject of the email
$fields = array('name' => 'Name', 'email' => 'Email', 'subject' => 'Subject', 'phone' => 'Phone', 'message' => 'Message'); // array variable name => Text to appear in email
$okMessage = 'Contact form successfully submitted. Thank you, I will get back to you soon!'; //the message text displayed on the web page when the message is successfully sent
$errorMessage = 'There was an error while submitting the form. Please try again later'; //the message text displayed on the web page when the message is error

// let's do the sending

try
{
    $emailText = "You have new message from contact form\n=============================\n";

    foreach ($_POST as $key => $value) {

        if (isset($fields[$key])) {
            $emailText .= "$fields[$key]: $value\n";
        }
    }

    mail($sendTo, $subject, $emailText, "From: " . $from);

    $responseArray = array('type' => 'success', 'message' => $okMessage);
}
catch (\Exception $e)
{
    $responseArray = array('type' => 'danger', 'message' => $errorMessage);
}

if (!empty($_SERVER['HTTP_X_REQUESTED_WITH']) && strtolower($_SERVER['HTTP_X_REQUESTED_WITH']) == 'xmlhttprequest') {
    $encoded = json_encode($responseArray);
    
    header('Content-Type: application/json');
    
    echo $encoded;
}
else {
    echo $responseArray['message'];
}