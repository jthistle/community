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

	var currentFamilyInd = 0;
	var currentPersonInd = null;

	updateDisplay = function(){
		runCommand("getFamilies", [], function(response){
			doDebug(response);
			$(" #familyList ").html("");
			response["value"].forEach(function(el){
				$(" #familyList ").append("<div class='family'><span>"+el+"</span></div>");
			});
			$
		});

		runCommand("getPeople", [currentFamilyInd], function(response){
			doDebug(response);
			$(" #personList ").html("");
			response["value"].forEach(function(el){
				$(" #personList ").append("<div class='person'><span>"+el+"</span></div>");
			});
			$
		});

		if (currentPersonInd != null){
			runCommand("inspectPerson", [currentFamilyInd, currentPersonInd], function(response){
				doDebug(response);
				inspection = response["value"];
				personName = inspection["name"];
				attributes = inspection["attributes"];
				flavour = inspection["flavour"].split("\n").join("<br />");
				$(" #inspector ").html("");
				$(" #inspector ").append("<div id='heading'>"+personName+"</div>");
				$(" #inspector ").append("<div id='content'>"+flavour+"</div>");
			});

			runCommand("getPersonLog", [currentFamilyInd, currentPersonInd, "latest"], function(response){
				doDebug(response);
				$(" #personEventLog ").html(response["value"].join("<br />"));
			});
		}

		runCommand("getCommunityLog", ["latest"], function(response){
			doDebug(response);
			$(" #communityEventLog ").html(response["value"].join("<br />"));
		});
	};

	updateDisplay();

	$(" #passTimeBtn ").on("click", function(){
		runCommand("passTime", [], function(response){
			doDebug(response);
			updateDisplay();
		});
	});

	$(" #familyList ").on("click", ".family", function(){
		currentFamilyInd = $(this).index();
		currentPersonInd = null;
		updateDisplay();
	});

	$(" #personList ").on("click", ".person", function(){
		currentPersonInd = $(this).index();
		updateDisplay();
	});
});
