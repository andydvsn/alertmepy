AlertMePy v0.01
===============

AlertMePy is a Python-based interface to the AlertMe home security and energy monitoring system, via their web API. It can be used directly, or imported into your own Python scripts. It's designed to reduce the initial hurdle of controlling and obtaining data from the AlertMe system, making it more straightforward to analyse your data and control your system.

Please note that while the AlertMe system is the backbone of both the Lowe's Iris and British Gas 'Safe & Secure' products, neither of these services currently provide an API interface. I would encourage you to contact the retailers of these products and request that this facility be added, as there is no good reason for its omission.

This script is just under development at the moment. Come back later and it should do more.

Installation
------------

You'll need Python v2.6.1 or later on your system; it may work with earlier versions, but has not been tested. If you're using Linux or Mac OS X then you will already have a version of Python installed. On Windows, you will need to visit http://www.python.org to download and install the language.

That's pretty much everything you need. Except for an AlertMe system, of course.

Usage
-----

	alertme.py [ options ]

Wherever possible, you should request as much data in one run as possible. It is much quicker to grab all the data you might need in one shot, rather than making multiple requests via the web API. This way it's also much less likely that you will bump into the server rate limiting.

### Authentication

To authenticate, AlertMePy needs your username and password. You can specify this in the script itself in the small configuration area, but if you prefer to hold your credentials separately, simply create a file containing your username on the first line and your password on the second. You can point AlertMePy to the file using the '-c' switch.

### Commands

You'll be able to send commands once I've written that bit.

Command options are always in uppercase, just to increase awareness that you are instructing your system to perform an action.

### Queries

There are a number of query options, which are described by issuing:

	alertme.py -h

The query options can be combined in a single invocation, with some options being dependant upon others. The more useful query options are shortened to single lowercase letters and output is transformed into alphabetical order and to lower case where applicable. Please note that some options, such as requesting a behaviour state, have a case-sensitive input (eg. --state=IntruderAlarm, and NOT --state=intruderalarm).

When imported as a module, calls return the exact response from the API. Case and alphabetisation are not altered.

Advanced
--------

AlertMePy contains all of the calls documented in the AlertMe Web API document, which can be downloaded here:

[AlertMe Web API Documentation v2.02](http://support.alertme.com/ics/support/DLRedirect.asp?fileNum=82326&deptID=5503 "AlertMe Web API Documentation v2.02")

However, it also contains a couple that are not documented and only appear in the example code posted by AlertMe:

[AlertMe Web API Example Code](https://api.alertme.com/webapi/test/v2/ "AlertMe Web API Example Code")

Supported calls are:

#### Account Actions
login
logout
getUserInfo
#### Hub Actions
getAllHubs
setHub
getHubStatus
getEventLog
getAllBehaviours
getBehaviour
getAllServices
getAllServiceStates
getCurrentServiceState
#### Device Actions
sendCommand
getAllDevices
getDeviceDetails
getAllDeviceChannels
getDeviceChannelValue
getAllDeviceChannelValues*
getDeviceChannelLog
getTrackingData*
	
Calls marked with an asterisk are those not documented.

The 'getTrackingData' call was marked as a temporary feature. However, as development on the original AlertMe system has long ceased and the documentation was written some five years ago, it is reasonably safe to assume that this option isn't going anywhere quickly.

### Notes

When generating it's own output, AlertMePy doesn't always use the calls that you might expect it to.

For example, when requesting values from a particular data channel on one device, AlertMePy will in fact use the undocumented 'getAllDeviceChannelValues' request. There are two reasons for this; firstly, there is a bug in 'getDeviceChannelValue' which will not cope with temperature readings below zero degrees. This is dealt with properly in 'getAllDeviceChannelValues'. Secondly, despite returning all values for all channels on all devices, 'getAllDeviceChannelValues' is the roughly the same speed as fetching only one value. This is because it only uses one request via the API; it is much more efficient to grab everything and parse the output, rather than calling the API over the web multiple times.

If you are importing AlertMePy, these are things you will need to take into account in your own script. All of the classes are there to be used, but choosing which are best for the job is over to you!

To Do
=====

* implement command options
* create useful options (eg. temperature readings) instead of fumbling through exact api call output
* parse the event log to figure out lengths of time in different behaviour modes
* presence / absence option for keyfobs
* a whole bunch of other stuff