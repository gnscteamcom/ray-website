<?php
session_start();
if (!isset($_SESSION['basic_is_logged_in']) 
    || $_SESSION['basic_is_logged_in'] !== true) {
    header('Location: login.php');
    exit;
}

?>
<?php
				
		$cur_page = htmlspecialchars($_GET["page"]);
		$cur_page = ($cur_page? $cur_page : 1);
		$search = htmlspecialchars($_GET["search"]);
	
		
	
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
		
		include '../lib/config.php';
		
		$dbconn = new DbConn($cchost,$ccuser,$ccpass,$ccname);
		define("DBH",$dbconn->conn);
		
		function get_table($result,$cur_page,$rows){
				
				$re = "";
				$i = 0;
				$start_i = ($cur_page-1)*25;
				
				while($i<25 and ($i+$start_i)<$rows){
					$l = $i + $start_i;
					$id = mysql_result($result,$l,"id");
					$name = mysql_result($result,$l,"short_url");
					$url = mysql_result($result,$l,"url");
					$lUrl = 0;
					if(strlen($url) > 50){
						$dUrl = $url;
						$url = substr($url,0,48).'...';
						
						$lUrl = 1; 
					}
					$created = mysql_result($result,$l,"created");
					$hits = mysql_result($result,$l,"hits");
					$re .= "\t<tr>\n";
					$re.= "\t\t<td>$id</td>\n";
					$re.= "\t\t<td>$name</td>\n";
					if($lUrl==0)
						$re.= "\t\t<td>$url</td>\n";
					else{
						$re.= "\t\t<td><a style=\"text-decoration:none; color:black;\" href=\"#\" title=\"$dUrl\" >$url</a></td>\n";
					}
					$re.= "\t\t<td>$created</td>\n";
					$re.= "\t\t<td>$hits</td>\n";
					$re.= "\t\t<td><a href=\"edit-entry.php?id=$id&page=$cur_page\"><i class=\"icon-pencil\"></i></a></td>\n";
					$re.= "\t\t<td><a href=\"#\" onclick=\"delete_entry($id,$cur_page);\"><i class=\"icon-trash\"></i></a></td>\n";
					$re.= "\t</tr>\n";
						
					$i+=1;
				}
				return $re;
		}
		function get_pager($cur_page,$rows){
			global $search;
			$pages = ceil(($rows+1)/25);
			$p1 = $cur_page-1;
			$p2 = $cur_page+1;
		
			$re= "<ul>\n";
			$re.= "<li ".($cur_page>1?  '' : 'class="active"')."><a href=".($cur_page>1? "index.php?page=$p1&search=$search":"#")." >&laquo;</a></li>\n";
				 
					if($cur_page==$pages && $pages>2){
						$l = $cur_page -2;
						$re.= "<li><a href=\"index.php?page=$l&search=$search\" \">$l</a></li>\n";
					}
					if($cur_page>1){
						$l = $cur_page -1;
						$re .= "<li><a href=\"index.php?page=$l&search=$search\" \">$l</a></li>\n";
					}
					
					$re .= "<li class=\"active\"><a href=\"#\" \">$cur_page</a></li>\n";
					if($pages>1){
						if($cur_page< $pages){
							$l = $cur_page+1;
							$re.= "<li><a href=\"index.php?page=$l&search=$search\"\">$l</a></li>\n";
						}
						if($cur_page==1 && $cur_page+2 <= $pages){
							$l = $cur_page+2;
							
							$re.= "<li><a href=\"index.php?page=$l&search=$search\" \">$l</a></li>\n";
						}
					}
				
				  
			$re.= "<li ".($pages==$cur_page? 'class="active"' : '')."><a href=".($pages!=$cur_page? "index.php?page=$p2&search=$search":"#").">&raquo;</a></li>\n";
			$re.= "</ul>";
			return $re;
		}
		
		function get_stats($search){
		
			if($search == ''){
					
				$query= "SELECT SUM(hits) AS total from urls";
				$result=  mysql_query($query, DBH);
				$t_hits = mysql_result($result,0,"total");
				$t_date = date('Y-m-d', time());
				$query= "SELECT COUNT(id) AS total from urls WHERE created='$t_date'";
				$result=  mysql_query($query,DBH);
				$n_urls = mysql_result($result,0,"total");
				$query="SELECT * FROM urls ORDER BY created DESC,id DESC ";
				$result = mysql_query($query,DBH);
				$rows =  mysql_num_rows($result);
				$re= "<div class=\"databox span3\"><span>Total Hits</span><h1>$t_hits</h1></div>";

				$re.="<div class=\"databox span3\"><span>Totoal Urls</span><h1>$rows</h1></div>";

				$re.="<div class=\"databox span3\"><span>New Urls Today</span><h1>$n_urls</h1></div>";
				
				return $re;
				
			}
			else{
				
				$query= "SELECT SUM(hits) AS total from urls WHERE ( id LIKE '%$search%' OR short_url LIKE '%$search%' OR url LIKE '%$search%')";
				$result=  mysql_query($query, DBH);
				$t_hits = mysql_result($result,0,"total");
				$t_date = date('Y-m-d', time());
				$query= "SELECT COUNT(id) AS total from urls WHERE created='$t_date' AND ( id LIKE '%$search%' OR short_url LIKE '%$search%' OR url LIKE '%$search%') ";
				$result=  mysql_query($query,DBH);
				$n_urls = mysql_result($result,0,"total");
				
				$query="SELECT * FROM urls WHERE ( id LIKE '%$search%' OR short_url LIKE '%$search%' OR url LIKE '%$search%') ORDER BY created DESC,id DESC ";
				$result = mysql_query($query,DBH);
				$rows =  mysql_num_rows($result);
				
				$re= "<div class=\"databox span3\"><span>Total Hits</span><h1>$t_hits</h1></div>\n";

				$re.="<div class=\"databox span3\"><span>Totoal Urls</span><h1>$rows</h1></div>\n";

				$re.="<div class=\"databox span3\"><span>New Urls Today</span><h1>$n_urls</h1></div>\n";
				
				return $re;
			
			}
		}
		if($search == ''){
				
				
				
				$query="SELECT * FROM urls ORDER BY created DESC,id DESC ";
				$result = mysql_query($query,DBH);
				$rows =  mysql_num_rows($result);
				
			
				$table = get_table($result,$cur_page,$rows);
				$pager = get_pager($cur_page,$rows);
				$stats = get_stats('');
				
				echo json_encode(array("table"=>$table,"pager"=>$pager,"stats"=>$stats));
				
		}
		else{
				
				
				
				
				$query="SELECT * FROM urls WHERE ( id LIKE '%$search%' OR short_url LIKE '%$search%' OR url LIKE '%$search%') ORDER BY created DESC,id DESC ";
				$result = mysql_query($query,DBH);
				$rows =  mysql_num_rows($result);
			
				$table = get_table($result,$cur_page,$rows);
				$pager = get_pager($cur_page,$rows);
				$stats = get_stats($search);
				
				echo json_encode(array("table"=>$table,"pager"=>$pager,"stats"=>$stats));
			
		}
		
		
?>
