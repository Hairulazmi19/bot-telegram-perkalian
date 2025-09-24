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

# Definisikan callback data untuk tombol, termasuk CANCEL
(
    ADD,
    SUBTRACT,
    MULTIPLY,
    DIVIDE,
    COMBINED,
    CANCEL, # BARU: Menambahkan konstanta untuk pembatalan
) = (
    "tambah",
    "kurang",

    "kali",
    "bagi",
    "gabungan",
    "cancel", # BARU: Nilai callback untuk tombol batal
)


# Fungsi untuk membuat tombol menu permanen
def get_main_menu_keyboard():
    """Membuat keyboard menu utama yang persisten."""
    keyboard = [["/start"]]
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True, one_time_keyboard=False)


# Fungsi yang dipanggil saat command /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Memulai percakapan dan menampilkan menu utama."""
    user = update.effective_user
    
    # Buat tombol-tombol inline, sekarang dengan tombol Batal
    inline_keyboard = [
        [InlineKeyboardButton("1. Penjumlahan", callback_data=ADD)],
        [InlineKeyboardButton("2. Pengurangan", callback_data=SUBTRACT)],
        [InlineKeyboardButton("3. Perkalian", callback_data=MULTIPLY)],
        [InlineKeyboardButton("4. Pembagian", callback_data=DIVIDE)],
        [InlineKeyboardButton("5. Gabungan", callback_data=COMBINED)],
        [InlineKeyboardButton("Batalkan ❌", callback_data=CANCEL)], # BARU: Menambahkan tombol Batal
    ]
    inline_markup = InlineKeyboardMarkup(inline_keyboard)
    
    # Jika percakapan sudah ada, edit pesannya. Jika baru, kirim pesan baru.
    if context.user_data.get('start_message_id'):
        await context.bot.edit_message_text(
            chat_id=update.effective_chat.id,
            message_id=context.user_data['start_message_id'],
            text=f"Halo {user.mention_html()}! 👋\n\nSilakan pilih lagi operasi matematika yang ingin Anda lakukan:",
            reply_markup=inline_markup,
            parse_mode='HTML'
        )
    else:
        message = await update.message.reply_html(
            f"Halo {user.mention_html()}! 👋\n\nSilakan pilih operasi matematika yang ingin Anda lakukan:",
            reply_markup=inline_markup,
        )
        context.user_data['start_message_id'] = message.message_id
        await update.message.reply_text(
            "Gunakan tombol 'Menu' di bawah jika ingin memulai ulang.",
            reply_markup=get_main_menu_keyboard()
        )
    
    return SELECTING_ACTION


# Fungsi yang dipanggil setelah pengguna menekan tombol operasi
async def ask_for_input(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Meminta input kepada pengguna berdasarkan pilihan mereka."""
    query = update.callback_query
    await query.answer()
    
    operation = query.data
    context.user_data["operation"] = operation
    
    if operation in [ADD, SUBTRACT, MULTIPLY, DIVIDE]:
        prompt = "Baik, silakan masukkan <b>dua angka</b> dipisahkan oleh spasi (contoh: <code>10 5</code>):"
    else:
        prompt = "Baik, silakan masukkan <b>ekspresi matematika</b> (contoh: <code>(100 + 50) / 2</code>):"
        
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
            result, operator = 0, ''

            if operation == ADD: result, operator = angka1 + angka2, '+'
            elif operation == SUBTRACT: result, operator = angka1 - angka2, '-'
            elif operation == MULTIPLY: result, operator = angka1 * angka2, '×'
            elif operation == DIVIDE:
                if angka2 == 0:
                    await update.message.reply_text("Error: Pembagian dengan nol tidak diizinkan.")
                    return ConversationHandler.END
                result, operator = angka1 / angka2, '÷'
            
            await update.message.reply_text(f"Hasil dari {angka1} {operator} {angka2} adalah\n\n👉 <b>{result}</b>", parse_mode='HTML')
            
    except ValueError as e:
        await update.message.reply_text(f"Input tidak valid! {e}. Silakan mulai lagi dengan /start.")
    except Exception:
        await update.message.reply_text("Terjadi error. Pastikan format ekspresi benar. Silakan mulai lagi dengan /start.")

    context.user_data.clear()
    return ConversationHandler.END

# Fungsi untuk membatalkan percakapan (via tombol atau command)
async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Membatalkan dan mengakhiri percakapan."""
    query = update.callback_query
    # Jika dibatalkan via tombol inline
    if query:
        await query.answer()
        await query.edit_message_text(text="Operasi dibatalkan. Kirim /start untuk memulai lagi.")
    # Jika dibatalkan via command /cancel
    else:
        await update.message.reply_text("Operasi dibatalkan. Kirim /start untuk memulai lagi.")
    
    context.user_data.clear()
    return ConversationHandler.END


def main() -> None:
    """Fungsi utama untuk menjalankan bot."""
    application = Application.builder().token(TOKEN).build()

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("start", start)],
        states={
            SELECTING_ACTION: [
                # BARU: Handler untuk tombol Batal. Harus diletakkan sebelum handler umum.
                CallbackQueryHandler(cancel, pattern=f"^{CANCEL}$"),
                # Handler ini akan menangani semua tombol lain yang bukan Batal
                CallbackQueryHandler(ask_for_input)
            ],
            PERFORMING_CALCULATION: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, calculate)
            ],
        },
        fallbacks=[CommandHandler("cancel", cancel)], # Mempertahankan /cancel sebagai command global
    )

    application.add_handler(conv_handler)
    
    print("Bot sedang berjalan... Tekan Ctrl+C untuk berhenti.")
    application.run_polling()


if __name__ == "__main__":
    main()