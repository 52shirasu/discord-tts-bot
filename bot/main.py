# --- 追加・修正インポート ---
from discord.ext import commands
import discord
import os
from dotenv import load_dotenv
import asyncio
from gtts import gTTS
import tempfile

load_dotenv()
TOKEN = os.getenv("DISCORD_TOKEN")
default_channel_id = int(os.getenv("DEFAULT_READ_CHANNEL_ID"))
read_target_channel_id = default_channel_id  # 初期読み上げチャンネル

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix=".", intents=intents)

# 音声を再生する関数
async def speak_text(text, vc):
    with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as fp:
        tts = gTTS(text=text, lang='ja')
        tts.save(fp.name)
        source = discord.FFmpegPCMAudio(fp.name)
        vc.play(source, after=lambda e: os.remove(fp.name))
        while vc.is_playing():
            await asyncio.sleep(1)

# 案内メッセージ送信用の関数
async def send_to_read_channel(guild, message):
    target_channel = guild.get_channel(read_target_channel_id)
    if target_channel:
        await target_channel.send(message)
    else:
        # チャンネルが見つからない場合は何もしないか、エラー処理
        pass

@bot.event
async def on_ready():
    print(f"✅ Bot起動完了：{bot.user}")

@bot.command()
async def join(ctx):
    global read_target_channel_id
    if ctx.author.voice:
        channel = ctx.author.voice.channel
        await channel.connect()
        await send_to_read_channel(ctx.guild, "✅ VCに接続しました！")

        help_text = """
🔊 **コマンド一覧**
`.join` - VCにBotを参加させ、このチャンネルのメッセージを読み上げ対象にします  
`.setchannel [チャンネルID]` - 読み上げ対象チャンネルを変更します  
`.bye` - VCからBotを退出させます  
💬 このチャンネルに書き込むと読み上げます
"""
        await send_to_read_channel(ctx.guild, help_text)
    else:
        await ctx.send("⚠️ まずは自分がボイスチャンネルに入ってください！")

@bot.command()
async def bye(ctx):
    if ctx.voice_client:
        await ctx.voice_client.disconnect()
        await send_to_read_channel(ctx.guild, "🔌 切断しました")
    else:
        await send_to_read_channel(ctx.guild, "⚠️ 接続されていません")

@bot.command()
async def setchannel(ctx, channel_id: int):
    global read_target_channel_id
    read_target_channel_id = channel_id
    await send_to_read_channel(ctx.guild, f"✅ 読み上げチャンネルを <#{channel_id}> に変更しました")


@bot.event
async def on_message(message):
    global read_target_channel_id

    if message.author.bot:
        return
    
    await bot.process_commands(message)

    # 指定されたチャンネル以外は無視
    if message.channel.id != read_target_channel_id:
        return

    if message.guild and message.guild.voice_client:
        vc = message.guild.voice_client
        await speak_text(message.content, vc)



@bot.event
async def on_voice_state_update(member, before, after):
    # BOT自身は無視
    if member.bot:
        return

    # ユーザーがVCから退出したとき
    if before.channel is not None and (after.channel is None or before.channel != after.channel):
        voice_client = member.guild.voice_client
        if voice_client and voice_client.channel == before.channel:
            # 残っているのがBOTだけなら退出
            non_bot_members = [m for m in before.channel.members if not m.bot]
            if len(non_bot_members) == 0:
                await voice_client.disconnect()
                await send_to_read_channel(member.guild, "👋 誰もいなくなったのでVCから退出しました")



def start_bot():
    bot.run(TOKEN)

if __name__ == "__main__":
    start_bot()
