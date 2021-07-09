# Reppo
## The Reputation tracking discord bot

### Reppo uses a .env file for secrete stuff, it should contain:
* TOKEN=(Bot Token)
* DB_USERNAME=(database username)
* DB_PASSWORD=(database password)
* GUID=(guid of the server that the bot is to run on)
* ADMIN_ROLE_ID=(admin role_id)
* EVERYONE_ROLE_ID=(everryone role_id)

Command line arguments:  
For debugging: (One or the other, however if you have both, the lower (more verbose) log level will be chosen)  

`python Reppo.py -d`
* debug mode; intense log level

`python Reppo.py -v`
* turn on verbose logging  

## Files:
Reppo_db.py
* Contains the Database class & custom Exception
* Handles all calls to sql server  

Reppo.py
* Main file, contains slash commands & starts bot
