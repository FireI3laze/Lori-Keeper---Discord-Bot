import discord


async def create_a_lobby(guild, channel, member, category_name, all_created_vc):
    category = discord.utils.get(guild.categories, name=category_name)
    if category:
        new_channel = await guild.create_voice_channel(
            "Temporary VC",
            category=category,
            position=channel.position,
            user_limit=channel.user_limit
        )
        #print("VC ", new_channel.name, "created")

        all_created_vc[new_channel.id] = new_channel

        await member.move_to(new_channel)
        #print(member.name, " got moved to ", new_channel.name)
    #else:
        #print("VC couldn't be created, ", category_name, " does not exist")

async def delete_a_lobby(channel, all_created_vc):
    user_count = len(channel.members)
    if user_count == 0:
        await channel.delete()
    else:
        if channel not in all_created_vc:
            all_created_vc[channel.id] = channel