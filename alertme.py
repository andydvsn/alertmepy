#!/usr/bin/env python

## alertme.py v0.02 (18th March 2013) by Andy Davison
##  A python interface to the AlertMe home security and energy system.

import xmlrpclib
import optparse, tempfile
import sys, time, datetime


### Configuration #########
username = ''
password = ''
identity = 'AlertMePy'
###########################


def main():
	"Our main function, which is called if we're being run directly."

	global username
	global password
	global devdump
	devdump = ''
	
	## Sort out our options.
	parser = optparse.OptionParser()
	# Main options
	parser.add_option("-c", metavar="FILE", dest="credentials", default= "", help="Specify a credentials file")
	parser.add_option("--debug", action="store_const", dest="output", const="debug", help="Set debug output.")
	parser.add_option("--human", "-u", action="store_const", dest="output", const="human", help="Set human output.")

	# Monitoring control options
	group = optparse.OptionGroup(parser, "Monitoring Control Options")

	parser.add_option_group(group)

	# Energy control options
	group = optparse.OptionGroup(parser, "Energy Control Options")
	group.add_option("-R", metavar="STATE", dest="setrelay", help="Specify the relay state of SmartPlug(s) (on|off|tog).")
	group.add_option("-P", metavar="PLUG", dest="plug", help="Specify name or ID of SmartPlug(s) to control. NOTE: Matching is case-sensitive, includes partial matches.")
	group.add_option("-S", action="store_true", dest="postrelaystate", default=False, help="Confirm the state of the SmartPlug after relay switch command has completed.")
	parser.add_option_group(group)
	
	# Device query options
	group = optparse.OptionGroup(parser, "Device Queries")
	group.add_option("-b", "--battery", metavar="DEVICE", dest="battery", help=alertme.getBatteryStates.__doc__)
	group.add_option("-d", "--devices", metavar="DEVICE", dest="devices", help=alertme.getAllDevices.__doc__)
	group.add_option("-f", "--firmware", metavar="DEVICE", dest="firmware", help=alertme.getFirmwareVersion.__doc__)
	group.add_option("-r", "--relay", metavar="DEVICE", dest="relaystate", help=alertme.getRelayState.__doc__)
	group.add_option("-t", "--temperature", metavar="DEVICE", dest="temperature", help=alertme.getTemperature.__doc__)
	group.add_option("-v", "--values", metavar="DEVICE", dest="values", help=alertme.getAllDeviceChannelValues.__doc__)
	group.add_option("-w", "--watts", action="store_true", dest="totalwatts", help=alertme.getTotalWatts.__doc__)
	parser.add_option_group(group)
	
	# Hub query options
	group = optparse.OptionGroup(parser, "Hub Queries")
	group.add_option("-m", "--behaviour", action="store_true", dest="behaviour", help=alertme.getBehaviour.__doc__)
	group.add_option("--behaviours", action="store_true", dest="behaviours", help=alertme.getAllBehaviours.__doc__)
	group.add_option("--hubs", action="store_true", dest="hubs", help=alertme.getAllHubs.__doc__)
	group.add_option("-s", "--hubstatus", action="store_true", dest="hubstatus", help=alertme.getHubStatus.__doc__)
	group.add_option("--services", action="store_true", dest="services", help=alertme.getAllServices.__doc__)
	group.add_option("-a", "--state", action="store_true", help=alertme.getCurrentServiceState.__doc__)
	group.add_option("--states", metavar="SERVICE", dest="states", help=alertme.getAllServiceStates.__doc__)
	group.add_option("--userinfo", action="store_true", dest="userinfo", help=alertme.getUserInfo.__doc__)
	parser.add_option_group(group)
	
	# Event log options
	group = optparse.OptionGroup(parser, "Log Queries")
	group.add_option("--log", metavar="TYPE", dest="log", help="Choose which log to read.")
	group.add_option("--logservice", metavar="SERVICE", dest="logservice", default="null", help="Which service to enquire about. [default: all]")
	group.add_option("--logstart", metavar="HOURS", dest="logstart", type="int", default=24, help="From how many hours in the past you would like retrieved log data to begin. [default: %default]")
	group.add_option("--logend", metavar="HOURS", dest="logend", type="int", default=0, help="From how many hours in the past you would like retrieved log data to end. [default: %default]")
	parser.add_option_group(group)
	
	parser.set_defaults(output="machine")

	(opts, args) = parser.parse_args()

		
	## Deal with credentials.
	if username == '' and password == '' and opts.credentials == '':
		print "You need to specify your login details."
		sys.exit()
	elif opts.credentials:
		try:
			credentials = open(opts.credentials).read().splitlines()
			username = credentials[0]
			password = credentials[1]
		except IOError as e:
			print "{1}".format(e.errno, e.strerror)
			sys.exit(2)


	### Do stuff!
				
	alertme.login(username,password,identity,opts.output)

	## Commands

	# Control SmartPlugs
	if opts.setrelay:
		output = alertme.setRelay(opts.setrelay,opts.plug,opts.postrelaystate,opts.output)
		if opts.output == "machine":
			sys.stdout.write("setrelay=")
			print output



	# Hub Options
	if opts.userinfo:
		output = alertme.getUserInfo(opts.output)
		if opts.output == "machine":
			sys.stdout.write("userinfo=")
			print output
		elif opts.output == "human":
			print "   getUserInfo:"
			for i in output.split(","):
				print "       " , i.split("|")[0],"=",i.split("|")[1]

	if opts.hubs:
		output = alertme.getAllHubs(opts.output)
		if opts.output == "machine":
			sys.stdout.write("hubs=")
			print output
		elif opts.output == "human":
			print "   getAllHubs:"
			for i in output.split(","):
				print "       " , i.split("|")[0]," (",i.split("|")[1],")"

	if opts.hubstatus:
		output = alertme.getHubStatus(opts.output)
		if opts.output == "machine":
			sys.stdout.write("hubstatus=")
			print output
		elif opts.output == "human":
			print "   getHubStatus:"
			for i in output.split(","):
				if "Uptime" in i:
					humantime = getDHMS(int(i.split("Uptime|")[1]))
					i = "Uptime|" + humantime
				print "       " , i.split("|")[0],"=",i.split("|")[1]

	if opts.behaviours:
		output = alertme.getAllBehaviours(opts.output)
		if opts.output == "machine":
			sys.stdout.write("behaviours=")
			print output
		elif opts.output == "human":
			print "   getAllBehaviours:"
			for i in output.split(","):
				print "       " , i

	if opts.behaviour:
		output = alertme.getBehaviourTime(opts.output)
		if opts.output == "machine":
			sys.stdout.write("behaviour=")
			print output
		if opts.output == "human":
			time = getDHMS(int(output.split("|")[1]))
			print output.split("|")[0] + " for " + time

	if opts.services:
		output = alertme.getAllServices(opts.output)
		if opts.output == "machine":
			sys.stdout.write("services=")
			print output
		if opts.output == "human":
			print "   getAllServices:"
			for i in output.split(","):
				print "       " , i

	if opts.states:
		if opts.states == "all" or "," in opts.states:
			print "Please specify one particular service for --states."
		else:
			output = alertme.getAllServiceStates(opts.states,opts.output)
			if opts.output == "machine":
				sys.stdout.write("states=")
				print output
			if opts.output == "human":
				print "   getAllServiceStates (" , opts.states, ")"
				for i in output.split(","):
					print "       " , i

	if opts.state:
		output = alertme.getCurrentServiceState(opts.output)
		if opts.output == "machine":
			sys.stdout.write("state=")
			print output
		if opts.output == "human":
			print "   getCurrentServiceState:"
			for i in output.split(","):
				print "       " , i.replace("|", " is ")


	# Device Options
	if opts.devices:
		output = alertme.getAllDevices(opts.devices,opts.output)
		if opts.output == "machine":
			sys.stdout.write("devices=")
			print output
		if opts.output == "human":
			print "   getAllDevices:"
			devicelist = []
			for i in output.split(","):
				print "      " + i

	if opts.firmware:
		output = alertme.getFirmwareVersion(opts.firmware,opts.output)
		if opts.output == "machine":
			sys.stdout.write("firmware=")
			print output
		if opts.output == "human":
			print "   getFirmwareVersion (" , opts.firmware, ")"
			for i in output.split(","):
				print "       " , i

	if opts.relaystate:
		output = alertme.getRelayState(opts.relaystate,opts.output)
		if opts.output == "machine":
			sys.stdout.write("relaystate=")
			print output
		if opts.output == "human":
			print "   getRelayState:"
			#return result.replace(',','\n')
			valueslist = []
			for i in output.split(","):
				print "      " + i

	if opts.totalwatts:
		output = alertme.getTotalWatts(opts.output)
		if opts.output == "machine":
			sys.stdout.write("totalwatts=")
			print output
		if opts.output == "human":
			print "   getTotalWatts:"
			for l in output.split(","):
				print "      " + l

	if opts.values:
		output = alertme.getAllDeviceChannelValues(opts.values,1,opts.output)
		if opts.output == "machine":
			sys.stdout.write("values=")
			print output
		if opts.output == "human":
			print "   getAllDeviceChannelValues:"
			for l in output.split(","):
				print "      " + l
					
	if opts.battery:
		output = alertme.getBatteryStates(opts.battery,opts.output)
		if opts.output == "machine":
			sys.stdout.write("battery=")
			print output
		if opts.output == "human":
			print "   getBatteryStates:"
			for i in output.split(","):
				print "       " + i

	if opts.temperature:
		output = alertme.getTemperature(opts.temperature,opts.output)
		if opts.output == "machine":
			sys.stdout.write("temperature=")
			print output
		if opts.output == "human":
			print "   getTemperature:"
			for i in output.split(","):
				print "       " + i



	# Log Options
	if opts.log:
		unixlogstart = int(time.time() - (opts.logstart * 60 * 60))
		unixlogend = int(time.time() - (opts.logend * 60 * 60))
		output = alertme.getEventLog(opts.logservice,opts.log,unixlogstart,unixlogend,"false",opts.output)
		if opts.output == "machine":
			sys.stdout.write("log=")
			print output
		elif output == "human":
			print "   getEventLog (" , service, "," , numEntries , "," , start , "," , end , "," , localiseTimes , ")"
			for i in result.split(","):
				print "       " , i
	
	sys.exit()


	
class AlertMePy:

	xmlrpc = ''
	sessionTicket = ''
	
	## Authentication
	
	# Hello.
	def login(self, username, password, identity, output):
		"Log in to the AlertMe servers and get our session ticket."
		
		amserver='https://api.alertme.com/webapi/v2'
		
		if output == "debug":
			print datetime.datetime.now() , "---> login (",username,", <secret> ,",identity,")"
			self.xmlrpc = xmlrpclib.ServerProxy(amserver, verbose = 1)
		else:
			self.xmlrpc = xmlrpclib.ServerProxy(amserver, verbose = 0)

		self.sessionTicket = self.xmlrpc.login(username,password,identity)
        
		if output == "debug":
			print datetime.datetime.now() , "<--- received:",self.sessionTicket
        
	# Goodbye.
	def logout(self, output):
		"Log out of the AlertMe servers."
		if output == "debug":
			print datetime.datetime.now() , "---> logout (",self.sessionTicket,")"
        
		result = self.xmlrpc.logout(self.sessionTicket)
        
		if output == "debug":
			print datetime.datetime.now() , "<--- received:", result
        
		self.sessionTicket = '';

	# Whoami?
	def getUserInfo(self, output):
		"Return the AlertMe account holder's details."
		if output == "debug":
			print datetime.datetime.now() , "---> getUserInfo( ", self.sessionTicket, ")"
		
		result = self.xmlrpc.getUserInfo( self.sessionTicket )
		
		if output == "debug":
			print datetime.datetime.now() , "<--- received:", result
		
		return result


	## Commands

	# The generic sendCommand function.
	def sendCommand(self,service,command,deviceid,output):
		"Sends a command to a service on the hub."
		if output == "debug":
			print datetime.datetime.now() , "---> sendCommand (",self.sessionTicket,",",service,",",command,",",deviceid,") "
		
		result = self.xmlrpc.sendCommand( self.sessionTicket, service, command, deviceid )
		
		if output == "debug":
			print datetime.datetime.now() , "<--- received:", result
		
		return result;

	# Control the relay state of a SmartPlug, optionally returning its condition post-switch.
	def setRelay(self,state,plug,postrelaystate,output):
				
		# Fill the device dump if it's empty.
		global devdump
		if devdump == "":
			devdump = self.xmlrpc.getAllDeviceChannelValues( self.sessionTicket )
		
		# Find IDs for names, names for IDs and relay states for everyone.
		nms=[]
		ids=[]
		rls=[]
		res=[]
		for l in sorted(devdump.split(",")):
			if "Power Controller" in l:
				if plug in l:
					# We've got one!
					nms.append(l.split("|")[0])
					ids.append(l.split("|")[1])
					rls.append(l.split(";")[8].split("|")[1])
		
		# Get switchin'
		for x,i in enumerate(ids):
			
			if "tog" in state:
				
				if rls[x] == "True":
					if output == "debug":
						print "---> sendCommand( \"Energy\" , \"off\" ,",i,",",output,")"
						print "----", nms[x], "going dark"
					
					res.append(alertme.sendCommand("Energy","off",i,output))
			
				elif rls[x] == "False":
					if output == "debug":
						print "---> sendCommand( \"Energy\" , \"on\" ,",i,",",output,")"
						print "----", nms[x], "lighting up"
					
					res.append(alertme.sendCommand("Energy","on",i,output))

				else:
					
					res.append("failed")

			elif "on" in state:
				if rls[x] == "False":
					if output == "debug":
						print "---> sendCommand( \"Energy\" , \"on\" ,",i,",",output,")"
						print "----", nms[x], "lighting up"
					
					res.append(alertme.sendCommand("Energy","on",i,output))

				elif rls[x] == "True":
					if output == "debug":
						print "----", nms[x], "already lit"
					
					res.append("nochange")

				else:
					
					res.append("failed")

			elif "off" in state:
				if rls[x] == "True":
					if output == "debug":
						print "---> sendCommand( \"Energy\" , \"off\" ,",i,",",output,")"
						print "----", nms[x], "going dark"
					
					res.append(alertme.sendCommand("Energy","off",i,output))
				
				elif rls[x] == "False":
					if output == "debug":
						print "----", nms[x], "already dark"
					
					res.append("nochange")

				else:
					
					res.append("failed")
							
			else:
				
				print "You need to specify 'on', 'off' or 'toggle'."
				sys.exit(2)
		
		# If requested, find out the power usage state after switching.
		pwr=[]
		if postrelaystate:
			
			time.sleep(4)
			devdump = self.xmlrpc.getAllDeviceChannelValues( self.sessionTicket )
			for l in sorted(devdump.split(",")):
				if "Power Controller" in l:
					if plug in l:
						# We've got one!
						rls = l.split(";")[8].split("|")[1]
						if "True" in rls:
							pwr.append(l.split(";")[10].split("|")[1])
						else:
							pwr.append("off")

		concat = []
		for x,i in enumerate(ids):
			if postrelaystate:
				postswitch = nms[x] + "|" + pwr[x]
			else:
				postswitch = nms[x] + "|" + res[x]
			concat.append(postswitch)
		result = ','.join(concat)

		return result

			
	## Device Actions

	# Show a list of all of the devices.
	def getAllDevices(self,device,output):
		"Lists devices in the system with their types and IDs."
		
		# Check and fill the device dump.
		global devdump
		if devdump == "":
			if output == "debug":
				print datetime.datetime.now() , "---> getAllDeviceChannelValues( ", self.sessionTicket, ")"
			devdump = self.xmlrpc.getAllDeviceChannelValues( self.sessionTicket )
		
		# Read what we need.
		nms=[]
		ids=[]
		types=[]
		
		def readThings(line):
			nms.append(line.split("|")[0])
			ids.append(line.split("|")[1])
			types.append(line.split("|")[2].split(";")[0])
		
		# Drop stuff we're not interested in.
		for l in sorted(devdump.split(",")):
			if device == "all":
				readThings(l)
			else:
				if device in l:
					readThings(l)
		
		# Format our output and return it.
		concat = []
		for x,i in enumerate(ids):
			deviceresult = nms[x] + "|" + types[x] + "|" + ids[x]
			concat.append(deviceresult)
		result = ','.join(concat)
		
		if output == "debug":
			print datetime.datetime.now() , "<--- received:", devdump
		
		return result


	# Retrieve some details about a device. Only seems to get the firmware version.
	def getFirmwareVersion(self,device,output):
		"Returns device firmware version."
		
		global devdump
		if devdump == "":
			if output == "debug":
				print datetime.datetime.now() , "---> getAllDeviceChannelValues( ", self.sessionTicket, ")"
			devdump = self.xmlrpc.getAllDeviceChannelValues( self.sessionTicket )
		
		nms=[]
		ids=[]
		types=[]
		
		def readDevice(line):
			nms.append(line.split("|")[0])
			ids.append(line.split("|")[1])
			types.append(line.split("|")[2].split(";")[0])
		
		for l in sorted(devdump.split(",")):
			if device == "all":
				readDevice(l)
			else:
				if device in l:
					readDevice(l)
		
		firmware=[]
		for i in ids:
			firmware.append((self.xmlrpc.getDeviceDetails( self.sessionTicket, i )).split("|")[1])
		
		concat = []
		for x,i in enumerate(ids):
			deviceresult = nms[x] + "|" + types[x] + "|" + firmware[x]
			concat.append(deviceresult)
		result = ','.join(concat)
		
		if output == "debug":
			print datetime.datetime.now() , "<--- received:", devdump
		
		
		if output == "debug":
			print datetime.datetime.now() , "---> getDeviceDetails( ", self.sessionTicket, "," , deviceid , ")"
		
		if output == "debug":
			print datetime.datetime.now() , "<--- received:", result
		
		return result




	# Gets the current values for specified data channels. We don't implement this because there's a bug with sub-zero temperatures and getAllDeviceChannelValues is quicker.
	def getDeviceChannelValue(self,deviceid,channel,output):
		"Returns the current values for either a single named channel on a particular device or all available channels if no channel name is specified."
		if ( channel == '' ):
			if output == "debug":
				print datetime.datetime.now() , "---> getDeviceChannelValue( ", self.sessionTicket, "," , deviceid , ")"
			
			result = self.xmlrpc.getDeviceChannelValue( self.sessionTicket, deviceid )
		else:
			if output == "debug":
				print datetime.datetime.now() , "---> getDeviceChannelValue( ", self.sessionTicket, "," , deviceid , "," , channel , ")"
			
			result = self.xmlrpc.getDeviceChannelValue( self.sessionTicket, deviceid, channel )
		
		if output == "debug":
			print datetime.datetime.now() , "<--- received:", result
		
		return result


	# Retrieve pretty much everything about every device. This is a most useful option.
	def getAllDeviceChannelValues(self,device,refresh,output):
		"Returns current values for all device data channels."
		if output == "debug":
			print datetime.datetime.now() , "---> getAllDeviceChannelValues( ", self.sessionTicket, ")"
		
		global devdump
		
		if refresh == 1 or devdump == "":
			devdump = self.xmlrpc.getAllDeviceChannelValues( self.sessionTicket )
		
		output=[]
		for l in sorted(devdump.split(",")):
			if device == "all":
				output.append(l)
			else:
				for d in device.split(","):
					if d in l:
						output.append(l)
		
		if output == "debug":
			print datetime.datetime.now() , "<--- received:", devdump
		
		return ','.join(output)


	# Retrieve all of the battery values for devices that have them, return them with a status.
	def getBatteryStates(self,device,output):
		"Returns current battery voltages and a status."
		if output == "debug":
			print datetime.datetime.now() , "---> getAllDeviceChannelValues( ", self.sessionTicket, ")"
		
		global devdump
		if devdump == "":
			devdump = self.xmlrpc.getAllDeviceChannelValues( self.sessionTicket )
		
		nms=[]
		ids=[]
		types=[]
		volts=[]
		vstat=[]
		
		def readThings(line):
			nms.append(line.split("|")[0])
			ids.append(line.split("|")[1])
			types.append(line.split("|")[2].split(";")[0])
			voltage = float(line.split(";")[4].split("|")[1])
			volts.append(round(voltage,2))
			
			if voltage >= 3.0:
				vstatus = "new"
			if voltage < 3.0:
				vstatus = "ok"
			if voltage < 2.8:
				vstatus = "low"
			if voltage < 2.7:
				vstatus = "replace"
			if voltage == 0.0:
				vstatus = "dead"
			vstat.append(vstatus)
		
		for l in sorted(devdump.split(",")):
			if (not "Power Controller" in l) and (not "Camera" in l):
				if device == "all":
					readThings(l)
				else:
					if device in l:
						readThings(l)
		
		concat = []
		for x,i in enumerate(ids):
			deviceresult = nms[x] + "|" + types[x] + "|" + str(volts[x]) + "|" + vstat[x]
			concat.append(deviceresult)
		result = ','.join(concat)
		
		if output == "debug":
			print datetime.datetime.now() , "<--- received:", devdump
		
		return result


	# Retrieve all temperatures from devices with temperature sensors.
	def getTemperature(self,device,output):
		"Returns current temperatures."
		if output == "debug":
			print datetime.datetime.now() , "---> getAllDeviceChannelValues( ", self.sessionTicket, ")"
		
		global devdump
		if devdump == "":
			devdump = self.xmlrpc.getAllDeviceChannelValues( self.sessionTicket )
		
		nms=[]
		ids=[]
		types=[]
		temps=[]
		
		def readTemps(line):
			nms.append(line.split("|")[0])
			ids.append(line.split("|")[1])
			types.append(line.split("|")[2].split(";")[0])
			temps.append(line.split(";")[6])#.split("|")[1])
			
		
		
		for l in sorted(devdump.split(",")):
			if (not "Keyfob" in l) and (not "Power Controller" in l) and (not "Camera" in l):	
				if device == "all":
					readTemps(l)
				else:
					if device in l:
						readTemps(l)
		
		concat = []
		for x,i in enumerate(ids):
			deviceresult = nms[x] + "|" + types[x] + "|" + temps[x]
			concat.append(deviceresult)
		result = ','.join(concat)
		
		if output == "debug":
			print datetime.datetime.now() , "<--- received:", devdump
		
		return result



	# Return the current state of a SmartPlug.
	def getRelayState(self,device,output):
		"Returns current power usage in watts through a SmartPlug, or 'off' if the relay is open."
		if output == "debug":
			print datetime.datetime.now() , "---> getAllDeviceChannelValues( ", self.sessionTicket, ")"
		
		global devdump
		if devdump == "":
			devdump = self.xmlrpc.getAllDeviceChannelValues( self.sessionTicket )
		
		nms=[]
		ids=[]
		relays=[]
		watts=[]
		mains=[]
		
		def readThings(line):
			nms.append(line.split("|")[0])
			ids.append(line.split("|")[1])
			relays.append(line.split(";")[8].split("|")[1])
			watts.append(line.split(";")[10].split("|")[1])
			mains.append(line.split(";")[9].split("|")[1])
						
		for l in sorted(devdump.split(",")):
			if "Power Controller" in l:
				if device == "all":
					readThings(l)
				else:
					if device in l:
						readThings(l)
		
		concat = []
		for x,i in enumerate(ids):
			if "True" in relays[x]:
				relays[x] = "on"
			if "False" in relays[x]:
				relays[x] = "off"
			if "True" in mains[x]:
				deviceresult = nms[x] + "|" + relays[x]+ "|" + watts[x]
			if "False" in mains[x]:
				deviceresult = nms[x] + "|" + relays[x]+ "|nomains"
			concat.append(deviceresult)
		result = ','.join(concat)
		
		if output == "debug":
			print datetime.datetime.now() , "<--- received:", devdump
		
		return result


	# Return the household power usage from the PowerClamp.
	def getTotalWatts(self,output):
		"Return the total power usage from the Power Clamp."
		
		# Check and fill the device dump.
		global devdump
		if devdump == "":
			if output == "debug":
				print datetime.datetime.now() , "---> getAllDeviceChannelValues( ", self.sessionTicket, ")"
			devdump = self.xmlrpc.getAllDeviceChannelValues( self.sessionTicket )
				
		# Drop stuff we're not interested in.
		for l in sorted(devdump.split(",")):
			if "PowerClamp" in l:
				total = l.split(";")[10].split("|")[1]

		if total == "":
			print "Have you got a Meter Reader in your system?"

		return total


    ## Hub Actions

	# We just use this to get the hub name, as AlertMe only seem to associate one hub per account.
	def getAllHubs(self, output):
		"Returns all hubs associated with the logged in user."
		if output == "debug":
			print datetime.datetime.now() , "---> getAllHubs( ", self.sessionTicket, ")"
        
		result = self.xmlrpc.getAllHubs( self.sessionTicket )
        
		if output == "debug":

			print datetime.datetime.now() , "<--- received:", result
		
		return result

	# Retained in case it's needed, but with only one hub per account, there's not much point implementing it right now.
	def setHub(self, hubid):
		"Once this method has been called, subsequent API commands in the session will operate on the specified hub."
		if output == "debug":
			print datetime.datetime.now() , "---> setHub( ", self.sessionTicket, ",", hubid , ")"
        
		result = self.xmlrpc.setHub( self.sessionTicket, hubid )
        
		if output == "debug":
			print datetime.datetime.now() , "<--- received:", result
        
		return result
	
	# This is used to grab hub status information.
	def getHubStatus(self, output):
		"Requests status information for the hub."
		if output == "debug":
			print datetime.datetime.now() , "---> getHubStatus( ", self.sessionTicket, ")"
        
		result = self.xmlrpc.getHubStatus( self.sessionTicket )
	
		# Weirdly, the uptime of the hub is returned as d|h|m|s. Convert it to seconds for consistency.
		resultwithsecs = []
		for l in result.split(","):
			if "Uptime" in l:
				uptime = l.split("Uptime|")[1]
				upsecs = (int(uptime.split("|")[0]) * 86400) + (int(uptime.split("|")[1]) * 3600) + (int(uptime.split("|")[2]) * 60) + int(uptime.split("|")[3])
				l = "Uptime|" + str(upsecs)
			resultwithsecs.append(l)
	        
		if output == "debug":
			print datetime.datetime.now() , "<--- received:", result
        
		return ','.join(resultwithsecs)

	# Return a specified number of entries from the event log.
	def getEventLog(self, service, numEntries, start, end, localiseTimes , output ):
		"Returns entries from the event log."
		if output == "debug":
			print datetime.datetime.now() , "---> getEventLog( ", self.sessionTicket, "," , service , "," , numEntries , "," , start , "," , end , "," , localiseTimes , ")"
		
		result = self.xmlrpc.getEventLog( self.sessionTicket, service, numEntries, start, end, localiseTimes )
		
		if output == "debug":
			print datetime.datetime.now() , "<--- received:", result
		
		return result
	
	# See what behaviour modes we can put this hub into.
	def getAllBehaviours(self, output):
		"Returns all possible behaviours for the hub."
		if output == "debug":
			print datetime.datetime.now() , "---> getAllBehaviours( ", self.sessionTicket, ")"
		
		result = self.xmlrpc.getAllBehaviours( self.sessionTicket )
		
		if output == "debug":
			print datetime.datetime.now() , "<--- received:", result
		
		return result
	
	# See which behaviour mode the hub is in right now.
	def getBehaviour(self, output):
		"Returns the current behaviour mode of the hub."
		if output == "debug":
			print datetime.datetime.now() , "---> getBehaviour( ", self.sessionTicket, ")"
		
		result = self.xmlrpc.getBehaviour( self.sessionTicket )
		
		if output == "debug":
			print datetime.datetime.now() , "<--- received:", result
		
		return result
	
	# Use the log to see which behaviour mode the hub is in, then return the behaviour and the time in that mode. Falls back to getBehaviour if data is not retrievable from the log.
	def getBehaviourTime(self, output):
		"Returns the current behaviour mode of the hub."
		if output == "debug":
			print datetime.datetime.now() , "---> getEventLog( ", self.sessionTicket, ", \"null\" , " , 50 , ", \"null\" , " , ", \"null\" , " , ", false" , ")"
		
		result = self.xmlrpc.getEventLog( self.sessionTicket, "null" , 50 , "null" , "null" , "false" )
				
		if "Behaviour changed to" in result:
			
			behavs=[]
			for l in result.split(","):
				if "Behaviour changed to" in l:
					behavs.append(l)
				
			tstamp = behavs[0].split("||")[0]
			behav = behavs[0].split("Behaviour changed to ")[1]
			if behav == "At home":
				behav = "Home"
			# How many seconds in this mode
			tbehav = int(time.time() - int(tstamp))
			result = str(behav),str(tbehav)
			result = '|'.join(result)
		
		else:
			
			result = self.xmlrpc.getBehaviour( self.sessionTicket )
			result = result+"|unknown"
				
		if output == "debug":
			print datetime.datetime.now() , "<--- received:", result
		
		return result
	
	# See which services are active on the hub.
	def getAllServices(self, output):
		"Returns all services enabled on the hub."
		if output == "debug":
			print datetime.datetime.now() , "---> getAllServices( ", self.sessionTicket, ")"
		
		result = self.xmlrpc.getAllServices( self.sessionTicket )
		
		if output == "debug":
			print datetime.datetime.now() , "<--- received:", result
		
		return result
	
	# See what states the active services on the hub can be set to.
	def getAllServiceStates(self,service,output):
		"Returns all possible states for one specified service."
		if output == "debug":
			print datetime.datetime.now() , "---> getAllServiceStates( ", self.sessionTicket, "," , service , ")"
		
		result = self.xmlrpc.getAllServiceStates( self.sessionTicket, service )
		
		if output == "debug":
			print datetime.datetime.now() , "<--- received:", result
		
		return result
	
	# See what state an active service on the hub is in right now. 
	def getCurrentServiceState(self,output):
		"Requests the current state for all available services."
		if output == "debug":
			print datetime.datetime.now() , "---> getCurrentServiceState( ", self.sessionTicket, "," , service , ")"
		
		result = self.xmlrpc.getCurrentServiceState( self.sessionTicket )
		
		if output == "debug":
			print datetime.datetime.now() , "<--- received:", result
		
		return result
			






# Handy functions
def getDHMS(seconds):
	minutes, seconds = divmod(seconds, 60)
	hours, minutes = divmod(minutes, 60)
	days, hours = divmod(hours, 24)
	
	if days > 0:
		return "%dd %dh %dm %ds" % (days, hours, minutes, seconds)
	elif hours > 0:
		return "%dh %dm %ds" % (hours, minutes, seconds)
	elif minutes > 0:
		return "%dm %ds" % (minutes, seconds)
	elif seconds > 0:
		return "%ds" % (seconds)



if __name__ == '__main__':
	
	alertme = AlertMePy()
	main()
