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
		<link rel="stylesheet" href="index.css?<?php echo time(); ?>">
	</head>
	<body>
		<h1>Community simulator</h1>
		<form>
			<input type="button" id="passTimeBtn" name="passTime" value="Pass time" />
		</form>
		<div id="mainContainer">
			<div class="row">
				<div id="familyListContainer">
					<span class="listLabel">Families</span>
					<div id="familyList">
						<div class="family">
							<span>Test Family</span>
						</div>
						<div class="family">
							<span>Test Family</span>
						</div>
						<div class="family">
							<span>Test Family</span>
						</div>
					</div>
				</div>
				<div id="personListContainer">
					<span class="listLabel">People</span>
					<div id="personList">
						<div class="person">
							<span>Test Person</span>
						</div>
						<div class="person">
							<span>Test Person</span>
						</div>
						<div class="person">
							<span>Test Person</span>
						</div>
					</div>
				</div>
				<div id="inspectorContainer">
					<span class="listLabel">Inspector</span>
					<div id="inspector">
						<div id="heading">
							No person selected
						</div>
						<div id="content">
							Pick a person to get started.
						</div>
					</div>
				</div>
			</div>
			<div class="row">
				<div id="communityEventLog">
					Loading...
				</div>
				<div id="personEventLog">
					No person selected.
				</div>
			</div>
		</div>
		<p id="debug"></p>
		<p id="error"></p>
		<p id="userId"><?php echo $userId; ?></p>
	</body>
</html>