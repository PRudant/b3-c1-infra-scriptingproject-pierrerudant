import discord
from discord.ext import commands

Token = "TATA"
client = discord.Client(intents=discord.Intents.default())

# Use the command decorator to define a command handler
@client.command()
async def log(ctx, channel: discord.TextChannel, search_query: str):
    # Search for messages in the specified channel that match the search query
    async for message in channel.history(limit=100, after=datetime.datetime.now() - datetime.timedelta(days=30)):
        if search_query in message.content:
            await ctx.send(f"{message.author}: {message.content}")

client.run(Token)
