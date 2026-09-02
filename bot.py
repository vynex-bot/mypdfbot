import io import random from datetime import datetime, timedelta from reportlab.lib.pagesizes import A4, A5 from reportlab.pdfgen import canvas from reportlab.lib.units import mm from reportlab.pdfbase import pdfmetrics from reportlab.pdfbase.ttfonts import TTFont from telegram import Update from telegram.ext import Application, CommandHandler, ContextTypes

TOKEN = "8748775050:AAFHcDI6JlYGmCKTiIoUe17fKGOG80KsaXA"

Регистрируем шрифт для корректного отображения кириллицы
try: pdfmetrics.registerFont(TTFont('DejaVu', 'DejaVuSans.ttf')) FONT = 'DejaVu' except: FONT = 'Helvetica'

def generate_tbank_receipt(account_number: str, amount: float) -> bytes: buf = io.BytesIO() c = canvas.Canvas(buf, pagesize=A5) width, height = A5  # 420 x 595 pt (примерно A5)

copy


# Устанавливаем шрифт
c.setFont(FONT, 9)

# Строка 1: дата и время (как в образце)
dt = datetime.now().strftime("%d.%m.%Y %H:%M:%S")
c.drawString(20, height - 30, dt)

# Строка 2: "Итого" справа
c.drawString(width - 100, height - 30, "Итого")
c.setFont(FONT, 12)
c.drawString(width - 60, height - 32, f"{amount:.0f} ₽")
c.setFont(FONT, 9)

# Блок "Покупка"
y = height - 60
c.drawString(20, y, "Покупка")
c.drawString(100, y, "По QR-коду")

# Блок "Статус" / "Сумма"
y -= 25
c.drawString(20, y, "Статус")
c.drawString(100, y, "Успешно")
c.drawString(180, y, "Сумма")
c.drawString(230, y, f"{amount:.0f} ₽")

# Блок "Магазин"
y -= 25
c.drawString(20, y, "Магазин")
c.drawString(100, y, "Wildberries")

# Блок "Наименование ЮЛ или ИП"
y -= 25
c.drawString(20, y, "Наименование ЮЛ или ИП")
c.drawString(100, y, "ООО 'РВБ'")

# Блок "Идентификатор операции СБП"
y -= 25
op_id = f"B{random.randint(1000000000000, 9999999999999)}F{random.randint(10, 99)}G{random.randint(1000, 9999)}"
c.drawString(20, y, "Идентификатор операции")
c.drawString(100, y, f"{op_id} СБП 30701")

# Блок "Банк получателя"
y -= 25
bank_account = "100000000259"  # Фиксированный банковский ID (как в образце)
c.drawString(20, y, "Банк получателя")
c.drawString(100, y, bank_account)

# Блок "Счет списания" - СЮДА ПОДСТАВЛЯЕТСЯ ВАШ НОМЕР СЧЁТА
y -= 25
# Маскируем счёт как в образце: первые цифры, потом звёздочки, последние 4
if len(account_number) >= 10:
    masked = account_number[:6] + "****" + account_number[-4:]
else:
    masked = account_number  # на случай короткого номера
c.drawString(20, y, "Счет списания")
c.drawString(100, y, masked)

# Блок "Квитанция №"
y -= 25
receipt_num = f"1-{random.randint(100,999)}-{random.randint(100,999)}-{random.randint(100,999)}-{random.randint(100,999)}"
c.drawString(20, y, f"Квитанция № {receipt_num}")

# Нижняя часть
y -= 30
c.setFont(FONT, 8)
c.drawString(20, y, "По вопросам зачисления обращайтесь к получателю")
y -= 15
c.drawString(20, y, "Служба поддержки fb@tbank.ru")

c.save()
buf.seek(0)
return buf.getvalue()
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE): await update.message.reply_text( "👋 Отправь мне данные в формате:\n" "номер_счёта сумма\n" "Пример:\n" "40817810900123456789 1500" )

async def handle_receipt(update: Update, context: ContextTypes.DEFAULT_TYPE): text = update.message.text.strip() parts = text.split() if len(parts) < 2: await update.message.reply_text("⚠️ Нужно: номер счёта и сумма через пробел") return

copy


account = parts[0]
try:
    amount = float(parts[1].replace(',', '.'))
except ValueError:
    await update.message.reply_text("⚠️ Сумма должна быть числом")
    return

if amount <= 0 or amount > 99999999:
    await update.message.reply_text("⚠️ Сумма должна быть от 1 до 99 999 999")
    return

pdf_bytes = generate_tbank_receipt(account, amount)
filename = f"receipt_{datetime.now().strftime('%d.%m.%Y')}.pdf"

await update.message.reply_document(
    document=io.BytesIO(pdf_bytes),
    filename=filename,
    caption=f"✅ Квитанция на {amount:.0f} ₽ по счёту {account[:4]}****{account[-4:]}"
)
def main(): app = Application.builder().token(TOKEN).build() app.add_handler(CommandHandler("start", start)) app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_receipt)) print("🚀 Бот запущен. Ожидаю сообщения в формате: номер_счёта сумма") app.run_polling()

if name == "main": main()
