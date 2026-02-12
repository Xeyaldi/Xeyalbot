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
# database_encryption_key əlavə edildi ki, Heroku-da 'database_encryption_key must be str' xətası verməsin.
bot = Client(
    api_id=int(os.getenv("API_ID")),
    api_hash=os.getenv("API_HASH"),
    token=os.getenv("BOT_TOKEN"),
    database_encryption_key="XeyalBotAcar123" 
)

# --- İNLINE HİSSƏSİ (Gizli mesaj yazmaq üçün) ---
@bot.on_inline_query()
async def secret_inline(c: Client, inline_query: types.InlineQuery):
    query = inline_query.query.strip()
    if " " not in query: return

    # Format: @username mesaj və ya 12345678 mesaj
    target, secret_text = query.split(" ", 1)
    msg_id = str(uuid.uuid4())[:8]
    
    save_msg(msg_id, target, secret_text)

    results = [
        types.InputInlineQueryResultArticle(
            id=msg_id,
            title=f"🔒 Mesaj: {target}",
            description="Buna bassanız mesaj gizli göndəriləcək.",
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

# --- CALLBACK HİSSƏSİ (Düyməyə basanda oxumaq üçün) ---
@bot.on_callback_query(filters=lambda _, c: c.payload.data.decode().startswith("read_"))
async def read_secret(c: Client, cb: types.CallbackQuery):
    msg_id = cb.payload.data.decode().split("_")[1]
    data = get_msg(msg_id)
    
    if not data:
        return await cb.answer("❌ Mesaj tapılmadı və ya silinib.", show_alert=True)

    target = data["to"]
    is_allowed = False
    
    # Həm ID-ni, həm də Username-i yoxlayırıq
    if str(cb.from_user.id) == target: 
        is_allowed = True
    elif cb.from_user.username and cb.from_user.username.lower() == target: 
        is_allowed = True

    if is_allowed:
        await cb.answer(f"🔒 Gizli Mesajınız:\n\n{data['msg']}", show_alert=True)
    else:
        await cb.answer(f"❌ Bu mesaj yalnız {target} üçündür!", show_alert=True)

# --- START HİSSƏSİ (Botu başladanda düymələrlə görünən) ---
@bot.on_message(filters.command("start"))
async def start(c: Client, m: types.Message):
    text = (
        "👋 **Salam! Mən Gizli Mesaj botuyam.**\n\n"
        "🛠 **İstifadə qaydası:**\n"
        "Hər hansı bir çatda mənim adımı yazın, ardınca **@username** (və ya ID) və **mesajı** qeyd edin.\n\n"
        "**Nümunə:**\n"
        "`@Xeyalbot @istifadeci salam`"
    )

    keyboard = [
        [
            types.InlineKeyboardButton(text="🧑‍💻 Developer", type=types.InlineKeyboardButtonTypeUrl("https://t.me/kullaniciadidi")),
            types.InlineKeyboardButton(text="📢Bildiriş kanalı", type=types.InlineKeyboardButtonTypeUrl("https://t.me/Ht_bots"))
        ],
        [
            types.InlineKeyboardButton(text="🆘 Kömək qrupu", type=types.InlineKeyboardButtonTypeUrl("https://t.me/ht_bots_chat"))
        ]
    ]

    await m.reply_text(
        text, 
        parse_mode="markdown", 
        reply_markup=types.ReplyMarkupInlineKeyboard(keyboard)
    )

bot.run()
