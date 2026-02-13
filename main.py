import uuid
from pyrogram import Client, filters, types

db = {}

def save_msg(msg_id, sender_id, target, msg):
    # Göndərənin ID-sini də bazada saxlayırıq ki, o da oxuya bilsin
    db[msg_id] = {"from": sender_id, "to": target, "msg": msg, "read": False}

bot = Client(
    "bot_session",
    api_id=34628590,
    api_hash="78a65ef180771575a50fcd350f027e9d",
    bot_token="8272572293:AAG3JFKyk4lX4cBosnZ6GYW8dbg1tvVyVew"
)

@bot.on_inline_query()
async def secret_inline(c: Client, inline_query: types.InlineQuery):
    query = inline_query.query.strip()
    if not query:
        return

    # Əgər boşluq yoxdursa, hər kəs üçün (anyone) mesaj kimi qəbul edirik
    if " " in query:
        target, secret_text = query.split(" ", 1)
    else:
        target = "anyone"
        secret_text = query

    msg_id = str(uuid.uuid4())[:8]
    save_msg(msg_id, inline_query.from_user.id, target, secret_text)

    title = "🔒 Hər kəs üçün gizli mesaj" if target == "anyone" else f"🔒 Mesaj: {target}"
    
    results = [
        types.InlineQueryResultArticle(
            id=msg_id,
            title=title,
            description="Göndərmək üçün toxunun",
            input_message_content=types.InputTextMessageContent(
                message_text=f"🎁 Sizin üçün gizli mesaj var!" if target == "anyone" else f"🎁 {target}, sizin üçün gizli mesaj var!"
            ),
            reply_markup=types.InlineKeyboardMarkup([
                [types.InlineKeyboardButton(text="👁 Mesajı Oxu", callback_data=f"read_{msg_id}")]
            ])
        )
    ]
    await c.answer_inline_query(inline_query.id, results, cache_time=1)

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

    # Məntiq: Əgər hər kəsədirsə, YA mesajı yazandırsa, YA DA hədəf istifadəçidirsə oxuya bilsin
    if data["to"] == "anyone" or user_id == sender_id or str(user_id) == target or username == target:
        await cb.answer(f"🔒 Gizli Mesaj:\n\n{data['msg']}", show_alert=True)
        
        # Əgər mesajı yazan yox, başqası (hədəf) oxuyubsa "Oxundu" işarəsi qoyaq
        if user_id != sender_id and not data["read"]:
            data["read"] = True
            await cb.edit_message_text(
                f"✅ {cb.from_user.first_name} mesajı oxudu.",
                reply_markup=None # Düyməni yox edirik (istəsən saxlaya da bilərsən)
            )
    else:
        await cb.answer(f"❌ Bu mesaj yalnız {data['to']} üçündür!", show_alert=True)

@bot.on_message(filters.command("start"))
async def start(c: Client, m: types.Message):
    await m.reply_text("👋 Salam! Məni çatda `@botun_adı mesaj` və ya `@botun_adı @user mesaj` kimi işlət.")

bot.run()
