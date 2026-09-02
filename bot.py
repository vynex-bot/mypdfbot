import io import os import random import requests from datetime import datetime from reportlab.lib.pagesizes import A5 from reportlab.pdfgen import canvas from reportlab.pdfbase import pdfmetrics from reportlab.pdfbase.ttfonts import TTFont from telegram import Update from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

TOKEN = os.environ.get("TELEGRAM_TOKEN") PORT = int(os.environ.get("PORT", 8080)) WEBHOOK_URL = os.environ.get("WEBHOOK_URL")  # https://ваш-сайт.railway.app

=== АВТОМАТИЧЕСКАЯ ЗАГРУЗКА ШРИФТА ===
FONT_NAME = "DejaVuSans" FONT_FILE = f"{FONT_NAME}.ttf"

if not os.path.exists(FONT_FILE): print("⬇️ Скачиваю шрифт...") url = "https://github.com/dejavu-fonts/dejavu-fonts/raw/master/ttf/DejaVuSans.ttf" response = requests.get(url) with open(FONT_FILE, "wb") as f: f.write(response.content) print("✅ Шрифт загружен")

pdfmetrics.registerFont(TTFont(FONT_NAME, FONT_FILE))

=== ГЕНЕРАТОР КВИТАНЦИЙ ===
def generate_receipt(account: str, amount: float) -> bytes: buf = io.BytesIO() c = canvas.Canvas(buf, pagesize=A5) width, height = A5

copy


c.setFont(FONT_NAME, 9)

# Дата
dt = datetime.now().strftime("%d.%m.%Y %H:%M:%S")
c.drawString(20, height - 30, dt)

# Итого
c.drawString(width - 100, height - 30, "Итого")
c.setFont(FONT_NAME, 12)
c.drawString(width - 60, height - 32, f"{amount:.0f} ₽")
c.setFont(FONT_NAME, 9)

# Покупка
y = height - 60
c.drawString(20, y, "Покупка")
c.drawString(100, y, "По QR-коду")

# Статус / Сумма
y -= 25
c.drawString(20, y, "Статус")
c.drawString(100, y, "Успешно")
c.drawString(180, y, "Сумма")
c.drawString(230, y, f"{amount:.0f} ₽")

# Магазин
y -= 25
c.drawString(20, y, "Магазин")
c.drawString(100, y, "Wildberries")

# ЮЛ
y -= 25
c.drawString(20, y, "Наименование ЮЛ или ИП")
c.drawString(100, y, "ООО 'РВБ'")

# ID операции
y -= 25
op_id = f"B{random.randint(10**12, 10**13-1)}F{random.randint(10,99)}G{random.randint(1000,9999)}"
c.drawString(20, y, "Идентификатор операции")
c.drawString(100, y, f"{op_id} СБП 30701")

# Банк получателя
y -= 25
c.drawString(20, y, "Банк получателя")
c.drawString(100, y, "100000000259")

# Счет списания (маскировка)
y -= 25
if len(account) >= 10:
    masked = account[:6] + "****" + account[-4:]
else:
    masked = account
c.drawString(20, y, "Счет списания")
c.drawString(100, y, masked)

# Квитанция №
y -= 25
receipt_num = f"1-{random.randint(100,999)}-{random.randint(100,999)}-{random.randint(100,999)}-{random.randint(100,999)}"
c.drawString(20, y, f"Квитанция № {receipt_num}")

# Подвал
y -= 30
c.setFont(FONT_NAME, 8)
c.drawString(20, y, "По вопросам зачисления обращайтесь к получателю")
y -= 15
c.drawString(20, y, "Служба поддержки fb@tbank.ru")

c.save()
buf.seek(0)
return buf.getvalue()
=== ОБРАБОТЧИКИ ===
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE): await update.message.reply_text( "👋 Отправь:\nномер_счёта сумма\nПример:\n40817810900123456789 1500" )

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE): text = update.message.text.strip() parts = text.split() if len(parts) < 2: await update.message.reply_text("⚠️ Нужно: номер_счёта и сумма") return

copy


account = parts[0]
try:
    amount = float(parts[1].replace(',', '.'))
except:
    await update.message.reply_text("⚠️ Сумма — число")
    return

if amount <= 0:
    await update.message.reply_text("⚠️ Сумма > 0")
    return

pdf = generate_receipt(account, amount)
await update.message.reply_document(
    document=io.BytesIO(pdf),
    filename=f"receipt_{datetime.now().strftime('%d.%m.%Y')}.pdf",
    caption=f"✅ {amount:.0f} ₽ по счёту {account[:4]}****{account[-4:]}"
)
=== ЗАПУСК (ВЕБХУК ДЛЯ RAILWAY) ===
def main(): app = Application.builder().token(TOKEN).build() app.add_handler(CommandHandler("start", start)) app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

copy


print(f"🚀 Запуск на порту {PORT} с вебхуком: {WEBHOOK_URL}")
app.run_webhook(
    listen="0.0.0.0",
    port=PORT,
    url_path=TOKEN,
    webhook_url=f"{WEBHOOK_URL}/{TOKEN}"
)
if name == "main": main()
