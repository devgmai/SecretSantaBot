# SantaBot

A Discord bot to organize secret santa gift exchanges using the discord.py Python library.

## Disclaimers:
======

This bot was originally created by Github user /SneakyBastardSword in year 2016. Since them, the libraries and dependencies have been updated. As a result, there are various portions of the program which no longer function. I have modified portions of the original code to make this functional.

Credits for the original code go to /SneakyBastardSword.

## The Matching Algorithm:
======

The problem with secret santa matchings is unstable matches from matching loops.

This bot uses a variation of a stable-marriage matching algorithm. All participants are shuffled in a random order and is each participant is assigned the next participant on the list. The last participant is assigned the first participat, completing the single assignment loop.

## Instructions: 
======
### Installation and Dependencies:

To add this bot to your Discord server, first ensure you have the following:

[Python version 3.6.0 or later installed](https://www.python.org/downloads/)

[the discord.py library](https://github.com/Rapptz/discord.py)

[the configobj library](http://www.voidspace.org.uk/python/configobj.html#installing)

Once all of the dependencies are installed, create a Discord bot token following the instructions [here](https://github.com/reactiflux/discord-irc/wiki/Creating-a-discord-bot-&-getting-a-token). Then, open the santa-bot.py file with your favorite plaintext editor, and replace the word `'insert_token_here'` in the last line that reads `client.run('insert_token_here')` with the token you have generated, keeping the single quotes. The santa-bot.py file can now be excecuted, and the bot should function as normal.

### Hosting the Discord Bot

You can host the bot on Heroku on a free personal developer account. You can host the bot for 500 hours per month with 24/7 uptime. Please [refer to the following reddit post](https://www.reddit.com/r/discordapp/comments/6qqtup/guide_creating_and_hosting_a_discord_bot_for_free/) on how to set this up.

### Bot Commands:

- `$$join` adds you to the list of secret santa participants.
- `$$setpreference` saves your gift preferences so your secret santa will know what kind of things you would like to receive. Keep in mind that your exact input is sent to your secret santa as is. 
- `$$listparticipants` makes the bot list all of the people currently participating in the secret santa exchange.
- `$$totalparticipants` makes the bot give the number of people currently participating in the secret santa exchange
- *`$$start` to have the bot assign each participant a partner
- *`$$shutdown` to make the bot self-terminate

all commands marked with a * can only be run by a server admin.