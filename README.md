# Auto-Calendar-Updater
I created this application in order to automatically update my Google Calendar with my part time work shifts. 

There are two parts;  
A python app to access, download, extract and format the shift data.  
A Node.js app that runs the python script and then takes the data provided and updates my Google Calendar via the Google Calendar API.

It performs the following:
1)  Logs into Woolworths employee portal
2)  Downloads all avaliable rosters
3)  Extracts my shift dates & times from the pdf document of all the stores employee's shifts
4)  Saves my shifts as JSON objects to a local file
5)  Every night the cron job in the web app runs
6)  Updates all my Google Calendar events 
