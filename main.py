# --- BOTUN TƏYİNİ ---
bot = Client("session_name", api_id=API_ID, api_hash="API_HASH", bot_token="TOKEN")

# --- INLINE HANDLER ---
@bot.on_inline_query()  # Dəyişdirildi
async def secret_inline(c: Client, inline_query: types.InlineQuery):
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

# --- CALLBACK HANDLER ---
@bot.on_callback_query()  # Dəyişdirildi
async def read_secret(c: Client, cb: types.CallbackQuery):
    msg_id = cb.payload.data.decode().split("_")[1]
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

# --- START HANDLER ---
@bot.on_message()  # Dəyişdirildi
async def start(c: Client, m: types.Message):
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
                text="🆘 Kömək kanalı",
                type=types.InlineKeyboardButtonTypeUrl("https://t.me/ht_bots_chat")
            )
        ]
    ]

    await m.reply_text(
        text=text,
        parse_mode="markdown",
        reply_markup=types.ReplyMarkupInlineKeyboard(keyboard)
    )   
