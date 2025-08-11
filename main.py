import asyncio
import logging
import sys
from distutils.command.config import config
from typing import Final
import os



from datetime import datetime, timedelta
import threading
import signal
import asyncio

import discord
from discord.ext import commands
from discord.ui import View, Button
from dotenv import load_dotenv
from unicodedata import category


import embeds
import responses
from responses import sendMessage

# Wähle die Umgebung über Umgebungsvariable oder fallback auf prod
#env = os.getenv("DISCORD_ENV", "test")  # test / prod
#cfg = getattr(config, env)

# Load Token
load_dotenv()
token = os.getenv('DISCORD_TOKEN')

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

# IDs
bot_id = 1403766234931265606

#guild_id = 1403166544535752734

player_role_id = 1403198812398293156
support_role_id = 1403199038253436988
mod_role_id = 1403198483795542106

applications_category_id = 1403197590375235614
application_channel_id = 1403182061413601310
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
    file = discord.File("pictures/application_question.webp", filename="application_question.webp")
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
    print("Bot is ready")

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
@commands.has_role(mod_role_id)
async def promotion_to_player(ctx, member: discord.Member):
    role = ctx.guild.get_role(player_role_id)
    await member.add_roles(role, reason=f"Role given by {ctx.author}")
    message = await ctx.send(f"Congratulations {member.mention}, your application got accepted! You are an official "
                             f"{role.mention} of the server now!!\nCheck out the https://discord.com/channels/1403166544535752734/1403183602371530872"
                             f" to get the Server IP & Modpack and finally dive in our world 🎮")
    await responses.add_celebration_reactions(message, 2)

@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.MissingRole):
        await ctx.reply("Leave that to the mods please ;)")
    else:
        raise error


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