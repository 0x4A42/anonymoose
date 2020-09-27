from config import Config
import discord
from discord.ext import commands
from dotenv import load_dotenv
import object_pickling
import os
import prefix
import reporting
import status_and_errors


CONFIG = Config("$", 0, 0)
config_file_name = 'config_value.pickle'
load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
GUILD = os.getenv('DISCORD_GUILD')
client = commands.Bot(command_prefix=CONFIG.prefix)
allowed_prefixes = ["!", "£", "$", "%", "^", "&", "*", "."]


@client.command(aliases=['command', 'commands', 'com', 'helpme'])
async def show_commands(ctx):
    """
    If the user enters the prefix + any phrase within the aliases,
    the bot will send a message with all of its commands and what they do.
    """
    embedVar = discord.Embed(title="Commands", description="This is everything I can do!", color=0x00ff00)
    embedVar.add_field(name=CONFIG.prefix + "help, " + CONFIG.prefix + "command, " + CONFIG.prefix + "commands",
                       value="Shows a list of my commands.", inline=False)
    embedVar.add_field(name=CONFIG.prefix + "prefix", value="Allows an admin to change the prefix.", inline=False)
    await ctx.send(embed=embedVar)


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
        return str(CONFIG.prefix)


async def change_prefix(ctx):
    """
    This function will deal with changing the prefix of this bot.

    Args:
        ctx: the message initially sent to trigger this change.
    """
    global CONFIG

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

    await ctx.send("Please enter your new prefix.")
    response = await client.wait_for('message', check=check_author, timeout=60)
    new_prefix = await check_new_prefix(ctx, response.content)
    if new_prefix is not client.command_prefix:
        if new_prefix in allowed_prefixes:
            CONFIG.prefix = new_prefix
            prefix.change_bot_prefix(new_prefix, client)
            await status_and_errors.change_bot_status(client)
            await ctx.send("Server prefix has been changed to: " + new_prefix)


async def change_reporting_channel(ctx):
    """
    This function will deal with changing the reporting channel where users submit reports.

    Args:
        ctx: the message initially sent to trigger this change.
    """
    global CONFIG

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

    await ctx.send("Please enter the name of your user reporting channel.")
    channel = await client.wait_for('message', check=check_author, timeout=60)
    try:
        new_report_channel = discord.utils.get(ctx.guild.channels, name=channel.content)
        CONFIG.initial_channel = new_report_channel.id
        await ctx.send("Your user reporting channel has been changed to: " + new_report_channel.mention)
    except AttributeError:
        await ctx.send("Cannot find a channel with the name of " + channel.content)


async def change_logging_channel(ctx):
    """
    This function will deal with changing the logging channel where reports are copied into.

    Args:
        ctx: the message initially sent to trigger this change.
    """
    global CONFIG

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

    await ctx.send("Please enter the name of your report logging channel.")
    channel = await client.wait_for('message', check=check_author, timeout=60)
    try:
        new_log_channel = discord.utils.get(ctx.guild.channels, name=channel.content)
        CONFIG.moved_channel = new_log_channel.id
        await ctx.send("Your reporting logging channel has been changed to: " + new_log_channel.mention)
    except AttributeError:
        await ctx.send("Cannot find a channel with the name of " + channel.content)


async def change_all_variables(ctx):
    """
    This function will deal with changing all three variables at once.
    This will change the prefix, the reporting channel and the logging channel.

    Args:
         ctx: the message initially sent to trigger this change.
    """
    global CONFIG

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

    try:
        response = await client.wait_for('message', check=check_author, timeout=60)
        new_prefix, new_reporting_channel, new_logging_channel = str.split(response.content)
        new_report_channel = discord.utils.get(ctx.guild.channels, name=new_reporting_channel)
        new_log_channel = discord.utils.get(ctx.guild.channels, name=new_logging_channel)
        prefix.change_bot_prefix(new_prefix, client)
        CONFIG = Config(new_prefix, new_report_channel.id, new_log_channel.id)
        await status_and_errors.change_bot_status(client)
        object_pickling.save_pickle(config_file_name, CONFIG)
    except ValueError:
        edit_all = discord.Embed(title="Error - Too many arguments.",
                                 description="You must submit three (3) values separated by spaces.",
                                 color=0xFF0000)
        edit_all.add_field(name="Example", value="$ reports report_logs", inline=False)
        await ctx.send(embed=edit_all)
    except TimeoutError:
        edit_all = discord.Embed(title="Error - Timeout.",
                                 description="You took too long. Please try again, submitting your desired prefix and "
                                             "channels within 60 seconds.",
                                 color=0xFF0000)
        await ctx.send(embed=edit_all)


@client.command(aliases=['change', 'edit', 'prefix', 'adjust', 'config', 'channels'])
@commands.has_permissions(administrator=True)
async def change_values(ctx):
    global CONFIG
    if CONFIG.initial_channel == 0 or CONFIG.moved_channel == 0:
        await status_and_errors.set_up_not_complete_error(ctx, CONFIG.prefix)
    else:
        embedVar = discord.Embed(title="Configuration", description="What would you like to edit?", color=0xFFA500)
        embedVar.add_field(name="Prefix", value="Please press 1.", inline=False)
        embedVar.add_field(name="Reporting Channel", value="Please press 2.", inline=False)
        embedVar.add_field(name="Logging Channel", value="Please press 3.", inline=False)
        embedVar.add_field(name="All of the above", value="Please press 4.", inline=False)
        await ctx.send(embed=embedVar)
        response = await client.wait_for('message', timeout=60)

        if response.content == "1":
            await change_prefix(ctx)
        elif response.content == "2":
            await change_reporting_channel(ctx)
        elif response.content == "3":
            await change_logging_channel(ctx)
        elif response.content == "4":
            edit_all = discord.Embed(title="Edit All",
                                     description="Please enter your new prefix, the name of the channel users will "
                                                 "report in and the name of your report logging channel",
                                     color=0xFFA500)
            edit_all.add_field(name="Example", value="$ reports report_logs", inline=False)
            await ctx.send(embed=edit_all)
            await change_all_variables(ctx)

        object_pickling.save_pickle(config_file_name, CONFIG)  # Saves changes to file


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

    if CONFIG.initial_channel == 0 or CONFIG.moved_channel == 0:
        await status_and_errors.set_up_not_complete_error(ctx, CONFIG.prefix)
    else:
        if ctx.channel.id == CONFIG.initial_channel and ctx.author != client.user:
            await ctx.message.delete()
            prompt = await ctx.send("Please enter details of your report - including a brief summary, the channel in "
                                    "which it "
                                    "occurred, and the offending user(s).")
            report_from_user = await client.wait_for('message', check=check_author, timeout=60)

            await reporting.copy_message(report_from_user, CONFIG, client)
            await report_from_user.delete()
            await prompt.delete()
            await report_from_user.channel.send("Thank you for your report - the moderators will look into the issue! "
                                                ":slight_smile:")


@anonymous_report.error
async def anonymous_report_error(ctx, error):
    """
    Handles the potential TimeoutError when asking for a user's report
    Args:
        ctx: The context, used to determine which channel to write to
        error: The error that has occurred.
    """
    if isinstance(error, commands.CommandInvokeError):
        await ctx.send("Your time to report has timed out. Please try again.")


@client.command()
async def setup(ctx):
    """
    Called to run the start up process.
    """

    global CONFIG
    set_up = discord.Embed(title="Initial Set Up", description="Please enter your desired prefix, the name of the "
                                                               "channel users will report in and the name of your "
                                                               "report logging channel", color=0xFFA500)
    set_up.add_field(name="Example ", value="$ reports report_logging", inline=False)
    await ctx.send(embed=set_up)
    await change_all_variables(ctx)


@client.event
async def on_ready():
    """
        On launch, will check if a .pickle file exists.
        If so, loads in the object from there.
        Else, goes through the set up to create a Config object and save it to a .pickle file.
    """
    global CONFIG  # ensures this function uses the global variable

    if os.path.exists(config_file_name):
        CONFIG = object_pickling.load_pickle(config_file_name)
        prefix.change_bot_prefix(CONFIG.prefix, client)

    await status_and_errors.change_bot_status(client)


if __name__ == '__main__':
    client.run(TOKEN)
