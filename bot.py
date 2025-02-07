try:
    import app
except: app = None
import discord
import os

token = os.getenv("token")
intents = discord.Intents.default()
intents.members = True
intents.message_content = True
client: discord.Client = discord.Client(intents=intents)

async def cmd_halls(message, app=app):
    return ("Registered halls: " + ", ".join(app.halls.keys()))

async def cmd_hall(message, app=app):
    try:
        hall = message.content.split(" ")[1].lower()
    except IndexError:
        return "Error: Please specify a hall."
    outstr = f"Washers in {hall.title()}: {' '.join(sorted([str(m['stickerNumber']) for m in app.machines(hall)['machines'] if m['type'] == 'washer']))}"
    outstr+= f"\nDryers in {hall.title()}: {' '.join(sorted([str(m['stickerNumber']) for m in app.machines(hall)['machines'] if m['type'] == 'dryer']))}"
    return outstr

async def cmd_time(message, app=app):
    hall = message.content.split(" ")[1].lower()
    return ("\n".join([f"{app.get_mach(int(m), hall)['timeRemaining']} mins on {hall.title()} {m}" for m in message.content.split(' ')[2:]]))

async def cmd_api(message, app=app):
    hall = message.content.split(" ")[1].lower()
    if (hall == "*" or hall == "all"):
        return ("\n".join([f"Raw data from {h.title()}:```json\n{app.machines(h)}\n```" for h in app.halls.keys()]))
    return ("\n".join([f"Raw data from {hall.title()} {m}:```json\n{app.mach_api(hall)}\n```" for m in message.content.split(' ')[2:]]))

async def cmd_laundry(message, app=app):
    return "Laundry commands:" + '\n'.join(['/' + c for c in cmds.keys()]) + "\nUsage: `/command hall id`\nYou can chain ids like this: `/api barton 220 221 222`"

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

if __name__ == "__main__":
    client.run(token)