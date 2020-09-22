import os
import discord
from discord.ext import commands
import dotenv
from dotenv import load_dotenv

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
GUILD = os.getenv('DISCORD_GUILD')
PREFIX = os.getenv('PREFIX_KEY')
client = commands.Bot(command_prefix=PREFIX)
allowed_prefix = ["!", "£", "$", "%", "^", "&", "*", "."]


@client.command(aliases=['command', 'commands', 'com', 'helpme'])
async def show_commands(ctx):
    """
    If the user enters the prefix + any phrase within the aliases,
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

    response = await client.wait_for('message', check=check_author, timeout=30)
    new_prefix = await check_new_prefix(ctx, response.content)
    old_prefix = client.command_prefix
    client.command_prefix = new_prefix
    if new_prefix is not old_prefix:
        change_env_var(new_prefix)
        await ctx.send("Server prefix has been changed to: " + new_prefix)


async def check_new_prefix(ctx, prefix_to_check):
    """
    This function checks the prefix submitted by the user.
    If it is within a list of allowed prefixes, returns the new prefix.
    Else, returns the original and sends an error message

    Args:
        ctx: the context from the message which initiated this.
        prefix_to_check (string): the prefix being checked
    Returns:
        prefix_to_check: The prefix being checked, if acceptable
        PREFIX: the env variable, if not acceptable
    """
    if prefix_to_check in allowed_prefix:
        return prefix_to_check
    else:
        allowed_prefix_string = ""
        for pref in allowed_prefix:
            allowed_prefix_string += pref + " "
        await ctx.send("Sorry, that isn't an acceptable prefix. \nPlease use one of the following: ```" +
                       allowed_prefix_string + "```")
        return str(PREFIX)


def change_env_var(new_prefix):
    """
    Edits the .env file with the new prefix key so that it is saved even
    when the bot goes offline.
    Args:
        new_prefix (string): The new prefix to write to file
    """
    dotenv_file = dotenv.find_dotenv()
    dotenv.load_dotenv(dotenv_file)
    os.environ["PREFIX_KEY"] = new_prefix
    dotenv.set_key(dotenv_file, "PREFIX_KEY", os.environ["PREFIX_KEY"])


@prefix.error
async def prefix_error(ctx, error):
    """
    Handles the potential TimeoutError when asking for a new prefix
    Args:
        ctx: The context, used to determine which channel to write to
        error: The error that has occurred.
    """
    if isinstance(error, commands.CommandInvokeError):
        await ctx.send("I don't have all day. Try a bit faster next time.")


@client.event
async def on_ready():
    await client.change_presence(status=discord.Status.online, activity=discord.Game('My prefix is ' +
                                                                                     client.command_prefix))
    for guild in client.guilds:
        if guild.name == GUILD:
            break

    print(f'{client.user} is connected to the following guild:\n'
          f'{guild.name}(id: {guild.id})')

    members = '\n - '.join([member.name for member in guild.members])
    print(f'Guild Members:\n - {members}')


if __name__ == '__main__':
    client.run(TOKEN)
