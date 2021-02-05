import discord
from discord.ext import commands
from discord.ext.commands import Cog
from pymongo import MongoClient
import os

bot = commands.Bot(command_prefix = "/")
bot.remove_command("help")

try:
    base = MongoClient(
        "mongodb+srv://<login>:<password>@cluster0.zhcp1.mongodb.net/DisData?retryWrites=true&w=majority")
    db = base["<name>"]
    coll = db["<name>"]
    print("MongoDB connected")
except:
    print("Not connect to MongoDB")

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

bad_words = [] #Chat filter

class Dis_bot():

    @bot.event
    async def on_ready():
        print("Bot connect")

    @bot.event
    async def on_member_join(member):
        await member.send("Поздравляю со вступлением на сервер!")
        id = member.id
        if coll.count_documents({"_id": id}) == 0:
            coll.insert_one(
                {"_id": id, "name": member.display_name, "balance": 50, "messages": 0, "level": 0, "xp": 0})

    @bot.event
    async def on_voice_state_update(member, before, after):
        if after.channel != None:
            if after.channel.id == 798419641323225099:
                for guild in bot.guilds:
                    ch_category = discord.utils.get(guild.categories, id=797105360308666388)
                    channel_2 = await guild.create_voice_channel(name=f"{member.display_name}", category=ch_category)
                    await channel_2.set_permissions(member, connect=True, manage_channels=True)
                    await member.move_to(channel_2)

                def check(x, y, z):
                    return len(channel_2.members) == 0

                await bot.wait_for("voice_state_update", check=check)
                await channel_2.delete()


    @bot.event
    async def on_message(message):
        await bot.process_commands(message)
        if message.author == bot.user:
            return

        id = message.author.id
        if coll.count_documents({"_id": id}) == 0:
            coll.insert_one(
                {"_id": id, "name": message.author.display_name, "balance": 0, "messages": 0, "level": 0, "xp": 0})

        messages = coll.find_one({"_id": id})["messages"]
        bal = coll.find_one({"_id": id})["balance"]
        xp = coll.find_one({"_id": id})["xp"]
        s = 0
        m = message.content.lower()
        del_sym = [".", ",", "^", "`", "~", "'", '"', "-", "_", "=", " "]

        for u in del_sym:
            s += 1
            if u in m:
                m = m.replace(u, "")
        for i in bad_words:
            if i in m:
                await message.channel.purge(limit=1)
        messages = int(messages) + 1

        level = coll.find_one({"_id": id})["level"]
        xp_i = xp + 1
        if xp_i >= 1000:
            xp_i = 0
            level = level + 1
            await message.channel.send(f"{message.author.display_name} получает уровень {level}")
            bal = bal + 501
        else:
            bal = bal + 1
        coll.update_one({"_id": id}, {"$set": {"balance": bal, "messages": messages, "level": level, "xp": xp_i}})

        @bot.event
        async def on_command_error(ctx, error):
            if isinstance(error, commands.CommandNotFound):
                await ctx.send("Такой команды не существует!")

bot.run("<token>")