# Reppo
## The Reputation tracking discord bot

reppo_db contains the database class, which handles all the calls to the sql server
  & custom Exceptions.

### .env should contain:
* TOKEN=(Bot Token)
* DB_USERNAME=(database username)
* DB_PASSWORD=(database password)
* GUID=(guid of the server that the bot is to run on)
* ADMIN_ROLE_ID=(admin role_id)
* EVERYONE_ROLE_ID=(everryone role_id)

Command line arguments:
  >For debugging: (One or the other, however if you have both,
                  the lower log level will be chosen; logLevel=DEBUG)
    -d
      debug mode; intense log levels
    -v
      turn on verbose logging
