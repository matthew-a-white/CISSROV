var portCheck = "";
var comPort = "";

var serialPort = require("serialport");
var SerialPort = serialPort.SerialPort; 
var serPort;

serialPort.list(function (err, ports) {
  ports.forEach(function(port) {
    portCheck = port.comName + ", " + port.pnpId + ", " + port.manufacturer;
    //if(portCheck.indexOf("FTDI") != -1) {
	console.log(portCheck);
	//serPort = new SerialPort(port.comName.toString(), { baudrate: 57600 });
    //}
  });
});

/*serPort.open();

serPort.on("open", function () {
  serPort.on('data', function(data) {
    console.log(data);
  });
});*/


