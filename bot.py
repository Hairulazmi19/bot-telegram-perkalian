# Import library yang diperlukan
import logging
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

# GANTI DENGAN TOKEN BOT ANDA
import os
TOKEN = os.environ.get("TELEGRAM_TOKEN")

# Mengaktifkan logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)

# Fungsi untuk command /start (pesannya sedikit diubah)
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None: # DIUBAH
    """Mengirim pesan ketika command /start dijalankan."""
    user = update.effective_user
    await update.message.reply_html(
        f"Halo {user.mention_html()}!\n\n"
        f"Saya adalah bot kalkulator perkalian. Gunakan perintah /kali diikuti dua angka.\n"
        f"<b>Contoh:</b> /kali 5 12"
    )

# FUNGSI BARU UNTUK PERKALIAN
async def kali(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Mengalikan dua angka yang diberikan setelah command /kali."""
    # context.args berisi daftar kata setelah command, contoh: ['5', '12']
    
    # Cek apakah pengguna memberikan dua argumen (angka)
    if len(context.args) != 2:
        await update.message.reply_text("Gagal! Harap berikan DUA angka saja.\nContoh: /kali 5 12")
        return # Hentikan fungsi jika input salah

    try:
        # Ubah argumen dari teks menjadi angka (integer)
        angka1 = int(context.args[0])
        angka2 = int(context.args[1])
        
        # Lakukan perhitungan
        hasil = angka1 * angka2
        
        # Kirim hasilnya kembali ke pengguna
        await update.message.reply_text(f"Hasil dari {angka1} x {angka2} adalah {hasil} ✨")
        
    except ValueError:
        # Tangani jika input yang diberikan bukan angka
        await update.message.reply_text("Gagal! Pastikan Anda memasukkan angka yang valid.")

# Fungsi echo bisa dihapus jika Anda mau bot hanya merespon command
async def echo(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Membalas pesan yang dikirim oleh user."""
    await update.message.reply_text(
        f"Saya tidak mengerti pesan '{update.message.text}'.\nCoba gunakan /start atau /kali."
    )

def main() -> None:
    """Fungsi utama untuk menjalankan bot."""
    application = Application.builder().token(TOKEN).build()

    # Mendaftarkan semua handler
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("kali", kali)) # BARU: Daftarkan command /kali

    # Handler untuk pesan teks biasa (bukan command)
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, echo))

    print("Bot sedang berjalan... Tekan Ctrl+C untuk berhenti.")
    application.run_polling()

if __name__ == "__main__":
    main()