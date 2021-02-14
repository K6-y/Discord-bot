import discord
from discord.ext import commands
import asyncio
from pymongo import MongoClient
from discord.ext.commands import Cog

try:
    base = MongoClient(
        "mongodb+srv://admin-user:SEdQtrptklcGpSg1@cluster0.zhcp1.mongodb.net/DisData?retryWrites=true&w=majority")
    db = base["DisBase"]
    coll = db["discord1"]
    print("MongoDB connected (Main_com)")
except:
    print("Not connect to MongoDB")


class Main_com(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    @commands.has_permissions(administrator=True)
    async def clear(self, ctx, amount=100):
        await ctx.channel.purge(limit=amount)

    @commands.command()
    @commands.has_permissions(administrator=True)
    async def kick(self, ctx, member: discord.Member, *, reason=None):
        await ctx.message.add_reaction('✅')
        await member.kick(reason=reason)
        emb = discord.Embed(title="Кик участника:", description=member.display_name, color=0xff0000)
        await ctx.send(embed=emb)

    @commands.command()
    @commands.has_permissions(administrator=True)
    async def ban(self, ctx, member: discord.Member, reason, help="Бан участника"):
        await ctx.message.add_reaction('✅')
        await member.ban(reason=reason)
        emb = discord.Embed(title="Бан участника:", description=member.display_name, color=0xff0000)
        await ctx.send(embed=emb)

    @commands.command()
    @commands.has_permissions(administrator=True)
    async def mute(self, ctx, type: str, member: discord.Member, time: str == None):
        if type.lower() == "chat":
            m_role = discord.utils.get(ctx.server.roles, name = "mute chat")
        elif type.lower() == "voice":
            m_role = discord.utils.get(ctx.server.roles, name = "mute voice")
        await member.add_roles(m_role)

        if time == None:
            emb = discord.Embed(title="Мут участника [Время не установлено]", description=f"{member.display_name}\nМут выдан: {ctx.author.display_name}", color=0xff0000)
        else:
            times = {"s": 0, "m": 60, "h": 3600}
            a = time[-1]
            del time[-1]
            asyncio.sleep(float(time.replace(",", "")) * times[a])
            member.remove_roles(m_role)
            emb = discord.Embed(title="Снятие мута", description=member.display_name, color = 0xff0000)

    @discord.ext.commands.cooldown(1, 1800)
    @commands.command(aliases=["rep"])
    async def repup(self, ctx, member: discord.Member, help="Благодарность за помощь"):
        m_id = member.id
        user = member.display_name
        if ctx.author == member:
            await ctx.send("Нельзя добавлять репутацию самому себе!")
            return
        else:
            member_info = coll.count_documents({"_id": m_id})
            if member_info == 0:
                coll.insert_one({"_id": m_id, "name": user, "balance": 30, "messages": 0, "level": 0, "xp": 0})
            bal = coll.find_one({"_id": m_id})["balance"] + 100
            xp = coll.find_one({"_id": m_id})["xp"] + 100
            coll.update_one({"_id": m_id}, {"$set": {"balance": bal, "xp": xp}})
            await ctx.message.add_reaction('✅')
            ctx.command.reset_cooldown(ctx)
            return

    @commands.command(aliases=[])
    async def transfer(self, ctx, limit: int, member: discord.Member, help="Перевод баллов"):
        a_id = ctx.author.id
        m_id = member.id
        user = ctx.author.display_name
        if coll.count_documents({"_id": a_id}) == 1:
            bal = coll.find_one({"_id": a_id})["balance"]
            if bal - limit < 0:
                await ctx.send("Недостаточно баллов!")
            else:
                if coll.count_documents({"_id": m_id}) == 0:
                    coll.insert_one(
                        {"_id": m_id, "name": member.display_name, "balance": 0, "messages": 0, "level": 0, "xp": 0})
                bal_2 = coll.find_one({"_id": m_id})["balance"]
                bal = bal - limit
                bal_2 = bal_2 + limit
                coll.update_one({"_id": a_id}, {"$set": {"balance": bal}})
                coll.update_one({"_id": m_id}, {"$set": {"balance": bal_2}})
                await ctx.message.add_reaction('✅')
        else:
            coll.insert_one({"_id": a_id, "name": user, "balance": 0, "messages": 0, "level": 0, "xp": 0})
            await ctx.send("У тебя 0 баллов!")

    @commands.command()
    async def calc(self, ctx, num_1: float, sym, num_2: float):
        if sym == "+":
            i = num_1 + num_2
            itog = f"```{num_1} + {num_2} = {i}```"

        elif sym == "-":
            i = num_1 - num_2
            itog = f"```{num_1} - {num_2} = {i}```"

        elif sym == "/":
            i = num_1 / num_2
            itog = f"```{num_1} / {num_2} = {i}```"

        elif sym == "*":
            i = num_1 * num_2
            itog = f"```{num_1} * {num_2} = {i}```"

        elif sym == "^":
            i = num_1 ** num_2
            itog = f"```{num_1} ^ {num_2} = {i}```"

        else:
            itog = "```Syntax error```"

        await ctx.send(itog)

    @commands.command()
    async def get_file(self, ctx, path: str, filename: str):
        if ctx.author.id == 694055134166253588:
            try:
                file = discord.File(path, filename=filename)
                await ctx.send(file=file)
            except:
                await ctx.send("Error!")
        else:
            await ctx.send("У вас нет прав для вызова даннгой команды!")

    # Обработка ошибок
    @get_file.error
    @calc.error
    @ban.error
    @kick.error
    @transfer.error
    async def required_argument_missing_error(self, ctx, error):
        if isinstance(error, commands.errors.MissingRequiredArgument):
            await ctx.send("Вы не указали нужные аргументы!")

    @repup.error
    async def repup_error(self, ctx, error):
        if isinstance(error, discord.ext.commands.errors.CommandOnCooldown):
            await ctx.send("Вы не можете вызывать эту команду чаще чем раз в пол часа!")


def setup(bot):
    bot.add_cog(Main_com(bot))
