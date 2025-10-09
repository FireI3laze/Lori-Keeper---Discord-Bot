import discord


async def open_embedded_statistics_field(ctx, total_messages, total_vc_joined,
                                                                     formatted_time, total_bot_commands,
                                                                     the_total_coins):
    statistics_embed = discord.Embed(
        title=f"📈 Statistiken von {ctx.author.display_name}",
        description=f"{ctx.author.mention}",
        color=discord.Color.red()
    )

    # Füge die Felder hinzu
    statistics_embed.add_field(
        name=f"Übersicht 📋",
        value=(
            f"- **Nachrichten gesendet:** {total_messages} \n"
            f"- **Voice-Channels beigetreten:** {total_vc_joined}\n"
            f"- **Zeit in Voice-Channels verbracht:** {formatted_time}\n"
            f"- **Bot Commands erstellt:** {total_bot_commands}\n"
            f"- **Coins:** {the_total_coins} 🪙\n"
        ),
        inline=False
    )

    statistics_embed.set_footer(text="Statistiken")

    await ctx.send(embed=statistics_embed)

async def open_embedded_weekly_field(ctx, weekly_first_message, the_user,
                                                                     weekly_resets, weekly_more_messages,
                                                                     weekly_first_vc_join, formatted_required_time, formatted_time, weekly_first_bot_command, weekly_more_bot_commands):
    weeklies_embed = discord.Embed(
        title=f"📋 Wöchentliche Aufgaben von {ctx.author.display_name}",
        description=f"{ctx.author.mention}",
        color=discord.Color.red()
    )

    # Füge die Felder hinzu
    weeklies_embed.add_field(
        name=f"Übersicht 📋",
        value=(
            f"- {weekly_first_message if weekly_resets[the_user][0] == 0 else weekly_first_message - weekly_resets[the_user][0]}/{weekly_first_message} Nachricht gesendet {'✔' if weekly_resets[the_user][0] == 0 else '✘'}\n"
            f"- {weekly_more_messages if weekly_resets[the_user][1] == 0 else weekly_more_messages - weekly_resets[the_user][1]}/{weekly_more_messages} Nachrichten gesendet {'✔' if weekly_resets[the_user][1] == 0 else '✘'}\n"
            f"- {weekly_first_bot_command if weekly_resets[the_user][5] == 0 else weekly_first_bot_command - weekly_resets[the_user][5]}/{weekly_first_bot_command} Bot Befehle gesendet {'✔' if weekly_resets[the_user][5] == 0 else '✘'}\n"
            f"- {weekly_more_bot_commands if weekly_resets[the_user][6] == 0 else weekly_more_bot_commands - weekly_resets[the_user][6]}/{weekly_more_bot_commands} Bot Befehle gesendet {'✔' if weekly_resets[the_user][6] == 0 else '✘'}\n"
            f"- {weekly_first_vc_join if weekly_resets[the_user][2] == 0 else weekly_first_vc_join - weekly_resets[the_user][2]}/{weekly_first_vc_join} Voice-Channels beigetreten {'✔' if weekly_resets[the_user][2] == 0 else '✘'}\n"
            f"- {formatted_required_time if weekly_resets[the_user][3] == 0 else formatted_time}/{formatted_required_time} Zeit in Voice-Channels verbracht {int(weekly_resets[the_user][4])}× ↻"
        ),
        inline=False
    )

    weeklies_embed.set_footer(text="Wöchentliche Aufgaben")

    await ctx.send(embed=weeklies_embed)

