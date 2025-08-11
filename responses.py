import random

def get_response(user_input: str) -> str:
    raise NotImplementedError('Code is missing...')

async def sendMessage(bot, message, channel):
    channel = await bot.fetch_channel(channel)
    return await channel.send(message)

async def add_celebration_reactions(message, total_reactions):
    celebration_emojis = ["🔥", "🥳", "👏", "🎊", "🎉", "💯"]
    while total_reactions > 0:
        random_zahl = random.randint(0, len(celebration_emojis) - 1)
        await message.add_reaction(celebration_emojis[random_zahl])
        celebration_emojis.remove(celebration_emojis[random_zahl])
        total_reactions -= 1

async def add_sad_reactions(message, total_reactions):
    celebration_emojis = ["🥺", "😭", "😥", "☹️", "😫", "😪", "😞", "😒"]
    while total_reactions > 0:
        random_zahl = random.randint(0, len(celebration_emojis) - 1)
        await message.add_reaction(celebration_emojis[random_zahl])
        celebration_emojis.remove(celebration_emojis[random_zahl])
        total_reactions -= 1

async def bot_chat_error_message(message, the_warning):
    await message.delete()
    warning = await message.channel.send(f"{message.author.mention}, {the_warning}")

    await warning.delete(delay=5)
