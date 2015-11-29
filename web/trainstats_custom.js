google.load('visualization', '1.1', {packages: ['corechart', 'bar']});

// *************************************************************
// Utility Functions For Graphs, etc.
// *************************************************************
var trainData = [];
trainData[0] = ['Train', 'Ontime or less than 5 minutes late', 'between 5 and 30 minutes late', '30 or more minutes late', { role: 'annotation' } ];



function drawStackedTripDelaysByTrain() {
	var data = google.visualization.arrayToDataTable(trainData);

	var options = {
		isStacked: 'percent',
		height: 450,
		backgroundColor: '#f8f8f8',
		legend: {position: 'top', alignment: 'center', maxLines: 3},
		hAxis: {
			title: 'Train Number',
		},
		vAxis: {
			title: 'Percentage of Trips'
		},
		chartArea:{left:60,top:30,width:"100%",height:350},
		colors: ['#FFD569', '#FEBA0D', '#A07300'],

		fontName: 'Montserrat',
		fontSize: 14,

	};

	var dailyTripDelaysChart = new google.visualization.ColumnChart(document.getElementById('dailyTripDelaysGraph'));

	dailyTripDelaysChart.draw(data, options);
}

function addDataCallback(e) {
	trainData.push(['Train ' + e['train_number'], e[0], e[10], e[30], '']);
}

function arrangeTrainBucketData(originStation, destStation) {
	var allTrains = getTrainsByRoute(originStation, destStation);
	var deferred = [];
	for (var i = 0; i < allTrains.length; i++) {
		deferred.push(getDelaysAtStation(allTrains[i], destStation, 180, addDataCallback));
	}
	$.when.apply($, deferred).then(function() {
		drawStackedTripDelaysByTrain();
	});
}


// From the same stackoverflow as always: http://stackoverflow.com/a/901144
function getParameterByName(name) {
	name = name.replace(/[\[]/, "\\[").replace(/[\]]/, "\\]");
	var regex = new RegExp("[\\?&]" + name + "=([^&#]*)"),
	results = regex.exec(location.search);
	return results === null ? "" : decodeURIComponent(results[1].replace(/\+/g, " "));
}

function toTitleCase(str)
{
	return str.replace(/\w\S*/g, function(txt){return txt.charAt(0).toUpperCase() + txt.substr(1).toLowerCase();});
}

function scrollToAnchor(aid){
    var aTag = $("a[name='"+ aid +"']");
    $('html,body').animate({scrollTop: aTag.offset().top},'slow');
}


// *************************************************************
// Helper Functions / Controllers of Page Content
// *************************************************************

function loadTripDelaysByTrain(originStation, destStation) {
  // getting the data how I want it
  arrangeTrainBucketData(originStation,destStation);
}

function loadTripFastFactsStats(originStation, destStation) {
	var numTrains = getTrainsByRoute(originStation, destStation).length;
	$('.num-trains-run-cta').text(numTrains + ' trains');
	$('.num-trains-run-desc').text('run between ' + toTitleCase(originStation) + ' and ' + toTitleCase(destStation) + ' most days');

	getAverageDelays(originStation,destStation,180,10, function(e){
		$('.num-ten-or-more-late-cta').text(Math.round(e) + '%');
	});

	getAverageDelays(originStation,destStation,180,30, function(e){
		$('.num-thirty-or-more-late-cta').text(Math.round(e) + '%');
	});


  //crappy height way
  // @todo: come back and fix this bc this is shit

  var routeHeight = $('#num-trains-route-stat').height();
  $('.stat-box').css('height', routeHeight + 15);
}

function loadAllStations() {
	var originStationMenu = $('#originSelect');
	var destStationMenu = $('#destinationSelect');

	var allStations = train_info.all_stops;

	for (var i = 0; i < allStations.length; i++) {
		originStationMenu.append("<option value=\"" + allStations[i] + "\">" + allStations[i] + "</option>");
		destStationMenu.append("<option value=\"" + allStations[i] + "\">" + allStations[i] + "</option>");
	};

	//  init for auto completing
	$(".select2").select2({});

	renderTrainDetails();
}

function renderTrainDetails() {
	var originStation = getParameterByName('originSelect');
	var destStation = getParameterByName('destinationSelect');

	if(originStation.length > 0 && destStation.length > 0) {
		$('[name=originSelect] option[value="' + originStation + '"]').prop('selected','selected');
		$('[name=destinationSelect] option[value="' + destStation + '"]').prop('selected',true);

		$('#originSelect').val(originStation).trigger('change');
		$('#destinationSelect').val(destStation).trigger('change');

		$('#statsBestWorst').hide();
		$('#statsTrainRoute').show();
		$('#dailyTripDelays').show();
		loadTripDelaysByTrain(originStation, destStation);
		loadTripFastFactsStats(originStation, destStation);
		scrollToAnchor('searchBox');
	}
	else {
		loadTop10Slow();
	}
}

function loadTop10Fast() {
	getBest(10, function(bestTrains){
		for (var j = 0; j < bestTrains.length; j++) {
			$('#bestTrainsTableBody').append('<tr><td>Train #' + bestTrains[j]['train'] + '</br><span class="stats-train-route">' + bestTrains[j]['first_station'] + ' - ' + bestTrains[j]['last_station'] + '</span</td><td>' + Math.round(bestTrains[j]['average']) + ' minutes</td></tr>');
		};
	})
}

function loadTop10Slow() {
	getWorst(10, function(worstTrains){
		for (var i = 0; i < worstTrains.length; i++) {
			$('#worstTrainsTableBody').append('<tr><td>Train #' + worstTrains[i]['train'] + '</br><span class="stats-train-route">' + worstTrains[i]['first_station'] + ' - ' + worstTrains[i]['last_station'] + '</span</td><td>' + Math.round(worstTrains[i]['average']) + ' minutes</td></tr>');
		};
		loadTop10Fast();
	})
}


// *************************************************************
// Controlling Page / On Load Controller
// *************************************************************

$( document ).ready(function() {
	dataInit(loadAllStations);
});
