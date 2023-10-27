# googledrive_backups

This repo contains assorted scripts involved in Google Drive data migrations and backups.

The code is totally rough, unfinished, missing parts that were done via command line, etc...


# sample of poism_folderBasedRename.py
This script renames files based on their parent folder hierarchies.

Note this example is with well named folders to begin with...

If your folder names are prestine (spaceless and perfect and exactly what you want reflected in filenames) then use --keep-folder-name

If ever the folder names are rather garbage, consider using --strict-folder-name which will force alphanumeric folder names and _ to designate subfolders into the filenames.

Else by default folder names will be stripped of all non-alphanumeric characters except -_. and these will be applied to filenames


```

sangpo@pobox:~/git/gdrive_tools$ python poism_folderBasedRename.py --help

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
        
Requires argument of starting directory be provided!


sangpo@pobox:~/git/gdrive_tools$ python poism_folderBasedRename.py --keep-sequence /datapool/media/photos/20200708_NM_MavicAir2/ 

Selected paths:
/datapool/media/photos/20200708_NM_MavicAir2/ 
--keep-sequence = Keeping sequences in filenames

Do you want to proceed? y/n:y 

======================================================
Exploring /datapool/media/photos/20200708_NM_MavicAir2
======================================================
Processing: DJI_0061 --> 20200708_NM_MavicAir2-0061.ab1c6f.jpg
Processing: DJI_0066 --> 20200708_NM_MavicAir2-0066.9b3b7a.mp4
Processing: DJI_0060 --> 20200708_NM_MavicAir2-0060.018c2b.mp4
Processing: DJI_0063 --> 20200708_NM_MavicAir2-0063.3f88fd.mp4
Processing: DJI_0058 --> 20200708_NM_MavicAir2-0058.412dd0.mp4
Processing: DJI_0064 --> 20200708_NM_MavicAir2-0064.9acf36.jpg
Processing: DJI_0065 --> 20200708_NM_MavicAir2-0065.f9da07.jpg
Processing: DJI_0057 --> 20200708_NM_MavicAir2-0057.88f544.mp4
Processing: DJI_0059 --> 20200708_NM_MavicAir2-0059.4c14fe.mp4
Processing: DJI_0062 --> 20200708_NM_MavicAir2-0062.b04389.mp4

------------------------RENAME------------------------
rename: DJI_0061.JPG ---> 20200708_NM_MavicAir2-0061.ab1c6f.jpg
rename: DJI_0066.MP4 ---> 20200708_NM_MavicAir2-0066.9b3b7a.mp4
rename: DJI_0060.MP4 ---> 20200708_NM_MavicAir2-0060.018c2b.mp4
rename: DJI_0063.MP4 ---> 20200708_NM_MavicAir2-0063.3f88fd.mp4
rename: DJI_0058.MP4 ---> 20200708_NM_MavicAir2-0058.412dd0.mp4
rename: DJI_0064.JPG ---> 20200708_NM_MavicAir2-0064.9acf36.jpg
rename: DJI_0065.JPG ---> 20200708_NM_MavicAir2-0065.f9da07.jpg
rename: DJI_0057.MP4 ---> 20200708_NM_MavicAir2-0057.88f544.mp4
rename: DJI_0059.MP4 ---> 20200708_NM_MavicAir2-0059.4c14fe.mp4
rename: DJI_0062.MP4 ---> 20200708_NM_MavicAir2-0062.b04389.mp4

------------------------CONFIRM-------------------------
Do you want to apply these actions? y/n:y

--------------------------LOG---------------------------
['rename', '20200708_NM_MavicAir2', 'DJI_0061.JPG', '20200708_NM_MavicAir2-0061.ab1c6f.jpg', 'ab1c6f68a6d73aea96d41711ee82d921']
['rename', '20200708_NM_MavicAir2', 'DJI_0066.MP4', '20200708_NM_MavicAir2-0066.9b3b7a.mp4', '9b3b7a03ca8c0e77a5e681a0ba143830']
['rename', '20200708_NM_MavicAir2', 'DJI_0060.MP4', '20200708_NM_MavicAir2-0060.018c2b.mp4', '018c2b44320ea87df4c2f69b12ccdafb']
['rename', '20200708_NM_MavicAir2', 'DJI_0063.MP4', '20200708_NM_MavicAir2-0063.3f88fd.mp4', '3f88fdec68856860f57ffe0fa6447482']
['rename', '20200708_NM_MavicAir2', 'DJI_0058.MP4', '20200708_NM_MavicAir2-0058.412dd0.mp4', '412dd0afa8a3f4a863ee652cbc518e40']
['rename', '20200708_NM_MavicAir2', 'DJI_0064.JPG', '20200708_NM_MavicAir2-0064.9acf36.jpg', '9acf36e03396fe3b8f4692f94bfeb4b4']
['rename', '20200708_NM_MavicAir2', 'DJI_0065.JPG', '20200708_NM_MavicAir2-0065.f9da07.jpg', 'f9da079ef0ac2ee27471b01302c25e00']
['rename', '20200708_NM_MavicAir2', 'DJI_0057.MP4', '20200708_NM_MavicAir2-0057.88f544.mp4', '88f5442d27aea78d068ce3f544557560']
['rename', '20200708_NM_MavicAir2', 'DJI_0059.MP4', '20200708_NM_MavicAir2-0059.4c14fe.mp4', '4c14fe2633ce67ed310d351dd144b80f']
['rename', '20200708_NM_MavicAir2', 'DJI_0062.MP4', '20200708_NM_MavicAir2-0062.b04389.mp4', 'b04389400fe80a234e90060b81cb3ac8']

Press CTRL+c to Quit or continue to next folder. (ENTER key) 


==================================================================================
Log File: /datapool/media/photos/20200708_NM_MavicAir2/renamed-20200708_222859.csv
==================================================================================

```
