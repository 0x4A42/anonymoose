import os
import discord
from dotenv import load_dotenv

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
GUILD = os.getenv('DISCORD_GUILD')
PREFIX = os.getenv('PREFIX_KEY')
client = discord.Client()
allowed_prefix = ["£", "$", "%", "^", "&", "*"]
help_commands = ["help", "command", "commands"]


@client.event
async def on_ready():
    for guild in client.guilds:
        if guild.name == GUILD:
            break

    print(f'{client.user} is connected to the following guild:\n'
          f'{guild.name}(id: {guild.id})')

    members = '\n - '.join([member.name for member in guild.members])
    print(f'Guild Members:\n - {members}')


@client.event
async def on_message(message):
    global PREFIX
    if message.author == client.user:
        return

    if message.content.startswith(PREFIX) and message.content[1:].lower() in help_commands:
        commands_response = "Here are a list of my commands:"
        await message.channel.send(commands_response)

    if message.content == PREFIX + 'prefix':
        if message.author.guild_permissions.administrator:
            new_prefix = await change_prefix(message)
            PREFIX = new_prefix
        else:
            no_permissions = "You don't have the permissions for this."
            await message.channel.send(no_permissions)


async def change_prefix(message):
    prompt_user = "Please enter a new prefix."
    await message.channel.send(prompt_user)
    new_prefix = await client.wait_for('message')
    if new_prefix.content in allowed_prefix:
        return new_prefix.content
    else:
        return PREFIX


if __name__ == '__main__':
    client.run(TOKEN)
