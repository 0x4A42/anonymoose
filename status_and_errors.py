import discord

"""
This script will host functions relating to the bot's status, as well as error posting.
These are somewhat miscellaneous and have thus been grouped together.
"""


async def change_bot_status(client):
    """
    Sets the status of the bot to show the prefix
    """
    await client.change_presence(status=discord.Status.online, activity=discord.Game('My prefix is ' +
                                                                                     client.command_prefix))


async def set_up_not_complete_error(ctx, prefix):
    """
    Sends an error message if set up has not been done and a user attempts to use a command.
    Args:
     ctx: the message which attempted to call a command.
     prefix: the server prefix
    """
    edit_all = discord.Embed(title="Error - Setup not complete.",
                             description="An administrator hasn't set me up yet. They can use " + prefix +
                                         "setup to do so.",
                             color=0xFF0000)

    await ctx.send(embed=edit_all)
