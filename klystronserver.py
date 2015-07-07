#!/usr/bin/python

import wsaccel, ujson
from bottle import route, run, request, abort, Bottle ,static_file
from klystron import Klystron
from gevent import monkey; monkey.patch_all()
from geventwebsocket import WebSocketServer, WebSocketApplication, Resource, WebSocketError
import logging

logger = logging.getLogger("klystronserverLogger")
formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
filehandler = logging.FileHandler("/var/log/klystronserver/klystronserver.log")
handler = logging.StreamHandler()
handler.setFormatter(formatter)
logger.addHandler(handler)
logger.addHandler(filehandler)
logger.setLevel(logging.DEBUG)
app = Bottle()

klystrons = {}
initialized_clients = set()
initialized = False

class KlystronServerApplication(WebSocketApplication):
	def __init__(self, ws):
		super(KlystronServerApplication, self).__init__(ws)
		if not initialized:
			self.initialize_klystrons()
		
	def initialize_klystrons(self):
		sectors = {}
		sectors[20] = [5,6,7,8];
		for s in range(21,31):
			sectors[s] = range(0,9)
		sectors[24] = [0,1,2,3,4,5,6,8]
		for sector in sectors:
			klystrons_in_sector = {}
			for station in sectors[sector]:
				klystrons_in_sector[station] = Klystron(sector,station,faults_callback=self.klystron_fault_callback, triggers_callback=self.klystron_triggers_callback)
			klystrons[sector] = klystrons_in_sector
		logger.debug("Finished connecting to klystrons.")
		initialized = True
	
	def klystron_fault_callback(self, sector, station, faults):
		for client in initialized_clients:
			client.ws.send(ujson.dumps({'sector': sector, 'station': station, 'faults': faults}))
		
	def klystron_triggers_callback(self, sector, station, trigger_status):
		for client in initialized_clients:
			client.ws.send(ujson.dumps({'sector': sector, 'station': station, 'trigger_status': trigger_status}))
			
	def send_current_state(self, client):
		for sector in klystrons:
			for station in klystrons[sector]:
				client.ws.send(ujson.dumps({'sector': sector, 'station': station, 'faults': klystrons[sector][station].faults, 'trigger_status': klystrons[sector][station].acc_trigger_status}))
		initialized_clients.add(client)
		
	def on_open(self):
		current_client = self.ws.handler.active_client
		logger.debug("Connection opened.")
		#Send initial state to the client.
		self.send_current_state(current_client)
		
	def on_message(self, message):
		pass
		
	def on_close(self, reason):
		current_client = self.ws.handler.active_client
		initialized_clients.remove(current_client)
		logger.debug("Connection closed.")
		
#@app.route('/<filename:path>')
#def send_html(filename):
#    return static_file(filename, root='./static')

#wsgi_app is the callable to use for WSGI servers.
wsgi_klystron_app = Resource({'^/klystrons$': KlystronServerApplication})

#start() starts the development server.
def start():
	logger.info("Starting klystronserver.")
	host = "127.0.0.1"
	port = 8889
	server = WebSocketServer((host, port), wsgi_klystron_app)
	server.serve_forever()

if __name__ == '__main__':
	start()