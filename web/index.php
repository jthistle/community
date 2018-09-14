
<html>
	<head>
		<title>Community</title>
	</head>
	<body>
		<h1>Community simulator</h1>
<?php
	ini_set('display_errors', 'on');
	error_reporting(E_ALL);

	session_start();

	function cmd($userId, $cmd){
		$BASE_DIR = "/var/www/html/com/web.py";
		$command = escapeshellcmd("$BASE_DIR $userId $cmd");
		$response = shell_exec($command);
		return $response;
	}

	// generate random user id if not set
	if (! isset($_SESSION["userId"])){	
		$_SESSION["userId"] = bin2hex(random_bytes(30));
	}
	$userId = $_SESSION["userId"];

	//$response = cmd($userId, "clear");
	$response = cmd($userId, "init");
	$response = cmd($userId, "getCommunityLog");

	$decoded = json_decode($response, true);
	foreach ($decoded as $event){
		echo "$event<br />";
	}

	echo "<p style='font-size: 1rem; color: green'>$response</p>";
	echo "<p style='font-size: 0.8rem; color: grey'>$userId</p>";
?>
	</body>
</html>