# bot/main.py

import discord
from discord.ext import commands
import asyncio
import os
from dotenv import load_dotenv

# 読み上げ音声ファイル生成に使う（gTTS）
from gtts import gTTS
import tempfile

load_dotenv()
TOKEN = os.getenv("DISCORD_TOKEN")


# botの初期化
intents = discord.Intents.default()
intents.message_content = True  # メッセージ読み取りに必要
bot = commands.Bot(command_prefix="!", intents=intents)

# 音声を再生する関数
async def speak_text(text, vc):
    with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as fp:
        tts = gTTS(text=text, lang='ja')
        tts.save(fp.name)
        source = discord.FFmpegPCMAudio(fp.name)
        vc.play(source, after=lambda e: os.remove(fp.name))
        while vc.is_playing():
            await asyncio.sleep(1)

@bot.event
async def on_ready():
    print(f"Bot起動完了：{bot.user}")

@bot.command()
async def join(ctx):
    if ctx.author.voice:
        channel = ctx.author.voice.channel
        await channel.connect()
        await ctx.send("VCに接続しました")
    else:
        await ctx.send("ボイスチャンネルに入ってから呼んでください")

@bot.command()
async def bye(ctx):
    if ctx.voice_client:
        await ctx.voice_client.disconnect()
        await ctx.send("切断しました")
    else:
        await ctx.send("接続されていません")

@bot.event
async def on_message(message):
    if message.author.bot:
        return

    if message.guild and message.guild.voice_client:
        vc = message.guild.voice_client
        await speak_text(message.content, vc)

    await bot.process_commands(message)

bot.run(TOKEN)
