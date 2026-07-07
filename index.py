import json
import os
import random
import string
from datetime import datetime
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup, BufferedInputFile
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, MessageHandler, filters, ContextTypes

# ==================== إعدادات البوت ====================
BOT_TOKEN = "8700905522:AAE30w5iFr8jmhIRf_eE0EpSAmk6j1lMfn8"
ADMIN_CHANNEL_ID = "-1004479419959"
ADMIN_ID = "8243108672"
ADMIN_PASSWORD = "T13AHA990POL"
DEVELOPER_USERNAME = "@MrXT1_3"
DB_FILE = 'database.json'

NIGHT_START_HOUR = 0
NIGHT_END_HOUR = 8
PAGE_SIZE = 6

# ==================== الكتالوج الافتراضي ====================
def default_catalog():
    cat = {}

    def add(nid, name, section, parent, ntype, kind=None, price=None, active=True, warning=None):
        cat[nid] = {
            "name": name, "section": section, "parent": parent, "type": ntype,
            "kind": kind, "price": price, "active": active, "deleted": False,
            "children": [], "warning": warning
        }
        if parent:
            cat[parent]["children"].append(nid)

    add("g1", "📁 PUBG MOBILE", "games", None, "folder")
    add("g2", "📁 ببجي عالمية", "games", "g1", "folder")
    add("g3", "📁 ببجي اكواد", "games", "g2", "folder")
    add("g4", "🎯 كود 60 شدة ~ 1.10$", "games", "g3", "product", "game_code", 1.10)
    add("g5", "🎯 كود 325 شدة ~ 5.0$", "games", "g3", "product", "game_code", 5.0)
    add("g6", "🎯 كود 660 شدة ~ 10.0$", "games", "g3", "product", "game_code", 10.0)
    add("g7", "🎯 كود 1800 شدة (السعر غير محدد)", "games", "g3", "product", "game_code", None, active=False)

    add("g8", "📁 Call of Duty", "games", None, "folder")
    add("g13", "📁 320 CP", "games", "g8", "folder")
    add("g14", "🎯 320 Cp ~ 5.0$", "games", "g13", "product", "game_code", 5.0)
    add("g15", "📁 480 CP", "games", "g8", "folder")
    add("g16", "🎯 480 Cp ~ 7.15$", "games", "g15", "product", "game_code", 7.15)
    add("g17", "📁 560 CP", "games", "g8", "folder")
    add("g18", "🎯 560 Cp ~ 8.30$", "games", "g17", "product", "game_code", 8.30)
    add("g19", "📁 1120 CP", "games", "g8", "folder")
    add("g20", "🎯 1120 Cp ~ 17.0$", "games", "g19", "product", "game_code", 17.0)

    add("g21", "📁 Free Fire", "games", None, "folder")
    add("g22", "📁 فري فاير شرق اوسط", "games", "g21", "folder")
    add("g23", "📁 فري فاير Garena", "games", "g22", "folder")
    add("g24", "🎯 100+10 جوهرة ~ 1.06$", "games", "g23", "product", "game_code", 1.06)
    add("g25", "🎯 210+21 جوهرة ~ 2.09$", "games", "g23", "product", "game_code", 2.09)
    add("g26", "🎯 530+53 جوهرة ~ 5.07$", "games", "g23", "product", "game_code", 5.07)
    add("g27", "🎯 1080+108 جوهرة ~ 11.0$", "games", "g23", "product", "game_code", 11.0)

    add("g28", "📁 ROBLOX", "games", None, "folder")
    add("g29", "🎯 كود روبوكس 10$ إمريكي ~ 11.0$", "games", "g28", "product", "game_code", 11.0)
    add("g30", "🎯 كود روبوكس 15$ إمريكي ~ 16.02$", "games", "g28", "product", "game_code", 16.02)

    add("g31", "📁 FC Mobile", "games", None, "folder")
    add("g32", "📁 FC Mobile Cambodia", "games", "g31", "folder")
    add("g33", "🎯 Silver 99 ~ 1.20$", "games", "g32", "product", "game_code", 1.20)
    add("g34", "🎯 Silver 499 ~ 5.99$", "games", "g32", "product", "game_code", 5.99)
    add("g35", "🎯 100 FC Points ~ 1.20$", "games", "g32", "product", "game_code", 1.20)
    add("g36", "🎯 520 FC Points ~ 5.99$", "games", "g32", "product", "game_code", 5.99)

    add("g37", "📁 Minecraft", "games", None, "folder")
    add("g38", "🎯 كود 3500 كوينز ~ 22.0$", "games", "g37", "product", "game_code", 22.0)
    add("g39", "🎯 كود 1720 كوينز ~ 11.0$", "games", "g37", "product", "game_code", 11.0)

    add("g40", "📁 Stumble Guys (نفذ المخزون مؤقتاً)", "games", None, "folder")

    add("c1", "📁 Steam Card", "cards", None, "folder")
    add("c2", "📁 Steam USA", "cards", "c1", "folder")
    add("c3", "🎯 Steam 20$ USA ~ 23$", "cards", "c2", "product", "card", 23.0)
    add("c4", "🎯 Steam 50$ USA ~ 57$", "cards", "c2", "product", "card", 57.0)
    add("c5", "🎯 Steam 100$ USA ~ 112$", "cards", "c2", "product", "card", 112.0)

    add("c6", "📁 XBOX Card", "cards", None, "folder")
    add("c7", "📁 XBOX USA", "cards", "c6", "folder")
    add("c8", "🎯 XBOX 20$ USA ~ 23$", "cards", "c7", "product", "card", 23.0)
    add("c9", "🎯 XBOX 50$ USA ~ 57$", "cards", "c7", "product", "card", 57.0)
    add("c10", "🎯 XBOX 100$ USA ~ 112$", "cards", "c7", "product", "card", 112.0)

    number_warning = (
        "⚠️ **تنبيه هام قبل الطلب:**\n"
        "سيتم إظهار الرقم بشكل مباشر ويمكنك طلب الكود من واتساب الرسمي.\n"
        "❌ حال لم يصل كود التفعيل، سيتم رفض الطلب تلقائياً واستعادة رصيدك.\n"
        "🚫 ممنوع طلب الكود مرتين على نفس الرقم: إن طلبت الكود مرتين، الكود الذي يصل لأول طلب فقط هو الصالح.\n"
        "✅ اطلب الكود مرة واحدة فقط.\n"
        "ℹ️ أحياناً عند وضع الرقم في واتساب يُرسل الطلب تلقائياً، تأكد قبل الطلب.\n"
        "⚠️ الأرقام وهمية وغير مكفولة نهائياً."
    )
    add("n2", "📁 أرقام واتساب", "numbers", None, "folder")
    add("n3", "🎯 المانيا 49+ ~ 2.00$", "numbers", "n2", "product", "whatsapp_number", 2.00, warning=number_warning)
    add("n4", "🎯 مصر 20+ ~ 1.50$", "numbers", "n2", "product", "whatsapp_number", 1.50, warning=number_warning)
    add("n5", "🎯 بريطانيا 44+ ~ 1.00$", "numbers", "n2", "product", "whatsapp_number", 1.00, warning=number_warning)
    add("n6", "📁 أرقام تيليجرام (نفذ المخزون مؤقتاً)", "numbers", None, "folder")

    return cat


def default_roots():
    return {
        "games": ["g1", "g8", "g21", "g28", "g31", "g37", "g40"],
        "cards": ["c1", "c6"],
        "numbers": ["n2", "n6"]
    }


# ==================== قاعدة البيانات ====================
def load_db():
    try:
        with open(DB_FILE, 'r', encoding='utf-8') as f:
            data = json.load(f)
    except:
        data = {}
    defaults = {
        "users": {}, "banned": {}, "muted": {}, "exchange_rate": 13800,
        "admin_notes": "", "bot_maintenance": False, "pending_orders": {},
        "catalog": default_catalog(), "catalog_roots": default_roots(),
        "next_node_seq": 100
    }
    for k, v in defaults.items():
        if k not in data:
            data[k] = v
    return data


def save_db(data):
    with open(DB_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


def get_balance(db, user_id):
    return db["users"].get(str(user_id), {}).get("balance_usd", 0)


def update_balance(db, user_id, amount):
    uid = str(user_id)
    if uid not in db["users"]:
        db["users"][uid] = {"name": "مستخدم", "balance_usd": 0, "joined": datetime.now().isoformat()}
    db["users"][uid]["balance_usd"] = db["users"][uid].get("balance_usd", 0) + amount


def generate_order_id():
    return ''.join(random.choices(string.digits, k=6))


def new_node_id(db, prefix="x"):
    seq = db.get("next_node_seq", 100)
    db["next_node_seq"] = seq + 1
    return f"{prefix}{seq}"


def is_night_time():
    h = datetime.now().hour
    if NIGHT_START_HOUR < NIGHT_END_HOUR:
        return NIGHT_START_HOUR <= h < NIGHT_END_HOUR
    return h >= NIGHT_START_HOUR or h < NIGHT_END_HOUR


async def notify_admin_dm(context, text, markup=None):
    """يرسل رسالة خاصة للأدمن (وليس داخل القناة) - القنوات لا تستقبل ردود نصية عادية للبوت"""
    try:
        await context.bot.send_message(ADMIN_ID, text, reply_markup=markup, parse_mode='Markdown')
    except Exception:
        pass


def clear_awaiting(ud):
    """يمسح كل حالات الانتظار (awaiting_*) لمنع تعليق الحالة"""
    for key in list(ud.keys()):
        if key.startswith('awaiting_'):
            ud[key] = False


# ==================== القوائم الثابتة ====================
main_menu = ReplyKeyboardMarkup([
    ['🏪 المتجر', '🤖 إنشاء بوت'],
    ['💳 المحفظة', '💰 استرجاع الأموال'],
    ['⚙️ الإعدادات', '📞 الدعم الفني']
], resize_keyboard=True)

store_menu = InlineKeyboardMarkup([
    [InlineKeyboardButton("🎮 قسم الألعاب", callback_data="root#games#0")],
    [InlineKeyboardButton("🎟️ قسم البطاقات", callback_data="root#cards#0")],
    [InlineKeyboardButton("📱 الأرقام", callback_data="root#numbers#0")],
    [InlineKeyboardButton("📱 شحن رصيد هاتف", callback_data="store#phone")],
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
    [InlineKeyboardButton("👥 المستخدمين", callback_data="adm#users"),
     InlineKeyboardButton("📊 الأرصدة", callback_data="adm#view_balances")],
    [InlineKeyboardButton("➕ إضافة رصيد يدوياً", callback_data="adm#add_balance")],
    [InlineKeyboardButton("📈 تعديل سعر الصرف", callback_data="adm#edit_rate")],
    [InlineKeyboardButton("🗂️ عرض شجرة المتجر", callback_data="adm#tree")],
    [InlineKeyboardButton("➕ إضافة قسم/مجلد", callback_data="adm#add_category"),
     InlineKeyboardButton("➕ إضافة منتج", callback_data="adm#add_product")],
    [InlineKeyboardButton("✏️ تعديل سعر منتج", callback_data="adm#edit_price"),
     InlineKeyboardButton("⛔ تعطيل/تفعيل منتج", callback_data="adm#toggle")],
    [InlineKeyboardButton("🗑️ حذف عنصر", callback_data="adm#delete_node"),
     InlineKeyboardButton("♻️ استرجاع محذوف", callback_data="adm#restore_node")],
    [InlineKeyboardButton("🧹 تنظيف الطلبات المعلقة", callback_data="adm#clean")],
    [InlineKeyboardButton("💾 نسخة احتياطية", callback_data="adm#backup")],
    [InlineKeyboardButton("🔙 القائمة الرئيسية", callback_data="main_menu")]
])


def render_listing(db, children_ids, back_cb, nav_prefix, page=0):
    cat = db["catalog"]
    items = []
    for cid in children_ids:
        node = cat.get(cid)
        if not node or node.get("deleted"):
            continue
        if node["type"] == "product" and not node.get("active", True):
            continue
        items.append((cid, node))

    total_pages = max(1, (len(items) + PAGE_SIZE - 1) // PAGE_SIZE)
    page = max(0, min(page, total_pages - 1))
    subset = items[page * PAGE_SIZE: (page + 1) * PAGE_SIZE]

    buttons = []
    for cid, node in subset:
        cb = f"buy#{cid}" if node["type"] == "product" else f"nav#{cid}#0"
        buttons.append([InlineKeyboardButton(node["name"], callback_data=cb)])

    nav_row = []
    if page > 0:
        nav_row.append(InlineKeyboardButton("⬅️ السابق", callback_data=f"{nav_prefix}#{page-1}"))
    if page < total_pages - 1:
        nav_row.append(InlineKeyboardButton("التالي ➡️", callback_data=f"{nav_prefix}#{page+1}"))
    if nav_row:
        buttons.append(nav_row)

    buttons.append([InlineKeyboardButton("🔙 رجوع", callback_data=back_cb)])
    buttons.append([InlineKeyboardButton("🔙 القائمة الرئيسية", callback_data="main_menu")])
    return InlineKeyboardMarkup(buttons)


def back_cb_for(node):
    if node.get("parent"):
        return f"nav#{node['parent']}#0"
    return f"root#{node['section']}#0"


# ==================== أوامر البوت ====================
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = str(update.effective_user.id)
    db = load_db()
    if user_id not in db["users"]:
        db["users"][user_id] = {"name": update.effective_user.first_name, "balance_usd": 0, "joined": datetime.now().isoformat()}
        save_db(db)
    balance = db["users"][user_id]["balance_usd"]
    rate = db.get("exchange_rate", 13800)
    text = (
        f"🔥 **أهلاً بك في بوت شام إن جيم** 🔥\n"
        f"━━━━━━━━━━━━━━━━━━━━\n"
        f"👤 مرحباً: {update.effective_user.first_name}\n"
        f"💰 رصيدك: ${balance:.2f}\n"
        f"🇸🇾 بالليرة: {balance * rate:,.0f} ل.س\n"
        f"📈 سعر الصرف: 1$ = {rate:,} ل.س\n"
        f"━━━━━━━━━━━━━━━━━━━━\n"
        f"⚠️ استخدم الأزرار للتنقل ❤️"
    )
    if is_night_time():
        text += "\n\n🌙 **ملاحظة:** نحن حالياً خارج أوقات الدعم المباشر، قد يتأخر الرد قليلاً وسنجيبك بأسرع وقت ممكن 🙏"
    await update.message.reply_text(text, reply_markup=main_menu, parse_mode='Markdown')


async def admin_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['awaiting_password'] = True
    await update.message.reply_text("🔐 اكتب كلمة السر للتحقق:")


async def panel_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = str(update.effective_user.id)
    if context.user_data.get('admin_dashboard') or user_id == ADMIN_ID:
        await update.message.reply_text("🛸 **لوحة التحكم الإدارية الخارقة**", reply_markup=admin_panel, parse_mode='Markdown')
    else:
        await update.message.reply_text("❌ ليس لديك صلاحية للدخول.")


async def cancel_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = str(update.effective_user.id)
    was_admin_dash = context.user_data.get('admin_dashboard', False)
    context.user_data.clear()
    if was_admin_dash:
        context.user_data['admin_dashboard'] = True
    if was_admin_dash or user_id == ADMIN_ID:
        await update.message.reply_text("✅ تم إلغاء أي عملية معلقة.", reply_markup=admin_panel)
    else:
        await update.message.reply_text("✅ تم إلغاء أي عملية معلقة.", reply_markup=main_menu)


# ==================== معالج القناة (تحذير إذا كتب الأدمن هناك) ====================
async def handle_channel_post(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if str(update.effective_chat.id) == ADMIN_CHANNEL_ID:
        await notify_admin_dm(
            context,
            "⚠️ **انتبه:** كتبت رداً داخل القناة نفسها ولن يصل للزبون!\n"
            "الرجاء الرد **هنا في هذه المحادثة الخاصة معي** وليس داخل القناة."
        )


# ==================== معالج النصوص ====================
async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message or not update.message.text:
        return
    user_id = str(update.effective_user.id)
    text = update.message.text
    db = load_db()
    ud = context.user_data

    if text == '🏪 المتجر':
        await update.message.reply_text("🛍️ اختر القسم:", reply_markup=store_menu)
        return
    if text == '💳 المحفظة':
        balance = get_balance(db, user_id)
        await update.message.reply_text(f"💳 **رصيدك الحالي:**\n💰 ${balance:.2f}", reply_markup=wallet_menu, parse_mode='Markdown')
        return
    if text == '💰 استرجاع الأموال':
        await update.message.reply_text("💰 اختر عملة الاسترجاع:", reply_markup=refund_menu)
        return
    if text == '🤖 إنشاء بوت':
        clear_awaiting(ud)
        ud['awaiting_bot_desc'] = True
        await update.message.reply_text("🤖 اكتب مواصفات البوت الذي تريده:")
        return
    if text == '⚙️ الإعدادات':
        await update.message.reply_text(f"⚙️ **الإعدادات**\n👤 {update.effective_user.first_name}\n🆔 `{user_id}`", parse_mode='Markdown')
        return
    if text == '📞 الدعم الفني':
        await update.message.reply_text(f"📞 **الدعم الفني**\n{DEVELOPER_USERNAME}", parse_mode='Markdown')
        return

    if ud.get('awaiting_password'):
        ud['awaiting_password'] = False
        if text == ADMIN_PASSWORD:
            ud['admin_dashboard'] = True
            await update.message.reply_text("✅ تم التحقق! استخدم /panel للوحة التحكم.")
        else:
            await update.message.reply_text("❌ كلمة سر خاطئة!")
        return

    # ---------------- تدفقات الأدمن ----------------
    if ud.get('awaiting_broadcast'):
        ud['awaiting_broadcast'] = False
        await update.message.reply_text("🚀 جاري الإرسال...")
        count = 0
        for uid in db["users"]:
            try:
                await context.bot.send_message(uid, f"📢 **إعلان عام**\n━━━━━━━━━━━━━━━━━━━━\n{text}", parse_mode='Markdown')
                count += 1
            except:
                pass
        await update.message.reply_text(f"✅ تم إرسال الإعلان إلى {count} مستخدم.")
        return

    if ud.get('awaiting_add_balance'):
        try:
            parts = text.split('|')
            target_id, amount = parts[0].strip(), float(parts[1].strip())
            if amount <= 0 or target_id not in db["users"]:
                raise ValueError
            update_balance(db, target_id, amount)
            save_db(db)
            await update.message.reply_text(f"✅ تم إضافة ${amount} إلى {db['users'][target_id]['name']}")
            await context.bot.send_message(target_id, f"🎉 تم إضافة ${amount} إلى محفظتك!")
        except:
            await update.message.reply_text("❌ الصيغة غير صحيحة! استخدم: `آيدي|المبلغ` — حاول مجدداً أو أرسل /cancel للإلغاء.", parse_mode='Markdown')
            return
        ud['awaiting_add_balance'] = False
        return

    if ud.get('awaiting_new_rate'):
        try:
            r = float(text)
            if r <= 0:
                raise ValueError
            db['exchange_rate'] = r
            save_db(db)
            await update.message.reply_text(f"✅ تم تعديل سعر الصرف إلى {r:,} ل.س")
        except:
            await update.message.reply_text("❌ اكتب رقماً صحيحاً! أو أرسل /cancel للإلغاء.")
            return
        ud['awaiting_new_rate'] = False
        return

    if ud.get('awaiting_add_category'):
        try:
            parts = text.split('|')
            parent_raw, section, name = parts[0].strip(), parts[1].strip(), parts[2].strip()
            parent = None if parent_raw.lower() == 'root' else parent_raw
            if section not in db['catalog_roots'] or (parent and parent not in db['catalog']):
                raise ValueError
            nid = new_node_id(db, "x")
            db['catalog'][nid] = {"name": f"📁 {name}", "section": section, "parent": parent,
                                   "type": "folder", "kind": None, "price": None, "active": True,
                                   "deleted": False, "children": [], "warning": None}
            if parent:
                db['catalog'][parent]['children'].append(nid)
            else:
                db['catalog_roots'][section].append(nid)
            save_db(db)
            await update.message.reply_text(f"✅ تم إضافة القسم [{name}] بمعرف `{nid}`", parse_mode='Markdown')
        except:
            await update.message.reply_text("❌ الصيغة غير صحيحة! استخدم:\n`parent_id_او_root|games_او_cards_او_numbers|الاسم`\nأو /cancel للإلغاء.", parse_mode='Markdown')
            return
        ud['awaiting_add_category'] = False
        return

    if ud.get('awaiting_add_product'):
        try:
            parts = text.split('|')
            parent, kind, name, price = parts[0].strip(), parts[1].strip(), parts[2].strip(), float(parts[3].strip())
            if parent not in db['catalog'] or price <= 0 or kind not in ('game_code', 'card', 'whatsapp_number', 'telegram_number'):
                raise ValueError
            nid = new_node_id(db, "x")
            db['catalog'][nid] = {"name": f"🎯 {name} ~ {price}$", "section": db['catalog'][parent]['section'],
                                   "parent": parent, "type": "product", "kind": kind, "price": price,
                                   "active": True, "deleted": False, "children": [], "warning": None}
            db['catalog'][parent]['children'].append(nid)
            save_db(db)
            await update.message.reply_text(f"✅ تم إضافة المنتج [{name}] بمعرف `{nid}`", parse_mode='Markdown')
        except:
            await update.message.reply_text("❌ الصيغة غير صحيحة! استخدم:\n`parent_id|kind|الاسم|السعر`\nkind: game_code / card / whatsapp_number / telegram_number\nأو /cancel للإلغاء.", parse_mode='Markdown')
            return
        ud['awaiting_add_product'] = False
        return

    if ud.get('awaiting_edit_price'):
        try:
            parts = text.split('|')
            nid, price = parts[0].strip(), float(parts[1].strip())
            node = db['catalog'][nid]
            node['price'] = price
            node['active'] = True
            base_name = node['name'].split(' ~ ')[0]
            node['name'] = base_name + f" ~ {price}$"
            save_db(db)
            await update.message.reply_text(f"✅ تم تعديل سعر `{nid}` إلى {price}$ وتفعيله.", parse_mode='Markdown')
        except:
            await update.message.reply_text("❌ الصيغة غير صحيحة! استخدم: `node_id|السعر_الجديد` أو /cancel للإلغاء.", parse_mode='Markdown')
            return
        ud['awaiting_edit_price'] = False
        return

    if ud.get('awaiting_toggle'):
        nid = text.strip()
        node = db['catalog'].get(nid)
        if not node:
            await update.message.reply_text("❌ لا يوجد عنصر بهذا المعرف. حاول مجدداً أو أرسل /cancel.")
            return
        node['active'] = not node.get('active', True)
        save_db(db)
        await update.message.reply_text(f"✅ الحالة الآن: {'مفعّل' if node['active'] else 'معطّل'} لـ `{nid}`", parse_mode='Markdown')
        ud['awaiting_toggle'] = False
        return

    if ud.get('awaiting_delete_node'):
        nid = text.strip()
        node = db['catalog'].get(nid)
        if not node:
            await update.message.reply_text("❌ لا يوجد عنصر بهذا المعرف. حاول مجدداً أو أرسل /cancel.")
            return
        node['deleted'] = True
        save_db(db)
        await update.message.reply_text(f"🗑️ تم حذف `{nid}` (يمكن استرجاعه لاحقاً).", parse_mode='Markdown')
        ud['awaiting_delete_node'] = False
        return

    if ud.get('awaiting_restore_node'):
        nid = text.strip()
        node = db['catalog'].get(nid)
        if not node:
            await update.message.reply_text("❌ لا يوجد عنصر بهذا المعرف. حاول مجدداً أو أرسل /cancel.")
            return
        node['deleted'] = False
        save_db(db)
        await update.message.reply_text(f"♻️ تم استرجاع `{nid}`.", parse_mode='Markdown')
        ud['awaiting_restore_node'] = False
        return

    # ---------------- شحن الرصيد ----------------
    if ud.get('awaiting_charge'):
        try:
            amount = float(text)
            if amount <= 0:
                raise ValueError
            currency = ud.get('charge_currency', 'usd')
            rate = db.get('exchange_rate', 13800)
            usd_amount = amount if currency == 'usd' else (amount / rate)
            ud['charge_amount'] = amount
            ud['charge_usd_amount'] = usd_amount
            ud['awaiting_charge_proof'] = True
            await update.message.reply_text(
                f"📸 المبلغ: {amount} {'$' if currency=='usd' else 'ل.س'} = **${usd_amount:.2f}**\n"
                f"أرسل الآن صورة إثبات الدفع (وصل التحويل) لتأكيد طلبك:", parse_mode='Markdown'
            )
        except:
            await update.message.reply_text("❌ اكتب رقماً صحيحاً! أو أرسل /cancel للإلغاء.")
            return
        ud['awaiting_charge'] = False
        return

    # ---------------- استرجاع الأموال ----------------
    if ud.get('awaiting_refund'):
        try:
            amount = float(text)
            if amount <= 0:
                raise ValueError
            currency = ud.get('refund_currency', 'usd')
            usd_amount = amount if currency == 'usd' else amount / db.get('exchange_rate', 13800)
            balance = get_balance(db, user_id)
            if balance < usd_amount:
                await update.message.reply_text(f"❌ رصيدك (${balance:.2f}) غير كافٍ لهذا المبلغ (${usd_amount:.2f})!")
                ud['awaiting_refund'] = False
                return
            order_id = generate_order_id()
            db['pending_orders'][order_id] = {"type": "refund", "user_id": user_id, "amount": usd_amount}
            save_db(db)
            await context.bot.send_message(
                ADMIN_CHANNEL_ID,
                f"💰 **طلب استرجاع أموال**\n━━━━━━━━━━━━━━━━━━━━\n📋 رقم الطلب: {order_id}\n"
                f"👤 {update.effective_user.first_name}\n🆔 {user_id}\n"
                f"💵 المبلغ المدخل: {amount} {'$' if currency=='usd' else 'ل.س'}\n💵 المعادل بالدولار: ${usd_amount:.2f}",
                reply_markup=InlineKeyboardMarkup([
                    [InlineKeyboardButton("✅ موافقة", callback_data=f"refund_ok#{order_id}")],
                    [InlineKeyboardButton("❌ رفض", callback_data=f"refund_no#{order_id}")]
                ])
            )
            await update.message.reply_text(f"✅ تم إرسال طلب الاسترجاع (رقم {order_id}) للإدارة.")
        except:
            await update.message.reply_text("❌ اكتب رقماً صحيحاً! أو أرسل /cancel للإلغاء.")
            return
        ud['awaiting_refund'] = False
        return

    # ---------------- كتابة آيدي اللعبة ----------------
    if ud.get('awaiting_game_id'):
        game_id = text
        node_id = ud.get('pending_node_id')
        node = db['catalog'].get(node_id)
        ud['awaiting_game_id'] = False
        if not node:
            await update.message.reply_text("❌ حدث خطأ، حاول من جديد.")
            return
        order_id = generate_order_id()
        db['pending_orders'][order_id] = {"type": "purchase", "user_id": user_id, "node_id": node_id,
                                           "price": node['price'], "item_name": node['name'], "game_id": game_id}
        save_db(db)
        await context.bot.send_message(
            ADMIN_CHANNEL_ID,
            f"🛒 **طلب شراء جديد**\n━━━━━━━━━━━━━━━━━━━━\n📋 رقم الطلب: {order_id}\n"
            f"👤 {update.effective_user.first_name}\n🆔 {user_id}\n🎁 {node['name']}\n"
            f"💰 ${node['price']}\n🆔 آيدي اللعبة: {game_id}",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("✅ موافقة وخصم", callback_data=f"order_ok#{order_id}")],
                [InlineKeyboardButton("❌ رفض", callback_data=f"order_no#{order_id}")]
            ])
        )
        await update.message.reply_text(f"✅ تم إرسال طلبك (رقم {order_id}) للإدارة، بانتظار الموافقة.")
        return

    # ---------------- شحن رصيد الهاتف ----------------
    if ud.get('awaiting_phone'):
        ud['phone_number'] = text
        ud['awaiting_phone'] = False
        ud['awaiting_phone_amount'] = True
        await update.message.reply_text("✍️ اكتب المبلغ بالليرة:")
        return

    if ud.get('awaiting_phone_amount'):
        try:
            amount = float(text)
            if amount <= 0:
                raise ValueError
            rate = db.get('exchange_rate', 13800)
            usd_amount = amount / rate
            balance = get_balance(db, user_id)
            if balance < usd_amount:
                await update.message.reply_text(f"❌ رصيدك (${balance:.2f}) غير كافٍ!")
                ud['awaiting_phone_amount'] = False
                return
            order_id = generate_order_id()
            db['pending_orders'][order_id] = {"type": "phone", "user_id": user_id, "usd_amount": usd_amount,
                                               "syr_amount": amount, "phone": ud.get('phone_number'),
                                               "card_type": ud.get('card_type')}
            save_db(db)
            await context.bot.send_message(
                ADMIN_CHANNEL_ID,
                f"📱 **طلب شحن هاتف**\n━━━━━━━━━━━━━━━━━━━━\n📋 رقم الطلب: {order_id}\n"
                f"👤 {update.effective_user.first_name}\n📞 {ud.get('phone_number')}\n"
                f"📶 {ud.get('card_type')}\n💰 {amount:,.0f} ل.س (${usd_amount:.2f})",
                reply_markup=InlineKeyboardMarkup([
                    [InlineKeyboardButton("✅ موافقة", callback_data=f"phone_ok#{order_id}")],
                    [InlineKeyboardButton("❌ رفض", callback_data=f"phone_no#{order_id}")]
                ])
            )
            await update.message.reply_text(f"✅ تم إرسال طلب الشحن (رقم {order_id}) للإدارة.")
        except:
            await update.message.reply_text("❌ اكتب رقماً صحيحاً! أو أرسل /cancel للإلغاء.")
            return
        ud['awaiting_phone_amount'] = False
        return

    # ---------------- إنشاء بوت (عميل) ----------------
    if ud.get('awaiting_bot_desc'):
        ud['bot_desc'] = text
        ud['awaiting_bot_desc'] = False
        ud['awaiting_bot_contact'] = True
        await update.message.reply_text("✍️ أرسل رقم تواصلك:")
        return

    if ud.get('awaiting_bot_contact'):
        ud['bot_contact'] = text
        ud['awaiting_bot_contact'] = False
        server_btn = InlineKeyboardMarkup([
            [InlineKeyboardButton("🔥 سيرفر قوي 24 ساعة (5$/شهر + أسبوع مجاناً)", callback_data="srv#strong")],
            [InlineKeyboardButton("💤 سيرفر عادي 12-18 ساعة (2$/شهر)", callback_data="srv#normal")]
        ])
        await update.message.reply_text("🖥️ **اختر نوع السيرفر:**", reply_markup=server_btn)
        return

    # ---------------- ردود الأدمن على طلب البوت (بالخاص) ----------------
    if ud.get('awaiting_bot_price'):
        target_id = ud.get('bot_target_id')
        ud['awaiting_bot_price'] = False
        await context.bot.send_message(target_id, f"💰 **السعر المتفق عليه:** {text}")
        await update.message.reply_text(f"✅ تم إرسال السعر إلى {target_id}")
        return

    if ud.get('awaiting_bot_time'):
        target_id = ud.get('bot_target_id')
        ud['awaiting_bot_time'] = False
        await context.bot.send_message(target_id, f"⏰ **الوقت المتوقع:** {text}")
        await update.message.reply_text(f"✅ تم إرسال الوقت إلى {target_id}")
        return

    # ---------------- تسليم كود المنتج (بعد order_ok) - بالخاص فقط ----------------
    if ud.get('awaiting_delivery_code'):
        order_id = ud.get('delivery_order_id')
        order = db['pending_orders'].get(order_id)
        ud['awaiting_delivery_code'] = False
        if not order:
            await update.message.reply_text("❌ الطلب غير موجود أو تم تسليمه مسبقاً.")
            return
        target_id = order['user_id']
        try:
            await context.bot.send_message(
                target_id,
                f"✅ **تم تفعيل طلبك!**\n━━━━━━━━━━━━━━━━━━━━\n"
                f"🎁 المنتج: {order.get('item_name', 'رقم/بطاقة')}\n"
                f"📋 رقم الطلب: {order_id}\n\n"
                f"🎟️ **الكود/التفاصيل:**\n{text}",
                parse_mode='Markdown'
            )
            await update.message.reply_text(f"✅ تم تسليم الطلب (رقم {order_id}) للزبون بنجاح.")
            del db['pending_orders'][order_id]
            save_db(db)
        except Exception as e:
            await update.message.reply_text(f"❌ فشل الإرسال للزبون: {e}\nحاول مجدداً.")
            ud['awaiting_delivery_code'] = True
            ud['delivery_order_id'] = order_id
        return

    # ---------------- تسليم ملف البوت كنص ----------------
    if ud.get('awaiting_bot_file'):
        target_id = ud.get('bot_target_id')
        ud['awaiting_bot_file'] = False
        await context.bot.send_message(target_id, f"📂 **ملف البوت:**\n{text}")
        await update.message.reply_text(f"✅ تم إرسال الملف (نص) إلى {target_id}")
        return

    await update.message.reply_text("⚠️ لم أفهم طلبك، استخدم الأزرار من القائمة. (أو أرسل /cancel لإلغاء أي عملية عالقة)")


# ==================== معالج الصور والملفات ====================
async def handle_photo_and_document(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message:
        return
    user_id = str(update.effective_user.id)
    db = load_db()
    ud = context.user_data

    if ud.get('awaiting_charge_proof') and update.message.photo:
        amount = ud.get('charge_amount')
        usd_amount = ud.get('charge_usd_amount')
        currency = ud.get('charge_currency', 'usd')
        order_id = generate_order_id()
        db['pending_orders'][order_id] = {"type": "charge", "user_id": user_id, "usd_amount": usd_amount,
                                           "amount": amount, "currency": currency}
        save_db(db)
        photo_id = update.message.photo[-1].file_id
        await context.bot.send_photo(
            ADMIN_CHANNEL_ID, photo_id,
            caption=(f"🏦 **طلب شحن رصيد**\n━━━━━━━━━━━━━━━━━━━━\n📋 رقم الطلب: {order_id}\n"
                     f"👤 {update.effective_user.first_name}\n🆔 {user_id}\n"
                     f"💰 {amount} {'$' if currency=='usd' else 'ل.س'} = **${usd_amount:.2f}**"),
            parse_mode='Markdown',
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("✅ قبول وإضافة الرصيد", callback_data=f"charge_ok#{order_id}")],
                [InlineKeyboardButton("❌ رفض", callback_data=f"charge_no#{order_id}")]
            ])
        )
        ud['awaiting_charge_proof'] = False
        await update.message.reply_text(f"🚀 تم إرسال طلب الشحن (رقم {order_id}) للإدارة.")
        return

    if ud.get('awaiting_bot_file') and update.message.document:
        target_id = ud.get('bot_target_id')
        ud['awaiting_bot_file'] = False
        await context.bot.send_document(target_id, update.message.document.file_id, caption="📂 تفضل ملف البوت الخاص بك جاهزاً!")
        await update.message.reply_text(f"✅ تم إرسال الملف إلى {target_id}")
        return


# ==================== معالج الأزرار ====================
async def handle_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    data = query.data
    user_id = str(update.effective_user.id)
    db = load_db()
    ud = context.user_data

    if data.startswith("adm#"):
        action = data.split('#')[1]

        if action == "stats":
            total_users = len(db["users"])
            total_balance = sum(u.get("balance_usd", 0) for u in db["users"].values())
            total_orders = len(db.get("pending_orders", {}))
            await query.edit_message_text(
                f"📊 **الإحصائيات**\n━━━━━━━━━━━━━━━━━━━━\n👥 المستخدمين: {total_users}\n"
                f"💰 إجمالي الأرصدة: ${total_balance:.2f}\n📦 الطلبات المعلقة: {total_orders}",
                parse_mode='Markdown')
            return

        if action == "broadcast":
            clear_awaiting(ud)
            ud['awaiting_broadcast'] = True
            await query.edit_message_text("✍️ اكتب رسالة الإعلان (أو /cancel للإلغاء):")
            return

        if action == "add_balance":
            clear_awaiting(ud)
            ud['awaiting_add_balance'] = True
            await query.edit_message_text("✍️ اكتب: `آيدي|المبلغ` (أو /cancel للإلغاء)", parse_mode='Markdown')
            return

        if action == "view_balances":
            s = "💰 **الأرصدة**\n━━━━━━━━━━━━━━━━━━━━\n"
            for uid, info in list(db["users"].items())[:25]:
                s += f"👤 {info.get('name','مجهول')} — ${info.get('balance_usd',0):.2f} (`{uid}`)\n"
            await query.edit_message_text(s or "لا يوجد مستخدمين.", parse_mode='Markdown')
            return

        if action == "users":
            s = "👥 **المستخدمين**\n━━━━━━━━━━━━━━━━━━━━\n"
            for uid, info in list(db["users"].items())[:25]:
                s += f"`{uid}` — {info.get('name','مجهول')}\n"
            await query.edit_message_text(s or "لا يوجد مستخدمين.", parse_mode='Markdown')
            return

        if action == "edit_rate":
            clear_awaiting(ud)
            ud['awaiting_new_rate'] = True
            await query.edit_message_text(f"📈 سعر الصرف الحالي: {db.get('exchange_rate',13800):,} ل.س\n✍️ اكتب السعر الجديد (أو /cancel):")
            return

        if action == "tree":
            lines = ["🗂️ **شجرة المتجر الكاملة** (المعرف: الاسم)\n━━━━━━━━━━━━━━━━━━━━"]
            for section, roots in db['catalog_roots'].items():
                lines.append(f"\n📦 __{section}__")

                def walk(nid, depth):
                    node = db['catalog'].get(nid)
                    if not node:
                        return
                    flag = ""
                    if node.get('deleted'):
                        flag = " 🗑️محذوف"
                    elif node['type'] == 'product' and not node.get('active', True):
                        flag = " ⛔معطّل"
                    price_txt = f" | {node['price']}$" if node.get('price') is not None else ""
                    lines.append(("  " * depth) + f"`{nid}` {node['name']}{price_txt}{flag}")
                    for c in node.get('children', []):
                        walk(c, depth + 1)

                for r in roots:
                    walk(r, 1)
            full_text = "\n".join(lines)
            if len(full_text) > 3800:
                full_text = full_text[:3800] + "\n...\n(القائمة طويلة، عدّلت المعروض)"
            await query.edit_message_text(full_text, parse_mode='Markdown')
            return

        if action == "add_category":
            clear_awaiting(ud)
            ud['awaiting_add_category'] = True
            await query.edit_message_text(
                "✍️ اكتب بالصيغة:\n`parent_id_او_root|games_او_cards_او_numbers|الاسم`\n\n"
                "مثال (قسم رئيسي جديد): `root|games|لعبة جديدة`\n"
                "مثال (مجلد فرعي داخل g1): `g1|games|مجلد فرعي`\n(أو /cancel)",
                parse_mode='Markdown')
            return

        if action == "add_product":
            clear_awaiting(ud)
            ud['awaiting_add_product'] = True
            await query.edit_message_text(
                "✍️ اكتب بالصيغة:\n`parent_id|kind|الاسم|السعر`\n\n"
                "kind: game_code / card / whatsapp_number / telegram_number\n"
                "مثال: `g3|game_code|كود 3200 شدة|45.5`\n(أو /cancel)",
                parse_mode='Markdown')
            return

        if action == "edit_price":
            clear_awaiting(ud)
            ud['awaiting_edit_price'] = True
            await query.edit_message_text("✍️ اكتب بالصيغة: `node_id|السعر_الجديد`\nمثال: `g7|24.5`\n(أو /cancel)", parse_mode='Markdown')
            return

        if action == "toggle":
            clear_awaiting(ud)
            ud['awaiting_toggle'] = True
            await query.edit_message_text("✍️ اكتب معرف العنصر (node_id) لتبديل حالته تفعيل/تعطيل (أو /cancel):")
            return

        if action == "delete_node":
            clear_awaiting(ud)
            ud['awaiting_delete_node'] = True
            await query.edit_message_text("✍️ اكتب معرف العنصر (node_id) لحذفه (قابل للاسترجاع لاحقاً، أو /cancel):")
            return

        if action == "restore_node":
            clear_awaiting(ud)
            ud['awaiting_restore_node'] = True
            await query.edit_message_text("✍️ اكتب معرف العنصر (node_id) لاسترجاعه (أو /cancel):")
            return

        if action == "clean":
            db["pending_orders"] = {}
            save_db(db)
            await query.edit_message_text("🧹 تم تنظيف كل الطلبات المعلقة.")
            return

        if action == "backup":
            backup_data = json.dumps(db, indent=2, ensure_ascii=False)
            await query.edit_message_text("💾 تم إنشاء نسخة احتياطية.")
            await context.bot.send_document(
                chat_id=user_id,
                document=BufferedInputFile(backup_data.encode('utf-8'), filename='database_backup.json'),
                caption="📂 نسخة احتياطية")
            return
        return

    # ---------- جذور الأقسام (مع ترقيم صفحات) ----------
    if data.startswith("root#"):
        parts = data.split('#')
        section, page = parts[1], int(parts[2]) if len(parts) > 2 else 0
        roots = db['catalog_roots'].get(section, [])
        title = {"games": "🎮 اختر اللعبة:", "cards": "🎟️ اختر البطاقة:", "numbers": "📱 اختر النوع:"}.get(section, "اختر:")
        await query.edit_message_text(title, reply_markup=render_listing(db, roots, "store#back", f"root#{section}", page))
        return

    if data == "store#phone":
        await query.edit_message_text("📱 **اختر شبكة الهاتف:**", reply_markup=phone_menu)
        return

    if data == "store#back":
        await query.edit_message_text("🛍️ **اختر القسم:**", reply_markup=store_menu)
        return

    if data.startswith("nav#"):
        parts = data.split('#')
        nid, page = parts[1], int(parts[2]) if len(parts) > 2 else 0
        node = db['catalog'].get(nid)
        if not node:
            await query.edit_message_text("⚠️ هذا القسم غير موجود.")
            return
        await query.edit_message_text(f"📁 **{node['name']}**", reply_markup=render_listing(db, node['children'], back_cb_for(node), f"nav#{nid}", page), parse_mode='Markdown')
        return

    if data.startswith("buy#"):
        nid = data.split('#')[1]
        node = db['catalog'].get(nid)
        if not node or node.get('deleted') or not node.get('active', True) or node.get('price') is None:
            await query.edit_message_text("⚠️ هذا المنتج غير متوفر حالياً.")
            return
        balance = get_balance(db, user_id)
        if balance < node['price']:
            await query.edit_message_text(f"❌ رصيدك (${balance:.2f}) لا يكفي لشراء [{node['name']}]!")
            return

        if node['kind'] == 'game_code':
            clear_awaiting(ud)
            ud['pending_node_id'] = nid
            ud['awaiting_game_id'] = True
            await query.edit_message_text(f"🎁 {node['name']}\n✍️ **أدخل الآيدي (ID) الخاص بك:**", parse_mode='Markdown')
            return

        if node['kind'] in ('whatsapp_number', 'telegram_number'):
            btn = InlineKeyboardMarkup([[InlineKeyboardButton("✅ تأكيد الطلب", callback_data=f"confirm_num#{nid}")]])
            await query.edit_message_text(f"{node.get('warning','')}\n\n🎁 {node['name']}", reply_markup=btn, parse_mode='Markdown')
            return

        order_id = generate_order_id()
        db['pending_orders'][order_id] = {"type": "purchase", "user_id": user_id, "node_id": nid,
                                           "price": node['price'], "item_name": node['name'], "game_id": None}
        save_db(db)
        await context.bot.send_message(
            ADMIN_CHANNEL_ID,
            f"🛒 **طلب شراء بطاقة**\n━━━━━━━━━━━━━━━━━━━━\n📋 رقم الطلب: {order_id}\n"
            f"👤 {update.effective_user.first_name}\n🆔 {user_id}\n🎁 {node['name']}\n💰 ${node['price']}",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("✅ موافقة وخصم", callback_data=f"order_ok#{order_id}")],
                [InlineKeyboardButton("❌ رفض", callback_data=f"order_no#{order_id}")]
            ])
        )
        await query.edit_message_text(f"✅ تم إرسال طلبك (رقم {order_id}) للإدارة، بانتظار الموافقة.")
        return

    if data.startswith("confirm_num#"):
        nid = data.split('#')[1]
        node = db['catalog'].get(nid)
        if not node:
            await query.edit_message_text("⚠️ هذا المنتج غير متوفر.")
            return
        balance = get_balance(db, user_id)
        if balance < node['price']:
            await query.edit_message_text(f"❌ رصيدك (${balance:.2f}) لا يكفي!")
            return
        order_id = generate_order_id()
        db['pending_orders'][order_id] = {"type": "purchase", "user_id": user_id, "node_id": nid,
                                           "price": node['price'], "item_name": node['name'], "game_id": None}
        save_db(db)
        await context.bot.send_message(
            ADMIN_CHANNEL_ID,
            f"📱 **طلب شراء رقم**\n━━━━━━━━━━━━━━━━━━━━\n📋 رقم الطلب: {order_id}\n"
            f"👤 {update.effective_user.first_name}\n🆔 {user_id}\n🎁 {node['name']}\n💰 ${node['price']}",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("✅ موافقة وخصم", callback_data=f"order_ok#{order_id}")],
                [InlineKeyboardButton("❌ رفض", callback_data=f"order_no#{order_id}")]
            ])
        )
        await query.edit_message_text(f"✅ تم إرسال طلبك (رقم {order_id}) للإدارة، بانتظار الموافقة.")
        return

    # ---------- موافقة/رفض الشراء ----------
    if data.startswith("order_ok#"):
        order_id = data.split('#')[1]
        order = db['pending_orders'].get(order_id)
        if not order:
            await query.edit_message_text("⚠️ هذا الطلب لم يعد موجوداً (ربما تمت معالجته مسبقاً).")
            return
        target_id = order['user_id']
        balance = get_balance(db, target_id)
        if balance < order['price']:
            await query.edit_message_text("❌ رصيد الزبون لم يعد كافياً!")
            return
        update_balance(db, target_id, -order['price'])
        save_db(db)
        await query.edit_message_text(f"✅ تم خصم ${order['price']} من الزبون (رقم الطلب {order_id}).\n📩 تحقق من رسائلك الخاصة مع البوت لإدخال الكود.")
        clear_awaiting(ud)
        ud['awaiting_delivery_code'] = True
        ud['delivery_order_id'] = order_id
        await notify_admin_dm(
            context,
            f"✍️ **اكتب الآن هنا** الكود/الرقم/المعلومات لتسليمها للزبون (طلب {order_id} — {order.get('item_name','')}):"
        )
        return

    if data.startswith("order_no#"):
        order_id = data.split('#')[1]
        order = db['pending_orders'].pop(order_id, None)
        save_db(db)
        await query.edit_message_text(f"❌ تم رفض الطلب (رقم {order_id})")
        if order:
            await context.bot.send_message(order['user_id'], f"❌ عذراً، تم رفض طلبك (رقم {order_id}).")
        return

    if data.startswith("charge_ok#"):
        order_id = data.split('#')[1]
        order = db['pending_orders'].pop(order_id, None)
        save_db(db)
        if not order:
            await query.edit_message_text("⚠️ هذا الطلب لم يعد موجوداً.")
            return
        update_balance(db, order['user_id'], order['usd_amount'])
        save_db(db)
        await query.edit_message_text(f"✅ تم قبول الشحن (رقم {order_id}) وإضافة ${order['usd_amount']:.2f}")
        await context.bot.send_message(order['user_id'], f"✅ تم شحن ${order['usd_amount']:.2f} إلى محفظتك (رقم {order_id}).")
        return

    if data.startswith("charge_no#"):
        order_id = data.split('#')[1]
        order = db['pending_orders'].pop(order_id, None)
        save_db(db)
        await query.edit_message_text(f"❌ تم رفض طلب الشحن (رقم {order_id})")
        if order:
            await context.bot.send_message(order['user_id'], f"❌ عذراً، تم رفض طلب الشحن (رقم {order_id}). تأكد من صحة إثبات الدفع.")
        return

    if data.startswith("refund_ok#"):
        order_id = data.split('#')[1]
        order = db['pending_orders'].pop(order_id, None)
        save_db(db)
        if not order:
            await query.edit_message_text("⚠️ هذا الطلب لم يعد موجوداً.")
            return
        update_balance(db, order['user_id'], -order['amount'])
        save_db(db)
        await query.edit_message_text(f"✅ تم قبول الاسترجاع (رقم {order_id}) وخصم ${order['amount']:.2f}")
        await context.bot.send_message(order['user_id'], f"✅ تم استرجاع ${order['amount']:.2f} وسيتم تحويلها لك (رقم {order_id}).")
        return

    if data.startswith("refund_no#"):
        order_id = data.split('#')[1]
        order = db['pending_orders'].pop(order_id, None)
        save_db(db)
        await query.edit_message_text(f"❌ تم رفض طلب الاسترجاع (رقم {order_id})")
        if order:
            await context.bot.send_message(order['user_id'], f"❌ عذراً، تم رفض طلب استرجاع الأموال (رقم {order_id}).")
        return

    if data.startswith("phone_ok#"):
        order_id = data.split('#')[1]
        order = db['pending_orders'].pop(order_id, None)
        save_db(db)
        if not order:
            await query.edit_message_text("⚠️ هذا الطلب لم يعد موجوداً.")
            return
        update_balance(db, order['user_id'], -order['usd_amount'])
        save_db(db)
        await query.edit_message_text(f"✅ تم قبول طلب شحن الهاتف (رقم {order_id})")
        await context.bot.send_message(
            order['user_id'],
            f"✅ **تم شحن هاتفك!**\n📋 رقم الطلب: {order_id}\n📞 {order['phone']}\n📶 {order['card_type']}\n💰 {order['syr_amount']:,.0f} ل.س"
        )
        return

    if data.startswith("phone_no#"):
        order_id = data.split('#')[1]
        order = db['pending_orders'].pop(order_id, None)
        save_db(db)
        await query.edit_message_text(f"❌ تم رفض طلب الشحن (رقم {order_id})")
        if order:
            await context.bot.send_message(order['user_id'], f"❌ عذراً، تم رفض طلب شحن الهاتف (رقم {order_id}).")
        return

    if data.startswith("phone#"):
        card_type = data.split('#')[1]
        ud['card_type'] = card_type.upper()
        clear_awaiting(ud)
        ud['awaiting_phone'] = True
        await query.edit_message_text(f"✍️ **أدخل رقم الهاتف** ({card_type.upper()}):")
        return

    if data.startswith("charge#"):
        currency = data.split('#')[1]
        clear_awaiting(ud)
        ud['charge_currency'] = currency
        ud['awaiting_charge'] = True
        await query.edit_message_text(f"✍️ **أدخل المبلغ** {'بالدولار' if currency=='usd' else 'بالليرة السورية'}:")
        return

    if data.startswith("refund#"):
        currency = data.split('#')[1]
        clear_awaiting(ud)
        ud['refund_currency'] = currency
        ud['awaiting_refund'] = True
        await query.edit_message_text(f"✍️ **أدخل المبلغ** {'بالدولار' if currency=='usd' else 'بالليرة السورية'} المراد استرجاعه:")
        return

    if data == "bot_order#start":
        clear_awaiting(ud)
        ud['awaiting_bot_desc'] = True
        await query.edit_message_text("🤖 **إنشاء بوت جديد**\n✍️ اكتب مواصفات البوت الذي تريده:")
        return

    if data.startswith("srv#"):
        srv_type = data.split('#')[1]
        srv_name = "🔥 قوي 24 ساعة (5$/شهر + أسبوع مجاناً)" if srv_type == 'strong' else "💤 عادي 12-18 ساعة (2$/شهر)"
        desc = ud.get('bot_desc', 'غير محدد')
        contact = ud.get('bot_contact', 'غير محدد')
        order_id = generate_order_id()
        await query.edit_message_text("🚀 جاري إرسال الطلب للإدارة...")
        await context.bot.send_message(
            ADMIN_CHANNEL_ID,
            f"🤖 **طلب إنشاء بوت جديد**\n📋 رقم الطلب: {order_id}\n👤 {update.effective_user.first_name}\n"
            f"🆔 {user_id}\n💬 {contact}\n📝 {desc}\n🖥️ {srv_name}",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("💰 السعر", callback_data=f"bot_price#{user_id}#{order_id}")],
                [InlineKeyboardButton("⏰ الوقت", callback_data=f"bot_time#{user_id}#{order_id}")],
                [InlineKeyboardButton("📂 ملف", callback_data=f"bot_file#{user_id}#{order_id}")],
                [InlineKeyboardButton("❌ رفض", callback_data=f"bot_reject#{user_id}#{order_id}")]
            ])
        )
        ud['awaiting_bot_desc'] = False
        ud['awaiting_bot_contact'] = False
        return

    if data.startswith("bot_price#"):
        parts = data.split('#')
        clear_awaiting(ud)
        ud['bot_target_id'] = parts[1]
        ud['awaiting_bot_price'] = True
        await query.edit_message_text(f"📩 تحقق من رسائلك الخاصة مع البوت لكتابة السعر (طلب {parts[2]}).")
        await notify_admin_dm(context, f"✍️ اكتب السعر الآن هنا للمستخدم `{parts[1]}` (طلب {parts[2]}):")
        return

    if data.startswith("bot_time#"):
        parts = data.split('#')
        clear_awaiting(ud)
        ud['bot_target_id'] = parts[1]
        ud['awaiting_bot_time'] = True
        await query.edit_message_text(f"📩 تحقق من رسائلك الخاصة مع البوت لكتابة الوقت (طلب {parts[2]}).")
        await notify_admin_dm(context, f"✍️ اكتب الوقت المتوقع الآن هنا للمستخدم `{parts[1]}` (طلب {parts[2]}):")
        return

    if data.startswith("bot_file#"):
        parts = data.split('#')
        clear_awaiting(ud)
        ud['bot_target_id'] = parts[1]
        ud['awaiting_bot_file'] = True
        await query.edit_message_text(f"📩 تحقق من رسائلك الخاصة مع البوت لإرسال الملف (طلب {parts[2]}).")
        await notify_admin_dm(context, f"📤 أرسل ملف البوت الآن هنا (كـ Document) للمستخدم `{parts[1]}` (طلب {parts[2]}):")
        return

    if data.startswith("bot_reject#"):
        parts = data.split('#')
        await query.edit_message_text(f"❌ تم رفض طلب البوت (رقم {parts[2]})")
        await context.bot.send_message(parts[1], f"❌ عذراً، تم رفض طلب إنشاء البوت (رقم {parts[2]}).")
        return

    if data == "main_menu":
        await context.bot.send_message(chat_id=update.effective_chat.id, text="🎯 **القائمة الرئيسية**", reply_markup=main_menu, parse_mode='Markdown')
        return

    await query.edit_message_text("⚠️ هذا الزر غير مفعل حالياً.")


# ==================== تشغيل البوت ====================
def main():
    app = Application.builder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("admin", admin_command))
    app.add_handler(CommandHandler("panel", panel_command))
    app.add_handler(CommandHandler("cancel", cancel_command))
    app.add_handler(CallbackQueryHandler(handle_callback))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND & filters.ChatType.PRIVATE, handle_text))
    app.add_handler(MessageHandler((filters.PHOTO | filters.Document.ALL) & filters.ChatType.PRIVATE, handle_photo_and_document))
    app.add_handler(MessageHandler(filters.ChatType.CHANNEL, handle_channel_post))
    print("🚀 البوت شغال بالبايثون!")
    app.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()
