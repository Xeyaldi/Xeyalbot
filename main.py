import uuid
from pyrogram import Client, filters, types

# --- MƏLUMAT BAZASI ---
db = {}

def save_msg(msg_id, sender_id, target, msg):
    # Kimin göndərdiyini (sender_id) də artıq saxlayırıq
    db[msg_id] = {"from": sender_id, "to": target, "msg": msg, "read": False}

bot = Client(
    "bot_session",
    api_id=34628590,
    api_hash="78a65ef180771575a50fcd350f027e9d",
    bot_token="8272572293:AAG3JFKyk4lX4cBosnZ6GYW8dbg1tvVyVew"
)

# --- INLINE HANDLER ---
@bot.on_inline_query()
async def secret_inline(c: Client, inline_query: types.InlineQuery):
    query = inline_query.query.strip()
    if not query:
        return

    # "Anyone" (hər kəsə) məntiqi: Əgər boşluq yoxdursa, hər kəs üçün sayılır
    if " " in query:
        target, secret_text = query.split(" ", 1)
    else:
        target = "anyone"
        secret_text = query

    msg_id = str(uuid.uuid4())[:8]
    save_msg(msg_id, inline_query.from_user.id, target, secret_text)

    # Başlıq hər kəsə və ya şəxsə görə dəyişir
    title_text = "🔒 Hər kəs üçün gizli mesaj" if target == "anyone" else f"🔒 Mesaj: {target}"
    msg_text = "🎁 Sizin üçün gizli mesaj var!" if target == "anyone" else f"🎁 {target}, sizin üçün gizli mesaj var!"

    results = [
        types.InlineQueryResultArticle(
            id=msg_id,
            title=title_text,
            description="Gizli göndərmək üçün toxunun",
            input_message_content=types.InputTextMessageContent(message_text=msg_text),
            reply_markup=types.InlineKeyboardMarkup([
                [types.InlineKeyboardButton(text="👁 Mesajı Oxu", callback_data=f"read_{msg_id}")]
            ])
        )
    ]
    await c.answer_inline_query(inline_query.id, results, cache_time=1)

# --- CALLBACK HANDLER ---
@bot.on_callback_query()
async def read_secret(c: Client, cb: types.CallbackQuery):
    if not cb.data.startswith("read_"):
        return

    msg_id = cb.data.split("_")[1]
    data = db.get(msg_id)
    
    if not data:
        return await cb.answer("❌ Mesaj tapılmadı.", show_alert=True)

    sender_id = data["from"]
    target = data["to"].replace("@", "").lower()
    user_id = cb.from_user.id
    username = (cb.from_user.username or "").lower()

    # OKUMA ŞƏRTİ: Hər kəsədirsə YA DA yazan adamdırsa YA DA hədəf şəxsdirsə
    if data["to"] == "anyone" or user_id == sender_id or str(user_id) == target or username == target:
        await cb.answer(f"🔒 Gizli Mesajınız:\n\n{data['msg']}", show_alert=True)
        
        # Əgər hədəf oxudusa, mətni "Oxundu" olaraq dəyişək
        if user_id != sender_id and not data["read"]:
            data["read"] = True
            try:
                await cb.edit_message_text(
                    f"✅ {cb.from_user.first_name} mesajı oxudu.",
                    reply_markup=None
                )
            except:
                pass
    else:
        await cb.answer(f"❌ Bu mesaj yalnız {data['to']} üçündür!", show_alert=True)

# --- START HANDLER ---
@bot.on_message(filters.command("start"))
async def start(c: Client, m: types.Message):
    # Sənin əvvəlki düymələrin və mətnin olduğu kimi qaldı
    text = (
        "👋 **Salam! Mən Gizli Mesaj botuyam.**\n\n"
        "🛠 **İstifadə qaydası:**\n"
        "Inline rejimdə mənim adımı yazın, sonra **@username** və **mesaj**.\n\n"
        "**Nümunə:**\n"
        "`@botun_adi @istifadeci salam necəsən?`"
    )

    keyboard = [
        [
            types.InlineKeyboardButton("🧑‍💻 Botun sahibi", url="https://t.me/kullaniciadidi"),
            types.InlineKeyboardButton("📢 Məlumat kanalı", url="https://t.me/ht_bots")
        ],
        [
            types.InlineKeyboardButton("🆘 Kömək qrupu", url="https://t.me/ht_bots_chat")
        ]
    ]

    await m.reply_text(text=text, reply_markup=types.InlineKeyboardMarkup(keyboard))

bot.run()
