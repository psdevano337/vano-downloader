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
      "Halo Vano! Bot downloader versi cepat siap. Kirimkan link YouTube atau"
      " TikTok!",
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

  msg = bot.reply_to(message, "Sedang memproses download via API, sabar ya...")

  try:
    # Menggunakan API publik gratis untuk mengambil data video
    api_url = (
        f"https://api.tikdownload.app/api/ajaxSearch?q={url}"
        # atau bisa menggunakan endpoint downloader umum
    )

    # Cara paling aman menggunakan request ke layanan scraper publik atau endpoint cobalt/y2mate api
    # Mari kita gunakan endpoint yang stabil untuk fetch direct link video:
    # Kita pakai request sederhana lewat API publik universal:
    r = requests.get(
        f"https://deliriussapi-v2.vercel.app/download/ytdl?url={url}", timeout=30
    )
    res = r.json()

    if res.get("status") and res.get("data"):
      video_url = res["data"]["download"]["url"]

      # Kirim langsung video ke Telegram berdasarkan direct link dari API
      bot.send_video(message.chat.id, video_url)
      bot.delete_message(message.chat.id, msg.message_id)
    else:
      # Cadangan pakai API alternatif jika yang pertama gagal
      r2 = requests.get(
          f"https://api.ryzendesu.vip/api/downloader/ytdl?url={url}", timeout=30
      )
      res2 = r2.json()
      if res2.get("url"):
        bot.send_video(message.chat.id, res2["url"])
        bot.delete_message(message.chat.id, msg.message_id)
      else:
        raise Exception(
            "Gagal mendapatkan link download dari server API publik."
        )

  except Exception as e:
    bot.edit_message_text(
        f"Gagal mendownload video:\n`{str(e)}`",
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
