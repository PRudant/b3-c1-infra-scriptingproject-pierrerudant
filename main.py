import discord
from discord.ext import commands

Token = "YOURTOKEN"
bot = discord.Bot(intents=discord.Intents.all(), command_prefix = "!", description = "Bot de Pierre")


@bot.event
async def on_ready():
    print("En ligne")

@bot.event
async def on_message_edit(before, after):
    await before.channel.send(
        f"{before.author} a édité un message \n"
        f"Before: {before.content} \n"
        f"After: {after.content}"
    )

@bot.event
async def on_message(message):
    print("yes message")
    if message.author == bot.user:
        return

    if message.content == "plop":
        print("yes plop")
        await message.channel.send("hello")


bot.run(Token)


# https://www.youtube.com/watch?v=DZLqwGVSpwA
