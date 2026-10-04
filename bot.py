import os
import telebot
import yt_dlp
from flask import Flask

TOKEN = os.getenv("BOT_TOKEN")  # Mengambil token dari Environment Variables Railway
bot = telebot.TeleBot(TOKEN)
app = Flask(__name__)


@app.route("/")
def home():
  return "Bot is running!"


@bot.message_handler(commands=["start", "help"])
def send_welcome(message):
  bot.reply_to(
      message,
      "Halo! Kirimkan link video YouTube atau TikTok, nanti saya download"
      " videonya.",
  )


@bot.message_handler(func=lambda message: True)
def download_media(message):
  url = message.text.strip()

  if not (
      "youtube.com" in url
      or "youtu.be" in url
      or "tiktok.com" in url
      or "vt.tiktok.com" in url
  ):
    bot.reply_to(message, "Kirim link YouTube atau TikTok yang bener ya, Vano!")
    return

  msg = bot.reply_to(message, "Sedang memproses download, sabar ya...")

  # Pengaturan yt-dlp anti-bot tanpa perlu file cookies
  ydl_opts = {
      "format": "mp4/best",
      "outtmpl": "video.mp4",
      "noplaylist": True,
      "geo_bypass": True,
      "nocheckcertificate": True,
      "user_agent": (
          "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML,"
          " like Gecko) Chrome/120.0.0.0 Safari/537.36"
      ),
  }

  try:
    if os.path.exists("video.mp4"):
      os.remove("video.mp4")

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
      ydl.download([url])

    # Cari file hasil download
    downloaded_file = "video.mp4"
    if not os.path.exists(downloaded_file):
      for f in os.listdir("."):
        if f.endswith(".mp4"):
          downloaded_file = f
          break

    with open(downloaded_file, "rb") as video:
      bot.send_video(message.chat.id, video)

    bot.delete_message(message.chat.id, msg.message_id)

    if os.path.exists(downloaded_file):
      os.remove(downloaded_file)

  except Exception as e:
    bot.edit_message_text(
        f"Gagal mendownload video:\n`{str(e)}`",
        message.chat.id,
        msg.message_id,
        parse_mode="Markdown",
    )


if __name__ == "__main__":
  import threading

  # Jalankan bot Telegram di background thread
  threading.Thread(
      target=lambda: bot.infinity_polling(none_stop=True), daemon=True
  ).start()

  # Jalankan server Flask untuk Railway (port 8080)
  port = int(os.environ.get("PORT", 8080))
  app.run(host="0.0.0.0", port=port)
