import discord

"""
This script will host functions related to the reporting functionality
"""


async def copy_message(msg, config, client):
    """
    This function will copy the message and paste it into another channel.
    """
    channel = client.get_channel(config.moved_channel)
    embedVar = discord.Embed(title="Report from " + str(msg.author), description=str(msg.content), color=0x008080)
    await channel.send(embed=embedVar)