import discord
from discord.ext import commands
import asyncio
from pymongo import MongoClient
from random import randint
import datetime
from bs4 import BeautifulSoup
import requests

bad_words = []  #запрещённые слова

try:  #Подключение к БД
    base = MongoClient(
        "mongodb+srv://<login>:<password>@cluster0.zhcp1.mongodb.net/DisData?retryWrites=true&w=majority")
    db = base["<base_name>"]
    coll = db["<collection_name>"]
    print("MongoDB connected")
except:
    print("Not connect to MongoDB")

#Настройки
class Settings:
    token = ""
    bot = commands.Bot(command_prefix="!")


bot = Settings.bot


class Discord_bot():

    @bot.event
    async def on_ready():
        print(" Бот вошел как: {0.user}".format(bot))

    @bot.event
    async def on_voice_state_update(member, before, after):
        if after.channel != None:
            if after.channel.id == <id>:
                for guild in bot.guilds:
                    ch_category = discord.utils.get(guild.categories, id=<id>)
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

    @bot.command()
    async def news(ctx, help="Главная новость дня с rambler.ru"):
        res = requests.get("https://news.rambler.ru")
        html = res.text
        soup = BeautifulSoup(html, "lxml")
        top_news = soup.find("div", class_="top-hot-card__title")
        top = top_news.text
        emb = discord.Embed(title=top, description="Новость дня", color=0xff0000)
        await ctx.send(embed=emb)

    @bot.command(aliases=["day", "datetime"])
    async def time(ctx, help="Текущее время и дата"):
        dt = datetime.datetime.now()
        day = str(dt).split(" ")[0]
        time = str(dt).split(" ")[1].split(".")[0]
        emb = discord.Embed(title="Дата", description=day, color=0xff0000)
        emb.add_field(name="Время [Часовой пояс]", value=time, inline=False)
        await ctx.send(embed=emb)

    @bot.command(aliases=["админ"])
    @commands.has_permissions(administrator=True)
    async def admin(ctx, help="Просмотр команд администратора"):
        await ctx.message.add_reaction('✅')
        emb = discord.Embed(title="!Команды бота для администраторов", color=0xff0000)
        emb.add_field(name="!clear", value="Очистка чата[Пример: !clear 15]", inline=True)
        emb.add_field(name="!ban", value="Бан участника [Пример: !ban @name]", inline=True)
        emb.add_field(name="!kick", value="Кик участника [Пример: !kick @name]", inline=True)
        emb.add_field(name="!mute", value="Мут участника [Пример: !mute 5m @name]", inline=True)
        await ctx.send(embed=emb)

    @bot.command()
    async def info(ctx, member: discord.Member = None, help="Информация об участнике сервера"):
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
            coll.insert_one({"_id": m_id, "name": user, "balance": 0, "messages": 0, "level": 0, "xp": 0})
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

    @bot.command()
    @commands.has_permissions(administrator=True)
    async def clear(ctx, amount=100, help="Очистка чата"):
        await ctx.channel.purge(limit=amount)

    @bot.command(aliases=["Кикни", "Кик", "кикни", "кик"])
    @commands.has_permissions(administrator=True)
    async def kick(ctx, member: discord.Member, *, reason=None, help="Кик участника"):
        await ctx.message.add_reaction('✅')
        await member.kick(reason=reason)
        emb = discord.Embed(title="Кик участника:", description=member.display_name, color=0xff0000)
        await ctx.send(embed=emb)

    @bot.command()
    @commands.has_permissions(administrator=True)
    async def ban(ctx, member: discord.Member, reason, help="Бан участника"):
        await ctx.message.add_reaction('✅')
        await member.ban(reason=reason)
        emb = discord.Embed(title="Бан участника:", description=member.display_name, color=0xff0000)
        await ctx.send(embed=emb)

    @discord.ext.commands.cooldown(1, 1800)
    @bot.command(aliases=["rep"])
    async def repup(ctx, member: discord.Member, help="Благодарность за помощь"):
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

    @repup.error
    async def repup_error(ctx, error):
        if isinstance(error, discord.ext.commands.errors.CommandOnCooldown):
            await ctx.send("Вы не можете вызывать эту команду чаще чем раз в пол часа!")

    @bot.command(aliases=[])
    async def transfer(ctx, limit: int, member: discord.Member, help="Перевод баллов"):
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

    @bot.command(aliases=["dices"])
    async def dice(ctx, limit: int, help="Игра в кости"):
        m_id = ctx.author.id
        user = ctx.author.display_name
        if coll.count_documents({"_id": m_id}) == 1:
            bal = coll.find_one({"_id": m_id})["balance"]
            value = bal - limit
            if value < 0:
                await ctx.send("У тебя недостаточно баллов!")
            elif int(limit) < 10:
                await ctx.send("Минимальная ставка - 10 токенов!")
            elif int(limit) <= 0:
                await ctx.send("Нельзя ставить 0 баллов!")
            else:
                r1 = randint(1, 6)
                r2 = randint(1, 6)
                r3 = randint(1, 6)
                r4 = randint(1, 6)
                sum1 = r1 + r2
                sum2 = r3 + r4
                await ctx.send("Твои кости:\n" + str(r1) + " и " + str(r2) + " [" + str(sum1) + "]")
                await asyncio.sleep(3)
                await ctx.send("Мои кости:\n" + str(r3) + " и " + str(r4) + " [" + str(sum2) + "]")
                if sum1 > sum2:
                    win = limit
                    itog = bal + win
                    title = "Победа!"
                elif sum1 == sum2:
                    await ctx.send("Ничья!")
                elif sum1 < sum2:
                    itog = bal - limit
                    title = "Проигрыш!"

                await ctx.send(title + "\n[Баланс: " + str(itog) + "]")
                coll.update_one({"_id": m_id}, {"$set": {"balance": itog}})
        else:
            await ctx.send("У тебя 0 баллов!")
            coll.insert_one({"_id": m_id, "name": user, "balance": 0, "messages": 0, "xp": 0})

    # Обработка ошибок
    @info.error
    @ban.error
    @kick.error
    @mute.error
    @transfer.error
    @dice.error
    async def required_argument_missing_error(ctx, error):
        if isinstance(error, commands.errors.MissingRequiredArgument):
            await ctx.send("Вы не указали нужные аргументы!")

    @bot.event
    async def on_command_error(ctx, error):
        if isinstance(error, commands.CommandNotFound):
            await ctx.send("Такой команды не существует!")


# Токен
bot.run(Settings.token)
