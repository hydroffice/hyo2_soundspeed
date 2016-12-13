Sound Speed Manager 2017.0 - Installation Notes

1. Just copy the folder "SoundSpeedManager.2017.0" on the machine (wherever you prefer).

2. Run "SoundSpeedManager.2017.0.exe" from within the folder. At first run, the application asks to download the WOA database (1.5 GB). Click "NO" and close the application (since we will manually copy the WOA09 database).

3. Manually copy the folder "Atlases" (that has the full world-coverage WOA09 database) to: 
- "C:/Documents and Settings/<user>/HydrOffice/Sound Speed 3.0.0" (WinXP), or
- "C:/Users/<user>/HydrOffice/Sound Speed 3.0.0" (newer Windows OS)


[Optional steps] 
4. SIS Interaction 
If you want that SSP Manager directly interacts with SIS, you need to:
- open the "Settings" tab
- go to the "Output' tab, and set the IP address of the SIS machine (127.0.0.1 if SIS and SSM are on the same machine). The port used by SIS to listen is alway 4001.
- go to the "Kongsberg" tab, and set the IP address and port that SIS uses to broadcast datagrams.

[Optional steps] 
5. RTOFS database
If you want to use the Real Time Operational Forecast System, you need that the machine has an Internet connection (with port 9090 open).
