google.load('visualization', '1.1', {packages: ['corechart', 'bar']});

// *************************************************************
// Utility Functions For Graphs, etc.
// *************************************************************
var trainData = [];
trainData[0] = ['Train', 'Ontime or less than 5 minutes late', 'between 5 and 30 minutes late', '30 or more minutes late', { role: 'annotation' } ];



function drawStackedTripDelaysByTrain() {
  console.log(trainData);
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
        colors: ['#FF9090', '#fc4242', '#B60707'],
  
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


// *************************************************************
// Helper Functions / Controllers of Page Content
// *************************************************************

function loadTripDelaysByTrain(originStation, destStation) {
  // getting the data how I want it
  arrangeTrainBucketData(originStation,destStation);
}

function loadTripFastFactsStats() {

}

function loadAllStations() {
  var originStationMenu = $('#originSelect');
  var destStationMenu = $('#destinationSelect');

  var allStations = train_info.all_stops;

  for (var i = 0; i < allStations.length; i++) {
    originStationMenu.append("<option>" + allStations[i] + "</option>");
    destStationMenu.append("<option>" + allStations[i] + "</option>");
  };

  //init for auto completing
  $(".select2").select2();

  renderTrainDetails();
}

function renderTrainDetails() {
  // check that we actually have parameters passed
  console.log('in render');
  var originStation = getParameterByName('originSelect');
  var destStation = getParameterByName('destinationSelect');

  if(originStation.length > 0 && destStation.length > 0) {
    $('#statsTrainRoute').show();
    $('#dailyTripDelays').show();
    loadTripDelaysByTrain(originStation, destStation);
  }
}


// *************************************************************
// Controlling Page / On Load Controller
// *************************************************************

$( document ).ready(function() {
  dataInit(loadAllStations);
});
