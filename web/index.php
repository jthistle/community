<?php
	ini_set('display_errors', 'on');
	error_reporting(E_ALL);
	session_start();
	// generate random user id if not set
	if (! isset($_SESSION["userId"])){	
		$_SESSION["userId"] = bin2hex(random_bytes(30));
	}
	$userId = $_SESSION["userId"];
?>
<html>
	<head>
		<title>Community</title>
		<script src="https://ajax.googleapis.com/ajax/libs/jquery/3.3.1/jquery.min.js"></script>
		<link rel="stylesheet" href="https://ajax.googleapis.com/ajax/libs/jqueryui/1.12.1/themes/smoothness/jquery-ui.css">
		<script src="https://ajax.googleapis.com/ajax/libs/jqueryui/1.12.1/jquery-ui.min.js"></script>
		<script src="main.js"></script>
		<link rel="stylesheet" href="index.css">
	</head>
	<body>
		<h1>Community simulator</h1>
		<form>
			<input type="button" id="passTimeBtn" name="passTime" value="Pass time" />
		</form>
		<div id="mainContainer">
			<div id="communityEventLog">

			</div>
			<div id="personEventLog">

			</div>
		</div>
		<p id="debug" style="font-size: 1rem; color: green"></p>
		<p id="error" style="font-size: 1rem; color: red"></p>
		<p style='font-size: 0.8rem; color: grey'><?php echo $userId; ?></p>
	</body>
</html>