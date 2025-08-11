import math


async def weekly_message_coins(the_user, weekly_resets, coins, kind_of_message):
    if kind_of_message == "message":
        position = 0
    elif kind_of_message == "bot_command":
        position = 5
    else:
        return coins
    if the_user not in coins:
            coins[the_user] = 0
    if weekly_resets[the_user][position] > 0:
        weekly_resets[the_user][position] -= 1
        await add_coins(the_user, coins, 100)

    if weekly_resets[the_user][position + 1] > 0:
        weekly_resets[the_user][position + 1] -= 1
        if weekly_resets[the_user][position + 1] == 0:
            await add_coins(the_user, coins, 200)

    return coins

async def weekly_voice_coins(the_user, time_spent_seconds, weekly_resets, coins):
    if the_user not in coins:
            coins[the_user] = 0
    if weekly_resets[the_user][2] == 1:
        weekly_resets[the_user][2] -= 1
        await add_coins(the_user, coins, 100)

    time_spent_hours = math.floor(time_spent_seconds / 3600)
    if weekly_resets[the_user][3] - time_spent_seconds % 3600 <= 0:
        time_spent_hours += 1
        weekly_resets[the_user][3] = 3600 + weekly_resets[the_user][3] - time_spent_seconds % 3600
    else:
        weekly_resets[the_user][3] -= time_spent_seconds % 3600

    if weekly_resets[the_user][4] == 0 and time_spent_hours > 0:
        await add_coins(the_user, coins, 150)

    weekly_resets[the_user][4] += time_spent_hours
    await add_coins(the_user, coins, time_spent_hours * 50)

    '''
    if weekly_resets[the_user][3] > 0:
        weekly_resets[the_user][3] -= time_spent_seconds
        if weekly_resets[the_user][3] <= 0:
            weekly_resets[the_user][3] = 0
            await add_coins(the_user, coins, 200)
    '''
    return coins

async def message_coins(the_user, total_coins):
    await add_coins(the_user, total_coins, 5)

async def voice_coins(the_user, time_spent_seconds, total_coins):
    if the_user not in total_coins:
        total_coins[the_user] = 0
    time_spent_minutes = math.ceil(time_spent_seconds / 60)
    await add_coins(the_user, total_coins, time_spent_minutes * 1)


async def add_coins(the_user, coins, amount):
    if the_user not in coins:
        coins[the_user] = 0
    else:
        coins[the_user] += round(amount, 1)