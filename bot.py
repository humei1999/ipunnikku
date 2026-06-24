import discord
from discord.ext import tasks
import json
import os

TOKEN = os.getenv("DISCORD_TOKEN")
CHANNEL_ID = int(os.getenv("CHANNEL_ID", "0"))

print("TOKENあり:", TOKEN is not None)
print("CHANNEL_ID:", CHANNEL_ID)

intents = discord.Intents.default()
client = discord.Client(intents=intents)

DATA_FILE = "haiku_data.json"


def load_haikus():
    haikus = []

    with open("haiku.txt", "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()

            if not line:
                continue

            if "|" not in line:
                continue

            haiku, author = line.split("|", 1)

            haikus.append({
                "haiku": haiku,
                "author": author
            })

    return haikus


def load_index():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            return json.load(f).get("index", 0)
    return 0


def save_index(index):
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump({"index": index}, f)


async def send_haiku():
    try:
        haikus = load_haikus()

        if len(haikus) == 0:
            print("haiku.txt が空です")
            return

        index = load_index()

        if index >= len(haikus):
            index = 0

        haiku = haikus[index]["haiku"]
        author = haikus[index]["author"]

        channel = client.get_channel(CHANNEL_ID)

        if channel is None:
            print("チャンネルを取得できませんでした")
            return

        await channel.send(
            f"📜 今日の一句\n\n"
            f"━━━━━━━━━━\n\n"
            f"**{haiku}**\n\n"
            f"✍ 作者: {author}\n\n"
            f"━━━━━━━━━━"
        )

        index += 1
        if index >= len(haikus):
            index = 0

        save_index(index)
        print("俳句を投稿しました")

    except Exception as e:
        print("投稿エラー:", e)


@client.event
async def on_ready():
    print(f"{client.user} が起動しました")

    try:
        await send_haiku()
    except Exception as e:
        print("起動時投稿エラー:", e)

    if not minute_haiku.is_running():
        minute_haiku.start()


@tasks.loop(minutes=1)
async def minute_haiku():
    await send_haiku()


client.run(TOKEN)
