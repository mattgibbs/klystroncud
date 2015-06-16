var trigger_scale = d3.scale.ordinal().domain([1, 2, 3, 4]).range(["#40DE30", "#A3A3A3", "#91A7FF", "#91A7FF"]);

function startConnection() {
  supportsWebSockets = 'WebSocket' in window || 'MozWebSocket' in window;
  var socket;
  if ('WebSocket' in window) {
    socket = new WebSocket('ws://lcls-prod03/klystrons');
  } else if ('MozWebSocket' in window) {
    socket = new MozWebSocket('ws://lcls-prod03/klystrons');
  }
  
  socket.onopen = function() {
    
  };
  
  socket.onmessage = function(event) {
    var json = JSON.parse(event.data);
    console.log(json);
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
      return d['trigger_status'] === 2;
    }).classed("text-offline", function(d, i) {
      return d['trigger_status'] === 3 || d['trigger_status'] === 4;
    }).select("div.status").text(function(d) {
      if (d['faults'] !== undefined && d['faults'].length > 0) {
        return d['faults'][0];
      }
      return "";
    });
    /*
    d3.select(klysSelector + " div.status").text(function(d) {
      if (d['faults'] !== undefined && d['faults'].length > 0) {
        return d['faults'][0];
      }
      return "";
    });
    */
  };
}

startConnection();
