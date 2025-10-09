import ast
import logging
import ssl
import os
from xml.dom import SyntaxErr

import matplotlib.pyplot as plt
import io

from datetime import datetime, timedelta, timezone
import signal
import asyncio

import aiohttp
import discord
from discord.ext import commands, tasks
from discord.ui import View, Button
from dotenv import load_dotenv
from unicodedata import category
from aiohttp import web
import json

import embeds
import responses
import urllib.parse
import json
from aiohttp import web

# Load Token
load_dotenv()
token = os.getenv('DISCORD_TOKEN_TEST')
CRAFTY_URL = os.getenv("CRAFTY_URL_TEST")
CRAFTY_USER = os.getenv("CRAFTY_USER")
CRAFTY_PASS = os.getenv("CRAFTY_PASS")
SERVER_ID = os.getenv("CRAFTY_SERVER_ID")

sslcontext = ssl.create_default_context()
sslcontext.check_hostname = False
sslcontext.verify_mode = ssl.CERT_NONE

handler = logging.FileHandler(filename='discord.log', encoding='utf-8', mode='w')

class LoriKeeperBot(commands.Bot):
    async def setup_hook(self):
        # Persistente Views registrieren
        self.add_view(ApplicationView())
        self.add_view(TicketView())

# Bot Setup
intents = discord.Intents.default()
intents.message_content = True  # NOQA
intents.reactions = True  # NOQA
intents.members = True  # NOQA
intents.guilds = True  # NOQA
intents.voice_states = True  # NOQA

bot = LoriKeeperBot(command_prefix='>', intents=intents, case_insensitive=True)

# Global Variables
user_join_times = {}
user_total_time_in_vc = {}
total_times_user_joined_vc = {}
user_deaf_times = {}  # Speichert taube Zeit pro Benutzer
user_deaf_start_times = {}  # Speichert den Start der tauben Zeit
total_times_user_sent_message = {}
total_times_user_sent_bot_command = {}
weekly_resets = {}
total_coins = {}
message_link = 1404508158243901514
cpu_history = []
ram_history = []
server_status_update_interval = 600

# IDs
bot_id = 1403766234931265606

guild_id = 1403166544535752734

bot_channel_id = 1403194456693538817
server_info_channel_id = 1403183602371530872
general_channel_id = 1403166544535752737
donation_channel_id = 1403540478691115202

visitor_role_id = 1403206694351405066
player_role_id = 1403198812398293156
donator_role_id = 1425732160031297618
support_role_id = 1403199038253436988
mod_role_id = 1403198483795542106

applications_category_id = 1403197590375235614
application_channel_id = 1403182061413601310
test_channel_id = 1403204592673751160
APPLICATION_EMOJI = "📝"

tickets_category_id = 1403197547664769084
ticket_channel_id = 1403183472243114035
TICKET_EMOJI = "📩"

archive_category_id = 1404218130502254757

@bot.command()
async def create_channel(guild, user, channel_category, channel_name: str):
    if category is None:
        print("Kategorie wurde nicht gefunden!")
        return

    # Neuen Text-Channel in der Kategorie erstellen
    new_channel = await guild.create_text_channel(
        name=channel_name,
        category=channel_category,
        reason=f"Auto generated channel for {user}"
    )

    # Permission Overwrites setzen
    overwrites = {
        guild.default_role: discord.PermissionOverwrite(read_messages=False),  # @everyone kann nicht lesen
        user: discord.PermissionOverwrite(read_messages=True, send_messages=True),  # Ticket-Ersteller hat Zugang
        guild.get_role(support_role_id): discord.PermissionOverwrite(read_messages=True, send_messages=True), # Beispiel: Support-Rolle hat auch Zugang
    }
    await new_channel.edit(overwrites=overwrites)
    return new_channel

async def handle_application_button(interaction: discord.Interaction):
    user = interaction.user
    guild = interaction.guild
    channel_category = guild.get_channel(applications_category_id)
    channel_name = user.name + "'s Application"
    application_channel = await create_channel(guild, user, channel_category, channel_name)
    embed = embeds.application_message_embed(discord, guild, user, support_role_id)
    current_working_directory = os.getcwd()
    print("Current Working Directory:", current_working_directory) #todo change the working directory
    file = discord.File("DiscordBots/Lori Keeper/pictures/application_question.png", filename="application_question.png")
    embed.set_image(url="attachment://application_question.png")
    await application_channel.send(embed=embed, file=file)
    return application_channel

async def handle_ticket_button(interaction: discord.Interaction):
    user = interaction.user
    guild = interaction.guild
    channel_category = guild.get_channel(tickets_category_id)
    channel_name = user.name + "'s Ticket"
    ticket_channel = await create_channel(guild, user, channel_category, channel_name)
    message = f"Hello {interaction.user.mention}! A {guild.get_role(support_role_id).mention} will join the conversation shortly. In the meantime please elaborate your request."
    await ticket_channel.send(message)
    return ticket_channel

class ApplicationView(View):
    def __init__(self):
        super().__init__(timeout=None)  # Keine Ablaufzeit

    @discord.ui.button(label=f"{APPLICATION_EMOJI} Apply", style=discord.ButtonStyle.gray, custom_id="start_application")
    async def application_button_callback(self, interaction: discord.Interaction, button: Button):
        if  interaction.guild.get_member(interaction.user.id).get_role(player_role_id) is None:
            new_channel = await handle_application_button(interaction)
            await interaction.response.send_message(f"Jump to {new_channel.jump_url} to continue!", ephemeral=True, delete_after=5)
        else:
            await interaction.response.send_message(f"You are already a player on the server ;)", ephemeral=True, delete_after=5)

class TicketView(View):
    def __init__(self):
        super().__init__(timeout=None)  # Keine Ablaufzeit

    @discord.ui.button(label=f"{TICKET_EMOJI} Create Ticket", style=discord.ButtonStyle.gray, custom_id="create_ticket")
    async def ticket_button_callback(self, interaction: discord.Interaction, button: Button):
        new_channel = await handle_ticket_button(interaction)
        await interaction.response.send_message(f"Jump to {new_channel.jump_url} to continue!", ephemeral=True, delete_after=5)

@bot.event
async def on_ready():

    #channel = bot.get_channel(application_channel_id)
    #if channel:
    #    embed = discord.Embed(
    #        title="Application",
    #        description="Press the button below to start the application progress.",
    #        color=discord.Color.blue()
    #    )
    #    embed.add_field(name="Info", value="We will try to process it as quickly as possible.", inline=False)
    #    await channel.send(embed=embed, view=ApplicationView())

    #channel = bot.get_channel(ticket_channel_id)
    #if channel:
    #    embed = discord.Embed(
    #        title="Support Tickets",
    #        description="Press the button below to create a ticket.",
    #        color=discord.Color.blue()
    #    )
    #    embed.add_field(name="Info", value="We will try to help you as soon as possible.", inline=False)
    #    await channel.send(embed=embed, view=TicketView())

    if not update_stats_loop.is_running():
        update_stats_loop.start()

    await start_webhook_server()
    print("Bot is ready")

@bot.event
async def on_member_join(member: discord.Member):
    guild = member.guild
    role = guild.get_role(visitor_role_id)
    if role:
        await member.add_roles(role, reason="Auto-assign Visitor role on join")


@bot.event  #Hier reagiert der Bot auf die gesetzte Nachricht um eine Auswahlmöglichkeit ein Rollen bereit zustellen
async def on_message(member_instance):
    global total_coins
    user = member_instance.author.name

    await bot.process_commands(member_instance)
    if member_instance.author.id != 1403766234931265606:
      #total_times_user_sent_bot_command[user] = await add_to_statistic_dictionary.add_one(user, total_times_user_sent_bot_command, total_coins, True)
      #total_coins = await coins.weekly_message_coins(user, weekly_resets, total_coins, "bot_command")
      return

@bot.command(name="close", help="Moves the channel to the archive")
async def close_ticket(ctx):
    channel = ctx.channel
    category = channel.category
    archive_category = discord.utils.get(ctx.guild.categories, id=archive_category_id)

    if not archive_category:
        await ctx.send("Archive category not found.")
        return

    if category.id == tickets_category_id or category.id == applications_category_id:
        category_overwrites = archive_category.overwrites
        await channel.edit(category=archive_category, overwrites=category_overwrites, reason=f"Archiviert von {ctx.author}")
        await ctx.send(f"Channel got moved to the **{archive_category.name}** category.")


def confirm_check(ctx):
    def inner_check(message):
        return (
            message.author == ctx.author  # gleicher Nutzer
            and message.channel == ctx.channel  # gleicher Channel
            and message.content.lower() in ["y", "n"]  # nur y/n erlaubt
        )
    return inner_check

@bot.command(name="del", help="Löscht den aktuellen Channel")
@commands.has_permissions(manage_channels=True)
async def delete_channel(ctx):
    channel = ctx.channel
    category = channel.category

    if category.id in (tickets_category_id, applications_category_id):
        await channel.delete(reason=f"Gelöscht von {ctx.author}")
    else:
        await ctx.send("Are you sure you want to delete this channel? It cannot be restored. y/n")

        try:
            msg = await bot.wait_for(
                "message",
                check=confirm_check(ctx),  # ausgelagerte Check-Funktion
                timeout=30.0
            )
        except asyncio.TimeoutError:
            await ctx.send("⏳ Time ran out. Canceled.")
            return

        if msg.content.lower() == "y":
            await channel.delete(reason=f"Deleted by {ctx.author}")
        else:
            await ctx.send("❌ Canceled.")

@bot.command(name="add", help="Give a player access to channel")
@commands.has_permissions(manage_channels=True)
async def give_access(ctx, member: discord.Member):
    channel = ctx.channel

    # Erstelle PermissionOverwrites für den Member
    overwrite = discord.PermissionOverwrite(read_messages=True, send_messages=True)

    # Setze die Overwrites im aktuellen Channel
    await channel.set_permissions(member, overwrite=overwrite)

    await ctx.send(f"Welcome to the conversation, {member.mention}!")

@bot.command(name="approve", help="Gives User Player Role and access to the server")
@commands.has_role(support_role_id)
async def promotion_to_player(ctx, member: discord.Member):
    visitor_role = ctx.guild.get_role(visitor_role_id)
    player_role = ctx.guild.get_role(player_role_id)
    await member.add_roles(player_role, reason=f"Role given by {ctx.author}")
    await member.remove_roles(visitor_role, reason=f"Role removed by {ctx.author}")
    channel = bot.get_channel(general_channel_id)
    message = await ctx.send(f"Congratulations {member.mention}, your application got accepted! You are an official "
                             f"{player_role.mention} of the server now!!\nCheck out the https://discord.com/channels/1403166544535752734/1403183602371530872"
                             f" to get the Server IP & Modpack and finally dive in our world 🎮\n"
                             f" Note: You'll get a Whitelist-Code when joining the server for the first time. Navigate to {channel.mention} and type /link with the given code to link your discord account with your mc account")
    await responses.add_celebration_reactions(message, 2)

@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.MissingRole):
        await ctx.reply("Leave that to the mods please ;)")
    else:
        raise error

# API
async def fetch_crafty_token(session):
    url = f"{CRAFTY_URL}/api/v2/auth/login"
    payload = {"username": CRAFTY_USER, "password": CRAFTY_PASS}
    async with session.post(url, json=payload, ssl=sslcontext) as resp:
        resp.raise_for_status()
        data = await resp.json()
        return data["data"]["token"]

async def fetch_server_stats(session, token):
    url = f"{CRAFTY_URL}/api/v2/servers/{SERVER_ID}/stats"
    headers = {"Authorization": f"Bearer {token}"}
    async with session.get(url, headers=headers, ssl=sslcontext) as resp:
        resp.raise_for_status()
        return await resp.json()


async def get_server_stats_embed(public_ip):
    async with aiohttp.ClientSession() as session:
        try:
            token = await fetch_crafty_token(session)
            stats = await fetch_server_stats(session, token)
        except Exception as e:
            embed = discord.Embed(
                title="Fehler bei Crafty API",
                description=f"Kann Daten nicht abrufen: {e}",
                color=discord.Color.red(),
                timestamp=datetime.utcnow()
            )
            return embed

    data = stats.get("data", {})
    running = data.get("running", {})
    waiting_start = data.get("waiting_start", {})
    online = data.get("online", "unbekannt")
    players_str = data.get("players", "[]")
    try:
        players = ast.literal_eval(players_str)
    except Exception as e:
        print(f"Fehler beim Parsen der Spieler-Liste: {e}")
        players = []
    player_names = ""
    server_name = data.get("server_name")
    cpu = data.get("cpu", "unbekannt")
    mem_percent = data.get("mem_percent", "unbekannt")

    MAX_POINTS = 20

    cpu_history.append(cpu)
    if len(cpu_history) > MAX_POINTS:
        cpu_history.pop(0)  # Ältesten Wert entfernen

    ram_history.append(mem_percent)
    if len(ram_history) > MAX_POINTS:
        ram_history.pop(0)

    # UTC+2 Zeitzone definieren
    tz_utc_plus_2 = timezone(timedelta(hours=2))

    # aktuelle Zeit in UTC+2, aber in UTC konvertieren
    local_time = datetime.now(tz_utc_plus_2)

    embed = discord.Embed(
        title=f"🖥️ Server Info",
        color=discord.Color.blue(),
        timestamp=local_time
    )
    embed.add_field(name="⚡ Status", value="offline" if not running else "starting" if waiting_start else "online")
    embed.add_field(name="🌐 IP Address", value=public_ip)
    if players:
        player_names = "\n".join(f"- {player}" for player in players)
    embed.add_field(name="👥 Player online", value=str(online), inline=True)
    if players:
        embed.add_field(name="Player List", value=player_names, inline=True)
    embed.set_footer(text="Data from Crafty API")

    return embed


def plot_stats(cpu_history, ram_history):
    fig, ax = plt.subplots(figsize=(6, 3))

    # Grauen Hintergrund setzen (helleres Grau z.B. 0.2 bis 0.5)
    fig.patch.set_facecolor('#242429')   # Figuren-Hintergrund
    ax.set_facecolor('#242429')          # Plot-Hintergrund (Achsenfläche)

    ax.plot(cpu_history, label="CPU %", color='cyan')
    ax.plot(ram_history, label="RAM %", color='magenta')

    ax.set_xlabel("Intervals", color='white')
    ax.set_ylabel("Usage %", color='white')
    ax.set_title("Server CPU- and RAM Usage", color='white')

    ax.legend(facecolor='#4a4a4a', edgecolor='white', labelcolor='white')

    ax.tick_params(axis='x', colors='white')
    ax.tick_params(axis='y', colors='white')

    plt.tight_layout()

    buf = io.BytesIO()
    plt.savefig(buf, format="png", facecolor=fig.get_facecolor())
    plt.close()
    buf.seek(0)
    return buf



@tasks.loop(seconds=server_status_update_interval)
async def update_stats_loop():
    global message_link
    channel = bot.get_channel(server_info_channel_id)
    if not channel:
        print("Channel not found")
        return

    public_ip = await fetch_public_ip()

    embed = await get_server_stats_embed(public_ip)
    image_buf = plot_stats(cpu_history, ram_history)
    file = discord.File(fp=image_buf, filename="stats.png")

    # Bild im Embed setzen
    embed.set_image(url="attachment://stats.png")

    if message_link:
        try:
            msg = await channel.fetch_message(int(message_link))
            await msg.edit(embed=embed, attachments=[file])
            return
        except discord.NotFound:
            print("Message not found, creating new one")
            message_link = None

    msg = await channel.send(embed=embed, file=file)
    message_link = str(msg.id)
    print(f"New message sent: {message_link}")

@bot.command(name="interval", help="Edits the interval for the updates of the server statistics")
@commands.has_role(mod_role_id)
async def interval(ctx, new_interval: int):
    global server_status_update_interval
    if new_interval < 10:
        await ctx.send("Number has to be >= 10.", delete_after=5)
        return

    server_status_update_interval = new_interval

    if update_stats_loop.is_running():
        update_stats_loop.cancel()  # Loop stoppen
        while update_stats_loop.is_running():  # Warten, bis Task wirklich gestoppt ist
            await asyncio.sleep(0.1)

    update_stats_loop.change_interval(seconds=server_status_update_interval)  # Intervall ändern
    update_stats_loop.start()  # Loop neu starten

    await ctx.send(f"{ctx.author.mention} put the update intervall on {new_interval} seconds.")

async def send_server_action(session, token, server_id, action):
    url = f"{CRAFTY_URL}/api/v2/servers/{server_id}/action/{action}"
    headers = {"Authorization": f"Bearer {token}"}
    async with session.post(url, headers=headers, ssl=sslcontext) as resp:
        resp.raise_for_status()
        return await resp.json()  # erwartet { "status":"ok", ... }

async def handle_server_action(ctx, action_name, success_msg):
    async with aiohttp.ClientSession() as session:
        try:
            token = await fetch_crafty_token(session)
            result = await send_server_action(session, token, SERVER_ID, action_name)
        except Exception as e:
            return await ctx.send(f"❌ Error trying to change the server status: `{action_name}`: `{e}`")

    if result.get("status") == "ok":
        await ctx.send(success_msg)
    else:
        await ctx.send(f"⚠️ Unexpected result: {result}")

async def fetch_public_ip():
    async with aiohttp.ClientSession() as session:
        try:
            async with session.get("https://api.ipify.org?format=json") as resp:
                resp.raise_for_status()
                data = await resp.json()
                return data["ip"]
        except Exception as e:
            print(f"Fehler beim Abrufen der IP: {e}")
            return "unbekannt"


# --- Discord Commands ---
@bot.command(name="start", help="Starts the Crafty Server")
@commands.has_role(mod_role_id)
async def start_server(ctx):
    await handle_server_action(ctx, "start_server", "✅ Server is being started!")

@bot.command(name="stop", help="Stops the CraftyServer")
@commands.has_role(mod_role_id)
async def stop_server(ctx):
    await handle_server_action(ctx, "stop_server", "🛑 Server is being stopped!")


# --- Ko-fi Webhook Handler ---
async def handle_kofi(request):
    try:
        post_data = await request.post()  # form-data
        raw_json = post_data.get("data")  # Ko-fi packt alles in "data"
        if not raw_json:
            raise ValueError("Kein 'data'-Feld gefunden")

        # URL-dekodieren
        decoded = urllib.parse.unquote_plus(raw_json)

        # JSON parsen
        data = json.loads(decoded)

    except Exception as e:
        body = await request.text()
        return web.Response(text="Invalid data", status=400)

    print("📦 Ko-fi Webhook received:", data)

    username = data.get("from_name", "Anonymous")
    amount = data.get("amount", "0")
    message = data.get("message", "")
    tier_name = data.get("tier_name", "")
    user_id = data.get("discord_userid", "")

    description = f"**{username}** has donated {amount}$"

    if message:
        description += f"\n\n> {message}"

    guild = bot.get_guild(guild_id)
    member = guild.get_member(int(user_id))
    if member:
        channel = bot.get_channel(donation_channel_id)
        donator_role = guild.get_role(donator_role_id)
        await member.add_roles(donator_role)
        embed = await kofi_message(channel, description, tier_name)
        await responses.add_celebration_reactions(embed, 3)

    else:
        channel = bot.get_channel(test_channel_id)
        embed = await kofi_message(channel, description, tier_name)
        await responses.add_celebration_reactions(embed, 3)


    return web.Response(text="OK", status=200)

async def kofi_message(channel, description, tier_name):
    if channel:
        embed = discord.Embed(
            title="☕ New Ko-fi Donation!",
            description=description,
            color=discord.Color.gold()
        )
        if tier_name:
            embed.add_field(name="Membership", value=tier_name)
        return await channel.send(embed=embed)


# --- Server Setup ---
async def start_webhook_server():
    app = web.Application()
    app.router.add_post('/kofi-webhook', handle_kofi)
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, '0.0.0.0', 8080)  # Port 8080, kann angepasst werden
    await site.start()
    print("🚀 Ko-fi Webhook Server läuft auf Port 8080")


async def cleanup():

    print("Saving User Data")
    print("Shutting Down")
    await bot.close()


def handle_signal():
    loop = asyncio.get_event_loop()
    loop.create_task(cleanup())


# Signale registrieren
signal.signal(signal.SIGINT, lambda *_: handle_signal())
signal.signal(signal.SIGTERM, lambda *_: handle_signal())


@bot.event
async def on_disconnect():
    print("disconnected")


my_secret = os.environ["DISCORD_TOKEN"]
bot.run(my_secret)