import logging
import discord
from discord.ext import commands
from discord import app_commands
import sqlite3
from datetime import datetime
from apikeys import BOTTOKEN
import os
import asyncio

# Configuração de logging
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s:%(levelname)s:%(name)s: %(message)s',
                    handlers=[
                        logging.FileHandler("bot.log"),
                        logging.StreamHandler()
                    ])

# Conexão global com o banco de dados
conn = sqlite3.connect('voice_time.db')
c = conn.cursor()

# Função para garantir que a tabela exista
def ensure_table_exists():
    c.execute('''CREATE TABLE IF NOT EXISTS voice_time (
                 user_id INTEGER PRIMARY KEY,
                 join_time TEXT,
                 total_time_seconds INTEGER)''')
    conn.commit()

ensure_table_exists()

# Defina os intents
intents = discord.Intents.default()
intents.message_content = True  # Permite que o bot leia o conteúdo das mensagens
intents.voice_states = True  # Permite que o bot leia o estado de voz dos usuários

# Define o bot
bot = commands.Bot(command_prefix='!', intents=intents)

@bot.event
async def on_ready():
    logging.info(f'Logged in as {bot.user.name} ({bot.user.id})')
    logging.info('------')
    try:
        synced = await bot.tree.sync()
        logging.info(f"Synced {len(synced)} command(s)")
    except Exception as e:
        logging.error(f"Failed to sync commands: {e}")

@bot.event
async def on_voice_state_update(member, before, after):
    if before.channel != after.channel:
        if before.channel is not None:
            await update_user_voice_time(member.id, False)
        if after.channel is not None:
            await update_user_voice_time(member.id, True)

async def update_user_voice_time(user_id, entered_channel):
    c.execute("SELECT join_time, total_time_seconds FROM voice_time WHERE user_id=?", (user_id,))
    user_data = c.fetchone()
    if user_data is None:
        c.execute("INSERT INTO voice_time (user_id, join_time, total_time_seconds) VALUES (?, ?, ?)", (user_id, datetime.now().isoformat(), 0))
        conn.commit()
        user_data = (datetime.now().isoformat(), 0)

    if entered_channel:
        c.execute("UPDATE voice_time SET join_time=? WHERE user_id=?", (datetime.now().isoformat(), user_id))
        conn.commit()
    else:
        join_time = datetime.fromisoformat(user_data[0])
        delta = datetime.now() - join_time
        total_time_seconds = user_data[1] + delta.total_seconds()
        c.execute("UPDATE voice_time SET total_time_seconds=?, join_time=? WHERE user_id=?", (total_time_seconds, None, user_id))
        conn.commit()

@bot.command(name="check_time")
async def check_time(ctx, user: discord.User = None):
    if user is None:
        user = ctx.author

    c.execute("SELECT total_time_seconds FROM voice_time WHERE user_id=?", (user.id,))
    user_data = c.fetchone()

    if user_data is None:
        await ctx.send("Esse usuário ainda não passou tempo em um canal de voz.")
    else:
        total_time_seconds = user_data[0]
        hours = total_time_seconds // 3600
        minutes = (total_time_seconds % 3600) // 60
        await ctx.send(f"O usuário {user.mention} passou {hours} horas e {minutes} minutos em chamadas de voz.")

@bot.command(name="check_all_times")
async def check_all_times(ctx):
    c.execute("SELECT user_id, total_time_seconds FROM voice_time")
    all_user_data = c.fetchall()

    if not all_user_data:
        await ctx.send("Nenhum dado de tempo de voz encontrado.")
    else:
        message = "```\n"
        message += f"{'Usuário':<20} {'TEMPO':<20}\n"
        message += f"{'-' * 20} {'-' * 20}\n"

        for user_data in all_user_data:
            user_id = user_data[0]
            total_time_seconds = user_data[1]
            user = ctx.guild.get_member(user_id)
            if user is not None:
                hours = total_time_seconds // 3600
                minutes = (total_time_seconds % 3600) // 60
                time_str = f"{hours}h {minutes}m"
                message += f"{user.display_name:<20} {time_str:<20}\n"
            else:
                message += f"ID de Usuário {user_id:<20} {total_time_seconds // 3600}h {(total_time_seconds % 3600) // 60}m\n"

        message += "```"
        await ctx.send(message)

@bot.command(name="reset_voice_time")
@commands.has_permissions(administrator=True)
async def reset_voice_time(ctx):
    await ctx.send("Você tem certeza que deseja resetar todos os dados de tempo de voz? Responda 'sim' para confirmar.")

    def check(m):
        return m.author == ctx.author and m.content.lower() == 'sim' and m.channel == ctx.channel

    try:
        confirmation = await bot.wait_for('message', check=check, timeout=30.0)
        if confirmation:
            c.execute("DELETE FROM voice_time")
            conn.commit()
            await ctx.send("Todos os dados de tempo de voz foram resetados.")
    except asyncio.TimeoutError:
        await ctx.send("Comando de reset cancelado. Nenhuma alteração foi feita.")

@reset_voice_time.error
async def reset_voice_time_error(ctx, error):
    if isinstance(error, commands.MissingPermissions):
        await ctx.send("Você não tem permissão para usar este comando.")

@bot.event
async def on_disconnect():
    logging.info("Bot desconectado do Discord.")

# Função principal para iniciar o bot
async def main():
    async with bot:
        await bot.load_extension("my_cog")  # Carregando o cog como uma extensão
        await bot.start(BOTTOKEN)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logging.info("Bot stopped manually")
