import discord
from discord.ext import commands
import sqlite3


class VotingCog(commands.Cog):
    """Cog for handling voting system."""

    def __init__(self, bot):
        self.bot = bot
        self.votes = {}
        self.voting_active = False
        self.voting_paused = False
        self.required_role_id = 920121491788533832  # ID da tag necessarily

        # Conectar ao banco de dados SQLite
        self.conn = sqlite3.connect('voting_data.db')
        self.c = self.conn.cursor()
        self.create_table()
        self.bot.loop.create_task(self.load_votes())

    def create_table(self):
        self.c.execute('''CREATE TABLE IF NOT EXISTS votes (
                            user_id INTEGER PRIMARY KEY,
                            vote_count INTEGER NOT NULL)''')
        self.conn.commit()

    async def load_votes(self):
        self.c.execute('SELECT user_id, vote_count FROM votes')
        rows = self.c.fetchall()
        for row in rows:
            user_id, vote_count = row
            user = self.bot.get_user(user_id) or await self.bot.fetch_user(user_id)
            self.votes[user] = vote_count

        if self.votes:
            self.voting_active = True
            print("Votos carregados e votação ativada.")
        else:
            print("Nenhum voto encontrado no banco de dados.")

    def save_votes(self):
        self.c.execute('DELETE FROM votes')
        for user, vote_count in self.votes.items():
            self.c.execute('INSERT INTO votes (user_id, vote_count) VALUES (?, ?)', (user.id, vote_count))
        self.conn.commit()

    @commands.command(name="start_voting")
    @commands.has_permissions(administrator=True)
    async def start_voting(self, ctx, *members: discord.Member):
        """Starts a new voting session with the mentioned users. Only administrators can use this command."""
        self.votes = {}
        self.c.execute('DELETE FROM votes')  # Limpa a tabela de votos antiga
        self.conn.commit()

        for member in members:
            self.votes[member] = 0

        if not self.votes:
            await ctx.send("Nenhum usuário válido fornecido para a votação.")
            return

        self.voting_active = True
        self.voting_paused = False
        self.save_votes()
        await self.display_participants(ctx)

    @commands.command(name="end_voting")
    @commands.has_permissions(administrator=True)
    async def end_voting(self, ctx):
        """Ends the current voting session. Only administrators can use this command."""
        # Verificar se existe votação no banco de dados
        self.c.execute('SELECT COUNT(*) FROM votes')
        if self.c.fetchone()[0] == 0:
            await ctx.send("Nenhuma votação está ativa no momento.")
            return

        self.voting_active = False

        results = "```\n"
        results += f"{'Nome':<20} {'Votos':<10}\n"
        results += f"{'-' * 20} {'-' * 10}\n"

        # Carregar dados do banco de dados para exibir os resultados
        self.c.execute('SELECT user_id, vote_count FROM votes')
        rows = self.c.fetchall()
        for row in rows:
            user_id, vote_count = row
            user = self.bot.get_user(user_id) or await self.bot.fetch_user(user_id)
            results += f"{user.display_name:<20} {vote_count:<10}\n"
        results += "```"

        await ctx.send(f"Votação encerrada! Resultados finais:\n{results}")

        # Reset the voting data
        self.votes = {}
        self.c.execute('DELETE FROM votes')
        self.conn.commit()

    @commands.command(name="pause_voting")
    @commands.has_permissions(administrator=True)
    async def pause_voting(self, ctx):
        """Pauses or resumes the current voting session. Only administrators can use this command."""
        # Verificar se existe votação no banco de dados
        self.c.execute('SELECT COUNT(*) FROM votes')
        if self.c.fetchone()[0] == 0:
            await ctx.send("Nenhuma votação está ativa no momento.")
            return

        self.voting_paused = not self.voting_paused
        status = "pausada" if self.voting_paused else "retomada"
        await ctx.send(f"A votação foi {status}.")

    @commands.command(name='vote')
    async def vote(self, ctx, user: discord.Member):
        """Vote for a user. Users can vote as many times as they want."""
        if not self.voting_active:
            await ctx.send("Nenhuma votação está ativa no momento.")
            return

        if self.voting_paused:
            await ctx.send("A votação está pausada no momento.")
            return

        # Verificar se o usuário tem a tag específica
        role = discord.utils.get(ctx.guild.roles, id=self.required_role_id)
        if role not in ctx.author.roles:
            await ctx.send("Você não tem permissão para votar. É necessário ter a tag específica.")
            return

        # Verificar se o usuário está em um canal de voz
        if not ctx.author.voice or not ctx.author.voice.channel:
            await ctx.send("Você precisa estar em um canal de voz para votar.")
            return

        # Verificar se o usuário está participando da votação
        self.c.execute('SELECT user_id FROM votes WHERE user_id = ?', (user.id,))
        if self.c.fetchone() is None:
            await ctx.send("Usuário inválido. Verifique os participantes da votação e tente novamente.")
            return

        # Incrementar o voto
        self.c.execute('UPDATE votes SET vote_count = vote_count + 1 WHERE user_id = ?', (user.id,))
        self.conn.commit()

        self.votes[user] = self.votes.get(user, 0) + 1
        await self.display_results(ctx)

    async def display_participants(self, ctx):
        """Displays the list of participants in the voting session."""
        participants = "```\n"
        participants += f"{'Nome':<20} {'Votos':<10}\n"
        participants += f"{'-' * 20} {'-' * 10}\n"

        for user in self.votes:
            participants += f"{user.display_name:<20} {self.votes[user]:<10}\n"

        participants += "```"
        await ctx.send(f"Votação iniciada! Os participantes são:\n{participants}")

    async def display_results(self, ctx):
        """Displays the current results of the voting session."""
        results = "```\n"
        results += f"{'Nome':<20} {'Votos':<10}\n"
        results += f"{'-' * 20} {'-' * 10}\n"

        for user, votes in self.votes.items():
            user = user if not isinstance(user, int) else await self.bot.fetch_user(user)
            results += f"{user.display_name:<20} {votes:<10}\n"

        results += "```"
        await ctx.send(f"Resultados atuais:\n{results}")


async def setup(bot):
    await bot.add_cog(VotingCog(bot))
