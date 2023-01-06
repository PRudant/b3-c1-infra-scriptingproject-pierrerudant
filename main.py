import discord
import random
from discord.ext import commands 
from discord import option

Token = "YOURTOKEN"
bot = discord.Bot(intents=discord.Intents.all(), command_prefix = "!", description = "Bot de Pierre")

# Message au démarrage du bot
@bot.event
async def on_ready():
    print("En ligne")

# Réponse à un édit
@bot.event
async def on_message_edit(before, after):
    await before.channel.send(
        f"{before.author} a édité un message \n"
        f"Before: {before.content} \n"
        f"After: {after.content}"
    )

# Réponse à un message
@bot.event
async def on_message(message):
    print("yes message")
    if message.author == bot.user:
        return

    if message.content == "plop":
        print("yes plop")
        await message.channel.send("hello")

# Réponse public
@bot.command(name = "test", description = "Test numéro 1")
async def self(interaction: discord.Interaction, name: str):
    await interaction.response.send_message(f"Hello {name} comment ça va ?")

# Réponse privée
@bot.command(name = "testephe", description = "Test numéro 2")
async def self(interaction: discord.Interaction, name: str):
    await interaction.response.send_message(f"Hello {name} comment ça va ?", ephemeral= True)

# Commande hybride
@bot.command(name = "firstslash") 
async def first_slash(ctx): 
    await ctx.respond("You executed the slash command!")

# PARTIE : FUN & GAMES


# Lancé de dé
#@bot.command(name = "roll", description = "Génère un nombre aléatoire entre 0 et 6")
#@Option(
#    "min", 
#    description="Nombre minimum souhaité",
#    required=False,
#    default= 0
#)
#@Option(
#    "max", 
#    description="Nombre maximum souhaité",
#    required=False,
#    default= 6
#)
#async def roll(ctx, min:int, max:int):


#    roll_n = random.randint(min, max)
#    await ctx.respond(f"Voici votre roll {roll_n} 🎲 ")

#@bot.slash.command(name = "roll", description = "Lance un dé pour toi", options=[
#    create_option(
#        name = "min_number", 
#        description = "Nombre minimum souhaité", 
#        options_type = 4, 
#        Requiered = False
#        )
#
#    create_option(
#        name = "max_number", 
#        description = "Nombre maximum souhaité", 
#        options_type = 4, 
#        Requiered = False
#        )
#])
#
#async def roll(ctx, min_number = 1, max_number = 6):
#    num = random.randint(min_number, max_number)
#    await ctx.send(f"**{num}** !")

bot.run(Token)


# https://www.youtube.com/watch?v=DZLqwGVSpwA
