import discord


def application_message_embed(discord, guild, user, support_role_id):
    embed = discord.Embed(
        title="Welcome to the Application!",
        description=(
            f"Hello {user.mention}! We are happy you are going to apply for the server. To speed up the process, "
            f"feel free to already tell us about you whatever you like so we can do a small vibe check. "
            f"A {guild.get_role(support_role_id).mention} will come shortly and review your responses."
        ),
        color=discord.Color.blue()
    )

    embed.add_field(
        name="Ice Breaker Questions (optional)",
        value=(
            "- **How was your day? Tell us something about it!**\n"
            "- **Have you played on a modded Minecraft server before?** If so, share your experience with us!\n"
            "- **What’s your playstyle?** (builder, explorer, redstone engineer, adventurer, etc.)\n"
            "- **Are you here to create content (YouTube, Twitch, TikTok, etc.) or just to play for fun?**\n"
            "- **This is a rude one and we all know it... would you pull the lever? (Picture)**"
        ),
        inline=False
    )

    # Bild wird unten im Embed angezeigt
    embed.set_image(url="attachment://application_question.webp")

    return embed

def server_stats_embed():
    embed = discord.Embed(
        title="Server Stats",
        description="Aktualisierte Daten hier",
        color=discord.Color.blue()
    )
    embed.add_field(name="Playtime", value="123h", inline=True)
    embed.add_field(name="Players Online", value="5", inline=True)
    return embed

