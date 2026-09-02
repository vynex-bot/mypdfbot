import io import os import random import requests from datetime import datetime from reportlab.lib.pagesizes import A5 from reportlab.pdfgen import canvas from reportlab.pdfbase import pdfmetrics from reportlab.pdfbase.ttfonts import TTFont from telegram import Update from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
TOKEN = os.environ.get("8748775050:AAFHcDI6JlYGmCKTiIoUe17fKGOG80KsaXA") PORT = int(os.environ.get("PORT", 8080)) WEBHOOK_URL = os.environ.get("WEBHOOK_URL")
FONT_NAME = "DejaVuSans" FONT_FILE = f"{FONT_NAME}.ttf"
if not os.path.exists(FONT_FILE): print("Downloading font...") url = "https://github.com/dejavu-fonts/dejavu-fonts/raw/master/ttf/DejaVuSans.ttf" response = requests.get(url) with open(FONT_FILE, "wb") as f: f.write(response.content) print("Font downloaded")
pdfmetrics.registerFont(TTFont(FONT_NAME, FONT_FILE))
def generate_receipt(account, amount): buf = io.BytesIO() c = canvas.Canvas(buf, pagesize=A5) width, height = A5
Python


c.setFont(FONT_NAME, 9)

dt = datetime.now().strftime("%d.%m.%Y %H:%M:%S")
c.drawString(20, height - 30, dt)

c.drawString(width - 100, height - 30, "Itogo")
c.setFont(FONT_NAME, 12)
c.drawString(width - 60, height - 32, f"{amount:.0f} RUB")
c.setFont(FONT_NAME, 9)

y = height - 60
c.drawString(20, y, "Pokupka")
c.drawString(100, y, "Po QR-kodu")

y -= 25
c.drawString(20, y, "Status")
c.drawString(100, y, "Uspehno")
c.drawString(180, y, "Summa")
c.drawString(230, y, f"{amount:.0f} RUB")

y -= 25
c.drawString(20, y, "Magazin")
c.drawString(100, y, "Wildberries")

y -= 25
c.drawString(20, y, "Naimenovanie YL ili IP")
c.drawString(100, y, "OOO RVB")

y -= 25
op_id = f"B{random.randint(10**12, 10**13-1)}F{random.randint(10,99)}G{random.randint(1000,9999)}"
c.drawString(20, y, "Identifikator operacii")
c.drawString(100, y, f"{op_id} SBP 30701")

y -= 25
c.drawString(20, y, "Bank poluchatelya")
c.drawString(100, y, "100000000259")

y -= 25
if len(account) >= 10:
    masked = account[:6] + "****" + account[-4:]
else:
    masked = account
c.drawString(20, y, "Schet spisaniya")
c.drawString(100, y, masked)

y -= 25
receipt_num = f"1-{random.randint(100,999)}-{random.randint(100,999)}-{random.randint(100,999)}-{random.randint(100,999)}"
c.drawString(20, y, f"Kvitantsiya N {receipt_num}")

y -= 30
c.setFont(FONT_NAME, 8)
c.drawString(20, y, "Po voprosam zachisleniya obrashaytes k poluchatelyu")
y -= 15
c.drawString(20, y, "Sluzhba podderzhki fb@tbank.ru")

c.save()
buf.seek(0)
return buf.getvalue()
async def start(update, context): await update.message.reply_text( "Send: account_number amount\n" "Example: 40817810900123456789 1500" )
async def handle_message(update, context): text = update.message.text.strip() parts = text.split() if len(parts) < 2: await update.message.reply_text("Need: account and amount") return
Python


account = parts[0]
try:
    amount = float(parts[1].replace(',', '.'))
except:
    await update.message.reply_text("Amount must be number")
    return

if amount <= 0:
    await update.message.reply_text("Amount > 0")
    return

pdf = generate_receipt(account, amount)
await update.message.reply_document(
    document=io.BytesIO(pdf),
    filename=f"receipt_{datetime.now().strftime('%d.%m.%Y')}.pdf",
    caption=f"OK {amount:.0f} RUB for account {account[:4]}****{account[-4:]}"
)
def main(): app = Application.builder().token(TOKEN).build() app.add_handler(CommandHandler("start", start)) app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
Python


print(f"Starting on port {PORT} with webhook: {WEBHOOK_URL}")
app.run_webhook(
    listen="0.0.0.0",
    port=PORT,
    url_path=TOKEN,
    webhook_url=f"{WEBHOOK_URL}/{TOKEN}"
)
if name == "main": main()
