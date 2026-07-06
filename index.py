import json
import os
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, MessageHandler, filters, ContextTypes

# ==================== الإعدادات ====================
BOT_TOKEN = "8700905522:AAE30w5iFr8jmhIRf_eE0EpSAmk6j1lMfn8"
ADMIN_CHANNEL_ID = "-1004479419959"
ADMIN_ID = "8243108672"
ADMIN_PASSWORD = "T13AHA990POL"
DEVELOPER_USERNAME = "@MrXT1_3"

DB_FILE = 'database.json'

# ==================== قاعدة البيانات ====================
def load_db():
    try:
        with open(DB_FILE, 'r') as f:
            return json.load(f)
    except:
        return {
            "users": {},
            "banned": {},
            "muted": {},
            "exchange_rate": 14500,
            "orders": [],
            "custom_store": {
                "games": {
                    "🎮 ببجي موبايل": ["60 شدة - 1.20$", "325 شدة - 5.00$", "660 شدة - 10.00$", "1800 شدة - 25.00$"],
                    "🔥 فري فاير": ["100 دايموند - 2.00$", "200 دايموند - 4.00$", "400 دايموند - 7.00$"],
                    "🎮 روبلوكس": ["100 روبوكس - 1.50$", "500 روبوكس - 6.00$", "1000 روبوكس - 11.00$"]
                }
            }
        }

def save_db(data):
    with open(DB_FILE, 'w') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

# ==================== القوائم ====================
main_menu = ReplyKeyboardMarkup([
    ['🏪 المتجر'],
    ['💳 المحفظة', '💰 استرجاع الأموال'],
    ['⚙️ الإعدادات', '📞 الدعم الفني']
], resize_keyboard=True)

store_menu = InlineKeyboardMarkup([
    [InlineKeyboardButton("🎮 قسم الألعاب", callback_data="m#games")],
    [InlineKeyboardButton("🎟️ قسم البطاقات", callback_data="m#cards")],
    [InlineKeyboardButton("📱 شحن رصيد هاتف", callback_data="m#phone")],
    [InlineKeyboardButton("🤖 إنشاء بوت", callback_data="bot_order#start")],
    [InlineKeyboardButton("🔙 القائمة الرئيسية", callback_data="main_menu")]
])

# ==================== دوال المساعدة ====================
def get_user_balance(user_id):
    db = load_db()
    return db["users"].get(str(user_id), {}).get("balance_usd", 0)

def update_balance(user_id, amount):
    db = load_db()
    uid = str(user_id)
    if uid not in db["users"]:
        db["users"][uid] = {"name": "مستخدم", "balance_usd": 0}
    db["users"][uid]["balance_usd"] = db["users"][uid].get("balance_usd", 0) + amount
    save_db(db)

# ==================== الأوامر ====================
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = str(update.effective_user.id)
    db = load_db()
    if user_id not in db["users"]:
        db["users"][user_id] = {"name": update.effective_user.first_name, "balance_usd": 0}
        save_db(db)
    balance = db["users"][user_id]["balance_usd"]
    await update.message.reply_text(
        f"👑 أهلاً {update.effective_user.first_name}\n💰 رصيدك: ${balance}",
        reply_markup=main_menu
    )

async def admin_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['awaiting_password'] = True
    await update.message.reply_text("🔐 اكتب كلمة السر:")

async def panel_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = str(update.effective_user.id)
    if context.user_data.get('admin_dashboard') or user_id == ADMIN_ID:
        admin_panel = InlineKeyboardMarkup([
            [InlineKeyboardButton("📊 الإحصائيات", callback_data="adm#stats")],
            [InlineKeyboardButton("📢 إرسال إعلان", callback_data="adm#broadcast")],
            [InlineKeyboardButton("👥 المستخدمين", callback_data="adm#users")],
            [InlineKeyboardButton("🔙 القائمة الرئيسية", callback_data="main_menu")]
        ])
        await update.message.reply_text("🛸 لوحة التحكم", reply_markup=admin_panel)
    else:
        await update.message.reply_text("❌ ليس لديك صلاحية.")

async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = str(update.effective_user.id)
    text = update.message.text
    db = load_db()

    # ===== كلمة السر =====
    if context.user_data.get('awaiting_password'):
        if text == ADMIN_PASSWORD:
            context.user_data['admin_dashboard'] = True
            context.user_data['awaiting_password'] = False
            await update.message.reply_text("✅ تم التحقق! اكتب /panel.")
        else:
            context.user_data['awaiting_password'] = False
            await update.message.reply_text("❌ كلمة سر خاطئة!")
        return

    # ===== كتابة الآيدي =====
    if context.user_data.get('awaiting_game_id'):
        game_name = context.user_data.get('game_name')
        item = context.user_data.get('item')
        price = context.user_data.get('price')
        context.user_data['game_id'] = text
        context.user_data['action'] = 'confirmed'
        confirm_btn = InlineKeyboardMarkup([
            [InlineKeyboardButton("✔️ تأكيد الشراء", callback_data="confirm_order")]
        ])
        await update.message.reply_text(
            f"🎯 تأكيد الطلب\n🎁 {item}\n💰 ${price}\n🆔 {text}",
            reply_markup=confirm_btn
        )
        return

    # ===== شحن الرصيد =====
    if context.user_data.get('awaiting_charge'):
        try:
            amount = float(text)
            if amount <= 0:
                raise ValueError
            update_balance(user_id, amount)
            context.user_data['awaiting_charge'] = False
            await update.message.reply_text(f"✅ تم شحن ${amount} إلى محفظتك!")
        except:
            await update.message.reply_text("❌ اكتب رقماً صحيحاً!")
        return

# ==================== معالج الأزرار ====================
async def handle_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    data = query.data
    user_id = str(update.effective_user.id)
    db = load_db()

    # ===== أزرار الإدارة =====
    if data.startswith("adm#"):
        action = data.split('#')[1]
        if action == "stats":
            total_users = len(db["users"])
            total_balance = sum(u.get("balance_usd", 0) for u in db["users"].values())
            await query.edit_message_text(f"📊 الإحصائيات\n👥 {total_users}\n💰 ${total_balance:.2f}")
        elif action == "broadcast":
            context.user_data['broadcast'] = True
            await query.edit_message_text("✍️ اكتب الرسالة:")
        elif action == "users":
            users_list = "👥 المستخدمين:\n"
            for uid, info in list(db["users"].items())[:20]:
                users_list += f"{info.get('name', 'مجهول')} (${info.get('balance_usd', 0)})\n"
            await query.edit_message_text(users_list)
        return

    # ===== أزرار المتجر =====
    if data == "m#games":
        games = db["custom_store"]["games"]
        buttons = []
        for name in games:
            buttons.append([InlineKeyboardButton(name, callback_data=f"shop#{name}")])
        buttons.append([InlineKeyboardButton("🔙 القائمة الرئيسية", callback_data="main_menu")])
        await query.edit_message_text("🎮 اختر اللعبة:", reply_markup=InlineKeyboardMarkup(buttons))

    elif data.startswith("shop#"):
        game_name = data.split('#')[1]
        items = db["custom_store"]["games"].get(game_name, [])
        if not items:
            await query.edit_message_text("⚠️ لا توجد عروض!")
            return
        buttons = []
        for item in items:
            price = float(item.split('-')[1].replace('$', ''))
            buttons.append([InlineKeyboardButton(item, callback_data=f"buy#{game_name}#{item}#{price}")])
        buttons.append([InlineKeyboardButton("🔙 رجوع", callback_data="m#games")])
        buttons.append([InlineKeyboardButton("🔙 القائمة الرئيسية", callback_data="main_menu")])
        await query.edit_message_text(f"🛒 عروض {game_name}", reply_markup=InlineKeyboardMarkup(buttons))

    elif data.startswith("buy#"):
        parts = data.split('#')
        game_name = parts[1]
        item = parts[2]
        price = float(parts[3])
        balance = get_user_balance(user_id)
        if balance < price:
            await query.edit_message_text(f"❌ رصيدك (${balance}) لا يكفي!")
            return
        context.user_data['game_name'] = game_name
        context.user_data['item'] = item
        context.user_data['price'] = price
        context.user_data['awaiting_game_id'] = True
        await query.edit_message_text("✍️ اكتب الآيدي (ID):")

    elif data == "confirm_order":
        if context.user_data.get('action') != 'confirmed':
            await query.edit_message_text("❌ لا يوجد طلب مؤكد.")
            return
        game_name = context.user_data.get('game_name')
        item = context.user_data.get('item')
        price = context.user_data.get('price')
        user_balance = get_user_balance(user_id)
        if user_balance < price:
            await query.edit_message_text(f"❌ رصيدك غير كافٍ!")
            return
        update_balance(user_id, -price)
        context.user_data['awaiting_game_id'] = False
        context.user_data['action'] = None
        await query.edit_message_text(f"✅ تم الشراء!\n🎁 {item}\n💰 ${price}")
        await context.bot.send_message(
            ADMIN_CHANNEL_ID,
            f"🛒 طلب شراء\n👤 {update.effective_user.first_name}\n🎁 {item}\n💰 ${price}"
        )

    elif data == "main_menu":
        await query.edit_message_text("🎯 القائمة الرئيسية", reply_markup=main_menu)

    else:
        await query.edit_message_text("⚠️ هذا الزر غير مفعل حالياً.")

# ==================== التشغيل ====================
def main():
    app = Application.builder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("admin", admin_command))
    app.add_handler(CommandHandler("panel", panel_command))
    app.add_handler(CallbackQueryHandler(handle_callback))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text))

    print("🚀 البوت شغال بالبايثون!")
    app.run_polling()

if __name__ == "__main__":
    main()
