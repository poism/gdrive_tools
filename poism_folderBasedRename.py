import os, sys, re, hashlib, csv, string, datetime

theDate = datetime.datetime.now().strftime("%Y%m%d_%H%M%S");
startPath = "" #global passed in as arg
rootDirName = "" #global set based on startPath

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


def md5(fileName):
	with open(fileName) as targetFile:
		md5res = hashlib.md5(targetFile.read()).hexdigest()
	return md5res

def sanitize(str):
	return re.sub(r'[^a-zA-Z0-9_\-]+', '', str)

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
	newName = sanitize( relPath.replace('/', '_') ) + "." + hash[0:6] + ext # trim hash to first 7 chars
	return newName

def processFile(path, fileName, relPath):
	#print("Processing "+f)
	name, ext = os.path.splitext(fileName)
	newExt = processExtension(ext)
	unwantedFile = False
	unwantedFile = unwantedFile if unwantedFile else checkIfUnwanted('extension', ext)
	unwantedFile = unwantedFile if unwantedFile else checkIfUnwanted('startswith', fileName)

	if unwantedFile:
		action = "delete"
		value = unwantedFile
		return action, value

	if not newExt:
		action = "skip"
		value = "Ignored filetype: " + ext
		return action, value

	filePath = path + "/" + fileName

	hash = md5( filePath )
	unwantedFile = True if unwantedFile else checkIfUnwanted('md5', hash)

	if unwantedFile:
		action = "delete"
		value = unwantedFile
		return action, value

	newName = getNewName(hash, name, newExt, relPath)
	newFilePath = path + "/" + newName

	if not os.path.exists(newFilePath):
		action = "rename"
		value = newName
	else:
		action = "error"
		value = "New name " + newName + " already exists!"

	return action, value

def applyActions(actions, path):
	for type in ['delete', 'rename', 'error', 'skip']:
		for v in actions[type]:
			if type == 'delete':
				os.remove(path + '/' + v['fn'])
			elif type == 'rename':
				os.rename(path + '/' + v['fn'], path + '/' + v['value'])

def confirm(question):
	while True:
		choice = raw_input(question).lower()
		if choice in ['yes', 'y']:
			return True
		elif choice in ['no', 'n']:
			return False
		else:
			print "Please answer 'yes' or 'no'\n"

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

def walkDirs(path):
	titleLength = formatTitle("Exploring " + path)
	pendingActions = False
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
		action, value = processFile(path, fileName, relPath)
		actions[action].append({ 'fn': fileName , 'value': value })

	for type in ['rename', 'delete', 'error', 'skip']:
		if len(actions[type]):
			pendingActions = True
			formatTitle(type.upper(), titleLength)
		for v in actions[type]:
			sep = ' ---> ' if type == 'rename' else ' , because '
			print( type + ': ' + v['fn'] + sep + v['value'] )

	if pendingActions:
		formatTitle('CONFIRM', titleLength)
		if confirm("Do you want to apply these actions? y/n: "):
			applyActions(actions, path)
		else:
			print("Skipping all actions in: " + path)
	else:
		print("Nothing to do...")

	for dirName in dirList:
		walkDirs(path + '/' + dirName)


def main():
	global startPath, rootDirName
	try:
		startPath = sys.argv[1]
	except:
		print "Requires argument of starting directory be provided!"
		sys.exit(1)

	startPath = os.path.abspath(startPath)
	rootDirName = os.path.basename(startPath)

	walkDirs(startPath)

if __name__ == "__main__":
	main()
