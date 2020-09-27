import change_config_values
from config import Config
import discord
from discord.ext import commands
from dotenv import load_dotenv
import object_pickling
import os
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
    if CONFIG.initial_channel == 0 or CONFIG.moved_channel == 0:
        await status_and_errors.set_up_not_complete_error(ctx, CONFIG.prefix)
    else:
        report_channel = discord.utils.get(ctx.guild.channels, id=CONFIG.initial_channel)
        embedVar = discord.Embed(title="Commands", description="This is everything I can do!", color=0x00ff00)
        embedVar.add_field(name=CONFIG.prefix + "helpme, " + CONFIG.prefix + "command, " + CONFIG.prefix + "commands, "
                           + CONFIG.prefix + "com", value="Shows a list of my commands (what you're reading what now!)"
                                                          ".",
                           inline=False)
        embedVar.add_field(name=CONFIG.prefix + "report, " + CONFIG.prefix + "submit, " + CONFIG.prefix + "rep",
                           value="Allows a user to anonymously submit a report to the moderators within "
                                 + report_channel.mention + ".", inline=False)
        embedVar.add_field(name=CONFIG.prefix + "setup",
                           value="Allows an admin to initially configure things like my prefix and the reporting "
                                 "channel.", inline=False)
        embedVar.add_field(name=CONFIG.prefix + "prefix, " + CONFIG.prefix + "change, " + CONFIG.prefix + "edit, "
                           + CONFIG.prefix + "adjust, " + CONFIG.prefix + "channels, " + CONFIG.prefix + "config",
                           value="Allows an admin to change the prefix.", inline=False)
        await ctx.send(embed=embedVar)


@client.command(aliases=['change', 'edit', 'prefix', 'adjust', 'config', 'channels'])
@commands.has_permissions(administrator=True)
async def change_values(ctx):
    """
    Allows an admin to change values within the Config object, such as prefix, reporting channel
    and the logging channel.
    Args:
     ctx: the message with the command, calling this function
    """
    global CONFIG
    global allowed_prefixes
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
            CONFIG = await change_config_values.change_prefix(ctx, client, CONFIG, allowed_prefixes)
        elif response.content == "2":
            CONFIG = await change_config_values.change_reporting_channel(ctx, client, CONFIG)
        elif response.content == "3":
            CONFIG = await change_config_values.change_logging_channel(ctx, client, CONFIG)
        elif response.content == "4":
            edit_all = discord.Embed(title="Edit All",
                                     description="Please enter your new prefix, the name of the channel users will "
                                                 "report in and the name of your report logging channel",
                                     color=0xFFA500)
            edit_all.add_field(name="Example", value="$ reports report_logs", inline=False)
            await ctx.send(embed=edit_all)
            CONFIG = await change_config_values.change_all_variables(ctx, client, CONFIG, config_file_name,
                                                                     allowed_prefixes)

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
    CONFIG = await change_config_values.change_all_variables(ctx, client, CONFIG, config_file_name, allowed_prefixes)


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
        change_config_values.change_bot_prefix(CONFIG.prefix, client)

    await status_and_errors.change_bot_status(client)


if __name__ == '__main__':
    client.run(TOKEN)
