import os
import logging
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes

# Ambil token dari environment variable untuk keamanan
TOKEN = os.environ.get("TELEGRAM_TOKEN")

# Mengaktifkan logging untuk melihat error
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)

# Fungsi untuk command /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Mengirim pesan ketika command /start dijalankan."""
    user = update.effective_user
    await update.message.reply_html(
        f"Halo {user.mention_html()}! 👋\n\n"
        f"Saya adalah bot kalkulator serbaguna. Gunakan perintah berikut:\n"
        f"<code>/tambah [angka1] [angka2]</code> - Untuk penjumlahan\n"
        f"<code>/kurang [angka1] [angka2]</code> - Untuk pengurangan\n"
        f"<code>/kali [angka1] [angka2]</code> - Untuk perkalian\n"
        f"<code>/bagi [angka1] [angka2]</code> - Untuk pembagian\n\n"
        f"<b>Contoh:</b> <code>/tambah 10 5</code>"
    )

# Fungsi untuk melakukan operasi perhitungan
async def hitung(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Fungsi generik untuk menangani semua operasi matematika."""
    command = update.message.text.split()[0].replace('/', '') # Mendapatkan nama command: 'tambah', 'kurang', dll.
    
    # Cek apakah pengguna memberikan dua argumen (angka)
    if len(context.args) != 2:
        await update.message.reply_text(f"Gagal! Harap berikan DUA angka saja.\nContoh: /{command} 10 5")
        return

    try:
        # Ubah argumen dari teks menjadi angka (float untuk mendukung desimal)
        angka1 = float(context.args[0])
        angka2 = float(context.args[1])
        hasil = 0
        operator = ''

        # Lakukan operasi berdasarkan command yang dipanggil
        if command == "tambah":
            hasil = angka1 + angka2
            operator = '+'
        elif command == "kurang":
            hasil = angka1 - angka2
            operator = '-'
        elif command == "kali":
            hasil = angka1 * angka2
            operator = '×' # Menggunakan simbol perkalian
        elif command == "bagi":
            # Cek pembagian dengan nol
            if angka2 == 0:
                await update.message.reply_text("Error: Tidak bisa melakukan pembagian dengan nol.")
                return
            hasil = angka1 / angka2
            operator = '÷' # Menggunakan simbol pembagian
        
        # Kirim hasilnya kembali ke pengguna
        await update.message.reply_text(f"Hasil dari {angka1} {operator} {angka2} adalah\n👉 **{hasil}**", parse_mode='Markdown')

    except ValueError:
        # Tangani jika input yang diberikan bukan angka
        await update.message.reply_text("Gagal! Pastikan Anda memasukkan angka yang valid.")
    except Exception as e:
        # Tangani error tak terduga lainnya
        logger.error(f"Error pada command {command}: {e}")
        await update.message.reply_text("Maaf, terjadi error tak terduga.")


def main() -> None:
    """Fungsi utama untuk menjalankan bot."""
    # Membuat objek Application
    application = Application.builder().token(TOKEN).build()
    logger.info("Bot berhasil dibuat.")

    # Mendaftarkan semua handler untuk setiap command
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("tambah", hitung))
    application.add_handler(CommandHandler("kurang", hitung))
    application.add_handler(CommandHandler("kali", hitung))
    application.add_handler(CommandHandler("bagi", hitung))
    
    # Menjalankan bot sampai user menekan Ctrl-C
    print("Bot sedang berjalan... Tekan Ctrl+C untuk berhenti.")
    application.run_polling()

if __name__ == "__main__":
    main()