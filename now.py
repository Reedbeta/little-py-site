#!/usr/bin/python3
import os, time;
timestr = time.strftime('Date: %Y-%m-%d %H:%M:%S %z')
print(timestr)

try:
	import pyperclip
	pyperclip.copy(timestr)
	print('(copied to clipboard)')
except:
	print('(no clipboard support available)')

if os.name == 'nt':
	os.system('pause')
