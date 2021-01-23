import discord
from discord.ext import commands
import asyncio
from pymongo import MongoClient
from random import randint
import datetime
from words import *

bad_words = []


class Settings:
    token = ""
    bot = commands.Bot(command_prefix="!")


try:
    base = MongoClient(
        "mongodb+srv://<login>:<password>@cluster0.zhcp1.mongodb.net/DisData?retryWrites=true&w=majority")
    db = base["DisBase"]
    coll = db["discord1"]
    print("MongoDB connected")
except:
    print("Not connect to MongoDB")

bot = Settings.bot


@bot.event
async def on_ready():
    print(" Бот вошел как: {0.user}".format(bot))


@bot.command(aliases=["day", "datetime"])
async def time(ctx):
    dt = datetime.datetime.now()
    day = str(dt).split(" ")[0]
    time = str(dt).split(" ")[1].split(".")[0]
    emb = discord.Embed(title="Дата", description=day, color=0xff0000)
    emb.add_field(name="Время [GMT + 06:00]", value=time, inline=False)
    await ctx.send(embed=emb)


@bot.command(aliases=["помоги мне", "помоги", "команды"])
async def helpme(ctx):
    await ctx.message.add_reaction('✅')
    emb = discord.Embed(title="!Команды бота", color=0xff0000)
    emb.add_field(name="!admin", value="Просмотр команд администратора")
    emb.add_field(name="!info", value="Информация об участнике на сервере\n[Пример: !info @name]")
    emb.add_field(name="!repup (!rep)", value="Благодарность за помощь\n[Пример: !rep @name]")
    emb.add_field(name="!balance - Баланс баллов", value="[Пример: !balance]")
    emb.add_field(name="!dice(s) - Игра в кости",
                  value="Побеждает тот, у кого сумма кубиков больше\n[Пример: !dice 100]")
    emb.add_field(name="!roll - Рулетка", value="Чётное число - победа,\nнечётное - проигрыш\n[Пример: !roll 100]")
    await ctx.send(embed=emb)


@bot.command(aliases=["инфо"])
@commands.has_permissions(administrator=True)
async def admin(ctx):
    await ctx.message.add_reaction('✅')
    emb = discord.Embed(title="!Команды бота для администраторов", color=0xff0000)
    emb.add_field(name="!clear", value="Очистка чата[Пример: !clear 15]", inline=True)
    emb.add_field(name="!ban", value="Бан участника [Пример: !ban @name]", inline=True)
    emb.add_field(name="!kick", value="Кик участника [Пример: !kick @name]", inline=True)
    emb.add_field(name="!mute", value="Мут участника [Пример: !mute 5m @name]", inline=True)
    await ctx.send(embed=emb)


@bot.command()
async def info(ctx, member: discord.Member):
    mention = []
    user = member.display_name
    for role in member.roles:
        mention.append(role.mention)
        role_m = ", ".join(mention)
        old = False
    m_id = member.id
    if coll.count_documents({"_id": m_id}) == 0:
        coll.insert_one({"_id": m_id, "name": user, "balance": 0, "messages": 0, "sen": 0})
    bal = coll.find_one({"_id": m_id})["balance"]
    msg = coll.find_one({"_id": m_id})["messages"]

    await ctx.message.add_reaction('✅')
    emb = discord.Embed(title="Информация о пользователе:", color=0xff0000)
    emb.add_field(name="Имя:", value=member.display_name, inline=False)
    emb.add_field(name="Когда присоединился:", value=member.joined_at, inline=False)
    emb.add_field(name="Роли", value=role_m, inline=False)
    emb.add_field(name="Баланс", value=str(bal), inline=False)
    emb.add_field(name="discord ID", value=m_id, inline=False)
    emb.add_field(name="Сообщения", value=msg, inline=False)
    await ctx.send(embed=emb)


@bot.command(aliases=["баланс"])
async def balance(ctx, member: discord.Member):
    if not member:
        m_id = member.id
        user = member.display_name
    else:
        m_id = ctx.author.id
        user = ctx.author.display_name
    if coll.count_documents({"_id": m_id}) == 1:
        bal = coll.find_one({"_id": m_id})["balance"]
        emb = discord.Embed(title="Баланс:", description=bal + " Баллов", color=0xff0000)
        await ctx.send(embed=emb)
    else:
        coll.insert_one({"_id": m_id, "name": user, "balance": 10, "messages": 0})
        bal = coll.find_one({"_id": m_id})["balance"]
        emb = discord.Embed(title="Баланс", description=str(bal) + " баллов", color=0xff0000)
        await ctx.send(embed=emb)
    await ctx.message.add_reaction('✅')


@bot.command()
@commands.has_permissions(administrator=True)
async def clear(ctx, amount=100):
    await ctx.channel.purge(limit=amount)


@bot.command(aliases=["Кикни", "Кик", "кикни", "кик"])
@commands.has_permissions(administrator=True)
async def kick(ctx, member: discord.Member, *, reason=None):
    await ctx.message.add_reaction('✅')
    await member.kick(reason=reason)
    emb = discord.Embed(title="Кик участника:", description=member.display_name, color=0xff0000)
    await ctx.send(embed=emb)


@bot.command()
@commands.has_permissions(administrator=True)
async def ban(ctx, member: discord.Member, reason):
    await ctx.message.add_reaction('✅')
    await member.ban(reason=reason)
    emb = discord.Embed(title="Бан участника:", description=member.display_name, color=0xff0000)
    await ctx.send(embed=emb)


@bot.command(aliases=["мут"])
@commands.has_permissions(administrator=True)
async def mute(ctx, limit, member: discord.Member):
    await ctx.message.add_reaction('✅')
    m_role = discord.utils.get(ctx.message.guild.roles, name="")
    o_role = discord.utils.get(ctx.message.guild.roles, name="")
    await member.add_roles(m_role)
    await member.remove_roles(o_role)

    if "h" in limit:
        limit2 = float(limit.replace("h", "")) * 3600
    elif "m" in limit:
        limit2 = float(limit.replace("m", "")) * 60
    elif "s" in limit:
        limit2 = float(limit.replace("s", ""))

    a = "Мут участника [" + limit + "]"
    emb = discord.Embed(title=a, description=member.display_name, color=0xff0000)
    emb.add_field(name="Мут выдан:", value=ctx.author.display_name)
    await ctx.send(embed=emb)
    await asyncio.sleep(float(limit2))
    await member.add_roles(o_role)
    await member.remove_roles(m_role)
    b = "Снятие мута [" + limit + "]"
    emb = discord.Embed(title=b, description=member.display_name, color=0xff0000)
    await ctx.send(embed=emb)


@discord.ext.commands.cooldown(1, 1800)
@bot.command(aliases=["rep"])
async def repup(ctx, member: discord.Member):
    m_id = member.id
    user = member.display_name
    if ctx.author == member:
        await ctx.send("Нельзя добавлять репутацию самому себе!")
        return
    member_info = coll.count_documents({"_id": m_id})
    if member_info == 0:
        coll.insert_one({"_id": m_id, "name": user, "balance": 30, "messages": 0})
        ctx.command.reset_cooldown(ctx)
        return
    coll.update_one({"_id": m_id}, {"$set": {"balance": 30}})
    await ctx.message.add_reaction('✅')


@repup.error
async def repup_error(ctx, error):
    if isinstance(error, discord.ext.commands.errors.CommandOnCooldown):
        await ctx.send("Вы не можете вызывать эту команду чаще чем раз в пол часа.")


# Игра в кости
@bot.command(aliases=["dices"])
async def dice(ctx, limit):
    m_id = ctx.author.id
    user = ctx.author.display_name
    if coll.count_documents({"_id": m_id}) == 1:
        bal = coll.find_one({"_id": m_id})["balance"]
        if bal < 0:
            await ctx.send("У тебя недостаточно баллов!")
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
                win = int(limit) * 2
                itog = int(bal) + win
                title = "Победа!"
            elif sum1 == sum2:
                await ctx.send("Ничья!")
            elif sum1 < sum2:
                itog = int(bal) - int(limit)
                title = "Проигрыш!"

            await ctx.send(title + "\n[Баланс: " + str(itog) + "]")
            coll.update_one({"_id": m_id}, {"$set": {"balance": itog}})
    else:
        await ctx.send("У тебя 0 баллов!")
        coll.insert_one({"_id": m_id, "name": user, "balance": 0, "messages": 0})


# Рулетка
@bot.command(aliases=["spin"])
async def roll(ctx, limit):
    m_id = ctx.author.id
    user = ctx.author.display_name
    if coll.count_documents({"_id": m_id}) == 1:
        bal = coll.find_one({"_id": m_id})["balance"]
        value = int(bal) - int(limit)
        if value < 0:
            await ctx.send("Недостаточно баллов!")
        elif int(limit) < 5:
            await ctx.send("Минимальная ставка - 5 токенов!")
        else:
            r = randint(1, 32)
            rand = randint(1, 32)
            rands = [randint(1, 32), randint(1, 32), randint(1, 32)]
            msg = await ctx.send("Твое число:" + str(rand))
            for i in rands:
                await msg.edit(content="Твоё число:" + str(i))
            await msg.edit(content="Твоё число:" + str(r))
            if (r % 2) == 0:
                itog = str(value)
                await ctx.send("Ты проиграл! [Баланс: " + str(value) + "]")
            else:
                win = int(limit) * 2
                itog = value + win
                await ctx.send("Ты выиграл! [Баланс: " + str(itog) + "]")
            coll.update_one({"_id": m_id}, {"$set": {"balance": itog}})
    else:  # Если участника нет в базе
        coll.insert_one({"_id": m_id, "name": user, "balance": 0, "messages": 0})
        await ctx.send("У тебя 0 баллов!")


@bot.event
async def on_message(message):
    await bot.process_commands(message)
    if message.author == bot.user:
        return

    id = message.author.id
    if coll.count_documents({"_id": id}) == 0:
        coll.insert_one({"_id": id, "name": message.author.display_name, "balance": 0, "messages": 0})

    messages = coll.find_one({"_id": id})["messages"]
    bal = coll.find_one({"_id": id})["balance"]
    s = 0
    msg = message.content.lower()
    m = message.content.lower()
    del_sym = [".", ",", "^", "`", "~", "'", '"', "-", "_", "=", " "]

    for u in del_sym:
        s += 1
        if u in m:
            m = m.replace(u, "")
    if s == len(del_sym):
        for i in bad_words:
            if i in m:
                await message.channel.purge(limit=1)
    coll.update_one({"_id": id}, {"$set": {"balance": bal + 1, "messages": messages + 1}})

    for i in all_lists:
        for u in i:
            if u in msg:
                ind = all_lists.index(i)
                answ = all_answ[ind]
                r = randint(0, len(answ) - 1)
                answer = answ[r]
                await message.channel.send(answer)

# Токен
bot.run(Settings.token)
