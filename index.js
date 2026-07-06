const { Telegraf, Markup } = require('telegraf');
const config = require('./config');
const dbFile = require('./database');
const callbackHandler = require('./callback_handler');

const bot = new Telegraf(config.BOT_TOKEN);
let db = dbFile.loadDB();
let userStates = {};
const saveDB = () => dbFile.saveDB(db);

// القوائم
const mainMenu = Markup.keyboard([
    ['🏪 المتجر'],
    ['💳 المحفظة', '💰 استرجاع الأموال'],
    ['⚙️ الإعدادات', '📞 الدعم الفني']
]).resize();

const storeMenu = Markup.inlineKeyboard([
    [Markup.button.callback("🎮 قسم الألعاب", "m#games")],
    [Markup.button.callback("🎟️ بطاقات ستيم وإكس بوكس", "m#cards")],
    [Markup.button.callback("📱 شحن رصيد هاتف", "m#phone")],
    [Markup.button.callback("🤖 إنشاء بوت", "bot_order#start")],
    [Markup.button.callback("🔙 القائمة الرئيسية", "main_menu")]
]);

// ===== الأوامر =====
bot.command('admin', ctx => {
    userStates[String(ctx.chat.id)] = { action: 'await_password' };
    ctx.reply("🔐 اكتب كلمة السر:");
});

bot.command('panel', ctx => {
    const uId = String(ctx.chat.id);
    if (userStates[uId]?.action === 'admin_dashboard') {
        const p = require('./callback_handler').getSuperAdminPanel(db);
        return ctx.reply(p.text, { reply_markup: p.markup });
    }
    ctx.reply("❌ ليس لديك صلاحية.");
});

bot.start(async (ctx) => {
    const uId = String(ctx.chat.id);
    if (!db.users) db.users = {};
    if (db.banned?.[uId]) return ctx.reply("🚫 أنت محظور.");
    if (!db.users[uId]) {
        db.users[uId] = { name: ctx.from.first_name, balance_usd: 0 };
        saveDB();
    }
    const rate = db.exchange_rate || 14500;
    const usd = db.users[uId].balance_usd || 0;
    ctx.reply(
        `👑 بوت شام إن جيم 👑\n👤 مرحباً: ${ctx.from.first_name}\n💰 رصيدك: $${usd.toFixed(2)} | ${(usd * rate).toLocaleString()} ل.س\n📈 سعر الصرف: 1$ = ${rate.toLocaleString()} ل.س`,
        { reply_markup: mainMenu }
    );
});

bot.hears('🏪 المتجر', ctx => ctx.reply("🛍️ اختر القسم:", storeMenu));
bot.hears('💳 المحفظة', ctx => require('./callback_handler').initCharge(ctx, userStates, String(ctx.chat.id), db));
bot.hears('🤖 إنشاء بوت', ctx => require('./callback_handler').initBotOrder(ctx, userStates, String(ctx.chat.id)));
bot.hears('⚙️ الإعدادات', ctx => require('./callback_handler').showSettings(ctx));
bot.hears('📞 الدعم الفني', ctx => require('./callback_handler').showSupport(ctx));

bot.hears('💰 استرجاع الأموال', ctx => {
    const btn = Markup.inlineKeyboard([
        [Markup.button.callback("💵 استرجاع بالدولار", "refund#usd")],
        [Markup.button.callback("🇸🇾 استرجاع بالليرة", "refund#syr")]
    ]);
    ctx.reply("💰 اختر عملة الاسترجاع:", btn);
});

// ===== معالج الكولباك =====
bot.on('callback_query', async (ctx) => {
    try {
        await callbackHandler(ctx, bot, db, userStates, saveDB);
    } catch (err) {
        console.error('❌ خطأ:', err);
        await ctx.reply('⚠️ حدث خطأ.').catch(() => {});
    }
});

// ===== معالج النصوص =====
bot.on('text', async (ctx) => {
    const uId = String(ctx.chat.id);
    const state = userStates[uId];
    const txt = ctx.message.text;
    if (!state) return;

    // كلمة السر
    if (state.action === 'await_password') {
        if (txt === config.ADMIN_PASSWORD) {
            userStates[uId] = { action: 'admin_dashboard' };
            return ctx.reply("✅ تم التحقق!");
        }
        userStates[uId] = null;
        return ctx.reply("❌ كلمة سر خاطئة!");
    }

    // كتابة الآيدي
    if (state.action === 'await_game_id') {
        userStates[uId] = { ...state, action: 'confirmed', gameId: txt };
        const confirmBtn = Markup.inlineKeyboard([
            [Markup.button.callback("✔️ تأكيد الشراء", "confirm_order")]
        ]);
        return ctx.reply(`🎯 تأكيد الطلب:\n🎁 المنتج: ${state.item}\n💰 السعر: $${state.price}\n🆔 الآيدي: ${txt}`, { reply_markup: confirmBtn });
    }

    // إرسال الكود
    if (state.action === 'await_send_code') {
        const clientId = state.clientUId;
        if (clientId) {
            await bot.telegram.sendMessage(clientId, `🎁 كود الشحن:\n\n${txt}`).catch(() => {});
            ctx.reply(`✅ تم إرسال الكود`);
        }
        userStates[uId] = null;
        return;
    }

    // شحن رصيد سوري
    if (state.action === 'await_syr_phone') {
        userStates[uId] = { ...state, phoneNumber: txt, action: 'await_syr_amount' };
        return ctx.reply("💸 اكتب المبلغ:");
    }
    if (state.action === 'await_syr_amount') {
        const syrAmount = parseFloat(txt);
        if (isNaN(syrAmount) || syrAmount <= 0) return ctx.reply("❌ اكتب رقماً!");
        const requiredUsd = (syrAmount * 1.5) / (db.exchange_rate || 14500);
        if ((db.users[uId]?.balance_usd || 0) < requiredUsd) return ctx.reply(`❌ رصيدك غير كافٍ!`);
        userStates[uId] = { type: 'card', item: `شحن ${syrAmount} ل.س`, price: requiredUsd, phoneNumber: state.phoneNumber, action: 'confirmed' };
        const confirmBtn = Markup.inlineKeyboard([
            [Markup.button.callback("✔️ تأكيد", "confirm_order")]
        ]);
        return ctx.reply(`🎯 تأكيد: ${syrAmount} ل.س = $${requiredUsd.toFixed(2)}`, { reply_markup: confirmBtn });
    }

    // استرجاع الأموال
    if (state.action === 'await_refund_amount') {
        let amount = 0;
        let currency = state.currency || 'usd';
        if (currency === 'usd') {
            amount = parseFloat(txt);
            if (isNaN(amount) || amount <= 0) return ctx.reply("❌ اكتب رقماً بالدولار!");
        } else {
            const syrAmount = parseFloat(txt);
            if (isNaN(syrAmount) || syrAmount <= 0) return ctx.reply("❌ اكتب رقماً بالليرة!");
            amount = syrAmount / (db.exchange_rate || 14500);
        }
        if ((db.users[uId]?.balance_usd || 0) < amount) return ctx.reply(`❌ رصيدك لا يكفي!`);
        ctx.reply("🚀 تم إرسال طلب الاسترجاع!");
        const btn = Markup.inlineKeyboard([
            [Markup.button.callback("✅ قبول", `ref_app#${uId}#${amount}`)],
            [Markup.button.callback("❌ رفض", `ref_rej#${uId}`)]
        ]);
        await bot.telegram.sendMessage(config.ADMIN_CHANNEL_ID, `⚠️ طلب استرجاع: ${ctx.from.first_name} - $${amount.toFixed(2)}`, { reply_markup: btn }).catch(() => {});
        userStates[uId] = null;
        return;
    }

    // طلب بوت (السعر، الوصف، الوقت، الملف)
    if (state.action === 'await_bot_price') {
        const clientId = state.targetCustomerId;
        if (clientId) {
            await bot.telegram.sendMessage(clientId, `💰 السعر: ${txt}`).catch(() => {});
            ctx.reply(`✅ تم إرسال السعر`);
        }
        userStates[uId] = null;
        return;
    }
    if (state.action === 'await_bot_desc_admin') {
        const clientId = state.targetCustomerId;
        if (clientId) {
            await bot.telegram.sendMessage(clientId, `📝 وصف إضافي: ${txt}`).catch(() => {});
            ctx.reply(`✅ تم إرسال الوصف`);
        }
        userStates[uId] = null;
        return;
    }
    if (state.action === 'await_bot_time') {
        const clientId = state.targetCustomerId;
        if (clientId) {
            await bot.telegram.sendMessage(clientId, `⏰ الوقت: ${txt}`).catch(() => {});
            ctx.reply(`✅ تم إرسال الوقت`);
        }
        userStates[uId] = null;
        return;
    }
    if (state.action === 'await_bot_file' && (ctx.message.document || txt)) {
        const clientId = state.targetCustomerId;
        if (clientId) {
            if (ctx.message.document) {
                await bot.telegram.sendDocument(clientId, ctx.message.document.file_id, { caption: "📂 ملف البوت" }).catch(() => {});
            } else {
                await bot.telegram.sendMessage(clientId, `📂 الملف: ${txt}`).catch(() => {});
            }
            ctx.reply(`✅ تم إرسال الملف`);
        }
        userStates[uId] = null;
        return;
    }

    // معالجة الشحن
    if (state.action?.startsWith('await_charge') || state.action === 'await_proof') {
        return require('./callback_handler').handleChargeSteps(ctx, state, uId, userStates, db);
    }

    return ctx.reply("⚠️ لم أفهم طلبك.");
});

// ===== التشغيل =====
bot.launch()
    .then(() => console.log("🚀 البوت شغال"))
    .catch(err => console.error("❌ خطأ:", err));
