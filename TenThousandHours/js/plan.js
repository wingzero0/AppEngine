function NewPlan(clickEvent){
	clickEvent.preventDefault();
	var postArray = new Array();
	postArray = {newPlan: $('[name=newPlan]').val() , planName: $('[name=planName]').val(), totalTime: $('[name=hour]').val(), comment: $('[name=comment]').val()};
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
				DrawPlan("plan" + data.id, postArray.planName , postArray.totalTime, 0);
			}else{
				alert("login first");
			}
		},
		"json");
}

function PlusHour(hourChange, planID){
	var sliderObj = $("#slider" +planID);
	var spendHour = sliderObj.slider("option", "value");
	sliderObj.slider("option", "value", spendHour + hourChange);
	
	$("#" + planID).attr("changed", 1);
}


function DrawPlan(planID, planName, totalTime, spendTime){
	var planTag = $("<div id='" + planID + "' class='planItem' changed=0>" + "</div>");
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
		//PlusHour(-1, "slider"+planID);
		PlusHour(-1, planID);
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
		//PlusHour(1, "slider"+planID);
		PlusHour(1, planID);
	});
	plusTag.append(plusButton);
	
	// final aggregate 
	planTag.append(minusTag);
	planTag.append(sliderTag);
	planTag.append(plusTag);
	
	$("#dynamicSliderRegion").append( planName );
	$("#dynamicSliderRegion").append( planTag );
	
	planList.push(planID);
}

function GetUserPlans(){
	var postArray = new Array();
	postArray = {"op": "userPlans"};
	$.get("/TenThousandHours/GetPlan", postArray, 
		function (data){
			if (data.result == 1){
				$.each(data.plans, function(index, plan){
					$.each(plan, function(field, value){
						console.log("index:"+index + " field:" + field +" value:" + value);
					});
					DrawPlan("plan" + plan.id, plan.planName , plan.totalTime, plan.spentTime);
				});
			}else{
				alert("login first");
			}
		},
		"json");
	
}

var timer = null; 
var planList = [];


var updateTimer = function () {
    //do stuff

    // By the way, can just pass in the function name instead of an anonymous
    // function unless if you want to pass parameters or change the value of 'this'
	SaveChanged();
    timer = setTimeout(updateTimer, 10000);
};

function SaveChanged(){
	DebugOutput("Saving Changed");
	$.each(planList, function (index, planID){
		var changed = $("#" + planID).attr("changed");
		if (changed == 0){
			DebugOutput(index + ":" + planID + ":" + changed);
		}else{
			DebugOutput(index + ":" + planID);
		}
	});
}

function DebugOutput(data){
	if ($.browser.chrome){
		console.log(data);
	}
}