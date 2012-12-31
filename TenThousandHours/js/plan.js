function NewPlan(clickEvent){
	clickEvent.preventDefault();
	var postArray = new Array();
	postArray = {newPlan: $('[name=newPlan]').val() , planName: $('[name=planName]').val(), hour: $('[name=hour]').val(), comment: $('[name=comment]').val()};
	/*
	$.each(postArray, function(index, value){
		console.log("index:"+index +" value:" + value);
	});
	 */
	$.post("/TenThousandHours/MakePlan", postArray, 
		function (data){
			if (data.result == 1){
				$.each(data, function(index, value){
					console.log("index:"+index +" value:" + value);
				});
				//DrawPlan(postArray.planName, postArray.hour, 0);
			}else{
				alert("login first");
			}
		},
		"json");
}


function DrawPlan(planName, totalTime, spendTime){
	var planTag = $("<div id='" + planName + "' class='planItem'></div>");
	var sliderTag = $("<div id='" + planName + "Slider' class='slider'></div>");
	var minusTag = $("<div class='minusEdit'><button onclick='PlusHour(-1, \"#" + planName + "Slider\")'>-</button></div>");
	var plusTag = $("<div class='plusEdit'><button onclick='PlusHour(1, \"#" + planName + "Slider\")'>+</button></div>");
	planTag.append(minusTag);
	planTag.append(sliderTag);
	planTag.append(plusTag);
	
	$("#dynamicSliderRegion").append( planTag );
	var newSlider = $( "#" + planName + "Slider" ).slider({ min: 0, max: totalTime, value: 1});
	
}