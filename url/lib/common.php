<?php
session_start();
$config = array();
$config['db_hostname'] = $cchost;
$config['db_username'] = $ccuser;
$config['db_password'] = $ccpass;
$config['db_name'] = $ccname;


/* Do not edit unless you know what you are doing. */
$config['valid'] = true;  
$config['rewrite'] = true;
$config['domain'] = str_replace("http://","",$config['domain']);
$_SESSION['config'] = $config;



class DbConn {
	public $conn;
	public function __construct($host,$user,$pass,$db) {
		$this->conn = mysql_connect($host, $user, $pass) or die("Couldn't connection to $host");
		mysql_select_db($db,$this->conn);
	}
	public function __destruct(){
		mysql_close($this->conn);
	}
}
$dbconn = new DbConn($_SESSION['config']['db_hostname'],$_SESSION['config']['db_username'],$_SESSION['config']['db_password'],$_SESSION['config']['db_name']);
define("DBH",$dbconn->conn);

$config_location = str_replace("http://","",$config_location);
$config_con = mysql_query("SELECT name,length,location,bar,analytics FROM settings",DBH) or die(mysql_error());	
$config_row = mysql_fetch_assoc($config_con);
$config_name = $config_row['name'];
$config_location = $config_row['location'];
$config_length = $config_row['length'];
$config_bar = $config_row['bar'];
$config_analytics = $config_row['analytics'];

function shortenit($url,$custom=""){
	$retVal = "";
    if ($url{strlen($url) - 1} == "/") $url = substr($url, 0, -1);
    if (!preg_match("/^(ht|f)t(p|ps)\:\/\//si", $url)) $url = "http://".$url;
    $length = strlen($url);
    $count  = 0;
	if( !empty($custom) ){
		$customyn = "Y";
		$short_url = str_replace(" ","",$custom);
		$suffix = $short_url{0};
		$sql = "INSERT INTO urls (short_url, url, created, time, custom) VALUES ('$short_url', '".mysql_real_escape_string($url)."', NOW(), NOW(),'{$customyn}')";
		mysql_query($sql,DBH) or die("<br/><h2>This name is already taken please choose another one.</h2> ");
		$id = mysql_insert_id();
	}else{
		$customyn = "N";
		$short_url = generate_url();
		$suffix = $short_url{0};
	    do {
			$customyn = "N";
	        $short_url = generate_url();
			$suffix = $short_url{0};
	        $result = mysql_query("SELECT id,url, short_url FROM urls WHERE short_url = '$short_url' OR url = '$url'",DBH) or die(mysql_error());
	        $count  = mysql_num_rows($result);
	        if ($count > 0) {
	            $row = mysql_fetch_assoc($result);
	            if (stripslashes($row['url']) == $url) {
					$short_url = $row['short_url'];
					$id = $row['id'];
	                break;
	            }
	        }else {
				$sql = "INSERT INTO urls (short_url, url, created, time, custom) VALUES ('$short_url', '".mysql_real_escape_string($url)."', NOW(), NOW(),'{$customyn}')";
	            mysql_query($sql,DBH) or die(mysql_error());
				$id = mysql_insert_id();
	            break;
	        }
	    } while ($count > 0);
	}
	mysql_close();
	return $short_url;
}


function generate_url() {
	$keys = "23456789";
    $i    = 0;
    $url  = "";
    global $config_length;
    while ($i < $config_length ) {
      $random = mt_rand(0, strlen($keys) - 1);
      $url   .= $keys{$random};
      $i++;
    }
    return $url;
}


function selfURL() {
	$s = empty($_SERVER["HTTPS"]) ? '' : ($_SERVER["HTTPS"] == "on") ? "s" : "";
	$protocol = strleft(strtolower($_SERVER["SERVER_PROTOCOL"]), "/").$s;
	$port = ($_SERVER["SERVER_PORT"] == "80") ? "" : (":".$_SERVER["SERVER_PORT"]);
	return $protocol."://".$_SERVER['SERVER_NAME'].$port.$_SERVER['REQUEST_URI'];
}
function strleft($s1, $s2) { return substr($s1, 0, strpos($s1, $s2));}


	
function onlyNumbers($string){
	$string = preg_replace("/[^0-9]/", "", $string);
	return (int) $string;
} 	
function isInteger($input){
	return preg_match('@^[-]?[0-9]+$@',$input) === 1;
}
function isValidUrl($url){
	if( $_SESSION['config']['valid'] == false){
		return ( ! preg_match('/^(http|https|ftp):\/\/([A-Z0-9][A-Z0-9_-]*(?:\.[A-Z0-9][A-Z0-9_-]*)+):?(\d+)?\/?/i', $url)) ? FALSE : TRUE;
	} else {
		return true;
	}
}

function get_headers_curl($url){
	$ch = curl_init();
	curl_setopt($ch, CURLOPT_URL,            $url);
	curl_setopt ($ch, CURLOPT_USERAGENT,	'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-US; rv:1.8.1.9) Gecko/20071025 Firefox/2.0.0.9');
	curl_setopt($ch, CURLOPT_HEADER,         true);
	curl_setopt($ch, CURLOPT_VERBOSE,        false);
	curl_setopt($ch, CURLOPT_NOBODY,         true);
	curl_setopt($ch, CURLOPT_RETURNTRANSFER, true);
	curl_setopt($ch,CURLOPT_SSL_VERIFYPEER, FALSE);
	curl_setopt($ch,CURLOPT_SSLVERSION,3);
	curl_setopt($ch,CURLOPT_SSL_VERIFYHOST, FALSE);		
	curl_setopt($ch, CURLOPT_TIMEOUT,        5);
	$httpcode = curl_getinfo($ch, CURLINFO_HTTP_CODE);
	return $httpcode[0];
}



function plural($num) {
	if ($num != 1)
		return "s";
}




function getRelativeTime($date) {
	return TimeAgoInWords( strtotime($date) );

}

function TimeAgoInWords($from_time, $include_seconds = true) {
	$to_time = time();
	$mindist = round(abs($to_time - $from_time) / 60);
	$secdist = round(abs($to_time - $from_time));
	if ($mindist >= 0 and $mindist <= 1) {
		if (!$include_seconds) {
			return ($mindist == 0) ? 'less than a minute' : '1 minute';
		} else {
			if ($secdist >= 0 and $secdist <= 4) {
				return 'less than 5 seconds';
			} elseif ($secdist >= 5 and $secdist <= 9) {
				return 'less than 10 seconds';
			} elseif ($secdist >= 10 and $secdist <= 19) {
				return 'less than 20 seconds';
			} elseif ($secdist >= 20 and $secdist <= 39) {
				return 'half a minute';
			} elseif ($secdist >= 40 and $secdist <= 59) {
				return 'less than a minute';
			} else {
				return '1 minute';
			}
		}
	} elseif ($mindist >= 2 and $mindist <= 44) {
		return $mindist . ' minutes';
	} elseif ($mindist >= 45 and $mindist <= 89) {
		return 'about 1 hour';
	} elseif ($mindist >= 90 and $mindist <= 1439) {
		return 'about ' . round(floatval($mindist) / 60.0) . ' hours';
	} elseif ($mindist >= 1440 and $mindist <= 2879) {
		return '1 day';
	} elseif ($mindist >= 2880 and $mindist <= 43199) {
		return 'about ' . round(floatval($mindist) / 1440) . ' days';
	} elseif ($mindist >= 43200 and $mindist <= 86399) {
		return 'about 1 month';
	} elseif ($mindist >= 86400 and $mindist <= 525599) {
		return round(floatval($mindist) / 43200) . ' months';
	} elseif ($mindist >= 525600 and $mindist <= 1051199) {
		return 'about 1 year';
	} else {
		return 'over ' . round(floatval($mindist) / 525600) . ' years';
	}
}	


function settingsdb($settingsquery) {
	
	$result = mysql_query("SELECT * FROM settings",DBH) or die(mysql_error());  
	$row = mysql_fetch_assoc($result);
	return $row[$settingsquery];

}



	
?>
