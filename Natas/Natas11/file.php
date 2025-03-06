<?
$cookie = "HmYkBwozJw4WNyAAFyB1VUcqOE1JZjUIBis7ABdmbU1GIjEJAyIxTRg%3D";

$defaultdata = array( "showpassword"=>"no", "bgcolor"=>"#ffffff");

// echo xor_encrypt(base64_decode($cookie), json_encode($defaultdata));die();
// echo "<br>";

function xor_encrypt($in1, $in2) {
  $key = $in2;
  $text = $in1;
  $outText = '';
  
  // Iterate through each character
  for($i=0;$i<strlen($text);$i++) {
    $outText .= $text[$i] ^ $key[$i % strlen($key)];
  }
  
  return $outText;
}

// $key = "DWoe";
$key = "eDWo";
$mydata = array( "showpassword"=>"yes", "bgcolor"=>"#ffffff");
echo base64_encode(xor_encrypt(json_encode($mydata), $key));
// base64_encode(xor_encrypt(json_encode($mydata), $key)); 
?>