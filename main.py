import uuid
from pyrogram import Client, types

# --- MƏLUMAT BAZASI (Müvəqqəti) ---
# Mesajları yadda saxlamaq üçün lazım olan funksiyalar
db = {}

def save_msg(msg_id, target, msg):
    db[msg_id] = {"to": target, "msg": msg}

def get_msg(msg_id):
    return db.get(msg_id)

# --- BOTUN TƏYİNİ ---
bot = Client(
    "session_name",
    api_id=34628590,
    api_hash="78a65ef180771575a50fcd350f027e9d",
    bot_token="8272572293:AAG3JFKyk4lX4cBosnZ6GYW8dbg1tvVyVew"
)

# --- INLINE HANDLER ---
@bot.on_inline_query()
async def secret_inline(c: Client, inline_query: types.InlineQuery):
    query = inline_query.query.strip()
    if " " not in query:
        return
    
    # Target və mesajı ayırırıq
    try:
        target, secret_text = query.split(" ", 1)
    except ValueError:
        return

    msg_id = str(uuid.uuid4())[:8]
    save_msg(msg_id, target, secret_text)

    results = [
        types.InputInlineQueryResultArticle(
            id=msg_id,
            title=f"🔒 Mesaj: {target}",
            description="Gizli göndərmək üçün toxunun",
            input_message_content=types.InputMessageText(
                text=f"🎁 {target}, sizin üçün gizli mesaj var!"
            ),
            reply_markup=types.InlineKeyboardMarkup([
                [types.InlineKeyboardButton(
                    text="👁 Mesajı Oxu",
                    callback_data=f"read_{msg_id}"
                )]
            ])
        )
    ]
    await c.answer_inline_query(inline_query.id, results, cache_time=1)

# --- CALLBACK HANDLER ---
@bot.on_callback_query()
async def read_secret(c: Client, cb: types.CallbackQuery):
    msg_id = cb.data.split("_")[1]
    data = get_msg(msg_id)
    
    if not data:
        return await cb.answer("❌ Mesaj tapılmadı.", show_alert=True)

    target = data["to"].replace("@", "").lower()
    user_id = str(cb.from_user.id)
    username = (cb.from_user.username or "").lower()
    
    # Yalnız hədəf şəxs oxuya bilsin
    if user_id == target or username == target:
        await cb.answer(f"🔒 Gizli Mesajınız:\n\n{data['msg']}", show_alert=True)
    else:
        await cb.answer(f"❌ Bu mesaj yalnız {data['to']} üçündür!", show_alert=True)

# --- START HANDLER ---
@bot.on_message(types.Filters.command("start"))
async def start(c: Client, m: types.Message):
    text = (
        "👋 **Salam! Mən Gizli Mesaj botuyam.**\n\n"
        "🛠 **İstifadə qaydası:**\n"
        "Inline rejimdə mənim adımı yazın, sonra **@username** və **mesaj**.\n\n"
        "**Nümunə:**\n"
        "`@BotAdı @istifadeci salam necəsən?`"
    )

    keyboard = [
        [
            types.InlineKeyboardButton("🧑‍💻 Developer", url="https://t.me/kullaniciadidi"),
            types.InlineKeyboardButton("📢 Məlumat kanalı", url="https://t.me/ht_bots")
        ],
        [
            types.InlineKeyboardButton("🆘 Kömək kanalı", url="https://t.me/ht_bots_chat")
        ]
    ]

    await m.reply_text(
        text=text,
        parse_mode="markdown",
        reply_markup=types.InlineKeyboardMarkup(keyboard)
    )

if __name__ == "__main__":
    bot.run()
    
