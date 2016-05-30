var express = require('express');
var app = express();
var wait = require('wait.for');
var SerialPort = require("serialport").SerialPort;
var sleep = require('sleep');

var serPort = new SerialPort("/dev/ttyUSB0", {
    baudrate: 57600
});

var serPort2 = new SerialPort("/dev/ttyACM0", {
    baudrate: 57600
});

var ypr = "";
var sensor = "";
			
serPort.on("open", function() {
    serPort.on("data", function(data){
	ypr = data.toString();	
	sleep.usleep(20000);
	process.stdout.write(ypr);	
	app.get('/', function (req, res) {
	    // Website you wish to allow to connect
	    res.setHeader('Access-Control-Allow-Origin', '*');

    	    //Request methods you wish to allow
    	    res.setHeader('Access-Control-Allow-Methods', 'GET, POST, OPTIONS, PUT, PATCH, DELETE');
	    res.send(ypr);
	});
    });
});

/*
serPort2.on("open", function() {
    serPort2.on("data", function(data) {
        sensor = data.toString();
        sleep.usleep(10000);
	process.stdout.write(sensor);
        app.get('/depth', function (req, res) {
            // Website you wish to allow to connect
            res.setHeader('Access-Control-Allow-Origin', '*');

            //Request methods you wish to allow
            res.setHeader('Access-Control-Allow-Methods', 'GET, POST, OPTIONS, PUT, PATCH, DELETE');
            res.send(sensor);
        });
    });
}); */

app.listen(3000, function () {
  console.log('App listening on port 3000!');
});
