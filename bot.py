from config import Config
import discord
from discord.ext import commands
import dotenv
from dotenv import load_dotenv
import os

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
GUILD = os.getenv('DISCORD_GUILD')
PREFIX = os.getenv('PREFIX_KEY')
INITIAL_CHANNEL = os.getenv('INITIAL_CHANNEL')
MOVED_CHANNEL = os.getenv('MOVED_CHANNEL')
client = commands.Bot(command_prefix=PREFIX)
allowed_prefixes = ["!", "£", "$", "%", "^", "&", "*", "."]


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


async def change_prefix(ctx):
    """
        If the user enters PREFIX + 'prefix',
        the bot will try to set a new prefix.
        Requires user to have admin rights.
        """



    await ctx.channel.send("Please enter a new prefix.")
    response = await client.wait_for('message', check=check_author, timeout=30)
    new_prefix = await check_new_prefix(ctx, response.content)
    old_prefix = client.command_prefix
    client.command_prefix = new_prefix
    await change_bot_status()
    if new_prefix is not old_prefix:
        change_env_prefix(new_prefix)
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
    if prefix_to_check in allowed_prefixes:
        return prefix_to_check
    else:
        allowed_prefix_string = ""
        for allowed_prefix in allowed_prefixes:
            allowed_prefix_string += allowed_prefix + " "
        await ctx.send("Sorry, that isn't an acceptable prefix. \nPlease use one of the following: ```" +
                       allowed_prefix_string + "```")
        return str(PREFIX)


def change_env_prefix(new_prefix):
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



async def change_bot_status():
    """
    Sets the status of the bot to show the prefix
    """
    await client.change_presence(status=discord.Status.online, activity=discord.Game('My prefix is ' +
                                                                                     client.command_prefix))


@client.command()
@commands.has_permissions(administrator=True)
async def setup(ctx):

    def check_author(m):
        """
        Checks that the subsequent message is from the same user and in the same channel
        as the message with the command

        Args:
            m: the message

        Return:
            : returns the message if author and channel match
        """
        return m.author == ctx.author and m.channel == ctx.channel

    embedVar = discord.Embed(title="Set Up", description="What would you like to edit?", color=0x00ff00)
    embedVar.add_field(name="Prefix", value="Please press 1.", inline=False)
    embedVar.add_field(name="Reporting Channel", value="Please press 2.", inline=False)
    embedVar.add_field(name="Logging Channel", value="Please press 3.", inline=False)
    embedVar.add_field(name="All of the above", value="Please press 4.", inline=False)
    await ctx.send(embed=embedVar)
    response = await client.wait_for('message', timeout=60)
    if response.content == "1":
        await ctx.send("Please enter your new prefix.")
        new_prefix = await client.wait_for('message', check=check_author, timeout=60)
        await change_prefix(new_prefix)
    elif response.content == "2":
        print("reporting channel")
    elif response.content == "3":
        print("logging channel")
    elif response.content == "4":
        print("all")
    else:
        print("not recognised")


@setup.error
async def prefix_error(ctx, error):
    """
    Handles the potential TimeoutError when asking for a new prefix
    Args:
        ctx: The context, used to determine which channel to write to
        error: The error that has occurred.
    """
    if isinstance(error, commands.CommandInvokeError):
        await ctx.send("I don't have all day. Try a bit faster next time.")

@client.command(aliases=['report', 'submit', 'rep'])
async def anonymous_report(ctx):
    """
    This function will be responsible for the additional calling of functions to copy and delete messages, provided
    that the message is sent in a specific channel and is not sent by the bot (to prevent recursive calls).

    Args:
        ctx: the message sent
    """

    def check_author(m):
        """
        Checks that the subsequent message is from the same user and in the same channel
        as the message with the command

        Args:
            m: the message

        Return:
            : returns the message if author and channel match
        """
        return m.author == ctx.author and m.channel == ctx.channel

    if ctx.channel.id == 757234289107533867 and ctx.author != client.user:
        await ctx.message.delete()
        prompt = await ctx.send("Please enter details of your report - including a brief summary, the channel in "
                                "which it "
                                "occurred, and the offending user(s).")
        report_from_user = await client.wait_for('message', check=check_author, timeout=60)

        await copy_message(report_from_user)
        await report_from_user.delete()
        await prompt.delete()
        await report_from_user.channel.send("Thank you for your report - the moderators will look into the issue! "
                                            ":slight_smile:")
    else:
        pass


@anonymous_report.error
async def prefix_error(ctx, error):
    """
    Handles the potential TimeoutError when asking for a user's report
    Args:
        ctx: The context, used to determine which channel to write to
        error: The error that has occurred.
    """
    if isinstance(error, commands.CommandInvokeError):
        await ctx.send("Your time to report has timed out. Please try again.")


async def copy_message(msg):
    """
    This function will copy the message and paste it into another channel.
    """
    channel = client.get_channel(757962643523895335)
    embedVar = discord.Embed(title="Report from " + str(msg.author), description=str(msg.content), color=0x00ff00)
    await channel.send(embed=embedVar)


@client.event
async def on_ready():
    """
        Some launch things.
    """
    await change_bot_status()
    for guild in client.guilds:
        if guild.name == GUILD:
            break

    print(f'{client.user} is connected to the following guild:\n'
          f'{guild.name}(id: {guild.id})')


if __name__ == '__main__':
    client.run(TOKEN)
