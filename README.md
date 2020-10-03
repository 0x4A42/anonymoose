# anonymoose
A simple Discord bot which will allow users to submit anonymous reports in a channel, have it copied and sent to another channel and have the original message wiped. Everything is handled within the server. 

This assumes you already have Python (3.8) installed and know how to use the command line.

# Dependencies
Use pip to install:
>discord  
>dotenv  
>os  
>pickle  

# Getting Started
1. Download the code and extract it.
2. Download the dependencies above (if not already installed).
3. Create a bot on the [Discord developer portal](https://discord.com/developers/applications). Invite it to the server (with admin privileges) you wish it to work within.
4. Update the 'DISCORD_TOKEN' value within .env, setting it to be your bot's token.
5. Run the bot.py script. The bot will now be live within your selected server. 
6. Call the setup command with $setup.

You should now be good to go! You can call $commands to see a list of the commands, such as to change the prefix or channels.

# Feature Requests

Always welcome. Feel free to use the [issues page](https://github.com/0x4A42/anonymoose)!

Currently working on setting up a database so the bot only needs to run on my end. But until then, the bot can be used through the above.
