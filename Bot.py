import discord
from discord.ext import commands
from discord.ext.commands import Cog
from pymongo import MongoClient
import os

bot = commands.Bot(command_prefix = "/")
bot.remove_command("help")


@bot.command()
async def load(ctx, extension):
    bot.load_extension(f"cogs.{extension}")

@bot.command()
async def unload(ctx, extension):
    bot.unload_extension(f"cogs.cogs.{extension}")

@bot.command()
async def reload(ctx, extension):
    bot.load_extension(f"cogs.{extension}")

for file_name in os.listdir("./cogs"):
    if file_name.endswith(".py"):
        bot.load_extension(f"cogs.{file_name[:-3]}")

bot.run("<token>")