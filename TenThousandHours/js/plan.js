function NewPlan(clickEvent){
	clickEvent.preventDefault();
	var postArray = new Array();
	//postArray = {op: $('[name=op]').val() , planName: $('[name=planName]').val(), totalTime: $('[name=hour]').val(), comment: $('[name=comment]').val()};
	postArray = {op: "newPlan" , planName: $('[name=planName]').val(), totalTime: $('[name=hour]').val(), comment: $('[name=comment]').val()};
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
	if (sliderObj.slider("option", "disabled")) return;
	
	var spendHour = sliderObj.slider("option", "value");
	sliderObj.slider("option", "value", spendHour + hourChange);
	//$("#" + planID).attr("changed", 1);
}


function DrawPlan(planID, planName, totalTime, spentTime){
	var planTag = $("<div id='" + planID + "' class='planItem' changed=0>" + "</div>");
	var sliderTag = $("<div />", {
		"id": "slider" + planID,
		"class": "slider"
	});
	sliderTag.slider({ 
			"min": 0, 
			"max": totalTime, 
			"value": spentTime, 
			"range":"min",
			"change" : function (){ $("#" + planID).attr("changed", 1); } 
		});
	
	// button minus
	var minusButton = $("<button />");
	minusButton.button({
		icons: { primary: "ui-icon-triangle-1-w" },
		text: false
	})
	.click(function(){
		//PlusHour(-1, "slider"+planID);
		PlusHour(-1, planID);
	});
	
	// button plus
	var plusButton = $("<button />");
	plusButton.button({
		icons: { primary: "ui-icon-triangle-1-e" },
		text: false
	})
	.click(function(){
		//PlusHour(1, "slider"+planID);
		PlusHour(1, planID);
	});
	
	// final aggregate 
	planTag.append(minusButton);
	planTag.append(sliderTag);
	planTag.append(plusButton);
	
	$("#dynamicSliderRegion").append( planName );
	$("#dynamicSliderRegion").append( planTag );
	
	planList.push(planID);
	
	minusButton.position({my:"center center", at: "left center", of: planTag});
	sliderTag.position({my:"center center", at: "center center", of: planTag});
	plusButton.position({my:"center center", at: "right center", of: planTag});
	
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
    timer = setTimeout(updateTimer, 5000);
};

function SaveChanged(){
	// 1. disable all buttons and sliders
	// 2. upload value if "changed" is set
	// 3. enable all buttons and sliders
	DebugOutput("Saving Changed");
	// disable
	//var updateList = new Array();
	var updateList = {};
	var i = 0;
	$.each(planList, function (index, planID){
		var sliderID = "#slider" + planID;
		$(sliderID).slider("disable");
		var changed = $("#" + planID).attr("changed");
		if (changed == 0){
			DebugOutput(index + ":" + planID);
		}else{
			//var planObj = new Object();
			//planObj.ID = planID;
			//planObj.spentTime = $(sliderID).slider("value");
			//updateList.push(planObj);
			
			updateList["id" + i] = planID;
			updateList["spentTime" + i] = $(sliderID).slider("value");
			DebugOutput(index + ":" + planID + ":" + updateList["spentTime" + i]);
			i++;
		}
	});
	//upload
	if (i > 0){
		//updateList use as postArray
		updateList["num"] = i;
		updateList["op"] = "update";
		$.post("/TenThousandHours/MakePlan", updateList, 
			function (data){
				if (data.result == 1){
					DebugOutput("update finish");
				}else{
					alert(data.errorMessage);
				}
			},
			"json");
	}
	//enable
	$.each(planList, function (index, planID){
		var sliderID = "#slider" + planID;
		$(sliderID).slider("enable");
		$("#" + planID).attr("changed", 0);
	});
}

function DebugOutput(data){
	if ($.browser.chrome){
		console.log(data);
	}
}