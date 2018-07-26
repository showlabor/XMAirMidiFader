#!/usr/bin/env python

#  Copyright (C) 2018 Felix Homann
#
#  This file is part of XMAirMidiFader.
#
#  XmrMidiFader is free software; you can redistribute it and/or
#  modify it under the terms of the GNU General Public License
#  as published by the Free Software Foundation; either version 2.1
#  of the License, or (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with XMAirMidiFader. If not, see <http://www.gnu.org/licenses/>.

import mido
import liblo
import time

# User data. Change these to adjust to your setup!
# You might want to look at the ouput of mido.get_input_names() to find
# the right port number
MIDI_PORT = 2
MIDI_CONTROL = 2 # Adjust!!!
MIDI_MIN = 0.0   # minimum value of the MIDI control
MIDI_MAX = 127.0 # maximum value of the MIDI control
XAIR_IP_ADDRESS = "192.168.178.52" # Adjust to your mixer console


# Some constants
XAIR_PORT = 10024
XAIR_FADER_PATH = "/lr/mix/fader"
XAIR_SUBSCRIPTION_PATH = "/xremote"
XAIR_SUBSCRIPTION_TIMEOUT = 8

# Global variables
xair_cur_idx = 0  # negative number: no values received yet
midi_cur_idx = 0  # negative number: no values received yet
midi_old_idx = 0  # negative number: no values received yet


# Helper function to calculate internal index of float fader value
def indexFromFloat(fvalue):
    # Number of fade level steps
    steps = 1024

    # clip fvalue to allowed [0.0, 1.0] interval
    if fvalue > 1.0:
        fvalue = 1.0
    elif fvalue < 0:
        fvalue = 0.0

    # index rounding according to private message from Jan Duwe @ Behringer. Thanks!
    idx = int(fvalue * (steps - 1 + 0.5))
    return idx


## Setup OSC server
try:
    server = liblo.ServerThread()
except liblo.ServerError as err:
    print(err)
    exit()

# Add listener for fader value
def xair_fader_callback(path, args):
    global xair_cur_idx
    xair_cur_idx = indexFromFloat(args[0])

server.add_method(XAIR_FADER_PATH, 'f', xair_fader_callback)
server.start()


# Adjust the ip address for your mixer console
xair = liblo.Address(XAIR_IP_ADDRESS, XAIR_PORT, liblo.UDP)

# Query current fader value
server.send(xair, XAIR_FADER_PATH)

# Callback to handle MIDI messages
def midi_callback(midi_msg):
    global MIDI_CONTROL, MIDI_MAX, MIDI_MIN
    global server
    global midi_cur_idx, midi_old_idx, xair_cur_idx

    # Exit early if it's not the right control
    if midi_msg.type != 'control_change' or midi_msg.control != MIDI_CONTROL:
        return

    midi_old_idx = midi_cur_idx
    midi_cur_val = midi_msg.value / (MIDI_MAX - MIDI_MIN)
    midi_cur_idx = indexFromFloat(midi_cur_val)

    # TODO: I'm pretty sure the following conditions can be simplified.
    # Too lazy to think about it right now ;-)
    if (midi_cur_idx >= midi_old_idx):
        velocity = midi_cur_idx - midi_old_idx
    else:
        velocity = midi_old_idx - midi_cur_idx

    # Only send out new midi value if it's reasonably close to the last known value on the
    # mixer. "Reasonably close" as estimated by the fader velocity.
    if ((midi_cur_idx >= xair_cur_idx and (midi_cur_idx - xair_cur_idx) < 2 * velocity) or
        (midi_cur_idx <= xair_cur_idx and (xair_cur_idx - midi_cur_idx) < 2 * velocity)) :
        server.send(xair, XAIR_FADER_PATH, midi_cur_val)


# Open MIDI port.
try:
    port = mido.open_input(mido.get_input_names()[MIDI_PORT])
    # Set callback
    port.callback = midi_callback
    print("Opened MIDI device: " + port.name)
except:
    print("Oops! Input device not available.")
    exit()

# Main loop. Just send regular subscription requests to the mixer
while True:
    server.send(xair, XAIR_SUBSCRIPTION_PATH)
    time.sleep(XAIR_SUBSCRIPTION_TIMEOUT)
