# XMAirMidiFader #

This is a small Python example that shows how to control a fader of Behringer (c) X Air or Midas (c) M Air mixers.
You need to adjust change the mixers IP address and choose the right MIDI control. Have fun with it!

## Dependencies

XMAirMidiFader uses [Mido](http://mido.readthedocs.io/en/latest/) and [python-rtmidi](https://github.com/SpotlightKid/python-rtmidi) for MIDI. OSC communication is handled by [pyliblo](https://github.com/dsacre/pyliblo) for OSC communication. You can install all of them via pip, i.e. `pip install --user mido pyliblo python-rtmidi`.

Those packages have their own dependencies. For instance, you need to have Cython and [liblo](https://github.com/radarsat1/liblo) installed. Please, check the respective documentations.

## Configure
As this is just an example project the mixer's IP address and the MIDI controllers name/index and control number are hard coded. You need to adjust some parameters to work in your environment

## What it does
XMAirMidiFader works by subscribing to the X/M Air mixer and listening to changes of the main fader. The subscription is periodically refreshed. Thus XMAirMidiFader always knows the current fader value on the mixer.
It listens for changes of the connected MIDI control. If the change occurs close to the current fader value on the mixer the fader value will be updated by sending a new value to the mixer. The notion of 'close' depends on the velocity of the MIDI fader being moved.
