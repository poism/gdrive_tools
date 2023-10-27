#!/usr/bin/python
""" poism_folderBasedRename.py
	Required args: /path/to/startFolder/
        Optional args: --keep-sequence = Keeping sequences in filenames eg. DCIM_001 keeps 001
        Optional args: --skip-hash = Skip md5 hashing
        Optional args: --hash-only = Keep original name, just append md5 hash
        Optional args: --use-mod-time = Use modified timestamp for naming
        Optional args: --keep-folder-name = Use original folder names for naming
        Optional args: --strict-folder-name = Use strict alphanumeric from folders (else -_. symbols are retained)
	All files below the startFolder will be renamed based on their parents
	and with the first characters from the md5 hash of the file itself.
	eg. startFolder/Some Folder/file.jpeg
	--> startFolder/Some Folder/startFolder_SomeFolder.2254d5.jpg
	Junk files and empty null files will be deleted.
	A timestamped csv log will be saved in the startingDirectory.
	Written by Sherab Sangpo Dorje ( po@poism.com )
"""
import os, sys, re, hashlib, csv, string, datetime, time

theDate = datetime.datetime.now().strftime("%Y%m%d_%H%M%S");
startPaths = []
startPath = "" #global passed in as arg
rootDirName = "" #global set based on startPath
outFileName = "renamed-"+theDate+".csv"
outFile = None
outWriter = None
outFileOpen = False
keepSequence = False
keepFolderName = False
strictFolderName = False
skipHash = False
hashOnly = False
useModTime = False


# Only the following file extensions will be processed
fileTypesToProcess = {
	'image': [ 'jpg', 'tga', 'tif', 'bmp', 'gif', 'png' ],
	'video': [ 'mp4', 'mov', 'mpg', 'wmv', 'flv', 'webm', 'avi', 'mkv', 'ogm' ],
	'audio': [ 'mp3', 'ogg', 'wav', 'wma', 'wmv' ]
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

def upper_replace(match):
    pre = match.group(1)
    post = match.group(3)
    if pre.isspace():
        pre = "_"
    if post.isspace():
        post = "_"
    return pre+match.group(2).upper()+post # _NYC-

def sanitize(str):
        global keepFolderName,strictFolderName
        if not keepFolderName:
            #note we are not replacing "/" here...
            str = re.sub('(?!^)([A-Z][a-z]+)', r' \1', str) #make "/CrazyFolder/! bad SUBFOLDER-0/file" into "/ Crazy Folder/! bad SUBFOLDER-0/file"
            if strictFolderName:
                str = re.sub(r'[^a-zA-Z0-9/]+', ' ', str) #result: "/ Crazy Folder/  bad SUBFOLDER 0/file"
            else:
                str = re.sub(r'[^\-\_\.a-zA-Z0-9/]+', ' ', str) #result: "/ Crazy Folder/  bad SUBFOLDER-0/file"

            parts = str.split(os.path.sep)
            for (p,part) in enumerate(parts):
            	# process individual folder names, if folder is all CAPS we will retain that, otherwise will Capitalize
            	if not part.isupper(): 
                    allcaps = re.findall(r'[-_. ]([A-Z][A-Z]?[A-Z])[-_. ]', part) # except we will also retain 2-3 character all caps codes, eg. NYC NY NM etc. FIXME: bug occurs if you have adjacent sets of matches, eg. -NM-NYC-AZ- would result in -NM-Nyc-AZ- 
	    	    parts[p] = part.title() #result: "/ Crazy Folder/  Bad Subfolder 0/File"
                    for caps in allcaps:
                        # caps[0] = [-_. ] , caps[1] = CAPS, caps[2] = [-_.]
                        parts[p] = re.sub(r'([-_. ])('+caps.title()+')([-_. ])', upper_replace, parts[p]) #, 1)
	    		
	    str = os.path.join('',*parts) #put it back together
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


def getNewName(hash, name, ext, relPath,modTime):
        global keepSequence,skipHash,hashOnly
        if hashOnly:
            newName = name
        else:
	    newName = sanitize( relPath )
            if keepSequence:
                foundSequence = re.match(r'.*?([0-9]+)$', name)
                if foundSequence:
                    foundSequence=foundSequence.group(1)
                    newName = newName +"-"+ foundSequence

	    newName = newName.replace('/', '_')

        if skipHash:
            newName = newName + ext
        else:
            newName = newName + "." + hash[0:6] + ext # trim hash to first 6 chars

        if modTime:
            modTime = datetime.datetime.fromtimestamp(modTime)
            timeStr = modTime.strftime('%Y%m%d%H%M%S')
            print "FIXME: applying modified time to filenames not yet implemented"
            print timeStr

        print "Processing: "+name +" --> "+newName
	return newName


def processFile(path, fileName, relPath):
	#print("Processing "+f)
        global skipHash, useModTime
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

        if not skipHash:
	    hash = md5( filePath )

	unwantedFile = True if unwantedFile else checkIfUnwanted('md5', hash)

	if unwantedFile:
		action = "delete"
		value = unwantedFile
		return action, value, hash


        if useModTime:
            modTime = os.path.getmtime(filePath)
        else:
            modTime = False

	newName = getNewName(hash, name, newExt, relPath, modTime)
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

def printHelp():
	print ('''
        Required args: /path/to/startFolder/
        Optional args: --keep-sequence = Keeping sequences in filenames eg. DCIM_001 keeps 001
        Optional args: --skip-hash = Skip md5 hashing
        Optional args: --use-mod-time = Use modified timestamp for naming
        Optional args: --keep-folder-name = Use original folder names for naming
        Optional args: --strict-folder-name = Use strict alphanumeric from folders (else -_. symbols are retained)
	All files below the startFolder will be renamed based on their parents
	and with the first characters from the md5 hash of the file itself.
	eg. startFolder/Some Folder/file.jpeg
	--> startFolder/Some Folder/startFolder_SomeFolder.2254d5.jpg
	Junk files and empty null files will be deleted.
	A timestamped csv log will be saved in the startingDirectory.
        ''')


def main():
	global startPaths, startPath, rootDirName, outFileName, outFileOpen, outFile, keepSequence, keepFolderName, strictFolderName, skipHash, hashOnly, useModTime
        argList = sys.argv[1:]
	try:

            if not argList:
                printHelp()
                sys.exit(1)

            for curArg in argList:
                if curArg in ("--help", "-h"):
                    printHelp()
		    sys.exit(0)
                elif curArg in ("--keep-sequence"):
                    keepSequence = True
                elif curArg in ("--keep-folder-name"):
                    keepFolderName = True
                elif curArg in ("--strict-folder-name"):
                    strictFolderName = True
                elif curArg in ("--skip-hash"):
                    skipHash = True
                elif curArg in ("--hash-only"):
                    hashOnly = True
                elif curArg in ("--use-mod-time"):
                    useModTime = True
                  
                else:
                    startPaths.append(curArg)

	except:
		print "Requires argument of starting directory be provided!"
		sys.exit(1)


        print "Selected paths:"
        for p in startPaths: print p
        if keepFolderName: print "--keep-folder-name = Keeping original folder names"
        if strictFolderName: print "--strict-folder-name = Use strict alphanumeric from folders (else -_. symbols are retained)"
        if keepSequence: print "--keep-sequence = Keeping sequences in filenames"
        if skipHash: print "--skip-hash = Skip md5 hashing"
        if useModTime: print "--use-mod-time = Use modified timestamp for naming"

        if not confirm("Do you want to proceed?"):
	    print("Exiting...")
            sys.exit(0)


        for startPath in startPaths:
	    startPath = os.path.abspath(startPath)
            if not (os.path.isdir(startPath)):
                print "Error: "+startPath+" does not exist!"
		sys.exit(1)

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
