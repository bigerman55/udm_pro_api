#!/usr/bin/python3

import discord
import asyncio
from tools import ping, get_recent_wan_events
from discord.ext import commands, tasks

intents = discord.Intents.default()
intents.typing = True
intents.message_content = True

EMERGENCY_CHANNEL = '<REDACTED>'
CHANNEL = '<REDACTED>'
TOKEN = '<REDACTED>'
# define test endpoints
isp_gateway = '<REDACTED>'
home_gateway = '<REDACTED>'
isp_endpoint = '<REDACTED>'
google = 'google.com'

# declare bot commands prefix
client = discord.Client(command_prefix='!', intents=intents)


# loop ping tests every 2 minutes towards isp, home endpoint, and isp next-hop
@tasks.loop(seconds=180)
async def ping_tests():
    # define variables for pinging endpoints and store result in said variable.
    isp_test = ping(isp_gateway)
    home_test = ping(home_gateway)
    isp_endpoint_test = ping(isp_endpoint)

    # wait for bot to become ready before moving forward (connected)
    await client.wait_until_ready()
    channel = client.get_channel(CHANNEL)
    emergency_channel = client.get_channel(EMERGENCY_CHANNEL)
    await channel.send(f'----------------------------------------------------')
    await channel.send(
        f'Hello, I will be testing ISP Gateway: {isp_gateway}, ISP Endpoint: {isp_endpoint}, and Home Gateway: {home_gateway}')
    await channel.send(f'----------------------------------------------------')

    # if all 3 tests come back as true, it will send message of it being up. Reverse if down.
    if home_test:
        await channel.send(f'Home Gateway {home_gateway}: UP')
    else:
        await emergency_channel.send(f'Home Gateway {home_gateway}: DOWN')

    if isp_test:
        await channel.send(f'ISP Gateway {isp_gateway}: UP')
    else:
        await emergency_channel.send(f'ISP Gateway {isp_gateway}: DOWN')

    if isp_endpoint_test:
        await channel.send(f'ISP Endpoint {isp_endpoint}: UP')
    else:
        await emergency_channel.send(f'ISP Gateway {isp_gateway}: DOWN')

    return


@tasks.loop(seconds=86400)
async def wan_events():
    recent_events = get_recent_wan_events()
    await client.wait_until_ready()
    emergency_channel = client.get_channel(EMERGENCY_CHANNEL)

    for event in recent_events:
        await emergency_channel.send(f'WAN EVENT - \n{event["msg"]} - {event["datetime"]}\n')
    return


async def main():
    async with client:
        client.loop.create_task(ping_tests())
        client.loop.create_task(wan_events())
        wan_events.start()
        ping_tests.start()
        await client.start(TOKEN)


asyncio.run(main())
