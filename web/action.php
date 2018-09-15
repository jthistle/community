<?php
	ini_set('display_errors', 'on');
	error_reporting(E_ALL);
	session_start();

	try {
		$response = json_encode([
			"responseType" => "error",
			"value" => "couldn't execute command"
		]);

		function cmd($userId, $cmd, $args){
			$argText = implode(" ", $args);
			$BASE_DIR = "/var/www/html/com/web.py";
			$command = escapeshellcmd("$BASE_DIR $userId $cmd $argText");
			$response = shell_exec($command);
			return $response;
		}

		$userId = $_SESSION["userId"];

		cmd($userId, "init", []);

		if (isset($_POST["command"])){
			$commandName = $_POST["command"];
			if (isset($_POST["arguments"])){
				$args = $_POST["arguments"];
			} else{
				$args = [];
			}
			$response = cmd($userId, $commandName, $args);
		}
	}
	catch(Exception $e) {
		echo $e->getMessage();
		$response = json_encode([
			"responseType" => "error",
			"value" => $e->getMessage()
		]);
	}
	echo $response;
?>