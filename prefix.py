"""
This script will host functions responsible for the changing of the prefix
"""


def change_bot_prefix(prefix, client):
    """
    Assigns the prefix of the bot. Called when a pickle file is loaded in or when the prefix is changed.
    """
    client.command_prefix = prefix
