#!/usr/bin/env python3
import time
import cec
import threading

sonos_name = 'Family Room'
adapter_name = 'SonosAdapter'

known_volume = 0
known_mute = False
changed_volume = False
changed_mute = False
button_up = False
last_report = 0.0

def log_cb(level, time, message):
	# TODO: Could polish by hooking levels into proper python logging
	#print(f'log: {level} {time} {message}')
	return 0

def keypress_cb(key, duration):
	#print(f'key: {key} {duration}')
	return 0

def report_audio_status():
	global known_volume, known_mute
	status = hex(known_volume + (int(known_mute) * 128)).upper()[2:]
	libcec.Transmit(libcec.CommandFromString(f'5F:7A:{status}'))

def command_cb(cmd):
	global known_volume, known_mute, changed_volume, changed_mute, button_up
	#print(f'cmd: {cmd}')
	cmd = [int(i,16) for i in cmd.split()[1].split(':')]
	address = cmd.pop(0)
	# only handle commands coming from TV to audio system
	if not address == 0x05:
		return 0
	opcode = cmd.pop(0)

	if opcode == cec.CEC_OPCODE_GIVE_AUDIO_STATUS:
		# LibCEC python bindings can't handle "reply" status for Transmit,
		# so we cant handle this properly. just update the status out of band
		return 0

	# return from callback as quickly as possible to be responsive
	if opcode == cec.CEC_OPCODE_USER_CONTROL_PRESSED:
		button = cmd.pop(0)
		if button == cec.CEC_USER_CONTROL_CODE_MUTE:
			known_mute = not known_mute
			changed_mute = True
			button_up = False
		if button == cec.CEC_USER_CONTROL_CODE_VOLUME_DOWN:
			known_volume = known_volume - 1
			changed_volume = True
			button_up = False
		if button == cec.CEC_USER_CONTROL_CODE_VOLUME_UP:
			known_volume = known_volume + 1
			changed_volume = True
			button_up = False
	if opcode == cec.CEC_OPCODE_VENDOR_REMOTE_BUTTON_UP:
		button_up = True
	return 0

print('initializing sonos connection...')
import soco
sonos = soco.discovery.by_name(sonos_name)
now = time.time()
known_mute = sonos.mute
known_volume = sonos.volume
last_check = now

print('initializing libcec...')
cecconfig = cec.libcec_configuration()
cecconfig.strDeviceName = adapter_name
cecconfig.bActivateSource = 1
cecconfig.deviceTypes.Add(cec.CEC_DEVICE_TYPE_AUDIO_SYSTEM)
cecconfig.clientVersion = cec.LIBCEC_VERSION_CURRENT
cecconfig.SetLogCallback(log_cb)
cecconfig.SetKeyPressCallback(keypress_cb)
cecconfig.SetCommandCallback(command_cb)

libcec = cec.ICECAdapter.Create(cecconfig)

adapter_name = libcec.DetectAdapters()[0].strComName
libcec.Open(adapter_name)

# return first physical address libcec controls
def get_physical_addr():
	addresses = libcec.GetLogicalAddresses()
	for i in range(0, 15):
		if not addresses.IsSet(i):
			continue
		return libcec.GetDevicePhysicalAddress(i)

this_addr = get_physical_addr()
this_addr_s = f'{hex(this_addr >> 8 & 0xFF)[2:]}:{hex(this_addr & 0xFF)[2:]}'

# Best reference for decoding/encoding CEC commands:
# https://www.cec-o-matic.com/
# Request System Audio Control to this address
libcec.Transmit(libcec.CommandFromString(f'50:70:{this_addr_s}'))
# Set system audio mode on
libcec.Transmit(libcec.CommandFromString(f'50:72:01'))

report_audio_status()
unreported_change = False

print('monitoring...')
while True:
	time.sleep(0.2)
	now = time.time()

	if changed_volume:
		sonos.volume = known_volume
	if changed_mute:
		sonos.mute = known_mute
	if changed_volume or changed_mute:
		changed_volume = False
		changed_mute = False
		# wait until button up to report 
		if button_up:
			report_audio_status()
		else:
			unreported_change = True
		continue

	if unreported_change and button_up:
		unreported_change = False
		report_audio_status()

	# check sonos actual state every 15 seconds
	if (now - last_check) > 15.0:
		last_check = now
		known_volume = sonos.volume
		known_mute = sonos.mute
		last_report = now
		report_audio_status()

print('exiting!')
exit()
