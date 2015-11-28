// *************************************************************
// Utility Functions For Graphs, etc.
// *************************************************************

function drawStackedTripDelaysByTrain() {
var data = google.visualization.arrayToDataTable([
        ['Train', 'Ontime or less than 5 minutes late', 'between 5 and 30 minutes late', '30 or more minutes late', { role: 'annotation' } ],
        ['Train 87', 10, 24, 20, ''],
        ['Train 64', 16, 22, 23, ''],
        ['Train 88', 28, 19, 29, '']
      ]);

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



// *************************************************************
// Helper Functions / Controllers of Page Content
// *************************************************************

function loadTripDelaysByTrain(originStation, DestStation) {
  // Calling google and draw stacked to provide graph
  google.load('visualization', '1.1', {packages: ['corechart', 'bar']});
  google.setOnLoadCallback(drawStackedTripDelaysByTrain);
}

function loadTripFastFactsStats() {

}

function loadAllStations() {
  var originStationMenu = $('#originSelect');
  var destStationMenu = $('#destinationSelect');

  var allStations = ['Cornwall', 'Toronto', 'Montreal'];

  for (var i = 0; i < allStations.length; i++) {
    originStationMenu.append("<option>" + allStations[i] + "</option>");
    destStationMenu.append("<option>" + allStations[i] + "</option>");
  };

  $(".select2").select2({
  });
}







// *************************************************************
// Controlling Page / On Load Controller
// *************************************************************

$( document ).ready(function() {
  loadAllStations();
});
