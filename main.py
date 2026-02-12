import os
import uuid
import json
from pytdbot import Client, types
from dotenv import load_dotenv

load_dotenv()

SESSION_DIR = "bot_sessions"
if not os.path.exists(SESSION_DIR):
    os.makedirs(SESSION_DIR)

DB_FILE = os.path.join(SESSION_DIR, "secrets.json")

def save_msg(msg_id, to_who, text):
    try:
        db = {}
        if os.path.exists(DB_FILE):
            with open(DB_FILE, "r") as f:
                db = json.load(f)
        db[msg_id] = {"to": str(to_who).replace("@", "").lower(), "msg": text}
        with open(DB_FILE, "w") as f:
            json.dump(db, f)
    except:
        pass

def get_msg(msg_id):
    try:
        if os.path.exists(DB_FILE):
            with open(DB_FILE, "r") as f:
                db = json.load(f)
                return db.get(msg_id)
    except:
        return None

# --- BOT YARADILIR ---
bot = Client(
    api_id=int(os.getenv("API_ID")),
    api_hash=str(os.getenv("API_HASH")),
    token=str(os.getenv("BOT_TOKEN")),
    database_encryption_key="XeyalBotAcar123",
    files_directory=SESSION_DIR
)

# --- INLINE HANDLER (Səhv burada idi: on_inline_query olmalı imiş) ---
@bot.on_inline_query()
async def secret_inline(c, inline_query):
    query = inline_query.query.strip()
    if " " not in query:
        return
    target, secret_text = query.split(" ", 1)
    msg_id = str(uuid.uuid4())[:8]
    save_msg(msg_id, target, secret_text)

    results = [
        types.InputInlineQueryResultArticle(
            id=msg_id,
            title=f"🔒 Mesaj: {target}",
            description="Gizli göndərmək üçün toxunun",
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


# --- CALLBACK HANDLER (Düzəldildi) ---
@bot.on_callback_query()
async def read_secret(c, cb):
    try:
        msg_id = cb.payload.data.decode().split("_")[1]
    except:
        return
    data = get_msg(msg_id)
    if not data:
        return await cb.answer("❌ Mesaj tapılmadı.", show_alert=True)

    target = data["to"]
    user_id = str(cb.from_user.id)
    username = (cb.from_user.username or "").lower()
    if user_id == target or username == target:
        await cb.answer(f"🔒 Gizli Mesajınız:\n\n{data['msg']}", show_alert=True)
    else:
        await cb.answer(f"❌ Bu mesaj yalnız {target} üçündür!", show_alert=True)


# --- START HANDLER (Düzəldildi) ---
@bot.on_message()
async def start(c, m):
    if not m.text or not m.text.startswith("/start"):
        return

    text = (
        "👋 **Salam! Mən Gizli Mesaj botuyam.**\n\n"
        "🛠 **İstifadə qaydası:**\n"
        "Inline rejimdə mənim adımı yazın, sonra **@username** və **mesaj**.\n\n"
        "**Nümunə:**\n"
        "`@BotAdı @istifadeci salam necəsən?`"
    )

    keyboard = [
        [
            types.InlineKeyboardButton(
                text="🧑‍💻 Developer",
                type=types.InlineKeyboardButtonTypeUrl("https://t.me/kullaniciadidi")
            ),
            types.InlineKeyboardButton(
                text="📢 Məlumat kanalı",
                type=types.InlineKeyboardButtonTypeUrl("https://t.me/ht_bots")
            )
        ],
        [
            types.InlineKeyboardButton(
                text="🆘 Kömək qrupu",
                type=types.InlineKeyboardButtonTypeUrl("https://t.me/ht_bots_chat")
            )
        ]
    ]

    await m.reply_text(
        text,
        parse_mode="markdown",
        reply_markup=types.ReplyMarkupInlineKeyboard(keyboard)
    )

# --- RUN BOT ---
bot.run()
