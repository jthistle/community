function runCommand(command, args, handleData) {
	var response;
	jQuery.ajax({
			type: "POST",
			url: 'action.php',
			dataType: 'json',
			data: {command: command, arguments: args},

			success: function (obj, textstatus) {
						if( !('error' in obj) ) {
							handleData(obj); // run callback
						} else {
							console.log(obj.error);
						}
					}
			});
}


$( document ).ready(function(){
	function doDebug(response){
		if (response["responseType"] == "error"){
			$(" #error ").text(response["value"]);
			console.error(response["value"]);
		} else if (response["responseType"] == "information"){
			$(" #debug ").text(response["value"]);
			console.log(response["value"]);
		} else{
			$(" #debug ").text("got response of type "+response["responseType"]);
			console.log(response["value"]);
		}
	};

	updateDisplay = function(){
		runCommand("getCommunityLog", ["latest"], function(response){
			doDebug(response);
			$(" #communityEventLog ").html(response["value"].join("<br />"));
		});

		runCommand("getPersonLog", ["latest"], function(response){
			doDebug(response);
			$(" #personEventLog ").html(response["value"].join("<br />"));
		});
	};

	updateDisplay();

	$(" #passTimeBtn ").bind("click", function(){
		runCommand("passTime", [], function(response){
			console.log("test");
			doDebug(response);
			updateDisplay();
		});
	});
});
