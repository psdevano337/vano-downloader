import os
from flask import Flask
import requests
import telebot

TOKEN = "8649093474:AAGWEWf-eWjd036MHO3q_dIVaLXEQfUfLx4"
bot = telebot.TeleBot(TOKEN)
app = Flask(__name__)


@app.route("/")
def home():
  app_status = "Bot downloader is active and running!"
  return app_status


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

    # Percobaan 1: Menggunakan API Cobalt yang sangat stabil untuk sosmed & YT
    headers = {
        "Accept": "application/json",
        "Content-Type": "application/json",
        "User-Agent": "Mozilla/5.0",
    }
    r = requests.post(
        "https://co.wuk.sh/api/json",
        json={"url": url},
        headers=headers,
        timeout=15,
    )
    res = r.json()
    if res.get("status") in ["stream", "redirect"] or res.get("url"):
      video_url = res.get("url")

    # Percobaan 2: Jika Cobalt gagal, lempar ke API alternatif publik
    if not video_url:
      r2 = requests.get(
          f"https://deliriussapi-v2.vercel.app/download/ytdl?url={url}",
          timeout=15,
      )
      res2 = r2.json()
      if res2.get("status") and res2.get("data"):
        video_url = res2["data"]["download"]["url"]

    if video_url:
      bot.send_video(message.chat.id, video_url)
      bot.delete_message(message.chat.id, msg.message_id)
    else:
      raise Exception("Server gagal merespon link unduhan.")

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
