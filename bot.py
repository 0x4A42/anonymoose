import os
import discord
from discord.ext import commands
from dotenv import load_dotenv

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
GUILD = os.getenv('DISCORD_GUILD')
PREFIX = os.getenv('PREFIX_KEY')
client = commands.Bot(command_prefix=PREFIX)
allowed_prefix = ["!", "£", "$", "%", "^", "&", "*"]


@client.command(aliases=['command', 'commands', 'com', 'helpme'])
async def show_commands(ctx):
    """
    If the user enters PREFIX + any phrase within the help_commands list,
    the bot will send a message with all of its commands and what they do.
    """
    embedVar = discord.Embed(title="Commands", description="This is everything I can do!", color=0x00ff00)
    embedVar.add_field(name=PREFIX + "help, " + PREFIX + "command, " + PREFIX + "commands", value="Shows a list "
                                                                                                  "of my "
                                                                                                  "commands.",
                       inline=False)
    embedVar.add_field(name=PREFIX + "prefix", value="Allows an admin to change the prefix.", inline=False)
    await ctx.send(embed=embedVar)


@client.command()
@commands.has_permissions(administrator=True)
async def prefix(ctx):
    """
        If the user enters PREFIX + 'prefix',
        the bot will try to set a new prefix.
        Requires user to have admin rights.
        """
    await ctx.send("Please enter a new prefix.")

    def check_author(m):
        return m.author == ctx.author and m.channel == ctx.channel

    response = await client.wait_for('message', check=check_author, timeout=10)
    print(response.content)



#@client.event
#async def on_message(message, author):
    #print("get new prefix call)")

    #def check():
        #return msg.author == author

    #msg = await client.wait_for('message', check=check)
    #print("before return")
    #return msg.content


@client.event
async def check_new_prefix(prefix_to_check, ctx):
    print("check")
    if prefix_to_check.content in allowed_prefix:
        return prefix_to_check.content
    else:
        allowed_prefix_string = ""
        for prefix in allowed_prefix:
            allowed_prefix_string += prefix + " "
        await ctx.send("Sorry, that isn't an acceptable prefix. \nPlease use one of the following: ```" +
                       allowed_prefix_string + "```")
        return str(PREFIX)


@client.event
async def on_ready():
    for guild in client.guilds:
        if guild.name == GUILD:
            break

    print(f'{client.user} is connected to the following guild:\n'
    f'{guild.name}(id: {guild.id})')

    members = '\n - '.join([member.name for member in guild.members])
    print(f'Guild Members:\n - {members}')


# async def change_prefix(message, author):
#


# def check(author, message):
#  if message.author is not author:
#     return False
# else:
#  return True


if __name__ == '__main__':
    client.run(TOKEN)
