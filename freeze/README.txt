Sound Speed Manager 2021.1.n - Installation Notes

1. Extract the "SoundSpeedManager.2021.1.n" folder from the zip archive to destination of your choice.

2. Run "SoundSpeedManager.2021.1.y.exe" from within the folder.

3. At first run, the application will ask to download the WOA database (~120 MB).
   If the machine does NOT have Internet access, click "NO" and close the application (since we will manually copy the WOA09 database).
   If the machine has a good Internet access, click "YES" and skip the next step (#4).

[Step required if the machine does not have direct Internet access]
4. Download from the application website (https://www.hydroffice.org/soundspeed/main) the WOA09 Atlas archive, unzip it, then manually copy the folder "woa09" (that has the world-coverage WOA09 database) to:
   - "C:/Documents and Settings/<username>/Application Data/HydrOffice/Sound Speed/atlases" (WinXP), or
   - "C:/Users/<username>/AppData/Local/HydrOffice/Sound Speed/atlases" (newer Windows OS)

[Optional, recommended]
5. Kongsberg SIS Interaction.
   If you want that Sound Speed Manager directly interacts with SIS, you need to:
   - Open the "Settings" tab.
   - Go to the "Input" sub-tab, and set to True one between "Listen SIS4" or "Listen SIS5". 
   - Go to the "Listeners" sub-tab, and set the port that SIS uses to broadcast datagrams.   
   - Go to the "Output" sub-tab, and set the IP address of the SIS machine (127.0.0.1 if SIS and Sound Speed Manager are on the same machine). The port used to listen is always 4001 for SIS4 and 14002 for SIS5. The protocol name is SIS.

[Optional]
6. RTOFS database.
   If you want to use the Real Time Operational Forecast System to enhance your casts, you need that the machine with Sound Speed Manager has a working Internet connection (with port 9090 open).
