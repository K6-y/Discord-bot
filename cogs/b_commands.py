import discord
from discord.ext import commands
from pymongo import MongoClient
import datetime
from bs4 import BeautifulSoup
import requests


try:
    base = MongoClient(
        "mongodb+srv://<login>:<password>@cluster0.zhcp1.mongodb.net/DisData?retryWrites=true&w=majority")
    db = base["<name>"]
    coll = db["<name>"]
    print("MongoDB connected")
except:
    print("Not connect to MongoDB")

class Info_com(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    @commands.command(aliases = ["coronavirus"])
    async def corona(self, ctx):
        html = requests.get("https://koronavirustoday.ru/news/russia/").text
        soup = BeautifulSoup(html, "lxml")
        world = soup.find("span", class_="big olivedrab")
        russia = soup.find("span", class_="small")
        date = str(datetime.datetime.now()).split(" ")[0]
        emb = discord.Embed(title=f"Зараженных на {date}", description=f"{world.text}\n{russia.text}", color=0xff0000)
        await ctx.send(embed=emb)

    @commands.command()
    async def news(self, ctx):
        res = requests.get("https://news.rambler.ru")
        html = res.text
        soup = BeautifulSoup(html, "html.parser")
        top_news = soup.find("div", class_="top-hot-card__title")
        top = top_news.text
        emb = discord.Embed(title=top, description="Новость дня", color=0xff0000)
        await ctx.send(embed=emb)

    @commands.command(aliases=["day", "datetime"])
    async def time(self, ctx, help="Текущее время и дата"):
        dt = datetime.datetime.now()
        day = str(dt).split(" ")[0]
        time = str(dt).split(" ")[1].split(".")[0]
        emb = discord.Embed(title="Дата", description=day, color=0xff0000)
        emb.add_field(name="Время [GMT + 06:00]", value=time, inline=False)
        await ctx.send(embed=emb)

    @commands.command()
    async def info(self, ctx, member: discord.Member = None):
        if member == None:
            user = ctx.author
        else:
            user = member
        mention = []
        for role in user.roles:
            mention.append(role.mention)
            role_m = ", ".join(mention)
        m_id = user.id
        if coll.count_documents({"_id": m_id}) == 0:
            coll.insert_one({"_id": m_id, "name": user.display_name, "balance": 0, "messages": 0, "level": 0, "xp": 0})
        bal = coll.find_one({"_id": m_id})["balance"]
        msg = coll.find_one({"_id": m_id})["messages"]
        level = coll.find_one({"_id": m_id})["level"]
        xp = 1000 - coll.find_one({"_id": m_id})["xp"]

        await ctx.message.add_reaction('✅')
        emb = discord.Embed(title="Информация о пользователе:", color=0xff0000)
        emb.add_field(name="Имя:", value=user.display_name, inline=False)
        emb.add_field(name="Когда присоединился:", value=user.joined_at, inline=False)
        emb.add_field(name="Роли", value=role_m, inline=False)
        emb.add_field(name="Баланс", value=str(bal), inline=False)
        emb.add_field(name="Уровень", value=level, inline=False)
        emb.add_field(name="Xp до нового уровня", value=xp, inline=False)
        emb.add_field(name="discord ID", value=m_id, inline=False)
        emb.add_field(name="Сообщения", value=msg, inline=False)
        await ctx.send(embed=emb)


def setup(bot):
    bot.add_cog(Info_com(bot))