#!/usr/bin/env python3

import argparse
import binascii
from pyfiglet import Figlet
from getpass import getpass
import os
import pyudev
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
	os.popen("shutdown -h now")


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
			panicButton()
			os._exit(1)
		else:
			panicButton()
			os._exit(1)


def main():
	parser = argparse.ArgumentParser(prog='usbwatchdog.py', description='monitor your usb ports for activity and wipe ram/shutdown if anything is plugged in or removed.')
	group = parser.add_mutually_exclusive_group()
	group.add_argument('-d', '--decrypt', type=str, help='decrypt files from a list, requires directory and filename of list (e.g.: ./files.txt).')
	group.add_argument('-e', '--encrypt', type=str, help='encrypt files from a list when watchdog executes, requires directory and filename of list (e.g., ./files.txt) - will ask for encryption key and then start watchdog.')
	args = parser.parse_args()
	global encFlag, userKey, encFile, decFile
	encFlag = False
	if (args.decrypt == None) and (args.encrypt == None):
		encFlag = False
		watchdog(encFlag)
	elif not args.decrypt == None:
		decFile = os.path.expanduser(args.decrypt)
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
	elif not args.encrypt == None:
		encFile = os.path.expanduser(args.encrypt)
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
