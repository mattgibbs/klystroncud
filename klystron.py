import numpy, epics

# Make a Klystron object that opens a connection to all of its status PVs and generates usable error messages.
class Klystron:
	def __init__(self, sector, station, faults_callback=None, triggers_callback=None):
		self.sector = sector
		self.station = station
		self.faults = []
		self.faults_callback = None
		self.triggers_callback = None
		self.swrdMonitor = epics.PV(self.swrdPV())
		self.statMonitor = epics.PV(self.statPV())
		self.hdscMonitor = epics.PV(self.hdscPV())
		self.dstaMonitor = epics.PV(self.dstaPV())
		self.swrd = self.swrdMonitor.get()
		self.stat = self.statMonitor.get()
		self.hdsc = self.hdscMonitor.get()
		self.dsta = self.dstaMonitor.get()
		self.recalcFaults()
		self.swrdMonitor.add_callback(self.swrdCallback)
		self.statMonitor.add_callback(self.statCallback)
		self.hdscMonitor.add_callback(self.hdscCallback)
		self.dstaMonitor.add_callback(self.dstaCallback)
		self.accelerateTriggersMonitor = epics.PV(self.beamcodeStatPV(self.typicalBeamcode()))
		self.acc_trigger_status = self.accelerateTriggersMonitor.get()
		self.accelerateTriggersMonitor.add_callback(self.triggersChanged)
		self.faults_callback = faults_callback
		self.triggers_callback = triggers_callback
	
	def basePV(self):
		return "KLYS:LI{0}:{1}1".format(self.sector, self.station)
	
	def beamcodeStatPV(self, beamcode):
		return "{0}:BEAMCODE{1}_STAT".format(self.basePV(), beamcode)
	
	def swrdPV(self):
		return "{0}:SWRD".format(self.basePV())
	
	def statPV(self):
		return "{0}:STAT".format(self.basePV())
	
	def hdscPV(self):
		return "{0}:HDSC".format(self.basePV())	
	
	def dstaPV(self):
		return "{0}:DSTA".format(self.basePV())
	
	def typicalBeamcode(self):
		if self.sector > 20:
			return 1
		if self.sector == 20 and self.station >= 5:
			return 1
		if self.sector >= 2:
			return 10
		if self.sector < 2:
			return 11
	
	def swrdCallback(self, pvname=None, value=None, **kw):
		if value != self.swrd:
			self.swrd = value
			self.recalcFaults()
		
	def statCallback(self, pvname=None, value=None, **kw):
		if value != self.stat:
			self.stat = value
			self.recalcFaults()
		
	def hdscCallback(self, pvname=None, value=None, **kw):
		if value != self.hdsc:
			self.hdsc = value
			self.recalcFaults()
		
	def dstaCallback(self, pvname=None, value=None, **kw):
		if not numpy.array_equal(value,self.dsta):
			self.dsta = value
			self.recalcFaults()
	
	def triggersChanged(self, pvname=None, value=None, **kw):
		if value != self.acc_trigger_status:
			self.acc_trigger_status = value
			if self.triggers_callback:
				self.triggers_callback(self.sector, self.station, self.acc_trigger_status)
	
	def accelerating(self):
		return self.acc_trigger_status == 1
	
	def recalcFaults(self):
		self.faults = all_fault_strings(swrd=self.swrd, stat=self.stat, hdsc=self.hdsc, dsta=self.dsta)
		if self.faults_callback:
			self.faults_callback(self.sector, self.station, self.faults)
			
#Below is the module-level stuff for turning status words into faults.
#Each key is a bit position.  Each value is a (Fault Name, Priority) tuple.
swrd_fault_map = {0: ("Bad Cable Status", 55), 1: ("MKSU Protect", 80), 2: ("No Triggers", 68), 3: ("Modulator Fault", 67), 5: ("Low RF Power", 80), 6: ("Amplitude Mean", 70), 7: ("Amplitude Jitter", 75), 8: ("Lost Phase", 90), 10: ("Phase Jitter", 75), 14: ("No Sample Rate", 69), 15: ("No Accelerate Rate", 990)}
stat_fault_map = {1: ("Maintenance Mode", 10), 2: ("Offline", 1), 3: ("Out of Tolerance", 100), 4: ("Bad CAMAC Status", 40), 6: ("Dead Man Timeout", 50), 7: ("Fox Phase Home Error", 57), 9: ("Phase Mean", 75), 12: ("IPL Required", 20), 14: ("Update Required", 30)}
hdsc_fault_map = {2: ("To Be Replaced", 5), 3: ("Awaiting Run Up", 5), 6: ("Check Phase", 5)}
dsta1_fault_map = {2: ("SLED Motor Not At Limit", 65), 3: ("SLED Upper Needle Fault", 65), 4: ("SLED Lower Needle Fault",65), 5: ("Electromagnet Current Out of Tolerance", 65), 6: ("Klystron Temperature", 65), 8: ("Reflected Energy", 65), 9: ("Over Voltage", 65), 10: ("Over Current", 65), 11: ("PPYY Resync", 67), 12: ("ADC Read Error", 50), 13: ("ADC Out of Tolerance", 72), 16: ("Water Summary Fault", 61), 17: ("Acc Flowswitch #1", 60), 18: ("Acc Flowswitch #2", 60), 19: ("Waveguide Flowswitch #1", 60), 20: ("Waveguide Flowswitch #2", 60), 21: ("Klystron Water Flowswitch", 60), 22: ("24 Volt Battery", 60), 23: ("Waveguide Vacuum", 60), 25: ("Klystron Vacuum", 60), 26: ("Electromagnet Current", 60), 27: ("Electromagnet Breaker", 60), 28: ("MKSU Trigger Enable", 60)}
dsta2_fault_map = {4: ("EVOC", 65), 6: ("End of Line Clipper", 65), 7: ("Mod Trigger Overcurrent", 65), 9: ("External Fault", 65), 10: ("Fault Lockout", 65), 11: ("HV Ready", 65), 13: ("Klystron Heater Delay", 65), 14: ("VVS Voltage", 65), 15: ("Control Power", 65)}

#Input an integer, and you'll get a list of fault strings, ordered by priority.
def swrd_fault_strings(swrd):
	return strings_from_fault_tuple_list(swrd_faults(swrd))
	
def stat_fault_strings(stat):
	return strings_from_fault_tuple_list(stat_faults(stat))

def hdsc_fault_strings(hdsc):
	return strings_from_fault_tuple_list(hdsc_faults(hdsc))

def dsta_fault_strings(dsta):
	return strings_from_fault_tuple_list(dsta_faults(dsta))
	
def all_fault_strings(swrd=0, stat=0, hdsc=0, dsta=0):
	return strings_from_fault_tuple_list(all_faults(swrd=swrd, stat=stat, hdsc=hdsc, dsta=dsta))
	
def strings_from_fault_tuple_list(faults):
	return [fault[0] for fault in faults]

#Input an integer, and you'll get a list of tuples, ordered by priority (lower number = higher priority).
def swrd_faults(swrd):
	return list_faults(swrd_fault_map, swrd)
	
def stat_faults(stat):
	return list_faults(stat_fault_map, stat)

def hdsc_faults(hdsc):
	return list_faults(hdsc_fault_map, hdsc)

def dsta_faults(dsta):
	faults = list_faults(dsta1_fault_map, dsta[0])
	faults.extend(list_faults(dsta2_fault_map,dsta[1]))
	return faults

def all_faults(swrd=0, stat=0, hdsc=0, dsta=0):
	faults = swrd_faults(swrd)
	faults.extend(stat_faults(stat))
	faults.extend(hdsc_faults(hdsc))
	faults.extend(dsta_faults(dsta))
	faults.sort(key=lambda tup: tup[1])
	return faults

def list_faults(fault_map, word):
	faults = []
	for bit in fault_map:
		if testbit(word, bit):
			faults.append(fault_map[bit])
	faults.sort(key=lambda tup: tup[1])
	return faults

def testbit(word, offset):
	mask = 1 << offset
	return ((int(word) & mask) > 0)