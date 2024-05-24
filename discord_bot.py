#!/usr/bin/python3

import discord
import asyncio
from tools import ping, get_recent_wan_events, get_monitors, get_wan_ip, handle_files
from discord.ext import commands, tasks

intents = discord.Intents.default()
intents.typing = True
intents.message_content = True

EMERGENCY_CHANNEL = ''
WAN_CHANNEL = ''
PING_CHANNEL = ''
TOKEN = ''
# define test endpoints
isp_gateway = ''
home_gateway = ''
isp_endpoint = ''
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
    wan_ip = get_wan_ip()

    # wait for bot to become ready before moving forward (connected)
    await client.wait_until_ready()
    channel = client.get_channel(PING_CHANNEL)
    emergency_channel = client.get_channel(EMERGENCY_CHANNEL)
    await channel.send(f'----------------------------------------------------')
    await channel.send(
        f'Hello, I will be testing ISP Gateway: {isp_gateway}, ISP Endpoint: {isp_endpoint}, and Home Gateway: {home_gateway} -- From WAN IP {wan_ip}')
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

    await channel.send(f'----------------------------------------------------')

    return


# Wait 24 hours before each wan event check
@tasks.loop(seconds=86400)
async def wan_events():
    recent_events = get_recent_wan_events()
    await client.wait_until_ready()
    emergency_channel = client.get_channel(EMERGENCY_CHANNEL)

    for event in recent_events:
        await emergency_channel.send(f'WAN EVENT - \n{event["msg"]} - {event["datetime"]}\n')
    return


#7.5 minutes
@tasks.loop(seconds=450)
async def wan_monitors():
    wan_stats = get_monitors()
    await client.wait_until_ready()
    channel = client.get_channel(WAN_CHANNEL)
    emergency_channel = client.get_channel(EMERGENCY_CHANNEL)
    await channel.send(f"--------------------------- INSPECTING WAN MONITORS ---------------------------")
    for wan, monitors in wan_stats.items():
        if monitors['unhealthy_monitors']:
            alarm_files = handle_files(wan_stats)
            if not alarm_files:
                await emergency_channel.send(f"--------------------------- UNHEALTHY {wan} MONITORS BELOW ---------------------------")
                for monitor, metrics in monitors['unhealthy_monitors'].items():
                    await emergency_channel.send(f"---- {monitor} --- {metrics} ----")
            else:
                await channel.send(f"---- {wan} ---- has already alarmed in the last hour ----")
            
        if monitors['healthy_monitors']:
            await channel.send(f"--------------------------- HEALTHY {wan} MONITORS BELOW ---------------------------")
            for monitor, metrics in monitors['healthy_monitors'].items():
                await channel.send(f"---- {monitor} --- {metrics} ----")

        if not monitors:
            await emergency_channel.send(f"---- WAN MONITOR HAS FAILED TO INSPECT - {wan} - {monitors} ----")

    await channel.send(f"--------------------------- COMPLETED WAN MONITOR INSPECTION ---------------------------")

    return


async def main():
    async with client:
        client.loop.create_task(ping_tests())
        client.loop.create_task(wan_events())
        client.loop.create_task(wan_monitors())
        wan_events.start()
        ping_tests.start()
        wan_monitors.start()
        await client.start(TOKEN)


asyncio.run(main())
