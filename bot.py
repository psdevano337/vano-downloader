import os
from flask import Flask
import requests
import telebot

TOKEN = "8649093474:AAGWEWf-eWjd036MHO3q_dIVaLXEQfUfLx4"
bot = telebot.TeleBot(TOKEN)
app = Flask(__name__)


@app.route("/")
def home():
  return "Bot API is running!"


@app.route("/health")
def health():
  return "OK", 200


@bot.message_handler(commands=["start", "help"])
def send_welcome(message):
  bot.reply_to(
      message,
      "Halo Vano! Bot downloader siap. Kirimkan link YouTube atau TikTok!",
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

  msg = bot.reply_to(message, "Sedang memproses link, sabar ya...")

  try:
    video_url = None

    # Menggunakan API downloader publik yang aktif
    headers = {"User-Agent": "Mozilla/5.0"}
    r = requests.get(
        f"https://api.ryzendesu.vip/api/downloader/ytdl?url={url}",
        headers=headers,
        timeout=20,
    )
    res = r.json()

    if res.get("url"):
      video_url = res["url"]
    elif res.get("data") and isinstance(res["data"], dict):
      video_url = res["data"].get("url")

    # Jika dapat linknya, kirim langsung ke Telegram
    if video_url:
      bot.send_video(message.chat.id, video_url)
      bot.delete_message(message.chat.id, msg.message_id)
    else:
      raise Exception("Gagal mendapatkan link video dari server API.")

  except Exception as e:
    bot.edit_message_text(
        f"Gagal mengambil video:\n`{str(e)}`",
        message.chat.id,
        msg.message_id,
        parse_mode="Markdown",
    )


if __name__ == "__main__":
  import threading

  threading.Thread(
      target=lambda: bot.infinity_polling(none_stop=True), daemon=True
  ).start()

  port = int(os.environ.get("PORT", 8080))
  app.run(host="0.0.0.0", port=port)
