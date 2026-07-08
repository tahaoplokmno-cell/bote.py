import json
import os
import random
import re
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

REDEMPTION_INSTRUCTIONS = (
    "\n\n📦 **تعليمات الاستبدال:**\n"
    "1️⃣ ادخل إلى الموقع الرسمي للشحن\n"
    "2️⃣ اختر لعبتك وأدخل آيدي حسابك\n"
    "3️⃣ اختر استرداد الاكواد وأدخل الكود\n"
    "4️⃣ اضغط استرداد\n"
    "🔔 شغّل VPN إذا كنت داخل سوريا"
)

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
    add("g29", "🎯 كود روبوكس 10$ ~ 11.0$", "games", "g28", "product", "game_code", 11.0)
    add("g30", "🎯 كود روبوكس 15$ ~ 16.02$", "games", "g28", "product", "game_code", 16.02)

    add("g31", "📁 FC Mobile", "games", None, "folder")
    add("g32", "📁 FC Mobile Cambodia", "games", "g31", "folder")
    add("g33", "🎯 Silver 99 ~ 1.20$", "games", "g32", "product", "game_code", 1.20)
    add("g34", "🎯 Silver 499 ~ 5.99$", "games", "g32", "product", "game_code", 5.99)
    add("g35", "🎯 100 FC Points ~ 1.20$", "games", "g32", "product", "game_code", 1.20)
    add("g36", "🎯 520 FC Points ~ 5.99$", "games", "g32", "product", "game_code", 5.99)

    add("g37", "📁 Minecraft", "games", None, "folder")
    add("g38", "🎯 كود 3500 كوينز ~ 22.0$", "games", "g37", "product", "game_code", 22.0)
    add("g39", "🎯 كود 1720 كوينز ~ 11.0$", "games", "g37", "product", "game_code", 11.0)

    add("g40", "📁 Stumble Guys (نفذ المخزون)", "games", None, "folder")

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
        "⚠️ **تنبيه هام:**\n"
        "سيتم إظهار الرقم بشكل مباشر\n"
        "❌ حال لم يصل كود التفعيل، سيتم رفض الطلب تلقائياً\n"
        "🚫 ممنوع طلب الكود مرتين على نفس الرقم\n"
        "⚠️ الأرقام وهمية وغير مكفولة"
    )
    add("n2", "📁 أرقام واتساب", "numbers", None, "folder")
    add("n3", "🎯 المانيا 49+ ~ 2.00$", "numbers", "n2", "product", "whatsapp_number", 2.00, warning=number_warning)
    add("n4", "🎯 مصر 20+ ~ 1.50$", "numbers", "n2", "product", "whatsapp_number", 1.50, warning=number_warning)
    add("n5", "🎯 بريطانيا 44+ ~ 1.00$", "numbers", "n2", "product", "whatsapp_number", 1.00, warning=number_warning)
    add("n6", "📁 أرقام تيليجرام (نفذ المخزون)", "numbers", None, "folder")

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
        "users": {}, "banned": {}, "exchange_rate": 13800,
        "admin_notes": "", "bot_maintenance": False, "pending_orders": {},
        "catalog": default_catalog(), "catalog_roots": default_roots(),
        "next_node_seq": 100, "authenticated_admins": [],
        "stats": {"purchases": 0, "refunds": 0, "deposits": 0, "complaints": 0},
        "activity_log": [], "bot_orders": {},
        "user_history": {}  # {"user_id": [{"type":"deposit/purchase/refund", "amount":X, "date":"..."}]}
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
    # تسجيل في السجل
    if amount != 0:
        htype = "deposit" if amount > 0 else "purchase" if amount < 0 else "refund"
        db.setdefault("user_history", {}).setdefault(uid, []).append({
            "type": htype, "amount": amount, "date": datetime.now().isoformat()
        })


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


def is_admin(db, user_id):
    return str(user_id) in db.get("authenticated_admins", [])


def log_activity(db, text):
    db.setdefault("activity_log", []).append(f"{datetime.now().strftime('%m-%d %H:%M')} | {text}")
    db["activity_log"] = db["activity_log"][-50:]


async def notify_admin_dm(context, text, markup=None):
    try:
        await context.bot.send_message(ADMIN_ID, text, reply_markup=markup)
    except:
        pass


def clear_awaiting(ud):
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

support_menu = InlineKeyboardMarkup([
    [InlineKeyboardButton("📩 إرسال شكوى / استفسار", callback_data="support#start")],
    [InlineKeyboardButton("🔙 القائمة الرئيسية", callback_data="main_menu")]
])

CANCEL_BTN = InlineKeyboardMarkup([[InlineKeyboardButton("❌ إلغاء العملية", callback_data="cancel_flow")]])


def get_admin_main_panel(db):
    """لوحة التحكم الرئيسية"""
    total_users = len(db.get("users", {}))
    s = db.get("stats", {})
    maintenance = "🛠️ مفعل" if db.get("bot_maintenance") else "✅ متوقف"
    total_balance = sum(u.get("balance_usd", 0) for u in db["users"].values())
    
    return InlineKeyboardMarkup([
        [InlineKeyboardButton(f"📊 إحصائيات شاملة", callback_data="adm#stats")],
        [InlineKeyboardButton(f"💰 إجمالي الأرصدة: ${total_balance:.2f}", callback_data="adm#view_balances")],
        [InlineKeyboardButton(f"👥 المستخدمين: {total_users} | 📩 الشكاوى: {s.get('complaints',0)}", callback_data="adm#users")],
        [InlineKeyboardButton(f"📦 الطلبات المعلقة: {len(db.get('pending_orders',{}))}", callback_data="adm#pending_list")],
        [InlineKeyboardButton(f"🛠️ الصيانة: {maintenance}", callback_data="adm#toggle_maintenance")],
        [InlineKeyboardButton("📋 آخر العمليات (سجل)", callback_data="adm#log"),
         InlineKeyboardButton("🔎 بحث عن مستخدم", callback_data="adm#search_user")],
        [InlineKeyboardButton("🤖 بحث عن طلب بوت", callback_data="adm#search_bot_order"),
         InlineKeyboardButton("📝 ملاحظات الإدارة", callback_data="adm#admin_notes")],
        [InlineKeyboardButton("👮 قائمة الأدمنية", callback_data="adm#list_admins"),
         InlineKeyboardButton("📤 تصدير المستخدمين", callback_data="adm#export_users")],
        [InlineKeyboardButton("📢 إرسال إعلان", callback_data="adm#broadcast"),
         InlineKeyboardButton("📊 عرض الأرصدة", callback_data="adm#view_balances")],
        [InlineKeyboardButton("➕ إضافة رصيد", callback_data="adm#add_balance"),
         InlineKeyboardButton("➖ خصم رصيد", callback_data="adm#sub_balance")],
        [InlineKeyboardButton("🚫 حظر مستخدم", callback_data="adm#ban_user"),
         InlineKeyboardButton("✅ رفع الحظر", callback_data="adm#unban_user")],
        [InlineKeyboardButton("📈 تعديل سعر الصرف", callback_data="adm#edit_rate")],
        [InlineKeyboardButton("🗂️ عرض شجرة المتجر", callback_data="adm#tree")],
        [InlineKeyboardButton("➕ إضافة قسم", callback_data="adm#add_category"),
         InlineKeyboardButton("➕ إضافة منتج", callback_data="adm#add_product")],
        [InlineKeyboardButton("✏️ تعديل سعر منتج", callback_data="adm#edit_price"),
         InlineKeyboardButton("⛔ تعطيل/تفعيل منتج", callback_data="adm#toggle")],
        [InlineKeyboardButton("🗑️ حذف عنصر", callback_data="adm#delete_node"),
         InlineKeyboardButton("♻️ استرجاع محذوف", callback_data="adm#restore_node")],
        [InlineKeyboardButton("🧹 تنظيف الطلبات المعلقة", callback_data="adm#clean")],
        [InlineKeyboardButton("💾 نسخة احتياطية", callback_data="adm#backup")],
        [InlineKeyboardButton("📌 نشر لوحة التحكم في القناة", callback_data="adm#post_channel")],
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


def safe_md(text):
    """تهريب آمن لأحرف Markdown"""
    if not text:
        return ""
    return str(text).replace('*', '\\*').replace('_', '\\_').replace('`', '\\`').replace('[', '\\[')


# ==================== أوامر البوت ====================
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = str(update.effective_user.id)
    db = load_db()
    if user_id in db.get("banned", {}):
        await update.message.reply_text("🚫 حسابك محظور من استخدام هذا البوت.")
        return
    if user_id not in db["users"]:
        db["users"][user_id] = {"name": update.effective_user.first_name or "مستخدم", "balance_usd": 0, "joined": datetime.now().isoformat()}
        save_db(db)
    balance = db["users"][user_id]["balance_usd"]
    rate = db.get("exchange_rate", 13800)
    name = safe_md(update.effective_user.first_name or "مستخدم")
    text = (
        f"🔥 **أهلاً بك في بوت شام إن جيم** 🔥\n"
        f"━━━━━━━━━━━━━━━━━━━━\n"
        f"👤 مرحباً: {name}\n"
        f"💰 رصيدك: ${balance:.2f}\n"
        f"🇸🇾 بالليرة: {balance * rate:,.0f} ل.س\n"
        f"📈 سعر الصرف: 1$ = {rate:,} ل.س\n"
        f"━━━━━━━━━━━━━━━━━━━━\n"
        f"⚠️ استخدم الأزرار للتنقل"
    )
    if is_night_time():
        text += "\n\n🌙 **ملاحظة:** نحن خارج أوقات الدعم المباشر"
    await update.message.reply_text(text, reply_markup=main_menu)


async def admin_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    db = load_db()
    user_id = str(update.effective_user.id)
    if is_admin(db, user_id):
        await update.message.reply_text("✅ أنت مصادق بالفعل! استخدم /panel للوحة التحكم.")
        return
    clear_awaiting(context.user_data)
    context.user_data['awaiting_password'] = True
    await update.message.reply_text("🔐 اكتب كلمة السر للتحقق:")


async def panel_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    db = load_db()
    user_id = str(update.effective_user.id)
    if is_admin(db, user_id):
        await update.message.reply_text("🛸 **لوحة التحكم الإدارية**", reply_markup=get_admin_main_panel(db))
    else:
        await update.message.reply_text("❌ ليس لديك صلاحية. استخدم /admin أولاً.")


async def cancel_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    db = load_db()
    user_id = str(update.effective_user.id)
    context.user_data.clear()
    await update.message.reply_text("✅ تم إلغاء أي عملية معلقة.", reply_markup=main_menu)
    if is_admin(db, user_id):
        await update.message.reply_text(
            "لديك صلاحية أدمن. اضغط لفتح لوحة التحكم:",
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🛸 فتح لوحة التحكم", callback_data="open_panel")]])
        )


# ==================== معالج النصوص ====================
async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message or not update.message.text:
        return
    user_id = str(update.effective_user.id)
    text = update.message.text
    db = load_db()
    ud = context.user_data

    if user_id in db.get("banned", {}) and not is_admin(db, user_id):
        await update.message.reply_text("🚫 حسابك محظور.")
        return

    if db.get("bot_maintenance", False) and not is_admin(db, user_id):
        await update.message.reply_text("🛠️ البوت في وضع الصيانة، الرجاء المحاولة لاحقاً.")
        return

    if ud.get('awaiting_charge_proof'):
        amount = ud.get('charge_amount')
        usd_amount = ud.get('charge_usd_amount')
        currency = ud.get('charge_currency', 'usd')
        order_id = generate_order_id()
        db['pending_orders'][order_id] = {"type": "charge", "user_id": user_id, "usd_amount": usd_amount,
                                           "amount": amount, "currency": currency, "ref": text}
        save_db(db)
        await context.bot.send_message(
            ADMIN_CHANNEL_ID,
            f"🏦 طلب شحن رصيد\n━━━━━━━━━━━━━━━━━━━━\n"
            f"📋 رقم الطلب: {order_id}\n"
            f"👤 {safe_md(update.effective_user.first_name or 'مستخدم')}\n"
            f"🆔 {user_id}\n"
            f"💰 {amount} {'$' if currency=='usd' else 'ل.س'} = ${usd_amount:.2f}\n"
            f"🧾 المرجع: {safe_md(text)}",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("✅ قبول", callback_data=f"charge_ok#{order_id}")],
                [InlineKeyboardButton("❌ رفض", callback_data=f"charge_no#{order_id}")]
            ])
        )
        ud['awaiting_charge_proof'] = False
        await update.message.reply_text(f"🚀 تم إرسال طلب الشحن (رقم {order_id}) للإدارة.")
        return

    if text == '🏪 المتجر':
        await update.message.reply_text("🛍️ اختر القسم:", reply_markup=store_menu)
        return
    if text == '💳 المحفظة':
        balance = get_balance(db, user_id)
        await update.message.reply_text(f"💳 رصيدك الحالي:\n💰 ${balance:.2f}", reply_markup=wallet_menu)
        return
    if text == '💰 استرجاع الأموال':
        await update.message.reply_text("💰 اختر عملة الاسترجاع:", reply_markup=refund_menu)
        return
    if text == '🤖 إنشاء بوت':
        clear_awaiting(ud)
        ud['awaiting_bot_desc'] = True
        await update.message.reply_text("🤖 اكتب مواصفات البوت الذي تريده:", reply_markup=CANCEL_BTN)
        return
    if text == '⚙️ الإعدادات':
        await update.message.reply_text(f"⚙️ الإعدادات\n👤 {safe_md(update.effective_user.first_name or 'مستخدم')}\n🆔 {user_id}")
        return
    if text == '📞 الدعم الفني':
        await update.message.reply_text(
            f"📞 الدعم الفني\nللتواصل: {DEVELOPER_USERNAME}\nأو أرسل شكواك من هنا:",
            reply_markup=support_menu
        )
        return

    if ud.get('awaiting_password'):
        ud['awaiting_password'] = False
        if text.strip() == ADMIN_PASSWORD:
            if user_id not in db['authenticated_admins']:
                db['authenticated_admins'].append(user_id)
                save_db(db)
            await update.message.reply_text("✅ تم التحقق! استخدم /panel للوحة التحكم.")
        else:
            await update.message.reply_text("❌ كلمة سر خاطئة!")
        return

    # شكوى
    if ud.get('awaiting_complaint'):
        ud['awaiting_complaint'] = False
        db['stats']['complaints'] += 1
        log_activity(db, f"شكوى من {user_id}")
        save_db(db)
        try:
            await context.bot.send_message(
                ADMIN_CHANNEL_ID,
                f"📩 شكوى جديدة\n👤 {safe_md(update.effective_user.first_name or 'مستخدم')}\n🆔 {user_id}\n\n📝 {safe_md(text)}",
                reply_markup=InlineKeyboardMarkup([
                    [InlineKeyboardButton("↩️ الرد على الزبون", callback_data=f"reply_user#{user_id}")]
                ])
            )
            await update.message.reply_text("✅ تم استلام رسالتك.")
        except:
            await update.message.reply_text("✅ تم استلام رسالتك.")
        return

    if ud.get('awaiting_reply_to_user'):
        target_id = ud.get('reply_target_id')
        ud['awaiting_reply_to_user'] = False
        try:
            await context.bot.send_message(target_id, f"💬 رد الدعم الفني:\n{text}")
            await update.message.reply_text(f"✅ تم إرسال الرد إلى {target_id}")
        except Exception as e:
            await update.message.reply_text(f"❌ فشل الإرسال: {e}")
        return

    # تدفقات الأدمن
    if ud.get('awaiting_broadcast'):
        ud['awaiting_broadcast'] = False
        await update.message.reply_text("🚀 جاري الإرسال...")
        count = 0
        for uid in db["users"]:
            try:
                await context.bot.send_message(uid, f"📢 إعلان عام\n━━━━━━━━━━━━━━━━━━━━\n{text}")
                count += 1
            except:
                pass
        await update.message.reply_text(f"✅ تم الإرسال إلى {count} مستخدم.")
        return

    if ud.get('awaiting_add_balance'):
        try:
            parts = text.split('|')
            target_id, amount = parts[0].strip(), float(parts[1].strip())
            if amount <= 0:
                raise ValueError
            update_balance(db, target_id, amount)
            log_activity(db, f"إضافة ${amount} لـ {target_id}")
            save_db(db)
            await update.message.reply_text(f"✅ تم إضافة ${amount} إلى {safe_md(db['users'].get(target_id,{}).get('name','?'))}")
            await context.bot.send_message(target_id, f"🎉 تم إضافة ${amount} إلى محفظتك!")
        except:
            await update.message.reply_text("❌ صيغة خاطئة! استخدم: آيدي|المبلغ", reply_markup=CANCEL_BTN)
            return
        ud['awaiting_add_balance'] = False
        return

    if ud.get('awaiting_sub_balance'):
        try:
            parts = text.split('|')
            target_id, amount = parts[0].strip(), float(parts[1].strip())
            if amount <= 0:
                raise ValueError
            update_balance(db, target_id, -amount)
            log_activity(db, f"خصم ${amount} من {target_id}")
            save_db(db)
            await update.message.reply_text(f"✅ تم خصم ${amount} من {safe_md(db['users'].get(target_id,{}).get('name','?'))}")
            await context.bot.send_message(target_id, f"⚠️ تم خصم ${amount} من محفظتك.")
        except:
            await update.message.reply_text("❌ صيغة خاطئة! استخدم: آيدي|المبلغ", reply_markup=CANCEL_BTN)
            return
        ud['awaiting_sub_balance'] = False
        return

    if ud.get('awaiting_ban_user'):
        target_id = text.strip()
        db.setdefault("banned", {})[target_id] = True
        log_activity(db, f"حظر {target_id}")
        save_db(db)
        await update.message.reply_text(f"🚫 تم حظر {target_id}")
        ud['awaiting_ban_user'] = False
        return

    if ud.get('awaiting_unban_user'):
        target_id = text.strip()
        db.setdefault("banned", {}).pop(target_id, None)
        log_activity(db, f"رفع الحظر عن {target_id}")
        save_db(db)
        await update.message.reply_text(f"✅ تم رفع الحظر عن {target_id}")
        ud['awaiting_unban_user'] = False
        return

    if ud.get('awaiting_search_user'):
        target = text.strip()
        info = db['users'].get(target)
        ud['awaiting_search_user'] = False
        if not info:
            await update.message.reply_text("❌ لا يوجد مستخدم.")
            return
        history = db.get('user_history', {}).get(target, [])
        hist_text = "\n".join([f"{h['date'][:10]} - {h['type']}: ${h['amount']:.2f}" for h in history[-10:]]) or "لا يوجد"
        await update.message.reply_text(
            f"🔎 بيانات المستخدم\n🆔 {target}\n👤 {safe_md(info.get('name','?'))}\n"
            f"💰 ${info.get('balance_usd',0):.2f}\n🚫 محظور: {'نعم' if target in db.get('banned',{}) else 'لا'}\n"
            f"📅 انضم: {info.get('joined','?')[:10]}\n\n📋 آخر العمليات:\n{hist_text}"
        )
        return

    if ud.get('awaiting_search_bot_order'):
        query_val = text.strip()
        ud['awaiting_search_bot_order'] = False
        bot_orders = db.get('bot_orders', {})
        found = []
        if query_val in bot_orders:
            found = [(query_val, bot_orders[query_val])]
        else:
            found = [(oid, o) for oid, o in bot_orders.items() if o.get('user_id') == query_val]
        if not found:
            await update.message.reply_text("❌ لم يتم إيجاد أي طلب.")
            return
        for oid, o in found[:5]:
            price_txt = f"${o['price']:.2f}" if o.get('price') else "غير محدد"
            msg = (
                f"🤖 طلب بوت {oid}\n👤 {o.get('user_id')}\n💬 {safe_md(o.get('contact',''))}\n"
                f"📝 {safe_md(o.get('desc',''))}\n🖥️ {safe_md(o.get('srv_name',''))}\n"
                f"💰 {price_txt}\n📌 {o.get('status')}\n🗒️ {safe_md(o.get('details') or 'لا يوجد')}"
            )
            buttons = []
            if o.get('file_id'):
                buttons.append([InlineKeyboardButton("📂 إعادة إرسال الملف", callback_data=f"resend_botfile#{oid}")])
            await update.message.reply_text(msg, reply_markup=InlineKeyboardMarkup(buttons) if buttons else None)
        return

    if ud.get('awaiting_admin_notes'):
        db['admin_notes'] = text
        save_db(db)
        ud['awaiting_admin_notes'] = False
        await update.message.reply_text("✅ تم تحديث الملاحظات.")
        return

    if ud.get('awaiting_new_rate'):
        try:
            r = float(text)
            if r <= 0:
                raise ValueError
            db['exchange_rate'] = r
            save_db(db)
            await update.message.reply_text(f"✅ سعر الصرف الآن: {r:,} ل.س")
        except:
            await update.message.reply_text("❌ اكتب رقماً صحيحاً!", reply_markup=CANCEL_BTN)
            return
        ud['awaiting_new_rate'] = False
        return

    if ud.get('awaiting_add_category'):
        try:
            parts = text.split('|')
            parent_raw, section, name = parts[0].strip(), parts[1].strip(), parts[2].strip()
            parent = None if parent_raw.lower() == 'root' else parent_raw
            if section not in db['catalog_roots']:
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
            await update.message.reply_text(f"✅ تم إضافة القسم [{name}] بمعرف {nid}")
        except:
            await update.message.reply_text("❌ صيغة: parent_او_root|games_او_cards_او_numbers|الاسم", reply_markup=CANCEL_BTN)
            return
        ud['awaiting_add_category'] = False
        return

    if ud.get('awaiting_add_product'):
        try:
            parts = text.split('|')
            parent, kind, name, price = parts[0].strip(), parts[1].strip(), parts[2].strip(), float(parts[3].strip())
            if parent not in db['catalog'] or price <= 0:
                raise ValueError
            nid = new_node_id(db, "x")
            db['catalog'][nid] = {"name": f"🎯 {name} ~ {price}$", "section": db['catalog'][parent]['section'],
                                   "parent": parent, "type": "product", "kind": kind, "price": price,
                                   "active": True, "deleted": False, "children": [], "warning": None}
            db['catalog'][parent]['children'].append(nid)
            save_db(db)
            await update.message.reply_text(f"✅ تم إضافة المنتج [{name}] بمعرف {nid}")
        except:
            await update.message.reply_text("❌ صيغة: parent_id|kind|الاسم|السعر", reply_markup=CANCEL_BTN)
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
            await update.message.reply_text(f"✅ تم تعديل سعر {nid} إلى {price}$")
        except:
            await update.message.reply_text("❌ صيغة: node_id|السعر", reply_markup=CANCEL_BTN)
            return
        ud['awaiting_edit_price'] = False
        return

    if ud.get('awaiting_toggle'):
        nid = text.strip()
        node = db['catalog'].get(nid)
        if not node:
            await update.message.reply_text("❌ لا يوجد عنصر.", reply_markup=CANCEL_BTN)
            return
        node['active'] = not node.get('active', True)
        save_db(db)
        await update.message.reply_text(f"✅ الحالة: {'مفعّل' if node['active'] else 'معطّل'}")
        ud['awaiting_toggle'] = False
        return

    if ud.get('awaiting_delete_node'):
        nid = text.strip()
        node = db['catalog'].get(nid)
        if not node:
            await update.message.reply_text("❌ لا يوجد عنصر.", reply_markup=CANCEL_BTN)
            return
        node['deleted'] = True
        save_db(db)
        await update.message.reply_text(f"🗑️ تم حذف {nid} (يمكن استرجاعه)")
        ud['awaiting_delete_node'] = False
        return

    if ud.get('awaiting_restore_node'):
        nid = text.strip()
        node = db['catalog'].get(nid)
        if not node:
            await update.message.reply_text("❌ لا يوجد عنصر.", reply_markup=CANCEL_BTN)
            return
        node['deleted'] = False
        save_db(db)
        await update.message.reply_text(f"♻️ تم استرجاع {nid}")
        ud['awaiting_restore_node'] = False
        return

    # شحن رصيد
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
                f"📸 المبلغ: {amount} {'$' if currency=='usd' else 'ل.س'} = ${usd_amount:.2f}\n"
                f"أرسل صورة الوصل أو اكتب رقم المرجع:",
                reply_markup=CANCEL_BTN
            )
        except:
            await update.message.reply_text("❌ اكتب رقماً صحيحاً!", reply_markup=CANCEL_BTN)
            return
        ud['awaiting_charge'] = False
        return

    # استرجاع
    if ud.get('awaiting_refund'):
        try:
            amount = float(text)
            if amount <= 0:
                raise ValueError
            currency = ud.get('refund_currency', 'usd')
            usd_amount = amount if currency == 'usd' else amount / db.get('exchange_rate', 13800)
            balance = get_balance(db, user_id)
            if balance < usd_amount:
                await update.message.reply_text(f"❌ رصيدك (${balance:.2f}) غير كافٍ!")
                ud['awaiting_refund'] = False
                return
            ud['refund_amount'] = amount
            ud['refund_usd_amount'] = usd_amount
            ud['awaiting_refund'] = False
            btn = InlineKeyboardMarkup([
                [InlineKeyboardButton("✅ تأكيد", callback_data="confirm_refund")],
                [InlineKeyboardButton("❌ إلغاء", callback_data="cancel_flow")]
            ])
            await update.message.reply_text(
                f"💰 المبلغ: {amount} {'$' if currency=='usd' else 'ل.س'} = ${usd_amount:.2f}\nهل تؤكد؟",
                reply_markup=btn
            )
        except:
            await update.message.reply_text("❌ اكتب رقماً صحيحاً!", reply_markup=CANCEL_BTN)
            return
        return

    # آيدي اللعبة
    if ud.get('awaiting_game_id'):
        game_id = text
        node_id = ud.get('pending_node_id')
        node = db['catalog'].get(node_id)
        ud['awaiting_game_id'] = False
        if not node:
            await update.message.reply_text("❌ حدث خطأ.")
            return
        ud['pending_game_id'] = game_id
        btn = InlineKeyboardMarkup([
            [InlineKeyboardButton("✅ تأكيد الشراء", callback_data=f"confirm_game_buy#{node_id}")],
            [InlineKeyboardButton("❌ إلغاء", callback_data="cancel_flow")]
        ])
        await update.message.reply_text(
            f"🎁 {safe_md(node['name'])}\n💰 السعر: ${node['price']}\n🆔 الآيدي: {safe_md(game_id)}\n\nتأكد من الآيدي!",
            reply_markup=btn
        )
        return

    # شحن هاتف
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
                await update.message.reply_text(f"❌ رصيدك غير كافٍ!")
                ud['awaiting_phone_amount'] = False
                return
            ud['phone_amount'] = amount
            ud['phone_usd_amount'] = usd_amount
            ud['awaiting_phone_amount'] = False
            btn = InlineKeyboardMarkup([
                [InlineKeyboardButton("✅ تأكيد الشحن", callback_data="confirm_phone_order")],
                [InlineKeyboardButton("❌ إلغاء", callback_data="cancel_flow")]
            ])
            await update.message.reply_text(
                f"📱 مراجعة شحن الهاتف\n📞 {safe_md(ud.get('phone_number',''))}\n"
                f"📶 {ud.get('card_type')}\n💰 {amount:,.0f} ل.س (${usd_amount:.2f})\n\nتأكد من الرقم!",
                reply_markup=btn
            )
        except:
            await update.message.reply_text("❌ اكتب رقماً صحيحاً!", reply_markup=CANCEL_BTN)
            return
        return

    # إنشاء بوت
    if ud.get('awaiting_bot_desc'):
        ud['bot_desc'] = text
        ud['awaiting_bot_desc'] = False
        ud['awaiting_bot_contact'] = True
        await update.message.reply_text("✍️ أرسل رقم تواصلك:", reply_markup=CANCEL_BTN)
        return

    if ud.get('awaiting_bot_contact'):
        ud['bot_contact'] = text
        ud['awaiting_bot_contact'] = False
        server_btn = InlineKeyboardMarkup([
            [InlineKeyboardButton("🔥 سيرفر قوي 24 ساعة (5$/شهر)", callback_data="srv#strong")],
            [InlineKeyboardButton("💤 سيرفر عادي 12-18 ساعة (2$/شهر)", callback_data="srv#normal")]
        ])
        await update.message.reply_text("🖥️ اختر نوع السيرفر:", reply_markup=server_btn)
        return

    if ud.get('awaiting_bot_price'):
        target_id = ud.get('bot_target_id')
        order_id = ud.get('bot_order_id')
        ud['awaiting_bot_price'] = False
        m = re.search(r'(\d+(\.\d+)?)', text)
        if not m:
            await update.message.reply_text("❌ اكتب السعر كرقم!", reply_markup=CANCEL_BTN)
            return
        price = float(m.group(1))
        order = db.get('bot_orders', {}).get(order_id)
        if order:
            order['price'] = price
            save_db(db)
        pay_btn = InlineKeyboardMarkup([[InlineKeyboardButton(f"✅ موافقة ودفع ${price:.2f}", callback_data=f"bot_pay#{order_id}")]])
        await context.bot.send_message(target_id, f"💰 سعر طلب البوت: ${price:.2f}\nاضغط للدفع:", reply_markup=pay_btn)
        await update.message.reply_text(f"✅ تم إرسال السعر ${price:.2f} إلى الزبون.")
        return

    if ud.get('awaiting_bot_time'):
        target_id = ud.get('bot_target_id')
        ud['awaiting_bot_time'] = False
        await context.bot.send_message(target_id, f"⏰ الوقت المتوقع: {text}")
        await update.message.reply_text(f"✅ تم إرسال الوقت إلى {target_id}")
        return

    if ud.get('awaiting_bot_notes'):
        order_id = ud.get('bot_order_id')
        ud['awaiting_bot_notes'] = False
        order = db.get('bot_orders', {}).get(order_id)
        if order:
            existing = order.get('details', '')
            order['details'] = (existing + "\n" + text).strip() if existing else text
            save_db(db)
        await update.message.reply_text(f"✅ تم حفظ التفاصيل لطلب {order_id}")
        return

    # تسليم كود
    if ud.get('awaiting_delivery_code'):
        order_id = ud.get('delivery_order_id')
        order = db['pending_orders'].get(order_id)
        ud['awaiting_delivery_code'] = False
        if not order:
            await update.message.reply_text("❌ الطلب غير موجود.")
            return
        target_id = order['user_id']
        delivery_text = (
            f"✅ تم تفعيل طلبك!\n━━━━━━━━━━━━━━━━━━━━\n"
            f"🎁 المنتج: {safe_md(order.get('item_name',''))}\n"
            f"📋 رقم الطلب: {order_id}\n\n"
            f"🎟️ الكود/التفاصيل:\n{safe_md(text)}"
        )
        if order.get('kind') == 'game_code':
            delivery_text += REDEMPTION_INSTRUCTIONS
        try:
            await context.bot.send_message(target_id, delivery_text)
            await update.message.reply_text(f"✅ تم تسليم الطلب {order_id}")
            db['stats']['purchases'] += 1
            log_activity(db, f"تسليم #{order_id} لـ {target_id}")
            del db['pending_orders'][order_id]
            save_db(db)
        except Exception as e:
            await update.message.reply_text(f"❌ فشل: {e}")
            ud['awaiting_delivery_code'] = True
            ud['delivery_order_id'] = order_id
        return

    if ud.get('awaiting_bot_file'):
        target_id = ud.get('bot_target_id')
        order_id = ud.get('bot_order_id')
        ud['awaiting_bot_file'] = False
        order = db.get('bot_orders', {}).get(order_id)
        if order:
            order['file_text'] = text
            save_db(db)
        await context.bot.send_message(target_id, f"📂 ملف البوت:\n{text}")
        await update.message.reply_text(f"✅ تم إرسال الملف إلى {target_id}")
        return

    await update.message.reply_text("⚠️ لم أفهم طلبك. استخدم /cancel للإلغاء.", reply_markup=CANCEL_BTN)


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
            caption=f"🏦 طلب شحن\n📋 {order_id}\n👤 {safe_md(update.effective_user.first_name or '?')}\n🆔 {user_id}\n💰 ${usd_amount:.2f}",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("✅ قبول", callback_data=f"charge_ok#{order_id}")],
                [InlineKeyboardButton("❌ رفض", callback_data=f"charge_no#{order_id}")]
            ])
        )
        ud['awaiting_charge_proof'] = False
        await update.message.reply_text(f"🚀 تم إرسال طلب الشحن {order_id}")
        return

    if ud.get('awaiting_bot_file') and update.message.document:
        target_id = ud.get('bot_target_id')
        order_id = ud.get('bot_order_id')
        ud['awaiting_bot_file'] = False
        order = db.get('bot_orders', {}).get(order_id)
        if order:
            order['file_id'] = update.message.document.file_id
            order['file_name'] = update.message.document.file_name
            save_db(db)
        await context.bot.send_document(target_id, update.message.document.file_id, caption="📂 ملف البوت جاهز!")
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

    if data == "cancel_flow":
        clear_awaiting(ud)
        await query.edit_message_text("✅ تم إلغاء العملية.")
        return

    if data.startswith("resend_botfile#"):
        if not is_admin(db, user_id):
            await query.answer("❌ غير مصرح", show_alert=True)
            return
        order_id = data.split('#')[1]
        order = db.get('bot_orders', {}).get(order_id)
        if not order or not order.get('file_id'):
            await query.answer("❌ لا يوجد ملف", show_alert=True)
            return
        try:
            await context.bot.send_document(order['user_id'], order['file_id'], caption="📂 ملف البوت")
            await query.answer("✅ تم الإرسال", show_alert=True)
        except Exception as e:
            await query.answer(f"❌ {e}", show_alert=True)
        return

    if data == "open_panel":
        if not is_admin(db, user_id):
            await query.edit_message_text("❌ غير مصرح.")
            return
        await query.edit_message_text("🛸 لوحة التحكم الإدارية", reply_markup=get_admin_main_panel(db))
        return

    if data.startswith("adm#"):
        if not is_admin(db, user_id):
            await query.edit_message_text("❌ غير مصرح.")
            return
        action = data.split('#')[1]

        if action == "stats":
            total_users = len(db["users"])
            total_balance = sum(u.get("balance_usd", 0) for u in db["users"].values())
            s = db.get("stats", {})
            await query.edit_message_text(
                f"📊 إحصائيات شاملة\n━━━━━━━━━━━━━━━━━━━━\n"
                f"👥 المستخدمين: {total_users}\n"
                f"💰 إجمالي الأرصدة: ${total_balance:.2f}\n"
                f"📦 طلبات معلقة: {len(db.get('pending_orders',{}))}\n"
                f"🛒 مشتريات: {s.get('purchases',0)}\n"
                f"💸 استرجاعات: {s.get('refunds',0)}\n"
                f"💳 إيداعات: {s.get('deposits',0)}\n"
                f"📩 شكاوى: {s.get('complaints',0)}"
            )
            return

        if action == "log":
            log = db.get("activity_log", [])[-15:]
            await query.edit_message_text("📋 آخر العمليات:\n" + "\n".join(log) if log else "لا يوجد سجل")
            return

        if action == "pending_list":
            orders = db.get("pending_orders", {})
            if not orders:
                await query.edit_message_text("📦 لا يوجد طلبات معلقة.")
                return
            lines = ["📦 الطلبات المعلقة:"]
            for oid, o in list(orders.items())[:20]:
                lines.append(f"{oid} — {o.get('type')} — {o.get('user_id')}")
            await query.edit_message_text("\n".join(lines))
            return

        if action == "broadcast":
            clear_awaiting(ud)
            ud['awaiting_broadcast'] = True
            await query.edit_message_text("✍️ اكتب رسالة الإعلان:", reply_markup=CANCEL_BTN)
            return

        if action == "add_balance":
            clear_awaiting(ud)
            ud['awaiting_add_balance'] = True
            await query.edit_message_text("✍️ اكتب: آيدي|المبلغ", reply_markup=CANCEL_BTN)
            return

        if action == "sub_balance":
            clear_awaiting(ud)
            ud['awaiting_sub_balance'] = True
            await query.edit_message_text("✍️ اكتب: آيدي|المبلغ", reply_markup=CANCEL_BTN)
            return

        if action == "ban_user":
            clear_awaiting(ud)
            ud['awaiting_ban_user'] = True
            await query.edit_message_text("✍️ اكتب آيدي المستخدم:", reply_markup=CANCEL_BTN)
            return

        if action == "unban_user":
            clear_awaiting(ud)
            ud['awaiting_unban_user'] = True
            await query.edit_message_text("✍️ اكتب آيدي المستخدم:", reply_markup=CANCEL_BTN)
            return

        if action == "search_user":
            clear_awaiting(ud)
            ud['awaiting_search_user'] = True
            await query.edit_message_text("✍️ اكتب آيدي المستخدم:", reply_markup=CANCEL_BTN)
            return

        if action == "view_balances":
            s = "💰 الأرصدة:\n"
            for uid, info in list(db["users"].items())[:20]:
                s += f"👤 {safe_md(info.get('name','?'))} — ${info.get('balance_usd',0):.2f} ({uid})\n"
            await query.edit_message_text(s or "لا يوجد مستخدمين.")
            return

        if action == "users":
            s = f"👥 المستخدمين ({len(db['users'])}):\n"
            for uid, info in list(db["users"].items())[:20]:
                s += f"{uid} — {safe_md(info.get('name','?'))}\n"
            await query.edit_message_text(s or "لا يوجد مستخدمين.")
            return

        if action == "edit_rate":
            clear_awaiting(ud)
            ud['awaiting_new_rate'] = True
            await query.edit_message_text(f"📈 السعر الحالي: {db.get('exchange_rate',13800):,} ل.س\n✍️ اكتب السعر الجديد:", reply_markup=CANCEL_BTN)
            return

        if action == "tree":
            lines = ["🗂️ شجرة المتجر:"]
            for section, roots in db['catalog_roots'].items():
                lines.append(f"\n📦 {section}")
                def walk(nid, depth):
                    node = db['catalog'].get(nid)
                    if not node:
                        return
                    flag = ""
                    if node.get('deleted'):
                        flag = " 🗑️"
                    elif node['type'] == 'product' and not node.get('active', True):
                        flag = " ⛔"
                    price_txt = f" | {node['price']}$" if node.get('price') else ""
                    lines.append(("  " * depth) + f"{nid} {safe_md(node['name'])}{price_txt}{flag}")
                    for c in node.get('children', []):
                        walk(c, depth + 1)
                for r in roots:
                    walk(r, 1)
            full = "\n".join(lines)
            if len(full) > 3800:
                full = full[:3800] + "\n..."
            await query.edit_message_text(full)
            return

        if action == "add_category":
            clear_awaiting(ud)
            ud['awaiting_add_category'] = True
            await query.edit_message_text("✍️ صيغة: parent_او_root|games_او_cards_او_numbers|الاسم", reply_markup=CANCEL_BTN)
            return

        if action == "add_product":
            clear_awaiting(ud)
            ud['awaiting_add_product'] = True
            await query.edit_message_text("✍️ صيغة: parent_id|kind|الاسم|السعر\nkind: game_code/card/whatsapp_number/telegram_number", reply_markup=CANCEL_BTN)
            return

        if action == "edit_price":
            clear_awaiting(ud)
            ud['awaiting_edit_price'] = True
            await query.edit_message_text("✍️ صيغة: node_id|السعر", reply_markup=CANCEL_BTN)
            return

        if action == "toggle":
            clear_awaiting(ud)
            ud['awaiting_toggle'] = True
            await query.edit_message_text("✍️ اكتب معرف العنصر:", reply_markup=CANCEL_BTN)
            return

        if action == "delete_node":
            clear_awaiting(ud)
            ud['awaiting_delete_node'] = True
            await query.edit_message_text("✍️ اكتب معرف العنصر للحذف:", reply_markup=CANCEL_BTN)
            return

        if action == "restore_node":
            clear_awaiting(ud)
            ud['awaiting_restore_node'] = True
            await query.edit_message_text("✍️ اكتب معرف العنصر للاسترجاع:", reply_markup=CANCEL_BTN)
            return

        if action == "clean":
            db["pending_orders"] = {}
            save_db(db)
            await query.edit_message_text("🧹 تم تنظيف الطلبات المعلقة.")
            return

        if action == "search_bot_order":
            clear_awaiting(ud)
            ud['awaiting_search_bot_order'] = True
            await query.edit_message_text("✍️ اكتب رقم الطلب أو آيدي الزبون:", reply_markup=CANCEL_BTN)
            return

        if action == "toggle_maintenance":
            db['bot_maintenance'] = not db.get('bot_maintenance', False)
            save_db(db)
            state = "مفعل 🛠️" if db['bot_maintenance'] else "متوقف ✅"
            await query.edit_message_text(f"الصيانة الآن: {state}")
            return

        if action == "admin_notes":
            clear_awaiting(ud)
            ud['awaiting_admin_notes'] = True
            current = db.get('admin_notes', '') or 'لا توجد ملاحظات'
            await query.edit_message_text(f"📝 الملاحظات:\n{safe_md(current)}\n\n✍️ اكتب ملاحظات جديدة:", reply_markup=CANCEL_BTN)
            return

        if action == "list_admins":
            admins = db.get('authenticated_admins', [])
            lines = ["👮 الأدمنية:"]
            for a in admins:
                name = safe_md(db['users'].get(a, {}).get('name', '?'))
                lines.append(f"{a} — {name}")
            await query.edit_message_text("\n".join(lines) if admins else "لا يوجد أدمنية.")
            return

        if action == "export_users":
            users_data = json.dumps(db.get('users', {}), indent=2, ensure_ascii=False)
            await context.bot.send_document(
                chat_id=user_id,
                document=BufferedInputFile(users_data.encode('utf-8'), filename='users_export.json'),
                caption=f"👥 {len(db.get('users', {}))} مستخدم"
            )
            await query.edit_message_text("📤 تم التصدير.")
            return

        if action == "backup":
            backup_data = json.dumps(db, indent=2, ensure_ascii=False)
            await context.bot.send_document(
                chat_id=user_id,
                document=BufferedInputFile(backup_data.encode('utf-8'), filename='database_backup.json'),
                caption="📂 نسخة احتياطية"
            )
            await query.edit_message_text("💾 تم النسخ الاحتياطي.")
            return

        if action == "post_channel":
            try:
                await context.bot.send_message(
                    ADMIN_CHANNEL_ID,
                    "🛸 لوحة التحكم الإدارية",
                    reply_markup=get_admin_main_panel(db)
                )
                await query.edit_message_text("✅ تم النشر في القناة.")
            except Exception as e:
                await query.edit_message_text(f"❌ فشل: {e}")
            return
        return

    # رد على شكوى
    if data.startswith("reply_user#"):
        if not is_admin(db, user_id):
            await query.answer("❌ غير مصرح", show_alert=True)
            return
        target_id = data.split('#')[1]
        clear_awaiting(ud)
        ud['awaiting_reply_to_user'] = True
        ud['reply_target_id'] = target_id
        await notify_admin_dm(context, f"✍️ اكتب ردك على {target_id}:")
        await query.answer("📩 اكتب الرد في الخاص مع البوت", show_alert=True)
        return

    if data == "support#start":
        clear_awaiting(ud)
        ud['awaiting_complaint'] = True
        await query.edit_message_text("📝 اكتب شكواك أو استفسارك:")
        return

    if data.startswith("root#"):
        parts = data.split('#')
        section, page = parts[1], int(parts[2]) if len(parts) > 2 else 0
        roots = db['catalog_roots'].get(section, [])
        title = {"games": "🎮 اختر اللعبة:", "cards": "🎟️ اختر البطاقة:", "numbers": "📱 اختر النوع:"}.get(section, "اختر:")
        await query.edit_message_text(title, reply_markup=render_listing(db, roots, "store#back", f"root#{section}", page))
        return

    if data == "store#phone":
        await query.edit_message_text("📱 اختر الشبكة:", reply_markup=phone_menu)
        return

    if data == "store#back":
        await query.edit_message_text("🛍️ اختر القسم:", reply_markup=store_menu)
        return

    if data.startswith("nav#"):
        parts = data.split('#')
        nid, page = parts[1], int(parts[2]) if len(parts) > 2 else 0
        node = db['catalog'].get(nid)
        if not node:
            await query.edit_message_text("⚠️ هذا القسم غير موجود.")
            return
        await query.edit_message_text(f"📁 {safe_md(node['name'])}", reply_markup=render_listing(db, node['children'], back_cb_for(node), f"nav#{nid}", page))
        return

    if data.startswith("buy#"):
        nid = data.split('#')[1]
        node = db['catalog'].get(nid)
        if not node or node.get('deleted') or not node.get('active', True) or node.get('price') is None:
            await query.edit_message_text("⚠️ المنتج غير متوفر.")
            return
        balance = get_balance(db, user_id)
        if balance < node['price']:
            await query.edit_message_text(f"❌ رصيدك (${balance:.2f}) لا يكفي!")
            return

        if node['kind'] == 'game_code':
            clear_awaiting(ud)
            ud['pending_node_id'] = nid
            ud['awaiting_game_id'] = True
            await query.edit_message_text(f"🎁 {safe_md(node['name'])}\n✍️ أدخل الآيدي:", reply_markup=CANCEL_BTN)
            return

        warn = node.get('warning', '')
        btn = InlineKeyboardMarkup([
            [InlineKeyboardButton("✅ تأكيد الشراء", callback_data=f"confirm_buy#{nid}")],
            [InlineKeyboardButton("❌ إلغاء", callback_data="cancel_flow")]
        ])
        msg = f"{warn}\n\n🎁 {safe_md(node['name'])}\n💰 ${node['price']}\n\nتأكيد الشراء؟" if warn else f"🎁 {safe_md(node['name'])}\n💰 ${node['price']}\n\nتأكيد الشراء؟"
        await query.edit_message_text(msg, reply_markup=btn)
        return

    if data.startswith("confirm_buy#"):
        nid = data.split('#')[1]
        node = db['catalog'].get(nid)
        if not node or node.get('deleted') or not node.get('active', True):
            await query.edit_message_text("⚠️ المنتج غير متوفر.")
            return
        balance = get_balance(db, user_id)
        if balance < node['price']:
            await query.edit_message_text(f"❌ رصيدك غير كافٍ!")
            return
        order_id = generate_order_id()
        db['pending_orders'][order_id] = {"type": "purchase", "user_id": user_id, "node_id": nid,
                                           "price": node['price'], "item_name": node['name'],
                                           "game_id": None, "kind": node['kind']}
        save_db(db)
        await context.bot.send_message(
            ADMIN_CHANNEL_ID,
            f"🛒 طلب شراء\n📋 {order_id}\n👤 {safe_md(update.effective_user.first_name or '?')}\n"
            f"🆔 {user_id}\n🎁 {safe_md(node['name'])}\n💰 ${node['price']}",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("✅ موافقة وخصم", callback_data=f"order_ok#{order_id}")],
                [InlineKeyboardButton("❌ رفض", callback_data=f"order_no#{order_id}")]
            ])
        )
        await query.edit_message_text(f"✅ تم إرسال طلبك {order_id} للإدارة.")
        return

    if data.startswith("confirm_game_buy#"):
        nid = data.split('#')[1]
        node = db['catalog'].get(nid)
        game_id = ud.get('pending_game_id')
        if not node or node.get('deleted') or not node.get('active', True) or not game_id:
            await query.edit_message_text("⚠️ حدث خطأ.")
            return
        balance = get_balance(db, user_id)
        if balance < node['price']:
            await query.edit_message_text(f"❌ رصيدك غير كافٍ!")
            return
        order_id = generate_order_id()
        db['pending_orders'][order_id] = {"type": "purchase", "user_id": user_id, "node_id": nid,
                                           "price": node['price'], "item_name": node['name'],
                                           "game_id": game_id, "kind": node['kind']}
        save_db(db)
        await context.bot.send_message(
            ADMIN_CHANNEL_ID,
            f"🛒 طلب شراء\n📋 {order_id}\n👤 {safe_md(update.effective_user.first_name or '?')}\n"
            f"🆔 {user_id}\n🎁 {safe_md(node['name'])}\n💰 ${node['price']}\n🆔 الآيدي: {safe_md(game_id)}",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("✅ موافقة وخصم", callback_data=f"order_ok#{order_id}")],
                [InlineKeyboardButton("❌ رفض", callback_data=f"order_no#{order_id}")]
            ])
        )
        ud['pending_game_id'] = None
        await query.edit_message_text(f"✅ تم إرسال طلبك {order_id} للإدارة.")
        return

    if data == "confirm_refund":
        amount = ud.get('refund_amount')
        usd_amount = ud.get('refund_usd_amount')
        currency = ud.get('refund_currency', 'usd')
        if amount is None:
            await query.edit_message_text("⚠️ حدث خطأ.")
            return
        balance = get_balance(db, user_id)
        if balance < usd_amount:
            await query.edit_message_text(f"❌ رصيدك غير كافٍ!")
            return
        order_id = generate_order_id()
        db['pending_orders'][order_id] = {"type": "refund", "user_id": user_id, "amount": usd_amount}
        save_db(db)
        await context.bot.send_message(
            ADMIN_CHANNEL_ID,
            f"💰 طلب استرجاع\n📋 {order_id}\n👤 {safe_md(update.effective_user.first_name or '?')}\n"
            f"🆔 {user_id}\n💵 ${usd_amount:.2f}",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("✅ موافقة", callback_data=f"refund_ok#{order_id}")],
                [InlineKeyboardButton("❌ رفض", callback_data=f"refund_no#{order_id}")]
            ])
        )
        await query.edit_message_text(f"✅ تم إرسال طلب الاسترجاع {order_id}")
        return

    if data == "confirm_phone_order":
        amount = ud.get('phone_amount')
        usd_amount = ud.get('phone_usd_amount')
        phone = ud.get('phone_number')
        card_type = ud.get('card_type')
        if amount is None or not phone:
            await query.edit_message_text("⚠️ حدث خطأ.")
            return
        balance = get_balance(db, user_id)
        if balance < usd_amount:
            await query.edit_message_text(f"❌ رصيدك غير كافٍ!")
            return
        order_id = generate_order_id()
        db['pending_orders'][order_id] = {"type": "phone", "user_id": user_id, "usd_amount": usd_amount,
                                           "syr_amount": amount, "phone": phone, "card_type": card_type}
        save_db(db)
        await context.bot.send_message(
            ADMIN_CHANNEL_ID,
            f"📱 طلب شحن هاتف\n📋 {order_id}\n👤 {safe_md(update.effective_user.first_name or '?')}\n"
            f"📞 {safe_md(phone)}\n📶 {card_type}\n💰 {amount:,.0f} ل.س (${usd_amount:.2f})",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("✅ موافقة", callback_data=f"phone_ok#{order_id}")],
                [InlineKeyboardButton("❌ رفض", callback_data=f"phone_no#{order_id}")]
            ])
        )
        await query.edit_message_text(f"✅ تم إرسال طلب الشحن {order_id}")
        return

    # موافقة/رفض
    if data.startswith("order_ok#"):
        order_id = data.split('#')[1]
        order = db['pending_orders'].get(order_id)
        if not order:
            await query.edit_message_text("⚠️ الطلب لم يعد موجوداً.")
            return
        target_id = order['user_id']
        balance = get_balance(db, target_id)
        if balance < order['price']:
            await query.edit_message_text("❌ رصيد الزبون غير كافٍ!")
            return
        update_balance(db, target_id, -order['price'])
        save_db(db)
        await query.edit_message_text(f"✅ تم خصم ${order['price']} من الزبون.\n📩 اكتب الكود في الخاص مع البوت.")
        clear_awaiting(ud)
        ud['awaiting_delivery_code'] = True
        ud['delivery_order_id'] = order_id
        await notify_admin_dm(context, f"✍️ اكتب الكود لتسليمه للزبون (طلب {order_id} — {safe_md(order.get('item_name',''))}):")
        return

    if data.startswith("order_no#"):
        order_id = data.split('#')[1]
        order = db['pending_orders'].pop(order_id, None)
        save_db(db)
        await query.edit_message_text(f"❌ تم رفض الطلب {order_id}")
        if order:
            await context.bot.send_message(order['user_id'], f"❌ تم رفض طلبك {order_id}.")
        return

    if data.startswith("charge_ok#"):
        order_id = data.split('#')[1]
        order = db['pending_orders'].pop(order_id, None)
        if not order:
            await query.edit_message_text("⚠️ الطلب غير موجود.")
            return
        update_balance(db, order['user_id'], order['usd_amount'])
        db['stats']['deposits'] += 1
        log_activity(db, f"إيداع #{order_id} ${order['usd_amount']:.2f}")
        save_db(db)
        await query.edit_message_text(f"✅ تم قبول الشحن {order_id}")
        await context.bot.send_message(order['user_id'], f"✅ تم شحن ${order['usd_amount']:.2f} إلى محفظتك.")
        return

    if data.startswith("charge_no#"):
        order_id = data.split('#')[1]
        order = db['pending_orders'].pop(order_id, None)
        save_db(db)
        await query.edit_message_text(f"❌ تم رفض الشحن {order_id}")
        if order:
            await context.bot.send_message(order['user_id'], f"❌ تم رفض طلب الشحن {order_id}.")
        return

    if data.startswith("refund_ok#"):
        order_id = data.split('#')[1]
        order = db['pending_orders'].pop(order_id, None)
        if not order:
            await query.edit_message_text("⚠️ الطلب غير موجود.")
            return
        update_balance(db, order['user_id'], -order['amount'])
        db['stats']['refunds'] += 1
        log_activity(db, f"استرجاع #{order_id} ${order['amount']:.2f}")
        save_db(db)
        await query.edit_message_text(f"✅ تم قبول الاسترجاع {order_id}")
        await context.bot.send_message(order['user_id'], f"✅ تم استرجاع ${order['amount']:.2f}.")
        return

    if data.startswith("refund_no#"):
        order_id = data.split('#')[1]
        order = db['pending_orders'].pop(order_id, None)
        save_db(db)
        await query.edit_message_text(f"❌ تم رفض الاسترجاع {order_id}")
        if order:
            await context.bot.send_message(order['user_id'], f"❌ تم رفض الاسترجاع {order_id}.")
        return

    if data.startswith("phone_ok#"):
        order_id = data.split('#')[1]
        order = db['pending_orders'].pop(order_id, None)
        if not order:
            await query.edit_message_text("⚠️ الطلب غير موجود.")
            return
        update_balance(db, order['user_id'], -order['usd_amount'])
        save_db(db)
        await query.edit_message_text(f"✅ تم قبول شحن الهاتف {order_id}")
        await context.bot.send_message(order['user_id'], f"✅ تم شحن هاتفك {order['phone']} بمبلغ {order['syr_amount']:,.0f} ل.س")
        return

    if data.startswith("phone_no#"):
        order_id = data.split('#')[1]
        order = db['pending_orders'].pop(order_id, None)
        save_db(db)
        await query.edit_message_text(f"❌ تم رفض شحن الهاتف {order_id}")
        if order:
            await context.bot.send_message(order['user_id'], f"❌ تم رفض شحن الهاتف {order_id}.")
        return

    if data.startswith("phone#"):
        card_type = data.split('#')[1]
        ud['card_type'] = card_type.upper()
        clear_awaiting(ud)
        ud['awaiting_phone'] = True
        await query.edit_message_text(f"✍️ أدخل رقم الهاتف ({card_type.upper()}):", reply_markup=CANCEL_BTN)
        return

    if data.startswith("charge#"):
        currency = data.split('#')[1]
        clear_awaiting(ud)
        ud['charge_currency'] = currency
        ud['awaiting_charge'] = True
        await query.edit_message_text(f"✍️ أدخل المبلغ {'بالدولار' if currency=='usd' else 'بالليرة'}:", reply_markup=CANCEL_BTN)
        return

    if data.startswith("refund#"):
        currency = data.split('#')[1]
        clear_awaiting(ud)
        ud['refund_currency'] = currency
        ud['awaiting_refund'] = True
        await query.edit_message_text(f"✍️ أدخل المبلغ المراد استرجاعه:", reply_markup=CANCEL_BTN)
        return

    if data.startswith("srv#"):
        srv_type = data.split('#')[1]
        srv_name = "🔥 قوي 24 ساعة (5$/شهر)" if srv_type == 'strong' else "💤 عادي 12-18 ساعة (2$/شهر)"
        desc = ud.get('bot_desc', 'غير محدد')
        contact = ud.get('bot_contact', 'غير محدد')
        order_id = generate_order_id()
        db.setdefault('bot_orders', {})[order_id] = {
            "user_id": user_id, "desc": desc, "contact": contact, "srv_name": srv_name,
            "price": None, "details": "", "file_id": None, "file_name": None, "status": "pending"
        }
        save_db(db)
        await query.edit_message_text("🚀 جاري إرسال الطلب...")
        await context.bot.send_message(
            ADMIN_CHANNEL_ID,
            f"🤖 طلب بوت جديد\n📋 {order_id}\n👤 {safe_md(update.effective_user.first_name or '?')}\n"
            f"🆔 {user_id}\n💬 {safe_md(contact)}\n📝 {safe_md(desc)}\n🖥️ {srv_name}",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("💰 تحديد السعر", callback_data=f"bot_price#{user_id}#{order_id}")],
                [InlineKeyboardButton("⏰ الوقت", callback_data=f"bot_time#{user_id}#{order_id}")],
                [InlineKeyboardButton("📝 تفاصيل", callback_data=f"bot_notes#{user_id}#{order_id}")],
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
        ud['bot_order_id'] = parts[2]
        ud['awaiting_bot_price'] = True
        await query.edit_message_text(f"📩 اكتب السعر في الخاص مع البوت (طلب {parts[2]}).")
        await notify_admin_dm(context, f"✍️ اكتب السعر للمستخدم {parts[1]} (طلب {parts[2]}):")
        return

    if data.startswith("bot_time#"):
        parts = data.split('#')
        clear_awaiting(ud)
        ud['bot_target_id'] = parts[1]
        ud['bot_order_id'] = parts[2]
        ud['awaiting_bot_time'] = True
        await query.edit_message_text(f"📩 اكتب الوقت في الخاص مع البوت.")
        await notify_admin_dm(context, f"✍️ اكتب الوقت للمستخدم {parts[1]} (طلب {parts[2]}):")
        return

    if data.startswith("bot_notes#"):
        parts = data.split('#')
        clear_awaiting(ud)
        ud['bot_target_id'] = parts[1]
        ud['bot_order_id'] = parts[2]
        ud['awaiting_bot_notes'] = True
        await query.edit_message_text(f"📩 اكتب التفاصيل في الخاص مع البوت.")
        await notify_admin_dm(context, f"📝 اكتب تفاصيل طلب {parts[2]}:")
        return

    if data.startswith("bot_file#"):
        parts = data.split('#')
        clear_awaiting(ud)
        ud['bot_target_id'] = parts[1]
        ud['bot_order_id'] = parts[2]
        ud['awaiting_bot_file'] = True
        await query.edit_message_text(f"📩 أرسل الملف في الخاص مع البوت.")
        await notify_admin_dm(context, f"📤 أرسل ملف البوت للمستخدم {parts[1]} (طلب {parts[2]}):")
        return

    if data.startswith("bot_pay#"):
        order_id = data.split('#')[1]
        order = db.get('bot_orders', {}).get(order_id)
        if not order or order['user_id'] != user_id:
            await query.edit_message_text("⚠️ الطلب غير موجود.")
            return
        if order.get('status') == 'paid':
            await query.edit_message_text("✅ تم الدفع مسبقاً.")
            return
        price = order.get('price')
        if price is None:
            await query.edit_message_text("⚠️ لم يتم تحديد السعر بعد.")
            return
        balance = get_balance(db, user_id)
        if balance < price:
            await query.edit_message_text(f"❌ رصيدك (${balance:.2f}) لا يكفي!")
            return
        update_balance(db, user_id, -price)
        order['status'] = 'paid'
        db['stats']['purchases'] += 1
        log_activity(db, f"دفع بوت #{order_id} ${price:.2f}")
        save_db(db)
        await query.edit_message_text(f"✅ تم خصم ${price:.2f}. سيتم التواصل معك.")
        await context.bot.send_message(ADMIN_CHANNEL_ID, f"💰 تم دفع طلب البوت {order_id} من {user_id} — ${price:.2f}")
        return

    if data.startswith("bot_reject#"):
        parts = data.split('#')
        await query.edit_message_text(f"❌ تم رفض طلب البوت {parts[2]}")
        order = db.get('bot_orders', {}).get(parts[2])
        if order:
            order['status'] = 'rejected'
            save_db(db)
        await context.bot.send_message(parts[1], f"❌ تم رفض طلب البوت {parts[2]}.")
        return

    if data == "main_menu":
        await context.bot.send_message(chat_id=update.effective_chat.id, text="🎯 القائمة الرئيسية", reply_markup=main_menu)
        return

    await query.edit_message_text("⚠️ هذا الزر غير مفعل.")


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
    print("🚀 البوت شغال!")
    app.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()
