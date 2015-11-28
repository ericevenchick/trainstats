var train_info
getTrainsByRoute = function(origin, dest) {
    /* given two station names, returns an array of train numbers that make the
       specified trip */
    var trains = [];
    for (var t in train_info.train_stops) {
        origin_index = train_info.train_stops[t].indexOf(origin);
        dest_index = train_info.train_stops[t].indexOf(dest);
        if (origin_index >= 0 && dest_index >= 0 && origin_index < dest_index) {
            trains.push(t);
        }
    }
    return trains;
}

getDelaysAtStation = function(train_number, station, period, callback) {
    $.getJSON('data/train/' + train_number + '/report-' + period, function(data) {
        result = {}
        for (bin in data.delays[station]) {
            result[bin] = data.delays[station][bin] / data.delays[station].count * 100;
        }
        callback(result);
    });
}

average_data = [];
getAverageDelays = function(origin, dest, period, threshold, callback) {
    average_data = [];
    train_numbers = getTrainsByRoute(origin, dest);

    // build list of deferreds to get data for each train
    deferred = [];
    for (var t in train_numbers) {
        deferred.push($.getJSON('data/train/' + train_numbers[t] + '/report-' + period, function(data) {
            average_data.push(data);
        }));
    }

    // get all of the data before calling the callback
    $.when.apply($, deferred).then(function() {
        var average = 0;
        var count = 0;
        // iterate over the trains
        for (var i in average_data) {
            if (threshold == 10) {
                delays = average_data[i].delays[dest][10];
                delays += average_data[i].delays[dest][30];
            } else {
                delays = average_data[i].delays[dest][30];
            }
            total = average_data[i].delays[dest].count;
            average += delays / total * 100.0;
            count++;
        }
        average = average / count;
        callback(average);
    });
}

getWorst = function(num, callback) {
    result = []
    $.getJSON('data/average_delays', function(data) {
        var worst = [];
        for (var train in data) {
            worst.push([train, data[train]]);
        }
        worst.sort(function(a, b) {return b[1] - a[1]});
        for (var i = 0; i < num; i++) {
            var train_number = worst[i][0];
            var delay = worst[i][1];
            var stops = train_info['train_stops'][train_number];
            result.push({'train': train_number, 'average': delay, 
                        'first_station': stops[0], 
                        'last_station': stops[stops.length-1]});
        }
        callback(result);
    });
}

getBest = function(num, callback) {
    result = []
    $.getJSON('data/average_delays', function(data) {
        var best = [];
        for (var train in data) {
            best.push([train, data[train]]);
        }
        best.sort(function(a, b) {return a[1] - b[1]});
        for (var i = 0; i < num; i++) {
            var train_number = best[i][0];
            var delay = best[i][1];
            var stops = train_info['train_stops'][train_number];
            result.push({'train': train_number, 'average': delay, 
                        'first_station': stops[0], 
                        'last_station': stops[stops.length-1]});
        }
        callback(result);
    });
}
