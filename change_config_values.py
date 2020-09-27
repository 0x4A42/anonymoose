from config import Config
import discord
import status_and_errors
import object_pickling
"""
This script will host functions responsible for the changing of the prefix
"""


async def change_prefix(ctx, client, config, allowed_prefixes):
    """
    This function will deal with changing the prefix of this bot.

    Args:
        ctx: the message initially sent to trigger this change.
        client:
        config:
        allowed_prefixes:
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

    await ctx.send("Please enter your new prefix.")
    response = await client.wait_for('message', check=check_author, timeout=60)
    new_prefix = await check_new_prefix(ctx, response.content, config, allowed_prefixes)
    if new_prefix is not client.command_prefix:
        if new_prefix in allowed_prefixes:
            config.prefix = new_prefix
            change_bot_prefix(new_prefix, client)
            await status_and_errors.change_bot_status(client)
            await ctx.send("Server prefix has been changed to: " + new_prefix)
            return config


def change_bot_prefix(prefix, client):
    """
    Assigns the prefix of the bot. Called when a pickle file is loaded in or when the prefix is changed.
    """
    client.command_prefix = prefix


async def check_new_prefix(ctx, prefix_to_check, config, allowed_prefixes):
    """
    This function checks the prefix submitted by the user.
    If it is within a list of allowed prefixes, returns the new prefix.
    Else, returns the original and sends an error message

    Args:
        ctx: the context from the message which initiated this.
        prefix_to_check (string): the prefix being checked
        config: the Config object used by the bot
        allowed_prefixes: a list of allowed prefixes
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
        return str(config.prefix)


async def change_all_variables(ctx, client, config, config_file_name, allowed_prefixes):
    """
    This function will deal with changing all three variables at once.
    This will change the prefix, the reporting channel and the logging channel.

    Args:
         ctx: the message initially sent to trigger this change.
         client: the bot
         config: the Config object used by the bot
         config_file_name: the name of the pickle file
         allowed_prefixes: a list of allowed prefixes
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

    try:
        response = await client.wait_for('message', check=check_author, timeout=60)
        new_prefix, new_reporting_channel, new_logging_channel = str.split(response.content)
        new_report_channel = discord.utils.get(ctx.guild.channels, name=new_reporting_channel)
        new_log_channel = discord.utils.get(ctx.guild.channels, name=new_logging_channel)
        new_prefix_final = await check_new_prefix(ctx, new_prefix, config, allowed_prefixes)
        change_bot_prefix(new_prefix_final, client)
        config = Config(new_prefix_final, new_report_channel.id, new_log_channel.id)
        await status_and_errors.change_bot_status(client)
        object_pickling.save_pickle(config_file_name, config)
        return config
    except ValueError:
        edit_all = discord.Embed(title="Error: Number of arguments.",
                                 description="You must submit three (3) values separated by spaces.",
                                 color=0xFF0000)
        edit_all.add_field(name="Example", value="$ reports report_logs", inline=False)
        await ctx.send(embed=edit_all)
    except TimeoutError:
        edit_all = discord.Embed(title="Error: Timeout.",
                                 description="You took too long. Please try again, submitting your desired prefix and "
                                             "channels within 60 seconds.",
                                 color=0xFF0000)
        await ctx.send(embed=edit_all)
    except AttributeError:
        await ctx.send("Error with one of your channel names. Either **" + new_reporting_channel + "** or **"
                       + new_logging_channel + "** does not exist.")


async def change_reporting_channel(ctx, client, config):
    """
    This function will deal with changing the reporting channel where users submit reports.

    Args:
        ctx: the message initially sent to trigger this change.
        client: the bot
        config: the Config object used by the bot
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

    await ctx.send("Please enter the name of your user reporting channel.")
    channel = await client.wait_for('message', check=check_author, timeout=60)
    try:
        new_report_channel = discord.utils.get(ctx.guild.channels, name=channel.content)
        config.initial_channel = new_report_channel.id
        await ctx.send("Your user reporting channel has been changed to: " + new_report_channel.mention)
        return config
    except AttributeError:
        await status_and_errors.cannot_find_channel_error(ctx, channel.content)


async def change_logging_channel(ctx, client, config):
    """
    This function will deal with changing the logging channel where reports are copied into.

    Args:
        ctx: the message initially sent to trigger this change.
        client: the bot
        config: the Config object used by the bot
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

    await ctx.send("Please enter the name of your report logging channel.")
    channel = await client.wait_for('message', check=check_author, timeout=60)
    try:
        new_log_channel = discord.utils.get(ctx.guild.channels, name=channel.content)
        config.moved_channel = new_log_channel.id
        await ctx.send("Your reporting logging channel has been changed to: " + new_log_channel.mention)
        return config
    except AttributeError:
        await status_and_errors.cannot_find_channel_error(ctx, channel.content)
