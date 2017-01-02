#!/usr/bin/env python3

import binascii
from pyfiglet import Figlet
from getpass import getpass
import os
import optparse
import pyudev
#from simplecrypt import encrypt, decrypt
import subprocess
import sys
import xxtea

def intro():
	f = Figlet(font='graffiti')
	print(f.renderText("NoRKSEC"))
	print('usbWatchdog.py - (c) 2017 NoRKSEC - no rights reserved\n')


def cls():
	os.system("cls" if os.name == "nt" else "clear")


def panicButton():
	subprocess.call("sdmem -llf", shell="TRUE")
	os.popen("reboot")


def encryptFile(fname, key):
	uKey = bytes(key, encoding='utf-8')
	with open(fname, 'r+b') as input:
		plaintext = input.read()
		ciphertext = xxtea.encrypt(plaintext, uKey)
		input.seek(0)
		input.write(ciphertext)
		input.truncate()
		input.close()


def decryptFile(fname, key):
	uKey = bytes(key, encoding='utf-8')
	with open(fname, 'r+b') as input:
		ciphertext = input.read()
		plaintext = xxtea.decrypt(ciphertext, uKey)
		input.seek(0)
		input.write(plaintext)
		input.truncate()
		input.close()


def passPrompt():
	global userKey
	userKey = getpass(" [*] Enter key: ")
	checkKey = getpass(" [*] Re-enter key: ")
	verifyKey = False
	while verifyKey == False:
		if (len(userKey) != 16):
			print(' [-] Key must be 16 characters.')
			return False
		else:
			if userKey != checkKey:
				print(' [-] Keys do not match.')
				return False
			else:
				return True


def watchdog(encFlag):
	print(' [+] Starting usbWatchdog...')
	context = pyudev.Context()

	initList = []
	for device in context.list_devices(subsystem='usb'):
		initList.append(device)
	checkSum = False
	while (checkSum == False):
		checkList = []
		for device in context.list_devices(subsystem='usb'):
			checkList.append(device)
		for i in checkList:
			if not i in initList:
				checkSum = True
			else:
				pass
		for j in initList:
			if not j in checkList:
				checkSum = True
			else:
				pass
	if (checkSum == True):
		print(' [+] Shit is going down, hang on...')
		if encFlag == True:
			input_file = open(encFile)
			for i in input_file.readlines():
				fileName = os.path.expanduser(i).strip('\n')
				print(' [*] Attempting to encrypt file: ' + str(fileName))
				if not os.path.isfile(fileName):
					print(' [-] Error: file does not exist. Skipping...')
				else:
					encryptFile(fileName, userKey)
					print(' [+] Successfully encrypted file.')
			print(' [+] Finished encrypting file list.')
			#panicButton()
			os._exit(1)
		else:
			#panicButton()
			os._exit(1)


def main():
	parser = optparse.OptionParser('%prog -e <file list to encrypt> / %prog -d <file list to decrypt>')
	parser.add_option('-e', dest='encFile', type='string', help='Specify the list of files to encrypt. Will prompt for a key (must be 16 bytes), and encrypt the files before wiping RAM and rebooting if the watchdog is triggered.')
	parser.add_option('-d', dest='decFile', type='string', help='Specify the list of files to decrypt. Will prompt for a key (must be 16 bytes) and decrypt the files. This mode does not start the watchdog.')
	(options, args) = parser.parse_args()
	global encFlag, userKey, encFile, decFile
	encFlag = False
	if (options.encFile == None) and (options.decFile == None):
		encFlag = False
		watchdog(encFlag)
	elif (not options.encFile == None) and (not options.decFile == None):
		print(' [-] Error: Can not select encrypt and decrypt at the same time. Closing...')
		os._exit(1)
	elif (options.encFile == None) and (not options.decFile == None):
		decFile = options.decFile
		if not os.path.isfile(decFile):
			print(' [-] Error: File list to decrypt does not exist. Exiting...')
			os._exit(1)
		else:
			verifyKey = False
			while verifyKey == False:
				userKey = getpass(" [*] Enter key: ")
				if (len(userKey) == 16):
					verifyKey = True
				else:
					print(' [-] Key must be 16 characters long.')
					verifyKey = False
			input_file = open(decFile)
			for i in input_file.readlines():
				fileName = os.path.expanduser(i).strip('\n')
				print(' [*] Attempting to decrypt: ' + fileName)
				if not os.path.isfile(fileName):
					print(' [-] File does not exist. Skipping...')
					break
				else:
					try:
						decryptFile(fileName, userKey)
						print(' [+] File successfully decrypted.')
					except:
						print(' [-] Error decrypting file. Is the key correct?')
	elif (not options.encFile == None) and (options.decFile == None):
		encFile = options.encFile
		if not os.path.isfile(encFile):
			print(' [-] File list to encrypt does not exist. Skipping encryption...')
			encFlag = False
			watchdog(encFlag)
		else:
			print(' [*] Establishing key for file encryption.')
			isSame = False
			while isSame == False:
				isSame = passPrompt()
				if isSame == False:
					print(' [-] Error with key entered.')
				else:
					print(' [+] Key set.')
			encFlag = True
			watchdog(encFlag)

if __name__ == '__main__':
	cls()
	intro()
	main()