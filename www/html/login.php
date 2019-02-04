<html>
<head>
<link rel="stylesheet" href="style.css">
</head>
<body>
  <div id="bg">
<?php
#ini_set('display_errors', 1);
#error_reporting(E_ALL);
if(isset($_POST["username"]) and $_POST["username"] != "" and $_POST["username"] != "root" and isset($_POST["pass"]) and $_POST["pass"] != ""){
   $user = $_POST["username"];
   $pass = $_POST["pass"];
   $token = $_POST["token"];

   if (file_exists('tokens.xml')){
      $xml = simplexml_load_file("tokens.xml");
   }
   else{
      echo "<script type='text/javascript'> alert(\"tokens.xml  doesnt exist\");</script>";
   }
   if(!$xml){
      echo "<script type='text/javascript'> alert(\"Error: Can't load tokens.xml\");</script>";
   }
   else{
      $saved_token = $xml->xpath("//tokens/tokenset[./token='" . $token . "']");
      if($saved_token[0]){
         $xml = simplexml_load_file("credentials.xml");
         $u = $xml->addChild('user');
         $chat = $u->addChild('chat', $saved_token[0]->chat);
         $username = $u->addChild('username', $user);
         $password = $u->addChild('password', $pass);

         if (is_writable("credentials.xml")){
            $domxml = new DOMDocument('1.0');
	    $domxml->preserveWhiteSpace = false;
	    $domxml->formatOutput = true;
            $domxml->loadXML($xml->asXML());
	    $domxml->save('credentials.xml');

            $xml = simplexml_load_file("tokens.xml");
            foreach ($xml->children() as $tokenset) {
               if ($tokenset->token == $token) {	
                  $dom=dom_import_simplexml($tokenset);
 		  $dom->parentNode->removeChild($dom);          
               }
	    }
				
	    $domxml = new DOMDocument('1.0');
	    $domxml->preserveWhiteSpace = false;
	    $domxml->formatOutput = true;
	    $domxml->loadXML($xml->asXML());
	    $domxml->save('tokens.xml');            
	 
            echo "<script type='text/javascript'> alert(\"Correctly logged in\")</script>";
            echo "<script type='text/javascript'> window.close();</script>";
          }
          else{
            echo "<script type='text/javascript'> alert(\"Cannot write to file. Insufficient permissions.\")</script>";
          }
      }
      else{
         echo "<script type='text/javascript'>alert('Invalid token. Use /on command in the telegram bot to generate a new one.')</script>";
      }
   }
}
else{
   echo "
    <form action=\"login.php\" method=\"post\">
      <input id=\"username\" name=\"username\" type=\"text\" placeholder=\"name\" class=\"email\" value=\"" . $_POST["username"] . "\"/>";
   if (isset($_POST["username"]) and $_POST["username"] == ""){
      echo "<label style=\"color:red\">Username cannot be blank</label>";
   }
   elseif (isset($_POST["username"]) and $_POST["username"] == "root"){
      echo "<label style=\"color:red\">Username cannot be root</label>";
   }
   echo "
      </br>
      <input id=\"pass\" name=\"pass\" type=\"password\" placeholder=\"password\" class=\"pass\" value=\"" . $_POST["pass"] . "\"/>";
   if (isset($_POST["pass"]) and $_POST["pass"] == ""){
      echo "<label style=\"color:red\">Password cannot be blank</label>";
   }

   echo "   <input id=\"token\" name=\"token\" type=\"hidden\" value=\"" . $_GET["token"] . $_POST["token"] . "\"/>

    </br>
      <button type=\"submit\">Login</button>
   </form>";
}
?>
  </div>
</body>
</html>

