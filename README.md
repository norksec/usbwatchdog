# usbWatchdog

# What is it?

usbWatchdog monitors for changes with your USB ports. If a change is detected, it will execute various commands, before wiping the RAM and shutting down the machine.

# Requirements

sdmem (apt-get install secure-delete)

- Python packages:

argparse

xxtea

pyudev

    pip3 install xxtea pyudev argparse

# Usage

    python3 usbwatchdog.py -e (file containing names of files to encrypt) | -d (file containing names of files to decrypt) | -n (file containing names of files to delete)

# About

Encryption is handled by the xxtea package - it may not be the most secure encryption in the world, but it's infinitely faster than trying to AES encrypt your data in a hurry before shutting down. Time is of the essence, and we couldn't afford to wait for a more secure encryption method. Use at your own risk.

Memory wiping is handled by secure-delete, again with the fastest options available (-llf). This is the least secure option for secure-delete but, again, speed is everything and we don't have ten minutes to wait while it writes it with random garbage.

The nuclear option is there to make sure your shit is gone before shutdown. That simple. Requires a list of filenames - won't work with a list of directories (yet.)

# Why? What can it be used for?

The why is simple - proof of concept. This was a mental exercise for myself to see if I could even do it. I wrote the basic program in an afternoon.

As for the uses - use your imagination. If someone gets a hold of your machine and tries to install something from a usb drive, or use a Rubber Ducky on it, or even tries to copy your data onto a flash drive, this will shut that down fast.

If your machine is encrypted or has a BIOS password, this should stop them in their tracks.

# Future plans/ideas/possibilities

I'm also interested in including the ability to use a paired Bluetooth device instead of a usb device - so if your device is paired to your machine, and the device (or you with the device) are removed from the immediate area the machine wipes and shuts down.

If you have any ideas or suggestions, let me know.
