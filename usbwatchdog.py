#!/usr/bin/env python3

import argparse
import os
import subprocess
from getpass import getpass

import pyudev
import xxtea


def intro():
	print(""" _______        __________ ____  __.  _____________________________
 \      \   ____\______   \    |/ _| /   _____/\_   _____/\_   ___ \\
 /   |   \ /  _ \|       _/      <   \_____  \  |    __)_ /    \  \/
/    |    (  <_> )    |   \    |  \  /        \ |        \\     \____
\____|__  /\____/|____|_  /____|__ \/_______  //_______  / \______  /
        \/              \/        \/        \/         \/         \/
	\n""")
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


def watchdog(encFlag, nukeFlag):
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
		elif nukeFlag == True:
			input_file = open(nukeFile)
			for i in input_file.readlines():
				fileName = os.path.expanduser(i).strip('\n')
				print(' [*] Attempting to nuke file: ' + str(fileName))
				if not os.path.isfile(fileName):
					print(' [-] Error: file does not exist. Skipping...')
				else:
					try:
						os.remove(fileName)
						print(' [+] ' + fileName + ' successfully removed.')
					except:
						print(' [-] Unable to remove file.')
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
	group.add_argument('-n', '--nuke', type=str, help='deletes files from a list, requires directory and filename of list (e.g., ./files.txt) - the nuclear option, for when you just want everything gone before shutdown.')
	args = parser.parse_args()
	global encFlag, userKey, encFile, decFile, nukeFlag, nukeFile
	encFlag = False
	if (args.decrypt == None) and (args.encrypt == None) and (args.nuke == None):
		encFlag = False
		nukeFlag = False
		watchdog(encFlag, nukeFlag)
	elif not args.decrypt == None:
		decFile = os.path.expanduser(args.decrypt)
		if not os.path.isfile(decFile):
			print(' [-] Error: File list to decrypt does not exist. Exiting...')
			os._exit(1)
		else:
			verifyKey = False
			while verifyKey == False:
				userKey = getpass(" [*] Enter 16-character key: ")
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
			nukeFlag = False
			watchdog(encFlag, nukeFlag)
		else:
			print(' [*] Establishing key for file encryption. Key entered must be 16 characters long.')
			isSame = False
			while isSame == False:
				isSame = passPrompt()
				if isSame == False:
					print(' [-] Error with key entered.')
				else:
					print(' [+] Key set.')
			encFlag = True
			nukeFlag = False
			watchdog(encFlag, nukeFlag)
	elif not args.nuke == None:
		nukeFile = os.path.expanduser(args.nuke)
		if not os.path.isfile(nukeFile):
			print(' [-] File list to nuke does not exist. Disarming nuclear option...')
			encFlag = False
			nukeFlag = False
			watchdog(encFlag, nukeFlag)
		else:
			print(' [+] Nuclear option online - say Goodbye to Moscow.')
			encFlag = False
			nukeFlag = True
			watchdog(encFlag, nukeFlag)

if __name__ == '__main__':
	cls()
	intro()
	main()
