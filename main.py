import discord
from discord.ext import commands

Token = "MTA1MDMyODEyNjUyMzE5MTM3OA.GtEPNx.KbbrYw_HYEuPC5PNHMntHvhDhNWN6ytqapmzlc"
client = discord.Client(intents=discord.Intents.default(), command_prefix = "!", description = "Bot de Pierre")


@client.event
async def on_ready():
    print("En ligne")


@client.event
async def on_message(message):
    print("yes message")
    if message.author == client.user:
        return

    if message.content == "plop":
        print("yes plop")
        await message.channel.send("hello")


@client.event
async def on_message_edit(before, after):
    await before.channel.send(
        f"{before.author} a édité un message \n"
        f"Before: {before.content} \n"
        f"After: {after.content}"
    )


client.run(Token)

# https://www.youtube.com/watch?v=DZLqwGVSpwA
