##########
#
#   LIBRAIRIES
#
##########

#from discord.ext import commands
#from discord import Intents
import discord

from nextcord.ext import commands
from nextcord import Interaction
import nextcord
intents = nextcord.Intents.all()
intents.message_content = True

from config import TOKEN, restartcommand
import asyncio
import aiosqlite
import random
from typing import Optional
#import datatime

bot = commands.Bot(command_prefix='$', intents=intents)
base_wallet = 0
base_bank = 500
base_maxbank = 10000

##########
#
#   LANCEMENT DU BOT
#
##########

@bot.event
async def on_ready():
    print("Papy vient de se réveiller")
    bot.db = await aiosqlite.connect("papy.db")
    await asyncio.sleep(3)
    async with bot.db.cursor() as cursor:
        await cursor.execute("CREATE TABLE IF NOT EXISTS economy(wallet INTEGER, bank INTEGER, maxbank INTEGER, user INTEGER)")
        ## Wallet = Valeur du Portefeuille, bank = Valeur en Banque, maxbank = Valeur maximum en Banque, user = ID de l'utilisateur Discord
        await cursor.execute("CREATE TABLE IF NOT EXISTS reply(message INTEGER, state INTEGER, game INTEGER, replyid INT)")
        ## message = Message lors du PREFIX(work, slut, crime), state = [success, escape, fail], game = [work, slut, crime], replyID = reconnaître un message
        await cursor.execute("CREATE TABLE IF NOT EXISTS job(minpaid INTEGER, maxpaid INTEGER, minfine INTEGER, maxfine INTEGER, chance INTEGER, game INTEGER)")
        ## minpaid = Paiement Minimum, maxpaid = Paiement Maximum, minfine = Amende Minimum, maxfine = Amende Maximum, chance = Chance de réussite, game = Jeu (work, slut, crime, rob)
        #print("Papy n'a pas trouver son classeur, il va donc en acheter un nouveau")
    await bot.db.commit()
    print("Papy vient de trouver son classeur")


##########
#
#   FONCTIONS D'ECONOMIE
#
##########

async def create_balance(user):
    async with bot.db.cursor() as cursor:
        await cursor.execute("INSERT INTO economy VALUES(?, ?, ?, ?)", (base_wallet, base_bank, base_maxbank, user.id))
    await bot.db.commit()
    return


async def get_balance(user):
    async with bot.db.cursor() as cursor:
        await cursor.execute("SELECT wallet, bank, maxbank FROM economy WHERE user = ?", (user.id,))
        data = await cursor.fetchone()
        if data is None:
            await create_balance(user)
            return base_wallet, base_bank, base_maxbank
        wallet, bank, maxbank = data[0], data[1], data[2]
        return wallet, bank, maxbank

async def update_wallet(user, amount):
    async with bot.db.cursor() as cursor:
        await cursor.execute("SELECT wallet FROM economy WHERE user = ?", (user.id,))
        data = await cursor.fetchone()

        if data is None:
            await create_balance(user)
            return 0

        await cursor.execute("UPDATE economy SET wallet = ? WHERE user = ?", (data[0] + amount, user.id))
    await bot.db.commit()


async def update_bank(user, amount):
    async with bot.db.cursor() as cursor:
        await cursor.execute("SELECT wallet, bank, maxbank FROM economy WHERE user = ?", (user.id,))
        data = await cursor.fetchone()
        
        if data is None:
            await create_balance(user)
            return 0

        capacity = int(data[2] - data[1])
        if amount > capacity:
            await update_wallet(user, amount)
            return 1

        await cursor.execute("UPDATE economy SET bank = ? WHERE user = ?", (data[1] + amount, user.id))
    await bot.db.commit()


##########
#
#   COMMANDES ECONOMIE
#
##########

@bot.command(name="balance", aliases=["bal", "b", "money",], description="Permet de voir l'argent dans le portefeuille et en banque d'un utilisateur")
async def balance(ctx: commands.Context, member: nextcord.Member = None):
    if not member:
        member = ctx.author
    wallet, bank, maxbank = await get_balance(member)
    em = nextcord.Embed(title=f"{member.name} Solde")
    em.add_field(name="Wallet", value=wallet)
    em.add_field(name="Bank", value=f"{bank}/{maxbank}")
    await ctx.send(embed=em)


@bot.command(name="work", aliases=["wor", "wk"], description="Fait un travail normal")
@commands.cooldown(1, 180, commands.BucketType.user)
async def work(ctx: commands.Context):
    chances = random.randint(1, 4)
    if chances == 1:
        return await ctx.send("Tu es en retard au travail, le patron ne veut plus de toi, tu pars les mains vides")
    amount = random.randint(50, 100)
    res = await update_wallet(ctx.author, amount)
    if res == 0:
        return await ctx.send("{restartcommand}")
    await ctx.send(f"Bravo grâce à votre travail, vous avez gagné {amount} coins !")


@bot.command(name="slut", aliases=["st"], description="Lance toi dans des travaux pas forcément bien vu")
@commands.cooldown(1, 240, commands.BucketType.user)
async def work(ctx: commands.Context):
    chances = random.randint(1, 4)
    if chances == 1:
        return await ctx.send("Tu n'as pas réussi à slut malheureusement")
    amount = random.randint(150, 300)
    res = await update_wallet(ctx.author, amount)
    if res == 0:
        return await ctx.send("{restartcommand}")
    await ctx.send(f"Bravo grâce à votre *travail*, vous avez gagné {amount} coins !")


@bot.command(name="crime", aliases=["cr", "cm"], description="Lance toi dans une carrière criminel")
@commands.cooldown(1, 300, commands.BucketType.user)
async def work(ctx: commands.Context):
    chances = random.randint(1, 4)
    if chances == 1:
        return await ctx.send("Malheureusement vous n'avez pas réussi votre coup cette fois-ci")
    amount = random.randint(300, 500)
    res = await update_wallet(ctx.author, amount)
    if res == 0:
        return await ctx.send("{restartcommand}")
    await ctx.send(f"Bravo grâce à votre *crime*, vous avez gagné {amount} coins !")


@bot.command(name="deposit", aliases=["dep", "dp"], description="Dépose de l'argent dans ta banque")
@commands.cooldown(1, 2, commands.BucketType.user)
async def deposit(ctx: commands.Context, amount):
    wallet, bank, maxbank = await get_balance(ctx.author)
    try:
        amount = int(amount)
    except ValueError:
        pass

    if type(amount) == str:
        if amount.lower() == "max" or amount.lower() == "all":
            amount = int(wallet)
    else:
        amount = int(amount)

    bank_res = await update_bank(ctx.author, amount)
    wallet_res = await update_wallet(ctx.author, -amount)
    if bank_res == 0 or wallet_res == 0:
        return await ctx.send("{restartcommand}")
    elif bank_res == 1:
        return await ctx.send("You don't have enough storage in your bank !")

    wallet, bank, maxbank = await get_balance(ctx.author)
    em = nextcord.Embed(title=f"{amount} coins have bein deposit")
    em.add_field(name="New Wallet", value=wallet)
    em.add_field(name="New Bank", value=f"{bank}/{maxbank}")
    await ctx.send(embed=em)


@bot.command(name="withdraw", aliases=["with", "wit", "wd"], description="Retire de l'argent de ta banque")
@commands.cooldown(1, 2, commands.BucketType.user)
async def withdraw(ctx: commands.Context, amount):
    wallet, bank, maxbank = await get_balance(ctx.author)
    try:
        amount = int(amount)
    except ValueError:
        pass

    if type(amount) == str:
        if amount.lower() == "max" or amount.lower() == "all":
            amount = int(bank)
    else:
        amount = int(amount)

    bank_res = await update_bank(ctx.author, -amount)
    wallet_res = await update_wallet(ctx.author, amount)
    if bank_res == 0 or wallet_res == 0:
        return await ctx.send("{restartcommand}")
    
    wallet, bank, maxbank = await get_balance(ctx.author)
    em = nextcord.Embed(title=f"{amount} coins have bein withdrew")
    em.add_field(name="New Wallet", value=wallet)
    em.add_field(name="New Bank", value=f"{bank}/{maxbank}")
    await ctx.send(embed=em)


@bot.command()
@commands.cooldown(1, 2, commands.BucketType.user)
async def give(ctx: commands.Context, member: nextcord.Member, amount):
    wallet, bank, maxbank = await get_balance(ctx.author)
    try:
        amount = int(amount)
    except ValueError:
        pass

    if type(amount) == str:
        if amount.lower() == "max" or amount.lower() == "all":
            amount = int(bank)
    else:
        amount = int(amount)

    wallet_res = await update_wallet(ctx.author, -amount)
    wallet_res2 = await update_wallet(member, amount)
    if wallet_res == 0 or wallet_res == 0:
        return ctx.send("{restartcommand}")

    wallet2, bank2, maxbank2 = await get_balance(member)

    em = nextcord.Embed(title=f"Gave {amount} coins to {member.name}")
    em.add_field(name=f"{ctx.author.name} Wallet", value=wallet-amount)
    em.add_field(name=f"{member.name} Wallet", value=wallet2)
    await ctx.send(embed=em)


##########
#
#   COMMANDES ECONOMIE ADMINISTRATEUR
#
##########

@bot.command("add-money", aliases=["addm", "am"], description="Donne de l'argent a un membre")
@commands.cooldown(1, 1, commands.BucketType.user)
async def add_money(ctx: commands.Context, member: nextcord.Member, amount):
    wallet, bank, maxbank = await get_balance(ctx.author)
    try:
        amount = int(amount)
    except ValueError:
        pass
    res = await update_wallet(member, amount)
    await ctx.send(f"Tu as donner {amount} à {member}")


@bot.command("remove-money", aliases=["removem", "rm"], description="Retire de l'argent a un membre")
@commands.cooldown(1, 1, commands.BucketType.user)
async def remove_money(ctx: commands.Context, member: nextcord.Member, amount):
    wallet, bank, maxbank = await get_balance(ctx.author)
    try:
        amount = int(amount)
    except ValueError:
        pass
    res = await update_wallet(member, -amount)
    await ctx.send(f"Tu as retirer {amount} à {member}")

@bot.command(name="work2")
@commands.cooldown(1, 1, commands.BucketType.user)
async def work2(ctx: commands.Context):
    chances = random.randint(1, 4)
    if chances == 1:
        return await ctx.send("Tu es en retard au travail, le patron ne veut plus de toi, tu pars les mains vides")
    amount = random.randint(50, 100)
    res = await update_wallet(ctx.author, amount)
    if res == 0:
        return await ctx.send("{restartcommand}")
    await ctx.send(f"Bravo grâce à votre travail, vous avez gagné {amount} coins !")

##########
#
#   SECTION 2 (TEST)
#
##########


@bot.slash_command("echo", description="Ecrit le message souhaité")
async def echo(interaction: Interaction, message:str):
    await interaction.response.send_message(
        f"You said: {message}"
    )


@bot.slash_command("hello", description="Dis bonjour à quelqu'un")
async def hi(interaction: nextcord.Interaction, user: nextcord.Member):
    await interaction.response.send_message(
        f"{interaction.user} just said hi to {user.mention}"
    )


@bot.message_command("saytest")
async def say(interaction: nextcord.Interaction, message: nextcord.Message):
    """Sends the content of the right-clicked message as an ephemeral response"""
    await interaction.response.send_message(message.content, ephemeral=True)


##########
#
#   SECTION 3
#
##########


@bot.slash_command()
async def main(interaction: nextcord.Interaction):
    """
    This is the main slash command that will be the prefix of all commands below.
    This will never get called since it has subcommands.
    """
    pass


@main.subcommand(description="Subcommand 1")
async def sub1(interaction: nextcord.Interaction):
    """
    This is a subcommand of the '/main' slash command.
    It will appear in the menu as '/main sub1'.
    """
    await interaction.response.send_message("This is subcommand 1!")


@main.subcommand(description="Subcommand 2")
async def sub2(interaction: nextcord.Interaction):
    """
    This is another subcommand of the '/main' slash command.
    It will appear in the menu as '/main sub2'.
    """
    await interaction.response.send_message("This is subcommand 2!")


@main.subcommand()
async def main_group(interaction: nextcord.Interaction):
    """
    This is a subcommand group of the '/main' slash command.
    All subcommands of this group will be prefixed with '/main main_group'.
    This will never get called since it has subcommands.
    """
    pass


@main_group.subcommand(description="Subcommand group subcommand 1")
async def subsub1(interaction: nextcord.Interaction):
    """
    This is a subcommand of the '/main main_group' subcommand group.
    It will appear in the menu as '/main main_group subsub1'.
    """
    await interaction.response.send_message("This is a subcommand group's subcommand!")


@main_group.subcommand(description="Subcommand group subcommand 2")
async def subsub2(interaction: nextcord.Interaction):
    """
    This is another subcommand of the '/main main_group' subcommand group.
    It will appear in the menu as '/main main_group subsub2'.
    """
    await interaction.response.send_message("This is subcommand group subcommand 2!")


##########
#
#   SECTION 4
#
##########



##########
#
#   LANCEMENT DU BOT
#
##########

bot.run(TOKEN)
