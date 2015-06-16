var trigger_scale = d3.scale.ordinal().domain([1, 2, 3, 4]).range(["#40DE30", "#A3A3A3", "#91A7FF", "#91A7FF"]);

var fault_class_map = {
  "Bad Cable Status": "text-faulted",
  "MKSU Protect": "text-faulted",
  "No Triggers": "text-faulted",
  "Modulator Fault": "text-faulted",
  "Low RF Power": "text-warn",
  "Amplitude Mean": "text-warn",
  "Amplitude Jitter": "text-warn",
  "Lost Phase": "text-warn",
  "Phase Jitter": "text-warn",
  "No Sample Rate": "text-warn",
  "Maintenance Mode": "text-offline",
  "Offline": "text-offline",
  "Out of Tolerance": "text-warn",
  "Bad CAMAC Status": "text-warn",
  "Dead Man Timeout": "text-faulted",
  "Fox Phase Home Error": "text-faulted",
  "Phase Mean": "text-warn",
  "IPL Required": "text-faulted",
  "Update Required": "text-faulted",
  "To Be Replaced": "text-offline",
  "Awaiting Run Up": "text-offline",
  "Check Phase": "text-offline",
  "SLED Motor Not At Limit": "text-faulted", 
  "SLED Upper Needle Fault": "text-faulted",
  "SLED Lower Needle Fault": "text-faulted",
  "Electromagnet Current Out of Tolerance": "text-faulted",
  "Klystron Temperature": "text-faulted",
  "Reflected Energy": "text-faulted",
  "Over Voltage": "text-faulted",
  "Over Current": "text-faulted",
  "PPYY Resync": "text-faulted",
  "ADC Read Error": "text-faulted",
  "ADC Out of Tolerance": "text-faulted",
  "Water Summary Fault": "text-faulted",
  "Acc Flowswitch #1": "text-faulted",
  "Acc Flowswitch #2": "text-faulted",
  "Waveguide Flowswitch #1": "text-faulted",
  "Waveguide Flowswitch #2": "text-faulted",
  "Klystron Water Flowswitch": "text-faulted",
  "24 Volt Battery": "text-faulted",
  "Waveguide Vacuum": "text-faulted",
  "Klystron Vacuum": "text-faulted",
  "Electromagnet Current": "text-faulted",
  "Electromagnet Breaker": "text-faulted",
  "MKSU Trigger Enable": "text-faulted",
  "EVOC": "text-faulted",
  "End of Line Clipper": "text-faulted",
  "Mod Trigger Overcurrent": "text-faulted",
  "External Fault": "text-faulted",
  "Fault Lockout": "text-faulted",
  "HV Ready": "text-faulted",
  "Klystron Heater Delay": "text-faulted",
  "VVS Voltage": "text-faulted",
  "Control Power": "text-faulted"
};

var retryTimer;
var socket;

function reloadPage() {
  document.location.reload()
}

function startSocket() {
  console.log("Attempting to connect.");
  supportsWebSockets = 'WebSocket' in window || 'MozWebSocket' in window;
  if (socket === undefined || socket.readyState === undefined || socket.readyState > 1) {
    if ('WebSocket' in window) {
      socket = new WebSocket('ws://lcls-prod03/klystrons');
    } else if ('MozWebSocket' in window) {
      socket = new MozWebSocket('ws://lcls-prod03/klystrons');
    }
  } else {
    console.log("Socket is not ready to connect: readyState = " + socket.readyState);
  }
};

startSocket();

socket.onopen = function() {
  console.log("Connection opened.");
};

socket.onclose = function() {
  //Wait a few seconds, then try to re-establish the websocket connection.
  console.log("Connection closed.  Attempting to reconnect in ten seconds...");
  retryTimer = window.setTimeout(reloadPage, 10000);
};

socket.onmessage = function(event) {
  var json = JSON.parse(event.data);
  var klysSelector = "#klys" + json.sector + "-" + json.station;
  d3.select(klysSelector).datum(function(d) {
    if (d === undefined) { d = {}; };
    if (json.trigger_status !== undefined) {
      d['trigger_status'] = json.trigger_status;
    }
    if (json.faults !== undefined) {
      d['faults'] = json.faults;
    }
    return d;
  }).classed("text-activated", function(d, i) {
    return d['trigger_status'] === 1;
  }).classed("text-deactivated", function(d, i) {
    return d['trigger_status'] > 1 ;
  }).classed("text-good", function(d, i) {
    return d['faults'] === undefined || d['faults'].length === 0;
  }).classed("text-offline", function(d, i) {
    return d['trigger_status'] === 3 || d['trigger_status'] === 4;
  }).classed("text-warn", function(d, i) {
    return (fault_class_map[d['faults'][0]] === "text-warn");
  }).classed("text-faulted", function(d, i) {
    return (fault_class_map[d['faults'][0]] === "text-faulted");
  }).select("div.status").classed("no-fault", function(d, i) {
    return (d['faults'] == undefined || d['faults'].length == 0);
  }).text(function(d) {
    if (d['faults'] !== undefined && d['faults'].length > 0) {
      return d['faults'][0];
    }
  });
};