import os
import uuid
import json
from pytdbot import Client, types, filters
from dotenv import load_dotenv

load_dotenv()

# Sadə JSON bazası funksiyaları
DB_FILE = "secrets.json"

def save_msg(msg_id, to_who, text):
    try:
        if os.path.exists(DB_FILE):
            with open(DB_FILE, "r") as f: db = json.load(f)
        else: db = {}
        db[msg_id] = {"to": str(to_who).replace("@", "").lower(), "msg": text}
        with open(DB_FILE, "w") as f: json.dump(db, f)
    except: pass

def get_msg(msg_id):
    try:
        with open(DB_FILE, "r") as f:
            db = json.load(f)
            return db.get(msg_id)
    except: return None

# Botu başladırıq
bot = Client(
    api_id=int(os.getenv("API_ID")),
    api_hash=os.getenv("API_HASH"),
    token=os.getenv("BOT_TOKEN")
)

@bot.on_inline_query()
async def secret_inline(c: Client, inline_query: types.InlineQuery):
    query = inline_query.query.strip()
    if " " not in query: return

    # @username mesaj və ya 12345678 mesaj formatını ayırırıq
    target, secret_text = query.split(" ", 1)
    msg_id = str(uuid.uuid4())[:8]
    
    # Mesajı bazaya yaddaşa veririk
    save_msg(msg_id, target, secret_text)

    results = [
        types.InputInlineQueryResultArticle(
            id=msg_id,
            title=f"🔒 Mesaj: {target}",
            description="Buna bassanız mesaj gizli gedəcək.",
            input_message_content=types.InputMessageText(
                text=types.FormattedText(text=f"🎁 {target}, sizin üçün gizli mesaj var!")
            ),
            reply_markup=types.ReplyMarkupInlineKeyboard([
                [types.InlineKeyboardButton(
                    text="👁 Mesajı Oxu", 
                    type=types.InlineKeyboardButtonTypeCallback(f"read_{msg_id}".encode())
                )]
            ])
        )
    ]
    await c.answerInlineQuery(inline_query.id, results, cache_time=1)

@bot.on_callback_query(filters=lambda _, c: c.payload.data.decode().startswith("read_"))
async def read_secret(c: Client, cb: types.CallbackQuery):
    msg_id = cb.payload.data.decode().split("_")[1]
    data = get_msg(msg_id)
    
    if not data:
        return await cb.answer("❌ Mesaj tapılmadı və ya köhnəlib.", show_alert=True)

    target = data["to"]
    # Həm ID-ni, həm də Username-i yoxlayırıq
    is_allowed = False
    
    if str(cb.from_user.id) == target: # ID yoxlanışı
        is_allowed = True
    elif cb.from_user.username and cb.from_user.username.lower() == target: # Username yoxlanışı
        is_allowed = True

    if is_allowed:
        await cb.answer(f"🔒 Gizli Mesajınız:\n\n{data['msg']}", show_alert=True)
    else:
        await cb.answer(f"❌ Bu mesaj yalnız {target} üçündür!", show_alert=True)

@bot.on_message(filters.command("start"))
async def start(c: Client, m: types.Message):
    await m.reply_text("Salam! Gizli mesaj yazmaq üçün yazı yerində məni çağırın.\n\nNümunələr:\n`@botadi @username salam`\n`@botadi 12345678 salam`")

bot.run()
