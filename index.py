import json
import os
import logging
from datetime import datetime
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, MessageHandler, filters, ContextTypes

# ==================== إعدادات البوت ====================
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
            "admin_notes": "",
            "bot_maintenance": False,
            "orders": [],
            "bot_orders": [],
            "installments": [],
            "products": [],
            "custom_store": {
                "games": {
                    "🎮 ببجي موبايل": ["60 شدة - 1.20$", "325 شدة - 5.00$", "660 شدة - 10.00$", "1800 شدة - 25.00$"],
                    "🔥 فري فاير": ["100 دايموند - 2.00$", "200 دايموند - 4.00$", "400 دايموند - 7.00$"],
                    "🎮 روبلوكس": ["100 روبوكس - 1.50$", "500 روبوكس - 6.00$", "1000 روبوكس - 11.00$"],
                    "🎮 كود فري فاير": ["كود 5$ - 5.00$", "كود 10$ - 10.00$"],
                    "🎮 ماين كرافت": ["1720 كوين - 10.00$", "3500 كوين - 20.00$"]
                },
                "cards": {
                    "🎟️ بطاقات ستيم": ["فئة 5$ - 5.50$", "فئة 10$ - 11.00$"],
                    "🎟️ بطاقات إكس بوكس": ["فئة 10$ - 10.50$", "فئة 25$ - 26.00$"]
                }
            }
        }

def save_db(data):
    with open(DB_FILE, 'w') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

def get_balance(user_id):
    db = load_db()
    return db["users"].get(str(user_id), {}).get("balance_usd", 0)

def update_balance(user_id, amount):
    db = load_db()
    uid = str(user_id)
    if uid not in db["users"]:
        db["users"][uid] = {"name": "مستخدم", "balance_usd": 0, "joined": datetime.now().isoformat()}
    db["users"][uid]["balance_usd"] = db["users"][uid].get("balance_usd", 0) + amount
    save_db(db)

# ==================== القوائم ====================
main_menu = ReplyKeyboardMarkup([
    ['🏪 المتجر', '🤖 إنشاء بوت'],
    ['💳 المحفظة', '💰 استرجاع الأموال'],
    ['⚙️ الإعدادات', '📞 الدعم الفني']
], resize_keyboard=True)

store_menu = InlineKeyboardMarkup([
    [InlineKeyboardButton("🎮 قسم الألعاب", callback_data="store#games")],
    [InlineKeyboardButton("🎟️ قسم البطاقات", callback_data="store#cards")],
    [InlineKeyboardButton("📱 شحن رصيد هاتف", callback_data="store#phone")],
    [InlineKeyboardButton("🔙 القائمة الرئيسية", callback_data="main_menu")]
])

games_menu = InlineKeyboardMarkup([
    [InlineKeyboardButton("🎮 ببجي موبايل", callback_data="game#🎮 ببجي موبايل")],
    [InlineKeyboardButton("🔥 فري فاير", callback_data="game#🔥 فري فاير")],
    [InlineKeyboardButton("🎮 روبلوكس", callback_data="game#🎮 روبلوكس")],
    [InlineKeyboardButton("🎮 كود فري فاير", callback_data="game#🎮 كود فري فاير")],
    [InlineKeyboardButton("🎮 ماين كرافت", callback_data="game#🎮 ماين كرافت")],
    [InlineKeyboardButton("🔙 رجوع للمتجر", callback_data="store#back")],
    [InlineKeyboardButton("🔙 القائمة الرئيسية", callback_data="main_menu")]
])

cards_menu = InlineKeyboardMarkup([
    [InlineKeyboardButton("🎟️ بطاقات ستيم", callback_data="card#ستيم")],
    [InlineKeyboardButton("🎟️ بطاقات إكس بوكس", callback_data="card#إكس بوكس")],
    [InlineKeyboardButton("🔙 رجوع للمتجر", callback_data="store#back")],
    [InlineKeyboardButton("🔙 القائمة الرئيسية", callback_data="main_menu")]
])

phone_menu = InlineKeyboardMarkup([
    [InlineKeyboardButton("📱 سيريتل", callback_data="phone#syr")],
    [InlineKeyboardButton("📱 إم تي إن", callback_data="phone#mtn")],
    [InlineKeyboardButton("🔙 رجوع للمتجر", callback_data="store#back")],
    [InlineKeyboardButton("🔙 القائمة الرئيسية", callback_data="main_menu")]
])

wallet_menu = InlineKeyboardMarkup([
    [InlineKeyboardButton("💵 شحن بالدولار", callback_data="charge#usd")],
    [InlineKeyboardButton("🇸🇾 شحن بالليرة", callback_data="charge#syr")],
    [InlineKeyboardButton("🔙 القائمة الرئيسية", callback_data="main_menu")]
])

refund_menu = InlineKeyboardMarkup([
    [InlineKeyboardButton("💵 استرجاع بالدولار", callback_data="refund#usd")],
    [InlineKeyboardButton("🇸🇾 استرجاع بالليرة", callback_data="refund#syr")],
    [InlineKeyboardButton("🔙 القائمة الرئيسية", callback_data="main_menu")]
])

admin_panel = InlineKeyboardMarkup([
    [InlineKeyboardButton("📊 الإحصائيات", callback_data="adm#stats")],
    [InlineKeyboardButton("📢 إرسال إعلان", callback_data="adm#broadcast")],
    [InlineKeyboardButton("💰 إدارة المحفظة", callback_data="adm#wallet")],
    [InlineKeyboardButton("👥 المستخدمين", callback_data="adm#users")],
    [InlineKeyboardButton("🛒 إدارة المتجر", callback_data="adm#store")],
    [InlineKeyboardButton("📱 طلبات الشحن", callback_data="adm#charge_orders")],
    [InlineKeyboardButton("🤖 طلبات البوتات", callback_data="adm#bot_orders")],
    [InlineKeyboardButton("💰 طلبات الاسترجاع", callback_data="adm#refund_orders")],
    [InlineKeyboardButton("⚙️ الإعدادات", callback_data="adm#settings")],
    [InlineKeyboardButton("🗑️ تنظيف البيانات", callback_data="adm#clean")],
    [InlineKeyboardButton("💾 نسخة احتياطية", callback_data="adm#backup")],
    [InlineKeyboardButton("🔙 القائمة الرئيسية", callback_data="main_menu")]
])

# ==================== أوامر البوت ====================
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = str(update.effective_user.id)
    db = load_db()
    if user_id not in db["users"]:
        db["users"][user_id] = {
            "name": update.effective_user.first_name,
            "balance_usd": 0,
            "joined": datetime.now().isoformat()
        }
        save_db(db)
    balance = db["users"][user_id]["balance_usd"]
    rate = db.get("exchange_rate", 14500)
    await update.message.reply_text(
        f"👑 **بوت شام إن جيم** 👑\n"
        f"━━━━━━━━━━━━━━━━━━━━\n"
        f"👤 مرحباً: {update.effective_user.first_name}\n"
        f"💰 رصيدك: ${balance:.2f}\n"
        f"🇸🇾 بالليرة: {balance * rate:,.0f} ل.س\n"
        f"📈 سعر الصرف: 1$ = {rate:,} ل.س\n"
        f"━━━━━━━━━━━━━━━━━━━━\n"
        f"⚠️ استخدم الأزرار للتنقل ❤️",
        reply_markup=main_menu,
        parse_mode='Markdown'
    )

async def admin_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['awaiting_password'] = True
    await update.message.reply_text("🔐 اكتب كلمة السر للتحقق:")

async def panel_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = str(update.effective_user.id)
    if context.user_data.get('admin_dashboard') or user_id == ADMIN_ID:
        await update.message.reply_text("🛸 **لوحة التحكم الإدارية**", reply_markup=admin_panel, parse_mode='Markdown')
    else:
        await update.message.reply_text("❌ ليس لديك صلاحية للدخول.")

# ==================== معالج النصوص ====================
async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = str(update.effective_user.id)
    text = update.message.text
    db = load_db()

    # ===== أزرار القائمة الرئيسية =====
    if text == '🏪 المتجر':
        await update.message.reply_text("🛍️ اختر القسم:", reply_markup=store_menu)
        return

    if text == '💳 المحفظة':
        balance = get_balance(user_id)
        await update.message.reply_text(f"💳 **رصيدك الحالي:**\n💰 ${balance:.2f}", reply_markup=wallet_menu, parse_mode='Markdown')
        return

    if text == '💰 استرجاع الأموال':
        await update.message.reply_text("💰 اختر عملة الاسترجاع:", reply_markup=refund_menu)
        return

    if text == '🤖 إنشاء بوت':
        context.user_data['awaiting_bot_desc'] = True
        await update.message.reply_text("🤖 اكتب مواصفات البوت الذي تريده:")
        return

    if text == '⚙️ الإعدادات':
        await update.message.reply_text(f"⚙️ **الإعدادات**\n👤 {update.effective_user.first_name}\n🆔 `{user_id}`", parse_mode='Markdown')
        return

    if text == '📞 الدعم الفني':
        await update.message.reply_text(f"📞 **الدعم الفني**\n{DEVELOPER_USERNAME}", parse_mode='Markdown')
        return

    # ===== كلمة السر =====
    if context.user_data.get('awaiting_password'):
        if text == ADMIN_PASSWORD:
            context.user_data['admin_dashboard'] = True
            context.user_data['awaiting_password'] = False
            await update.message.reply_text("✅ تم التحقق! استخدم /panel للوحة التحكم.")
        else:
            context.user_data['awaiting_password'] = False
            await update.message.reply_text("❌ كلمة سر خاطئة!")
        return

    # ===== إضافة رصيد (أدمن) =====
    if context.user_data.get('awaiting_add_balance'):
        try:
            parts = text.split('|')
            if len(parts) != 2:
                raise ValueError
            target_id = parts[0].strip()
            amount = float(parts[1].strip())
            if amount <= 0:
                raise ValueError
            if target_id not in db["users"]:
                await update.message.reply_text("❌ المستخدم غير موجود!")
                return
            db["users"][target_id]["balance_usd"] = db["users"][target_id].get("balance_usd", 0) + amount
            save_db(db)
            context.user_data['awaiting_add_balance'] = False
            await update.message.reply_text(f"✅ تم إضافة ${amount} إلى {db['users'][target_id]['name']}")
            await context.bot.send_message(target_id, f"🎉 تم إضافة ${amount} إلى محفظتك!")
        except:
            await update.message.reply_text("❌ الصيغة غير صحيحة! استخدم: `آيدي|المبلغ`")
        return

    # ===== شحن الرصيد =====
    if context.user_data.get('awaiting_charge'):
        try:
            amount = float(text)
            if amount <= 0:
                raise ValueError
            currency = context.user_data.get('charge_currency', 'usd')
            if currency == 'syr':
                rate = db.get('exchange_rate', 14500)
                amount = amount / rate
            update_balance(user_id, amount)
            context.user_data['awaiting_charge'] = False
            await update.message.reply_text(f"✅ تم شحن ${amount:.2f} إلى محفظتك!")
        except:
            await update.message.reply_text("❌ اكتب رقماً صحيحاً!")
        return

    # ===== استرجاع الأموال =====
    if context.user_data.get('awaiting_refund'):
        try:
            amount = float(text)
            if amount <= 0:
                raise ValueError
            currency = context.user_data.get('refund_currency', 'usd')
            if currency == 'syr':
                rate = db.get('exchange_rate', 14500)
                amount = amount / rate
            balance = get_balance(user_id)
            if balance < amount:
                await update.message.reply_text(f"❌ رصيدك (${balance:.2f}) غير كافٍ!")
                return
            # إرسال طلب للأدمن
            await context.bot.send_message(
                ADMIN_CHANNEL_ID,
                f"💰 **طلب استرجاع أموال**\n"
                f"━━━━━━━━━━━━━━━━━━━━\n"
                f"👤 الزبون: {update.effective_user.first_name}\n"
                f"🆔 المعرف: {user_id}\n"
                f"💵 المبلغ: ${amount:.2f}\n"
                f"📅 التاريخ: {datetime.now().strftime('%Y-%m-%d %H:%M')}",
                reply_markup=InlineKeyboardMarkup([
                    [InlineKeyboardButton("✅ موافقة", callback_data=f"refund_accept#{user_id}#{amount}")],
                    [InlineKeyboardButton("❌ رفض", callback_data=f"refund_reject#{user_id}")]
                ])
            )
            await update.message.reply_text("✅ تم إرسال طلب الاسترجاع للإدارة، في انتظار الموافقة.")
            context.user_data['awaiting_refund'] = False
        except:
            await update.message.reply_text("❌ اكتب رقماً صحيحاً!")
        return

    # ===== كتابة الآيدي (الشراء) =====
    if context.user_data.get('awaiting_game_id'):
        context.user_data['game_id'] = text
        context.user_data['action'] = 'confirmed'
        item = context.user_data.get('item')
        price = context.user_data.get('price')
        game_name = context.user_data.get('game_name')
        # إرسال طلب للأدمن
        await context.bot.send_message(
            ADMIN_CHANNEL_ID,
            f"🛒 **طلب شراء جديد**\n"
            f"━━━━━━━━━━━━━━━━━━━━\n"
            f"👤 الزبون: {update.effective_user.first_name}\n"
            f"🆔 المعرف: {user_id}\n"
            f"🎁 المنتج: {item}\n"
            f"💰 السعر: ${price:.2f}\n"
            f"🆔 الآيدي: {text}\n"
            f"📅 التاريخ: {datetime.now().strftime('%Y-%m-%d %H:%M')}",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("✅ موافقة وخصم", callback_data=f"order_accept#{user_id}#{price}#{item}#{text}")],
                [InlineKeyboardButton("❌ رفض", callback_data=f"order_reject#{user_id}")]
            ])
        )
        await update.message.reply_text("✅ تم إرسال طلبك للإدارة، في انتظار الموافقة.")
        context.user_data['awaiting_game_id'] = False
        return

    # ===== طلب بوت (من الأدمن) =====
    if context.user_data.get('awaiting_bot_price'):
        target_id = context.user_data.get('bot_target_id')
        if target_id:
            await context.bot.send_message(target_id, f"💰 **السعر المتفق عليه:** {text}")
            await update.message.reply_text(f"✅ تم إرسال السعر إلى المستخدم {target_id}")
        context.user_data['awaiting_bot_price'] = False
        return

    if context.user_data.get('awaiting_bot_desc_admin'):
        target_id = context.user_data.get('bot_target_id')
        if target_id:
            await context.bot.send_message(target_id, f"📝 **وصف إضافي:** {text}")
            await update.message.reply_text(f"✅ تم إرسال الوصف إلى المستخدم {target_id}")
        context.user_data['awaiting_bot_desc_admin'] = False
        return

    if context.user_data.get('awaiting_bot_time'):
        target_id = context.user_data.get('bot_target_id')
        if target_id:
            await context.bot.send_message(target_id, f"⏰ **الوقت المتوقع:** {text}")
            await update.message.reply_text(f"✅ تم إرسال الوقت إلى المستخدم {target_id}")
        context.user_data['awaiting_bot_time'] = False
        return

    await update.message.reply_text("⚠️ لم أفهم طلبك، استخدم الأزرار من القائمة.")

# ==================== معالج الأزرار ====================
async def handle_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    data = query.data
    user_id = str(update.effective_user.id)
    db = load_db()

    # ============================================================
    # ==================== أزرار الإدارة ========================
    # ============================================================
    if data.startswith("adm#"):
        action = data.split('#')[1]

        if action == "stats":
            total_users = len(db["users"])
            total_balance = sum(u.get("balance_usd", 0) for u in db["users"].values())
            await query.edit_message_text(
                f"📊 **الإحصائيات**\n"
                f"━━━━━━━━━━━━━━━━━━━━\n"
                f"👥 المستخدمين: {total_users}\n"
                f"💰 إجمالي الرصيد: ${total_balance:.2f}",
                parse_mode='Markdown'
            )
            return

        if action == "broadcast":
            context.user_data['awaiting_broadcast'] = True
            await query.edit_message_text("✍️ اكتب الرسالة:")
            return

        if action == "wallet":
            await query.edit_message_text(
                "💰 **إدارة المحفظة**",
                reply_markup=InlineKeyboardMarkup([
                    [InlineKeyboardButton("➕ إضافة رصيد", callback_data="adm#add_balance")],
                    [InlineKeyboardButton("📊 عرض الأرصدة", callback_data="adm#view_balances")],
                    [InlineKeyboardButton("🔙 رجوع", callback_data="adm#back")]
                ])
            )
            return

        if action == "add_balance":
            context.user_data['awaiting_add_balance'] = True
            await query.edit_message_text("✍️ اكتب: `آيدي|المبلغ`")
            return

        if action == "view_balances":
            users_list = "💰 **الأرصدة**\n━━━━━━━━━━━━━━━━━━━━\n"
            for uid, info in list(db["users"].items())[:20]:
                users_list += f"👤 {info.get('name', 'مجهول')} (${info.get('balance_usd', 0):.2f})\n"
            await query.edit_message_text(users_list, parse_mode='Markdown')
            return

        if action == "users":
            users_list = "👥 **المستخدمين**\n━━━━━━━━━━━━━━━━━━━━\n"
            for uid, info in list(db["users"].items())[:20]:
                users_list += f"{uid}. {info.get('name', 'مجهول')} - ${info.get('balance_usd', 0):.2f}\n"
            await query.edit_message_text(users_list, parse_mode='Markdown')
            return

        if action == "store":
            games = db["custom_store"]["games"]
            cards = db["custom_store"]["cards"]
            store_info = "🛒 **إدارة المتجر**\n━━━━━━━━━━━━━━━━━━━━\n"
            store_info += "🎮 **الألعاب:**\n"
            for name in games:
                store_info += f"  📂 {name} ({len(games[name])} منتج)\n"
            store_info += "\n🎟️ **البطاقات:**\n"
            for name in cards:
                store_info += f"  📂 {name} ({len(cards[name])} منتج)\n"
            await query.edit_message_text(store_info, parse_mode='Markdown')
            return

        if action == "charge_orders":
            await query.edit_message_text("📱 **طلبات الشحن**\nقيد التطوير...")
            return

        if action == "bot_orders":
            await query.edit_message_text("🤖 **طلبات البوتات**\nقيد التطوير...")
            return

        if action == "refund_orders":
            await query.edit_message_text("💰 **طلبات الاسترجاع**\nقيد التطوير...")
            return

        if action == "settings":
            rate = db.get('exchange_rate', 14500)
            maintenance = "🛑 معطل" if db.get('bot_maintenance', False) else "✅ شغال"
            await query.edit_message_text(
                f"⚙️ **الإعدادات**\n"
                f"━━━━━━━━━━━━━━━━━━━━\n"
                f"📈 سعر الصرف: 1$ = {rate:,} ل.س\n"
                f"⚙️ حالة البوت: {maintenance}",
                parse_mode='Markdown'
            )
            return

        if action == "clean":
            db["orders"] = []
            save_db(db)
            await query.edit_message_text("🧹 تم التنظيف.")
            return

        if action == "backup":
            backup_data = json.dumps(db, indent=2, ensure_ascii=False)
            await query.edit_message_text("💾 تم إنشاء نسخة احتياطية.")
            await context.bot.send_document(
                chat_id=user_id,
                document=('database_backup.json', backup_data.encode('utf-8')),
                caption="📂 نسخة احتياطية"
            )
            return

        if action == "back":
            await query.edit_message_text("🛸 **لوحة التحكم**", reply_markup=admin_panel)
            return

        return

    # ============================================================
    # ==================== أزرار المتجر ========================
    # ============================================================
    if data == "store#games":
        await query.edit_message_text("🎮 **اختر اللعبة:**", reply_markup=games_menu)
        return

    if data == "store#cards":
        await query.edit_message_text("🎟️ **اختر البطاقة:**", reply_markup=cards_menu)
        return

    if data == "store#phone":
        await query.edit_message_text("📱 **اختر شبكة الهاتف:**", reply_markup=phone_menu)
        return

    if data == "store#back":
        await query.edit_message_text("🛍️ **اختر القسم:**", reply_markup=store_menu)
        return

    # ============================================================
    # ==================== أزرار الألعاب ========================
    # ============================================================
    if data.startswith("game#"):
        game_name = data.split('#')[1]
        items = db["custom_store"]["games"].get(game_name, [])
        if not items:
            await query.edit_message_text("⚠️ لا توجد عروض!")
            return
        buttons = []
        for item in items:
            price = float(item.split('-')[1].replace('$', ''))
            buttons.append([InlineKeyboardButton(item, callback_data=f"buy#game#{game_name}#{item}#{price}")])
        buttons.append([InlineKeyboardButton("🔙 رجوع للألعاب", callback_data="store#games")])
        buttons.append([InlineKeyboardButton("🔙 القائمة الرئيسية", callback_data="main_menu")])
        await query.edit_message_text(f"🛒 **عروض {game_name}**", reply_markup=InlineKeyboardMarkup(buttons))
        return

    # ============================================================
    # ==================== أزرار البطاقات =======================
    # ============================================================
    if data.startswith("card#"):
        card_name = data.split('#')[1]
        full_name = f"🎟️ بطاقات {card_name}"
        items = db["custom_store"]["cards"].get(full_name, [])
        if not items:
            await query.edit_message_text("⚠️ لا توجد عروض!")
            return
        buttons = []
        for item in items:
            price = float(item.split('-')[1].replace('$', ''))
            buttons.append([InlineKeyboardButton(item, callback_data=f"buy#card#{card_name}#{item}#{price}")])
        buttons.append([InlineKeyboardButton("🔙 رجوع للبطاقات", callback_data="store#cards")])
        buttons.append([InlineKeyboardButton("🔙 القائمة الرئيسية", callback_data="main_menu")])
        await query.edit_message_text(f"🛒 **عروض بطاقات {card_name}**", reply_markup=InlineKeyboardMarkup(buttons))
        return

    # ============================================================
    # ==================== عملية الشراء ========================
    # ============================================================
    if data.startswith("buy#"):
        parts = data.split('#')
        item_type = parts[1]
        game_name = parts[2]
        item = parts[3]
        price = float(parts[4])
        balance = get_balance(user_id)
        if balance < price:
            await query.edit_message_text(f"❌ رصيدك (${balance:.2f}) لا يكفي!")
            return
        context.user_data['item_type'] = item_type
        context.user_data['game_name'] = game_name
        context.user_data['item'] = item
        context.user_data['price'] = price
        context.user_data['awaiting_game_id'] = True
        await query.edit_message_text("✍️ **أدخل الآيدي (ID) الخاص بك:**")
        return

    # ============================================================
    # ==================== موافقة الأدمن على الشراء ============
    # ============================================================
    if data.startswith("order_accept"):
        parts = data.split('#')
        target_id = parts[1]
        price = float(parts[2])
        item = parts[3]
        game_id = parts[4]
        balance = get_balance(target_id)
        if balance < price:
            await query.edit_message_text(f"❌ رصيد المستخدم غير كافٍ!")
            return
        update_balance(target_id, -price)
        await query.edit_message_text(f"✅ تم قبول الطلب وخصم ${price:.2f} من {target_id}")
        await context.bot.send_message(
            target_id,
            f"✅ **تم قبول طلبك!**\n"
            f"━━━━━━━━━━━━━━━━━━━━\n"
            f"🎁 المنتج: {item}\n"
            f"💰 المبلغ: ${price:.2f}\n"
            f"🆔 الآيدي: {game_id}\n"
            f"━━━━━━━━━━━━━━━━━━━━\n"
            f"📦 **تعليمات الاسترداد:**\n"
            f"1️⃣ اذهب إلى موقع midasbuy.com\n"
            f"2️⃣ أدخل الآيدي والكود\n"
            f"3️⃣ اضغط استرداد"
        )
        return

    if data.startswith("order_reject"):
        target_id = data.split('#')[1]
        await query.edit_message_text(f"❌ تم رفض الطلب")
        await context.bot.send_message(target_id, "❌ عذراً، تم رفض طلبك.")
        return

    # ============================================================
    # ==================== موافقة الأدمن على الاسترجاع =========
    # ============================================================
    if data.startswith("refund_accept"):
        parts = data.split('#')
        target_id = parts[1]
        amount = float(parts[2])
        update_balance(target_id, amount)
        await query.edit_message_text(f"✅ تم قبول الاسترجاع وإضافة ${amount:.2f} إلى {target_id}")
        await context.bot.send_message(target_id, f"✅ تم استرجاع ${amount:.2f} إلى محفظتك!")
        return

    if data.startswith("refund_reject"):
        target_id = data.split('#')[1]
        await query.edit_message_text(f"❌ تم رفض طلب الاسترجاع")
        await context.bot.send_message(target_id, "❌ عذراً، تم رفض طلب استرجاع الأموال.")
        return

    # ============================================================
    # ==================== شحن رصيد الهاتف ====================
    # ============================================================
    if data.startswith("phone#"):
        card_type = data.split('#')[1]
        context.user_data['card_type'] = card_type.upper()
        context.user_data['awaiting_phone'] = True
        await query.edit_message_text(f"✍️ **أدخل رقم الهاتف**\nالرجاء كتابة رقم الهاتف المراد شحنه ({card_type.upper()}):")
        return

    if context.user_data.get('awaiting_phone'):
        phone = update.message.text
        context.user_data['phone_number'] = phone
        context.user_data['awaiting_phone'] = False
        context.user_data['awaiting_phone_amount'] = True
        await update.message.reply_text("✍️ اكتب المبلغ بالليرة:")
        return

    if context.user_data.get('awaiting_phone_amount'):
        try:
            amount = float(update.message.text)
            if amount <= 0:
                raise ValueError
            rate = db.get('exchange_rate', 14500)
            usd_amount = amount / rate
            balance = get_balance(user_id)
            if balance < usd_amount:
                await update.message.reply_text(f"❌ رصيدك (${balance:.2f}) غير كافٍ!")
                return
            # إرسال طلب للأدمن
            await context.bot.send_message(
                ADMIN_CHANNEL_ID,
                f"📱 **طلب شحن هاتف**\n"
                f"━━━━━━━━━━━━━━━━━━━━\n"
                f"👤 الزبون: {update.effective_user.first_name}\n"
                f"📞 الهاتف: {context.user_data.get('phone_number')}\n"
                f"📶 الشبكة: {context.user_data.get('card_type')}\n"
                f"💰 المبلغ: {amount:,.0f} ل.س\n"
                f"💵 الخصم: ${usd_amount:.2f}",
                reply_markup=InlineKeyboardMarkup([
                    [InlineKeyboardButton("✅ موافقة", callback_data=f"phone_accept#{user_id}#{usd_amount}#{amount}#{context.user_data.get('phone_number')}#{context.user_data.get('card_type')}")],
                    [InlineKeyboardButton("❌ رفض", callback_data=f"phone_reject#{user_id}")]
                ])
            )
            await update.message.reply_text("✅ تم إرسال طلب الشحن للإدارة.")
            context.user_data['awaiting_phone_amount'] = False
        except:
            await update.message.reply_text("❌ اكتب رقماً صحيحاً!")
        return

    # ============================================================
    # ==================== موافقة الأدمن على شحن الهاتف =======
    # ============================================================
    if data.startswith("phone_accept"):
        parts = data.split('#')
        target_id = parts[1]
        usd_amount = float(parts[2])
        syr_amount = float(parts[3])
        phone = parts[4]
        card_type = parts[5]
        update_balance(target_id, -usd_amount)
        await query.edit_message_text(f"✅ تم قبول طلب شحن الهاتف")
        await context.bot.send_message(
            target_id,
            f"✅ **تم شحن هاتفك!**\n"
            f"━━━━━━━━━━━━━━━━━━━━\n"
            f"📞 الهاتف: {phone}\n"
            f"📶 الشبكة: {card_type}\n"
            f"💰 المبلغ: {syr_amount:,.0f} ل.س"
        )
        return

    if data.startswith("phone_reject"):
        target_id = data.split('#')[1]
        await query.edit_message_text(f"❌ تم رفض طلب الشحن")
        await context.bot.send_message(target_id, "❌ عذراً، تم رفض طلب شحن الهاتف.")
        return

    # ============================================================
    # ==================== شحن الرصيد ========================
    # ============================================================
    if data.startswith("charge#"):
        currency = data.split('#')[1]
        context.user_data['charge_currency'] = currency
        context.user_data['awaiting_charge'] = True
        await query.edit_message_text(f"✍️ **أدخل المبلغ**\nالرجاء كتابة المبلغ {currency if currency == 'usd' else 'بالليرة السورية'}:")
        return

    # ============================================================
    # ==================== استرجاع الأموال ====================
    # ============================================================
    if data.startswith("refund#"):
        currency = data.split('#')[1]
        context.user_data['refund_currency'] = currency
        context.user_data['awaiting_refund'] = True
        await query.edit_message_text(f"✍️ **أدخل المبلغ**\nالرجاء كتابة المبلغ {currency if currency == 'usd' else 'بالليرة السورية'} المراد استرجاعه:")
        return

    # ============================================================
    # ==================== إنشاء بوت ==========================
    # ============================================================
    if data == "bot_order#start":
        context.user_data['awaiting_bot_desc'] = True
        await query.edit_message_text(
            "🤖 **إنشاء بوت جديد**\n"
            "━━━━━━━━━━━━━━━━━━━━\n"
            "✍️ اكتب مواصفات البوت الذي تريده:"
        )
        return

    if context.user_data.get('awaiting_bot_desc'):
        desc = update.message.text
        context.user_data['bot_desc'] = desc
        context.user_data['awaiting_bot_desc'] = False
        context.user_data['awaiting_bot_contact'] = True
        await update.message.reply_text("✍️ أرسل رقم تواصلك:")
        return

    if context.user_data.get('awaiting_bot_contact'):
        contact = update.message.text
        context.user_data['bot_contact'] = contact
        context.user_data['awaiting_bot_contact'] = False
        server_btn = InlineKeyboardMarkup([
            [InlineKeyboardButton("🔥 سيرفر قوي 24 ساعة (5$/شهر + أسبوع مجاناً)", callback_data="srv#strong")],
            [InlineKeyboardButton("💤 سيرفر عادي 12-18 ساعة (2$/شهر)", callback_data="srv#normal")]
        ])
        await update.message.reply_text("🖥️ **اختر نوع السيرفر:**", reply_markup=server_btn)
        return

    if data.startswith("srv#"):
        srv_type = data.split('#')[1]
        srv_name = "🔥 قوي 24 ساعة (5$/شهر + أسبوع مجاناً)" if srv_type == 'strong' else "💤 عادي 12-18 ساعة (2$/شهر)"
        desc = context.user_data.get('bot_desc', 'غير محدد')
        contact = context.user_data.get('bot_contact', 'غير محدد')
        await query.edit_message_text("🚀 جاري إرسال الطلب للإدارة...")
        await context.bot.send_message(
            ADMIN_CHANNEL_ID,
            f"🤖 **طلب إنشاء بوت جديد**\n"
            f"━━━━━━━━━━━━━━━━━━━━\n"
            f"👤 الزبون: {update.effective_user.first_name}\n"
            f"🆔 المعرف: {user_id}\n"
            f"💬 التواصل: {contact}\n"
            f"📝 المواصفات: {desc}\n"
            f"🖥️ السيرفر: {srv_name}",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("💰 السعر", callback_data=f"bot_price#{user_id}")],
                [InlineKeyboardButton("⏰ الوقت", callback_data=f"bot_time#{user_id}")],
                [InlineKeyboardButton("📂 ملف", callback_data=f"bot_file#{user_id}")],
                [InlineKeyboardButton("❌ رفض", callback_data=f"bot_reject#{user_id}")]
            ])
        )
        context.user_data['awaiting_bot_desc'] = False
        context.user_data['awaiting_bot_contact'] = False
        return

    # ============================================================
    # ==================== أزرار طلب البوت (إدارة) ============
    # ============================================================
    if data.startswith("bot_price"):
        target_id = data.split('#')[1]
        context.user_data['bot_target_id'] = target_id
        context.user_data['awaiting_bot_price'] = True
        await query.edit_message_text(f"✍️ اكتب السعر للمستخدم {target_id}:")
        return

    if data.startswith("bot_time"):
        target_id = data.split('#')[1]
        context.user_data['bot_target_id'] = target_id
        context.user_data['awaiting_bot_time'] = True
        await query.edit_message_text(f"✍️ اكتب الوقت المتوقع للمستخدم {target_id}:")
        return

    if data.startswith("bot_file"):
        target_id = data.split('#')[1]
        await query.edit_message_text(f"📤 أرسل ملف البوت للمستخدم {target_id}:")
        return

    if data.startswith("bot_reject"):
        target_id = data.split('#')[1]
        await query.edit_message_text(f"❌ تم رفض طلب البوت")
        await context.bot.send_message(target_id, "❌ عذراً، تم رفض طلب إنشاء البوت.")
        return

    # ============================================================
    # ==================== العودة للقائمة الرئيسية ============
    # ============================================================
    if data == "main_menu":
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text="🎯 **القائمة الرئيسية**",
            reply_markup=main_menu,
            parse_mode='Markdown'
        )
        return

    await query.edit_message_text("⚠️ هذا الزر غير مفعل حالياً.")

# ==================== تشغيل البوت ====================
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
