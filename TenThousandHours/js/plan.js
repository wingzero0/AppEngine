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
				DrawPlan("plan" + data.id, postArray.planName , postArray.hour, 0);
			}else{
				alert("login first");
			}
		},
		"json");
}

function PlusHour(hourChange, sliderID){
	var sliderObj = $("#" + sliderID);
	var spendHour = sliderObj.slider("option", "value");
	sliderObj.slider("option", "value", spendHour + hourChange);
}


function DrawPlan(planID, planName, totalTime, spendTime){
	var planTag = $("<div id='" + planID + "' class='planItem'>" + "</div>");
	var sliderTag = $("<div />", {
		"id": "slider" + planID,
		"class": "slider"
	});
	sliderTag.slider({ "min": 0, "max": totalTime, "value": spendTime});
	
	// button minus
	var minusTag = $("<div />", {"class": "minusEdit"} );
	var minusButton = $("<button />");
	minusButton.button({
		icons: { primary: "ui-icon-triangle-1-w" },
		text: false
	})
	.click(function(){
		PlusHour(-1, "slider"+planID);
	});
	minusTag.append(minusButton);
	
	// button plus
	//var plusTag = $("<div />", {"class": "plusEdit"} );
	var plusTag = $("<div />" );
	var plusButton = $("<button />");
	plusButton.button({
		icons: { primary: "ui-icon-triangle-1-e" },
		text: false
	})
	.click(function(){
		PlusHour(1, "slider"+planID);
	});
	plusTag.append(plusButton);
	
	// final aggregate 
	planTag.append(minusTag);
	planTag.append(sliderTag);
	planTag.append(plusTag);
	
	$("#dynamicSliderRegion").append( planName );
	$("#dynamicSliderRegion").append( planTag );
}

