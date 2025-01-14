import app
import discord
import os

token = os.getenv("token")
intents = discord.Intents.default()
intents.members = True
intents.message_content = True
client: discord.Client = discord.Client(intents=intents)

async def cmd_halls(message):
    return ("Registered halls: " + ", ".join(app.halls.keys()))

async def cmd_hall(message):
    hall = message.content.split(" ")[1].lower()
    return (f"Machines in {hall.title()}: {', '.join([str(m['stickerNumber']) for m in app.machines(hall)['machines']])}")

async def cmd_time(message):
    hall = message.content.split(" ")[1].lower()
    return ("\n".join([f"{app.get_mach(int(m), hall)['timeRemaining']} mins on {hall.title()} {m}" for m in message.content.split(' ')[2:]]))

async def cmd_api(message):
    hall = message.content.split(" ")[1].lower()
    return ("\n".join([f"Raw data from {hall.title()} {m}:```json\n{app.get_mach(int(m), hall)}\n```" for m in message.content.split(' ')[2:]]))

async def cmd_laundry(message):
    return "Laundry commands: + '\n'.join(['/' + c for c in cmds.keys()])" + "\nUsage: `/command hall id`\nYou can chain ids like this: `/api barton 220 221 222`"

cmds = {
    "halls": cmd_halls,
    "hall": cmd_hall,
    "time": cmd_time,
    "api": cmd_api,
    "laundry": cmd_laundry,
}

@client.event
async def on_ready():
    print(f"[SYS] Logged in as {client.user.name}")

@client.event
async def on_message(message: discord.Message):
    if message.content.startswith("/"):
        cmd = message.content.strip("/").split(" ")[0]
        if cmd in cmds:
            print(f"[CMD] @{message.author} used {message.content}")
            cmdout = await cmds[cmd](message)
            print("[API] >> " + cmdout.replace('\n', '\n[API] >> '))
            await message.channel.send(cmdout)

client.run(token)