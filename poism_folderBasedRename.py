#!/usr/bin/python
""" poism_folderBasedRename.py
	Required args: /path/to/startFolder/
	All files below the startFolder will be renamed based on their parents
	and with the first characters from the md5 hash of the file itself.
	eg. startFolder/Some Folder/file.jpeg
	--> startFolder/Some Folder/startFolder_SomeFolder.2254d5.jpg
	Junk files and empty null files will be deleted.
	A timestamped csv log will be saved in the startingDirectory.
	Written by Sherab Sangpo Dorje ( po@poism.com )
"""
import os, sys, re, hashlib, csv, string, datetime

theDate = datetime.datetime.now().strftime("%Y%m%d_%H%M%S");
startPath = "" #global passed in as arg
rootDirName = "" #global set based on startPath
outFileName = "renamed-"+theDate+".csv"
outFile = None
outWriter = None
outFileOpen = False

# Only the following file extensions will be processed
fileTypesToProcess = {
	'image': [ 'jpg', 'tga', 'tif', 'bmp', 'gif', 'png' ],
	'video': [ 'mp4', 'mov', 'mpg', 'wmv', 'flv', 'webm' ]
}
# The following defines what types of files to delete if found
unwantedFiles = {
	'extension': [ 'tmp' ],
	'startswith': [ '._' , '__MACOSX' , '.DS_Store' , 'Thumbs.db' ],
	'md5': [ 'd41d8cd98f00b204e9800998ecf8427e' ] #null file
}

def clearTerminal():
	os.system('cls' if os.name == 'nt' else 'clear')

def md5(fileName):
	with open(fileName) as targetFile:
		md5res = hashlib.md5(targetFile.read()).hexdigest()
	return md5res


def sanitize(str):
	#note we are not replacing "/" here...
	str = re.sub('(?!^)([A-Z][a-z]+)', r' \1', str) #make "/CrazyFolder/! bad SUBFOLDER-0/file" into "/ Crazy Folder/! bad SUBFOLDER-0/file"
	str = re.sub(r'[^a-zA-Z0-9/]+', ' ', str) #result: "/ Crazy Folder/  bad SUBFOLDER 0/file"
	str = str.title() #result: "/ Crazy Folder/  Bad Subfolder 0/File"
	str = re.sub(r"\s+", '', str) #remove all spaces, result: "/CrazyFolder/BadSubfolder0/File"
	return str #re.sub(r'[^a-zA-Z0-9_\-]+', '', str)


def processExtension(ext):
	ext = ext.lower()[1:]
	# List of extensions that should be normalized to the key:
	fix = {
		'jpg': [ 'jpg', 'jpeg' ],
		'tga': [ 'tga', 'targa', 'icb', 'vda', 'vst', 'pix' ],
		'tif': [ 'tif', 'tiff' ],
		'mpg': [ 'mpg', 'mpeg', 'mpe' ]
	}
	for k in fix:
		if ext in fix[k]:
			ext = k

	for type in fileTypesToProcess:
		if ext in fileTypesToProcess[type]:
			return "." + ext

	return False


def checkIfUnwanted(criteria,value):
	if criteria == 'extension':
		for v in unwantedFiles[criteria]:
			if value.replace('.','') == v:
				return criteria + ' = ' + v
	elif criteria == 'startswith':
		for v in unwantedFiles[criteria]:
			if value.startswith(v):
				return criteria + ' = ' + v
	elif criteria == 'md5':
		for v in unwantedFiles[criteria]:
			if v == value:
				return criteria + ' = ' + v
	else:
		return False


def getNewName(hash, name, ext, relPath):
	newName = sanitize( relPath )
	newName = newName.replace('/', '_') + "." + hash[0:6] + ext # trim hash to first 6 chars
	return newName


def processFile(path, fileName, relPath):
	#print("Processing "+f)
	name, ext = os.path.splitext(fileName)
	newExt = processExtension(ext)
	hash = ""
	unwantedFile = checkIfUnwanted('extension', ext)
	unwantedFile = unwantedFile if unwantedFile else checkIfUnwanted('startswith', fileName)

	if unwantedFile:
		action = "delete"
		value = unwantedFile
		return action, value, hash

	if not newExt:
		action = "skip"
		value = "Ignored filetype: " + ext
		return action, value, hash

	filePath = path + "/" + fileName

	hash = md5( filePath )
	unwantedFile = True if unwantedFile else checkIfUnwanted('md5', hash)

	if unwantedFile:
		action = "delete"
		value = unwantedFile
		return action, value, hash

	newName = getNewName(hash, name, newExt, relPath)
	newFilePath = path + "/" + newName

	if not os.path.exists(newFilePath):
		action = "rename"
		value = newName
	else:
		action = "error"
		value = "New name " + newName + " already exists!"

	return action, value, hash


def logAction(action, relPath, hash, fileName, newName=''):
	global outFileOpen, outFileName, outFile, outWriter
	if not outFileOpen:
		outFile = open(outFileName, 'a')
		outWriter = csv.writer(outFile)
		outFileOpen = True
		outWriter.writerow( list( [ "Action", "Folder", "FileName", "NewName", "MD5 Hash" ] ) )

	row = list( [ action, relPath, fileName, newName, hash ] )
	print(row)
	outWriter.writerow( row )


def applyActions(actions, absPath, relPath):
	for type in ['delete', 'rename', 'error', 'skip']:
		for v in actions[type]:
			if type == 'delete':
				os.remove(absPath + '/' + v['fn'])
				logAction(type, relPath, v['hash'], v['fn'], '')
			elif type == 'rename':
				os.rename(absPath + '/' + v['fn'], absPath + '/' + v['value'])
				logAction(type, relPath, v['hash'], v['fn'], v['value'])


def confirm(question, continueOnEmpty=False):
	if continueOnEmpty:
		question = question + " (ENTER key) "
	else:
		question = question + " y/n:"
	while True:
		choice = raw_input(question).lower()
		if choice in ['yes', 'y']:
			return True
		elif choice in ['no', 'n']:
			return False
		elif not continueOnEmpty:
			print "WARNING: You did not answer 'yes' or 'no'! We are assuming YES, are you sure?"
			question = "Press ENTER again to confirm YES or type 'no'.\n"
			continueOnEmpty = True
		else:
			return True

def formatTitle(title, length=0):
	if length == 0:
		length = len(title)
		hr = ( "=" * length )
		print( "\n" + hr + "\n" + title + "\n" + hr)
		return length
	else:
		hr = ( "-" * (length/2 - len(title)/2))
		txt = hr + title + hr
		txt = txt if length - len(txt) == 0 else txt + "-"
		print("\n" + txt)


def walkDirs(path, level=None):
	clearTerminal();
	titleLength = formatTitle("Exploring " + path)
	pendingActions = False
	seriousActions = False
	actions = { 'rename': [], 'delete': [], 'error': [], 'skip': [] }
	fileList = [];
	dirList = [];
	relPath = rootDirName + path.replace(startPath, '')

	for itemName in os.listdir(path):
		itemPath = path + "/" + itemName
		if os.path.isfile(itemPath):
			fileList.append(itemName)
		else:
			dirList.append(itemName)

	for fileName in fileList:
		action, value, hash = processFile(path, fileName, relPath)
		actions[action].append({ 'hash': hash, 'fn': fileName , 'value': value })

	for type in ['rename', 'delete', 'error', 'skip']:
		if len(actions[type]):
			pendingActions = True
			if type == 'rename' or  type == 'delete':
				seriousActions = True

			formatTitle(type.upper(), titleLength)
		for v in actions[type]:
			sep = ' ---> ' if type == 'rename' else ' , because '
			print( type + ': ' + v['fn'] + sep + v['value'] )

	if seriousActions:
		formatTitle('CONFIRM', titleLength)
		if confirm("Do you want to apply these actions?"):
			formatTitle('LOG', titleLength)
			applyActions(actions, path, relPath)
		else:
			print("Skipping all actions in: " + path)
	elif not pendingActions:
		print("Nothing to do...")

	print("")
	if confirm('Press CTRL+c to Quit or continue to next folder.', True):
		for dirName in dirList:
			walkDirs(path + '/' + dirName)


def main():
	global startPath, rootDirName, outFileName, outFileOpen, outFile
	try:
		startPath = sys.argv[1]
	except:
		print "Requires argument of starting directory be provided!"
		sys.exit(1)

	startPath = os.path.abspath(startPath)
	rootDirName = os.path.basename(startPath)
	outFileName = startPath + '/' + outFileName

	walkDirs(startPath, 0)

	if outFileOpen:
		outFile.close()
		formatTitle("Log File: "+outFileName)
	else:
		formatTitle("Log File: Not created, no actions applied.")


if __name__ == "__main__":
	main()
