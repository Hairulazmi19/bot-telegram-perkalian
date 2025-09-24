import os
import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup
from telegram.ext import (
    Application,
    CommandHandler,
    ContextTypes,
    ConversationHandler,
    CallbackQueryHandler,
    MessageHandler,
    filters,
)

# Ambil token dari environment variable untuk keamanan
TOKEN = os.environ.get("TELEGRAM_TOKEN")

# Mengaktifkan logging untuk melihat error
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)

# Definisikan state untuk ConversationHandler
SELECTING_ACTION, PERFORMING_CALCULATION = range(2)

# Definisikan callback data untuk tombol
(
    ADD,
    SUBTRACT,
    MULTIPLY,
    DIVIDE,
    COMBINED,
) = (
    "tambah",
    "kurang",
    "kali",
    "bagi",
    "gabungan",
)

# --- FUNGSI BARU UNTUK MEMBUAT TOMBOL MENU ---
def get_main_menu_keyboard():
    """Membuat keyboard menu utama yang persisten."""
    keyboard = [["/start"]]  # Tombol ini akan mengirimkan command /start
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True, one_time_keyboard=False)


# Fungsi yang dipanggil saat command /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Memulai percakapan dan menampilkan menu utama."""
    user = update.effective_user
    
    # Buat tombol-tombol inline untuk pilihan operasi
    inline_keyboard = [
        [InlineKeyboardButton("1. Penjumlahan", callback_data=ADD)],
        [InlineKeyboardButton("2. Pengurangan", callback_data=SUBTRACT)],
        [InlineKeyboardButton("3. Perkalian", callback_data=MULTIPLY)],
        [InlineKeyboardButton("4. Pembagian", callback_data=DIVIDE)],
        [InlineKeyboardButton("5. Gabungan (contoh: 5 * (3+2))", callback_data=COMBINED)],
    ]
    inline_markup = InlineKeyboardMarkup(inline_keyboard)
    
    await update.message.reply_html(
        f"Halo {user.mention_html()}! 👋\n\nSilakan pilih operasi matematika yang ingin Anda lakukan:",
        reply_markup=inline_markup, # Ini tombol inline
    )
    
    # Kirim pesan terpisah HANYA untuk menampilkan tombol menu utama
    await update.message.reply_text(
        "Gunakan tombol 'Menu' di bawah jika ingin memulai ulang.",
        reply_markup=get_main_menu_keyboard() # Ini tombol menu permanen
    )
    
    # Masuk ke state pertama: memilih aksi
    return SELECTING_ACTION


# Fungsi yang dipanggil setelah pengguna menekan tombol
async def ask_for_input(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Meminta input kepada pengguna berdasarkan pilihan mereka."""
    query = update.callback_query
    await query.answer()
    
    operation = query.data
    context.user_data["operation"] = operation
    
    if operation in [ADD, SUBTRACT, MULTIPLY, DIVIDE]:
        prompt = "Baik, silakan masukkan <b>dua angka</b> dipisahkan oleh spasi (contoh: <code>10 5</code>):"
    else:
        prompt = "Baik, silakan masukkan <b>ekspresi matematika</b> yang ingin dihitung (contoh: <code>(100 + 50) / 2</code>):"
        
    await query.edit_message_text(text=prompt, parse_mode='HTML')
    
    return PERFORMING_CALCULATION


# Fungsi yang menangani input angka atau ekspresi dari pengguna
async def calculate(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Melakukan perhitungan dan mengakhiri percakapan."""
    operation = context.user_data.get("operation")
    user_input = update.message.text
    
    try:
        if operation == COMBINED:
            allowed_chars = "0123456789.+-*/() "
            if not all(char in allowed_chars for char in user_input):
                raise ValueError("Ekspresi mengandung karakter tidak valid.")
            
            result = eval(user_input)
            await update.message.reply_text(f"Hasil dari <code>{user_input}</code> adalah\n\n👉 <b>{result}</b>", parse_mode='HTML')

        else:
            parts = user_input.split()
            if len(parts) != 2:
                raise ValueError("Harap masukkan DUA angka.")
                
            angka1 = float(parts[0])
            angka2 = float(parts[1])
            result = 0
            operator = ''

            if operation == ADD:
                result = angka1 + angka2; operator = '+'
            elif operation == SUBTRACT:
                result = angka1 - angka2; operator = '-'
            elif operation == MULTIPLY:
                result = angka1 * angka2; operator = '×'
            elif operation == DIVIDE:
                if angka2 == 0:
                    await update.message.reply_text("Error: Tidak bisa melakukan pembagian dengan nol.")
                    return ConversationHandler.END
                result = angka1 / angka2; operator = '÷'
            
            await update.message.reply_text(f"Hasil dari {angka1} {operator} {angka2} adalah\n\n👉 <b>{result}</b>", parse_mode='HTML')
            
    except ValueError as e:
        await update.message.reply_text(f"Input tidak valid! {e}. Silakan mulai lagi dengan /start.")
    except Exception:
        await update.message.reply_text("Terjadi error saat menghitung ekspresi. Pastikan formatnya benar. Silakan mulai lagi dengan /start.")

    return ConversationHandler.END

# Fungsi untuk membatalkan percakapan
async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Membatalkan dan mengakhiri percakapan."""
    await update.message.reply_text(
        "Operasi dibatalkan. Kirim /start untuk memulai lagi.",
        reply_markup=get_main_menu_keyboard() # Tampilkan lagi menu utama saat batal
    )
    return ConversationHandler.END


def main() -> None:
    """Fungsi utama untuk menjalankan bot."""
    application = Application.builder().token(TOKEN).build()

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("start", start)],
        states={
            SELECTING_ACTION: [CallbackQueryHandler(ask_for_input)],
            PERFORMING_CALCULATION: [MessageHandler(filters.TEXT & ~filters.COMMAND, calculate)],
        },
        fallbacks=[CommandHandler("cancel", cancel)],
    )

    application.add_handler(conv_handler)
    
    print("Bot sedang berjalan... Tekan Ctrl+C untuk berhenti.")
    application.run_polling()


if __name__ == "__main__":
    main()