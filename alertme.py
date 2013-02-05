#!/usr/bin/env python

## alertme.py v0.01 (5th February 2013) by Andy Davison
##  A python interface to the AlertMe home security and energy system.

import xmlrpclib
import optparse, tempfile
import sys, time, datetime

global username
global password

### Configuration #########
username = ''
password = ''
identity = 'AlertMePy'
###########################


def main():
	"Our main function, which is called if we're being run directly."

	global username
	global password
	
	## Sort out our options.
	parser = optparse.OptionParser()
	# Main options
	parser.add_option("-c", metavar="FILE", dest="credentials", default= "", help="Specify a credentials file")
	parser.add_option("-D", action="store_const", dest="output", const="debug", help="Set debug output.")
	parser.add_option("-H", action="store_const", dest="output", const="human", help="Set human output.")

	# Command options
	group = optparse.OptionGroup(parser, "Commands")
	#group.add_option("-M", dest="mode", help="set the hub behaviour mode: <home|away|night> [default: %default]")
	group.add_option("--plug", metavar="NAME", dest="plugid", help="Control the power relay of a SmartPlug, specified by its name. NB: Includes partial matches.")
	group.add_option("--plugid", metavar="DEVID", dest="plugid", help="Control the power relay of a SmartPlug, specified by its device ID.")
	group.add_option("--relay", metavar="STATE", dest="relay", help="Specify the target relay state (on|off).")
	parser.add_option_group(group)
	
	# Hub query options
	group = optparse.OptionGroup(parser, "Hub Queries")
	group.add_option("--behaviour", action="store_true", dest="behaviour", help=alertme.getBehaviour.__doc__)
	group.add_option("--behaviours", action="store_true", dest="behaviours", help=alertme.getAllBehaviours.__doc__)
	group.add_option("--hubs", action="store_true", dest="hubs", help=alertme.getAllHubs.__doc__)
	group.add_option("--hubstatus", action="store_true", dest="hubstatus", help=alertme.getHubStatus.__doc__)
	group.add_option("--services", action="store_true", dest="services", help=alertme.getAllServices.__doc__)
	group.add_option("--state", metavar="SERVICE", dest="state", help=alertme.getCurrentServiceState.__doc__)
	group.add_option("--states", metavar="SERVICE", dest="states", help=alertme.getAllServiceStates.__doc__)
	group.add_option("--userinfo", action="store_true", dest="userinfo", help=alertme.getUserInfo.__doc__)
	parser.add_option_group(group)
	
	# Device query options
	group = optparse.OptionGroup(parser, "Device Queries")
	group.add_option("--channels", metavar="DEVID", dest="channels", help=alertme.getAllDeviceChannels.__doc__)
	group.add_option("--devices", action="store_true", dest="devices", help=alertme.getAllDevices.__doc__)
	group.add_option("--details", metavar="DEVID", dest="details", help=alertme.getDeviceDetails.__doc__)
	group.add_option("--values", action="store_true", dest="values", help=alertme.getAllDeviceChannelValues.__doc__)
	parser.add_option_group(group)

	# Event log options
	group = optparse.OptionGroup(parser, "Event Log Queries")
	group.add_option("--log", metavar="NUM", dest="log", help=alertme.getEventLog.__doc__ + " Maximum of 50.")
	group.add_option("--logservice", metavar="SERVICE", dest="logservice", default="null", help="Which service to enquire about. [default: all]")
	group.add_option("--logstart", metavar="HOURS", dest="logstart", type="int", default=24, help="From how many hours in the past you would like retrieved log data to begin. [default: %default]")
	group.add_option("--logend", metavar="HOURS", dest="logend", type="int", default=0, help="From how many hours in the past you would like retrieved log data to end. [default: %default]")
	parser.add_option_group(group)

	# Device channel log options
	group = optparse.OptionGroup(parser, "Device Channel Log Queries")
	group.add_option("--dlog", metavar="NUM", dest="dlog", help=alertme.getDeviceChannelLog.__doc__ + " Maximum of 50.")
	group.add_option("--dlogid", metavar="DEVID", dest="dlogid", help="Which device should we retrieve data from.")
	group.add_option("--dlogchannel", metavar="CHAN", dest="dlogchannel", help="Which data channel to enquire about.")
	group.add_option("--dlogstart", metavar="HOURS", dest="dlogstart", type="int", default=24, help="From how many hours in the past you would like retrieved log data to begin. [default: %default]")
	group.add_option("--dlogend", metavar="HOURS", dest="dlogend", type="int", default=0, help="From how many hours in the past you would like retrieved log data to end. [default: %default]")
	parser.add_option_group(group)

	# Tracking log options
	group = optparse.OptionGroup(parser, "Tracking Log Queries")
	group.add_option("--tlog", metavar="NUM", dest="tlog", help=alertme.getEventLog.__doc__ + " Maximum of 50.")
	group.add_option("--tlogid", metavar="DEVID", dest="tlogid", help="Which device should we retrieve data from.")
	group.add_option("--tlogstart", metavar="HOURS", dest="tlogstart", type="int", default=24, help="From how many hours in the past you would like retrieved log data to begin. [default: %default]")
	group.add_option("--tlogend", metavar="HOURS", dest="tlogend", type="int", default=0, help="From how many hours in the past you would like retrieved log data to end. [default: %default]")
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


	## Do stuff!
				
	alertme.login(username,password,identity,opts.output)

	# Commands

	if opts.plugid:
		if opts.relay:
			output = alertme.sendCommand("Energy",opts.relay,opts.plugid,opts.output)
			if opts.output == "machine":
				sys.stdout.write("plug=")
				print output
		else:
			relaystate = alertme.getAllDeviceChannelValues("machine")
			for i in relaystate.split(","):
				if opts.plugid in i:
					for v in i.split(";"):
						if "RelayState" in v:
							relaystate = v.split("|")[1].lower()
							if relaystate == "false":
								output = alertme.sendCommand("Energy","on",opts.plugid,opts.output)
							if relaystate == "true":
								output = alertme.sendCommand("Energy","off",opts.plugid,opts.output)
							print output
			
			
			






#if opts.state is not None and opts.plug is None:
#	print "You need to specify which device to control."
#	sys.exit(2)



	# The Hub Options
	if opts.userinfo:
		output = alertme.getUserInfo(opts.output)
		if opts.output == "machine":
			sys.stdout.write("userinfo=")
			print (output.lower())

	if opts.hubs:
		output = alertme.getAllHubs(opts.output)
		if opts.output == "machine":
			sys.stdout.write("hubs=")
			print output

	if opts.hubstatus:
		output = alertme.getHubStatus(opts.output)
		if opts.output == "machine":
			sys.stdout.write("hubstatus=" + (output.lower()) + "\n")
		else:
			print output

	if opts.behaviours:
		output = alertme.getAllBehaviours(opts.output)
		if opts.output == "machine":
			sys.stdout.write("behaviours=")
			print (output.lower())

	if opts.behaviour:
		output = alertme.getBehaviour(opts.output)
		if opts.output == "machine":
			sys.stdout.write("behaviour=")
			print (output.lower())

	if opts.services:
		output = alertme.getAllServices(opts.output)
		if opts.output == "machine":
			sys.stdout.write("services=")
			print output

	if opts.states:
		output = alertme.getAllServiceStates(opts.states,opts.output)
		if opts.output == "machine":
			sys.stdout.write("states=")
			print output

	if opts.state:
		output = alertme.getCurrentServiceState(opts.state,opts.output)
		if opts.output == "machine":
			sys.stdout.write("state_" + (opts.state.lower()) + "=")
			print (output.lower())

	# The Log Options
	if opts.log:
		unixlogstart = int(time.time() - (opts.logstart * 60 * 60))
		unixlogend = int(time.time() - (opts.logend * 60 * 60))
		output = alertme.getEventLog(opts.logservice,opts.log,unixlogstart,unixlogend,"false",opts.output)
		if opts.output == "machine":
			sys.stdout.write("log=")
			print output

	if opts.dlog:
		if opts.dlogchannel and opts.dlogid:
			unixlogstart = int(time.time() - (opts.dlogstart * 60 * 60))
			unixlogend = int(time.time() - (opts.dlogend * 60 * 60))
			output = alertme.getDeviceChannelLog(opts.dlogid,opts.dlogchannel,opts.dlog,unixlogstart,unixlogend,opts.output)
			if opts.output == "machine":
				sys.stdout.write("dlog=")
				print output
		else:
			if opts.dlogchannel:
				print "You need to specify the device ID using --dlogid."
			elif opts.dlogid:
				print "You need to specify the data channel using --dlogchannel."
			else:
				print "You need to specify the device ID using --dlogid and the data channel with --dlogchannel."
			sys.exit()
	
	if opts.tlog:
		if opts.tlogid:
			unixlogstart = int(time.time() - (opts.logstart * 60 * 60))
			unixlogend = int(time.time() - (opts.logend * 60 * 60))
			output = alertme.getTrackingData(opts.tlogid,opts.tlog,unixlogstart,unixlogend,"false",opts.output)
			if opts.output == "machine":
				sys.stdout.write("tlog=")
				print output
		else:
			print "You need to specify the device ID using --tlogid."
			sys.exit()

	# The Device Options
	if opts.devices:
		output = alertme.getAllDevices(opts.output)
		if opts.output == "machine":
			sys.stdout.write("devices=")
			print (output.lower())

	if opts.details:
		output = alertme.getDeviceDetails(opts.details,opts.output)
		if opts.output == "machine":
			sys.stdout.write("details_" + (opts.details.lower()) + "=")
			print (output.lower())

	if opts.channels:
		output = alertme.getAllDeviceChannels(opts.channels,opts.output)
		if opts.output == "machine":
			sys.stdout.write("channels_" + (opts.channels.lower()) + "=")
			print (output.lower())

	if opts.values:
		output = alertme.getAllDeviceChannelValues(opts.output)
		if opts.output == "machine":
			sys.stdout.write("values=")
			print (output.lower())

	
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
			print datetime.datetime.now() , "---> Received:",self.sessionTicket
        
	# Goodbye.
	def logout(self, output):
		"Log out of the AlertMe servers."
		if output == "debug":
			print datetime.datetime.now() , "---> logout (",self.sessionTicket,")"
        
		result = self.xmlrpc.logout(self.sessionTicket)
        
		if output == "debug":
			print datetime.datetime.now() , "---> Received:", result
        
		self.sessionTicket = '';

	# Whoami?
	def getUserInfo(self, output):
		"Return the AlertMe account holder's details."
		if output == "debug":
			print datetime.datetime.now() , "---> getUserInfo( ", self.sessionTicket, ")"
		
		result = self.xmlrpc.getUserInfo( self.sessionTicket )
		
		if output == "debug":
			print datetime.datetime.now() , "---> Received:", result
		elif output == "human":
			print "   getUserInfo:"
			for i in result.split(","):
				print "       " , i.split("|")[0],"=",i.split("|")[1]
		else:
			return result


	## Commands
	
	def sendCommand(self,service,command,deviceid,output):
		"Sends a command to a service on the hub."
		if output == "debug":
			print datetime.datetime.now() , "---> sendCommand (",self.sessionTicket,",",service,",",command,",",deviceid,") "
		
		result = self.xmlrpc.sendCommand( self.sessionTicket, service, command, deviceid )
		
		if output == "debug":
			print datetime.datetime.now() , "---> Received:", result
		
		return result;


    ## Hub Actions

	# We just use this to get the hub name, as AlertMe only seem to associate one hub per account.
	def getAllHubs(self, output):
		"Returns all hubs associated with the logged in user."
		if output == "debug":
			print datetime.datetime.now() , "---> getAllHubs( ", self.sessionTicket, ")"
        
		result = self.xmlrpc.getAllHubs( self.sessionTicket )
        
		if output == "debug":

			print datetime.datetime.now() , "---> Received:", result
	
		elif output == "human":
			
			print "   getAllHubs:"
			for i in result.split(","):
				print "       " , i.split("|")[0]," (",i.split("|")[1],")"
	
		else:

			return result

	# Retained in case it's needed, but with only one hub per account, there's not much point implementing it right now.
	def setHub(self, hubid):
		"Once this method has been called, subsequent API commands in the session will operate on the specified hub."
		if output == "debug":
			print datetime.datetime.now() , "---> setHub( ", self.sessionTicket, ",", hubid , ")"
        
		result = self.xmlrpc.setHub( self.sessionTicket, hubid )
        
		if output == "debug":
			print datetime.datetime.now() , "---> Received:", result
        
		return result
	
	# This is used to grab hub status information.
	def getHubStatus(self, output):
		"Requests status information for the hub."
		if output == "debug":
			print datetime.datetime.now() , "---> getHubStatus( ", self.sessionTicket, ")"
        
		result = self.xmlrpc.getHubStatus( self.sessionTicket )
        
		if output == "debug":

			print datetime.datetime.now() , "---> Received:", result
        
		elif output == "human":

			print "   getHubStatus:"
			for i in result.split(","):
				print "       " , i.split("|")[0],"=",i.split("|")[1]

		return result

	# Return a specified number of entries from the event log.
	def getEventLog(self, service, numEntries, start, end, localiseTimes , output ):
		"Returns entries from the event log."
		if output == "debug":
			print datetime.datetime.now() , "---> getEventLog( ", self.sessionTicket, "," , service , "," , numEntries , "," , start , "," , end , "," , localiseTimes , ")"
		
		result = self.xmlrpc.getEventLog( self.sessionTicket, service, numEntries, start, end, localiseTimes )
		
		if output == "debug":
			print datetime.datetime.now() , "---> Received:", result
		
		if output == "human":
			print "   getEventLog (" , service, "," , numEntries , "," , start , "," , end , "," , localiseTimes , ")"
			for i in result.split(","):
				print "       " , i
		
		return result
	
	# See what behaviour modes we can put this hub into.
	def getAllBehaviours(self, output):
		"Returns all possible behaviours for the hub."
		if output == "debug":
			print datetime.datetime.now() , "---> getAllBehaviours( ", self.sessionTicket, ")"
		
		result = self.xmlrpc.getAllBehaviours( self.sessionTicket )
		
		if output == "debug":
			print datetime.datetime.now() , "---> Received:", result
		
		if output == "human":
			print "   getAllBehaviours:"
			for i in result.split(","):
				print "       " , i
		
		return result
	
	# See which behaviour mode the hub is in right now.
	def getBehaviour(self, output):
		"Returns the current behaviour mode of the hub."
		if output == "debug":
			print datetime.datetime.now() , "---> getBehaviour( ", self.sessionTicket, ")"
		
		result = self.xmlrpc.getBehaviour( self.sessionTicket )
		
		if output == "debug":
			print datetime.datetime.now() , "---> Received:", result
		
		if output == "human":
			print result
		
		return result
	
	# See which services are active on the hub.
	def getAllServices(self, output):
		"Returns all services enabled for the hub."
		if output == "debug":
			print datetime.datetime.now() , "---> getAllServices( ", self.sessionTicket, ")"
		
		result = self.xmlrpc.getAllServices( self.sessionTicket )
		
		if output == "debug":
			print datetime.datetime.now() , "---> Received:", result
		
		if output == "human":
			print "   getAllServices:"
			for i in result.split(","):
				print "       " , i
		
		return result
	
	# See what states the active services on the hub can be set to.
	def getAllServiceStates(self,service,output):
		"Returns all possible states for a specified service."
		if output == "debug":
			print datetime.datetime.now() , "---> getAllServiceStates( ", self.sessionTicket, "," , service , ")"
		
		result = self.xmlrpc.getAllServiceStates( self.sessionTicket, service )
		
		if output == "debug":
			print datetime.datetime.now() , "---> Received:", result
		
		if output == "human":
			print "   getAllServiceStates (" , service, ")"
			for i in result.split(","):
				print "       " , i
		
		return result
	
	# See what state an active service on the hub is in right now. 
	def getCurrentServiceState(self,service,output):
		"Requests the current state for either a single named service or all available services if 'all' is specified."
		if output == "debug":
			print datetime.datetime.now() , "---> getCurrentServiceState( ", self.sessionTicket, "," , service , ")"
		
		if service == "all":
			result = self.xmlrpc.getCurrentServiceState( self.sessionTicket )
		else:
			result = self.xmlrpc.getCurrentServiceState( self.sessionTicket, service )
		
		if output == "debug":
			print datetime.datetime.now() , "---> Received:", result
		
		if output == "human":
			print "   getCurrentServiceState (" , service, ")"
			if ( service == "all" ):
				for i in result.split(","):
					print "       " , i.replace("|", " is ")
			else:
				print result
		
		return result
			

	## Device Actions
	
	# Show a list of all of the devices.
	def getAllDevices(self,output):
		"Returns a list of all devices in the system."
		if output == "debug":
			print datetime.datetime.now() , "---> getAllDevices( ", self.sessionTicket, ")"
		
		result = self.xmlrpc.getAllDevices( self.sessionTicket )
		
		if output == "debug":
			print datetime.datetime.now() , "---> Received:", result
		
		if output == "human":
			
			print "   getAllDevices"
			devicelist = []
			for d in result.split(","):
				devicelist.append(d)
				
			for i in sorted(devicelist):
				print "      " + i

		return result
	
	# Retrieve some details about a device. Only seems to get the software version.
	def getDeviceDetails(self,deviceid,output):
		"Returns details about a particular device."
		if output == "debug":
			print datetime.datetime.now() , "---> getDeviceDetails( ", self.sessionTicket, "," , deviceid , ")"
		
		result = self.xmlrpc.getDeviceDetails( self.sessionTicket, deviceid )
		
		if output == "debug":
			print datetime.datetime.now() , "---> Received:", result
		
		if output == "human":
			print "   getDeviceDetails (" , deviceid, ")"
			for i in result.split(","):
				print "       " , i
		
		return result
			
	# Shows which data channels are available on a device.
	def getAllDeviceChannels(self,deviceid,output):
		"Returns the data channels available on a device."
		if output == "debug":
			print datetime.datetime.now() , "---> getAllDeviceChannels( ", self.sessionTicket, "," , deviceid , ")"
		
		result = self.xmlrpc.getAllDeviceChannels( self.sessionTicket, deviceid )
		
		if output == "debug":
			print datetime.datetime.now() , "---> Received:", result
		
		if output == "human":
			print "   getAllDeviceChannels (" , deviceid, ")"
			for i in result.split(","):
				print "       " , i
		
		return result

	# Gets the current values for specified data channels. We don't implement this because of a bug with sub-zero temperatures and 
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
			print datetime.datetime.now() , "---> Received:", result

		if output == "human":
			if ( channel == '' ):
				print "   getDeviceChannelValue (" , deviceid, ")"
			else:
				print "   getDeviceChannelValue (" , deviceid, ",", channel, ")"
			
			print "       " , result

		return result

	# Retrieve pretty much everything about every device. This is the most useful option.
	def getAllDeviceChannelValues(self,output):
		"Returns the current values for all available channels on all devices."
		if output == "debug":
			print datetime.datetime.now() , "---> getAllDeviceChannelValues( ", self.sessionTicket, ")"
		
		result = self.xmlrpc.getAllDeviceChannelValues( self.sessionTicket )
		
		if output == "debug":
			print datetime.datetime.now() , "---> Received:", result
		
		if output == "human":
			print "   getAllDeviceChannelValues:"
			#return result.replace(',','\n')
			valueslist = []
			for d in result.split(","):
				valueslist.append(d)
			
			for i in sorted(valueslist):
				print "      " + i
		
		return result

	# Return a specified number of entries from the device log.
	def getDeviceChannelLog(self,deviceid,channel,numEntries,start,end,output):
		"Returns logged values from a device for a specific data channel."
		if output == "debug":
			print datetime.datetime.now() , "---> getDeviceChannelLog( ", self.sessionTicket, "," , deviceid , "," , channel , "," , numEntries , "," , start , "," , end , ")"
		
		result = self.xmlrpc.getDeviceChannelLog( self.sessionTicket, deviceid, channel, numEntries, start, end )
		
		if output == "debug":
			print datetime.datetime.now() , "---> Received:", result
		
		if output == "human":
			print "   getDeviceChannelLog (" , deviceid , "," , channel , "," , numEntries , "," , start , "," , end , ")"
			for i in result.split(","):
				print "       " , i
		
		return result

	# Return a specified number of entries from the tracking log.
	def getTrackingData( self, deviceid, numEntries, start, end, localiseTimes , output):
		"Returns tracking information for a given device."
		if output == "debug":
			print datetime.datetime.now() , "---> getTrackingData( ", self.sessionTicket, "," , deviceid , "," , numEntries , "," , start , "," , end , "," , localiseTimes , ")"
		
		result = self.xmlrpc.getTrackingData( self.sessionTicket, deviceid, numEntries, start, end, localiseTimes )
		
		if output == "debug":
			print datetime.datetime.now() , "---> Received:", result
		
		if output == "human":
			print "   getEventLog (" , deviceid, "," , numEntries , "," , start , "," , end , "," , localiseTimes , ")"
			for i in result.split(","):
				print "       " , i
		
		return result



if __name__ == '__main__':
	
	alertme = AlertMePy()
	main()
