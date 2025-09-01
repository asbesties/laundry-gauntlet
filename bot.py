import discord
import os
import data
import ifaces

token = os.getenv("token")
intents = discord.Intents.default()
intents.members = True
intents.message_content = True
client: discord.Client = discord.Client(intents=intents)

def report_hall(hall):
    outstr = f"Washers in {hall.title()}: {' '.join(sorted([str(m['stickerNumber']) for m in ifaces.machines(hall)['machines'] if m['type'] == 'washer']))}"
    outstr+= f"\nDryers in {hall.title()}: {' '.join(sorted([str(m['stickerNumber']) for m in ifaces.machines(hall)['machines'] if m['type'] == 'dryer']))}"
    return outstr

async def cmd_halls(message):
    return ("Registered halls: " + ", ".join(data.halls.keys()))

async def cmd_hall(message):
    try:
        hall = message.content.split(" ")[1].lower()
    except IndexError:
        return "Error: Please specify a hall."
    outstr = ""
    if hall == '*':
        for h in data.halls.keys():
            outstr += report_hall(h) + "\n\n"
    elif hall != '':
        outstr += report_hall(hall)
    return outstr

async def cmd_time(message):
    args = message.content.split(" ")
    if len(args) > 3:
        hall = args[1].lower()
        return ("\n".join([f"{ifaces.get_mach(int(m), hall)['timeRemaining']} mins on {hall.title()} {m}" for m in args[2:]]))
    else:
        return "Improper command format."

async def cmd_api(message):
    hall = message.content.split(" ")[1].lower()
    output = []
    if (hall == "*" or hall == "all"):
        for h in data.halls.keys():
            for m in ifaces.machines(h)['machines']:
                hall_data = ifaces.mach_api(h)
                output.append(f"Raw data from {h.title()} {m}:```\n{hall_data}\n```")
        return output
    elif (hall in data.halls.keys()):
        if (len(message.content.split(' ')) == 2):
            for m in message.content.split(' ')[2:]:
                hall_data = ifaces.mach_api(hall)
                output.append(f"Raw data from {hall.title()} {m}:```\n{hall_data}\n```")
        else:
            for m in ifaces.machines(hall)['machines']:
                hall_data = ifaces.mach_api(hall)
                output.append(f"Raw data from {hall.title()} {m}:```\n{hall_data}\n```")
        return output
    else:
        return "Error: Invalid hall"

async def cmd_laundry(message):
    return "Laundry commands:\n" + '\n'.join(['a!' + c for c in cmds.keys()]) + "\nUsage: `a!command hall id`\nYou can chain ids like this: `a!api barton 220 221 222`"

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
    if message.author != client.user:
        async with message.channel.typing():
            cmdout = ""
            if message.content.startswith("a!"):
                cmd = message.content.strip("a!").split(" ")[0]
                if cmd in cmds:
                    print(f"[CMD] @{message.author} used {message.content}")
                    cmdout = await cmds[cmd](message)
                    print("[API] >> " + cmdout.replace('\n', '\n[API] >> '))
            await message.channel.send(cmdout)

if __name__ == "__main__":
    client.run(token)