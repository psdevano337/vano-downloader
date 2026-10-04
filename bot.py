import telebot, yt_dlp, os, uuid, glob
from flask import Flask

TOKEN = '8649093474:AAGWEWf-eWjd036MHO3q_dIVaLXEQfUfLx4'
bot = telebot.TeleBot(TOKEN)
app = Flask(__name__)

@app.route('/')
def home():
    return "Bot VanoDownloader aktif!"

@bot.message_handler(commands=['start'])
def welcome_message(message):
    bot.reply_to(message, "Halo Vano! Bot Downloader siap meluncur di server.")

@bot.message_handler(func=lambda message: True)
def handle_message(message):
    links = [word for word in message.text.split() if word.startswith('http')]
    if not links:
        bot.reply_to(message, "❌ Link tidak valid.")
        return
    bot.reply_to(message, f"⏳ Memproses {len(links)} link Super HD...")
    for url in links:
        kode_unik = str(uuid.uuid4())[:8]
        nama_file = f"video_{kode_unik}"
        ydl_opts = {
            'format': 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best',
            'merge_output_format': 'mp4',
            'outtmpl': f'{nama_file}.%(ext)s',
            'extractor_args': {'youtube': {'client': ['android', 'web']}}, 
        }
        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.download([url])
            dikirim = False
            for file in os.listdir():
                if file.startswith(nama_file):
                    with open(file, 'rb') as video_file:
                        bot.send_video(message.chat.id, video_file, timeout=600)
                    os.remove(file)
                    dikirim = True
                    break
            if not dikirim:
                bot.reply_to(message, "❌ Gagal dikirim.")
        except Exception as e:
            bot.reply_to(message, "❌ Gagal memproses link.")
            for f in glob.glob(f"{nama_file}*"):
                try: os.remove(f)
                except: pass

if __name__ == "__main__":
    import threading
    t = threading.Thread(target=lambda: bot.infinity_polling(none_stop=True))
    t.start()
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
