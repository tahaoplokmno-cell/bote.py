const { Markup } = require('telegraf');
const config = require('./config');

// ==================== أزرار المتجر ====================
async function handleShop(ctx, data, uId, db, userStates, saveDB, bot) {
    // عرض الألعاب
    if (data === "m#games") {
        const games = db.custom_store?.games || {};
        const keys = Object.keys(games);
        if (keys.length === 0) return ctx.reply("⚠️ لا توجد ألعاب!");
        const buttons = keys.map(g => [Markup.button.callback(g, `shop_cat#${g}`)]);
        buttons.push([Markup.button.callback("🔙 العودة للقائمة الرئيسية", "main_menu")]);
        return ctx.editMessageText("🎮 اختر اللعبة:", { reply_markup: Markup.inlineKeyboard(buttons) });
    }

    // عرض عروض اللعبة
    if (data.startsWith("shop_cat#")) {
        const catName = data.split('#')[1];
        const list = db.custom_store?.games?.[catName] || [];
        if (list.length === 0) return ctx.reply(`⚠️ لا توجد عروض!`);
        const rawButtons = list.map(item => {
            const price = parseFloat(item.split('-')[1]) || 0;
            return Markup.button.callback(item, `buy_item#${catName}#${item}#${price}`);
        });
        let buttons = [];
        for (let i = 0; i < rawButtons.length; i += 2) buttons.push(rawButtons.slice(i, i + 2));
        buttons.push([Markup.button.callback("🔙 رجوع للألعاب", "m#games")]);
        buttons.push([Markup.button.callback("🔙 القائمة الرئيسية", "main_menu")]);
        return ctx.editMessageText(`🛒 عروض ${catName}:`, { reply_markup: Markup.inlineKeyboard(buttons) });
    }

    // شراء منتج
    if (data.startsWith("buy_item#")) {
        const parts = data.split('#');
        const catName = parts[1];
        const item = parts[2];
        const price = parseFloat(parts[3]) || 0;
        const userBal = db.users[uId]?.balance_usd || 0;
        if (userBal < price) return ctx.reply(`❌ رصيدك ($${userBal.toFixed(2)}) لا يكفي!`);
        userStates[uId] = { type: 'game', name: catName, item, price, action: 'await_game_id' };
        return ctx.reply(`✍️ اكتب الآيدي (ID) الخاص بك:`);
    }

    // تأكيد الشراء
    if (data === "confirm_order") {
        const state = userStates[uId];
        if (!state || state.action !== 'confirmed') return ctx.reply("❌ لا يوجد طلب مؤكد.");
        const userBal = db.users?.[uId]?.balance_usd || 0;
        if (userBal < state.price) return ctx.reply(`❌ رصيدك غير كافٍ!`);
        db.users[uId].balance_usd = userBal - state.price;
        saveDB(db);
        userStates[uId] = null;
        const msg = `✅ تم الشراء بنجاح!\n🎁 المنتج: ${state.item}\n💰 الخصم: $${state.price}`;
        await ctx.editMessageText(msg);
        const adminBtn = Markup.inlineKeyboard([
            [Markup.button.callback("📤 إرسال الكود للزبون", `send_code#${uId}`)]
        ]);
        await bot.telegram.sendMessage(config.ADMIN_CHANNEL_ID,
            `🛒 طلب شراء جديد!\n👤 ${ctx.from.first_name}\n🆔 ${uId}\n🎁 ${state.item}\n💰 $${state.price}\n🆔 الآيدي: ${state.gameId || 'غير محدد'}`,
            { reply_markup: adminBtn }
        ).catch(() => {});
        return;
    }

    // إرسال الكود
    if (data.startsWith("send_code#")) {
        const clientId = data.split("#")[1];
        userStates[uId] = { action: 'await_send_code', clientUId: clientId };
        return ctx.editMessageText(`✍️ اكتب الكود للمستخدم ${clientId}:`);
    }

    // البطاقات
    if (data === "m#cards") {
        const buttons = [
            [Markup.button.callback("🎮 بطاقات ستيم", "shop_cat#🎮 بطاقات ستيم")],
            [Markup.button.callback("🎮 بطاقات إكس بوكس", "shop_cat#🎮 بطاقات إكس بوكس")],
            [Markup.button.callback("🔙 القائمة الرئيسية", "main_menu")]
        ];
        return ctx.editMessageText("🎟️ اختر البطاقة:", { reply_markup: Markup.inlineKeyboard(buttons) });
    }

    // شحن رصيد الهاتف
    if (data === "m#phone") {
        const buttons = [
            [Markup.button.callback("📱 سيريتل", "order#syr")],
            [Markup.button.callback("📱 إم تي إن", "order#mtn")],
            [Markup.button.callback("🔙 القائمة الرئيسية", "main_menu")]
        ];
        return ctx.editMessageText("📱 اختر شبكة الهاتف:", { reply_markup: Markup.inlineKeyboard(buttons) });
    }

    if (data.startsWith("order#")) {
        const type = data.split('#')[1];
        userStates[uId] = { action: 'await_syr_phone', cardType: type };
        return ctx.reply(`✍️ اكتب رقم الهاتف (${type.toUpperCase()}):`);
    }
}

// ==================== أزرار الإدارة ====================
function getSuperAdminPanel(db) {
    const totalUsers = Object.keys(db.users || {}).length;
    return {
        text: `🛸 لوحة التحكم\n👥 المستخدمين: ${totalUsers}`,
        markup: Markup.inlineKeyboard([
            [Markup.button.callback("📊 إحصائيات", "adm#stats")],
            [Markup.button.callback("🔙 القائمة الرئيسية", "main_menu")]
        ])
    };
}

async function handleAdmin(ctx, data, uId, userStates, db, bot) {
    const action = data.split('#')[1];
    if (action === "stats") {
        const totalUsers = Object.keys(db.users || {}).length;
        return ctx.editMessageText(`📊 الإحصائيات:\n👥 المستخدمين: ${totalUsers}`);
    }
    if (action === "main") {
        const p = getSuperAdminPanel(db);
        return ctx.editMessageText(p.text, { reply_markup: p.markup });
    }
    return ctx.reply("🔐 هذا زر خاص بالأدمن.");
}

async function handlePayment(ctx, data, uId, db, saveDB) {
    const parts = data.split("#");
    const targetId = parts[1];
    const amount = parseFloat(parts[2]) || 0;
    if (data.startsWith("pay_approve#")) {
        if (!db.users[targetId]) db.users[targetId] = { balance_usd: 0 };
        db.users[targetId].balance_usd += amount;
        saveDB(db);
        await ctx.editMessageText(`✅ تم قبول الشحن`);
        await ctx.telegram.sendMessage(targetId, `✅ تم إضافة $${amount}`);
    } else {
        await ctx.editMessageText(`❌ تم رفض الشحن`);
        await ctx.telegram.sendMessage(targetId, "❌ عذراً، تم رفض الشحن.");
    }
}

// ==================== إنشاء بوت ====================
function initBotOrder(ctx, userStates, uId) {
    userStates[uId] = { action: 'await_bot_desc' };
    ctx.reply("🤖 مرحباً بك في قسم إنشاء البوتات:\n✍️ اكتب مواصفات البوت:");
}

function askContact(ctx, text, uId, userStates) {
    userStates[uId] = { desc: text, action: 'await_bot_contact' };
    ctx.reply("✍️ أرسل رقم تواصلك:");
}

function askServer(ctx, text, uId, userStates) {
    const state = userStates[uId];
    userStates[uId] = { ...state, contact: text, action: 'await_srv_choice' };
    const btn = Markup.inlineKeyboard([
        [Markup.button.callback("🔥 سيرفر قوي", "srv#strong")],
        [Markup.button.callback("💤 سيرفر عادي", "srv#normal")]
    ]);
    ctx.reply("🖥️ اختر نوع السيرفر:", btn);
}

function handleServerChoice(ctx, data, uId, userStates, bot) {
    const srvType = data.split('#')[1];
    const state = userStates[uId];
    if (!state) return ctx.reply("❌ انتهت الجلسة.");
    const srvName = srvType === 'strong' ? '🔥 قوي 24 ساعة' : '💤 عادي 12-18 ساعة';
    ctx.reply("🚀 جاري الإرسال للإدارة...");
    const adminMsg = `📥 طلب بوت جديد:\n👤 ${ctx.from.first_name}\n🆔 ${uId}\n💬 ${state.contact}\n📝 ${state.desc}\n🖥️ ${srvName}`;
    const btn = Markup.inlineKeyboard([
        [Markup.button.callback("💰 السعر", `bot_dec#price#${uId}`)],
        [Markup.button.callback("📝 الوصف", `bot_dec#desc#${uId}`)],
        [Markup.button.callback("⏰ الوقت", `bot_dec#time#${uId}`)],
        [Markup.button.callback("📂 ملف", `bot_dec#file#${uId}`)]
    ]);
    bot.telegram.sendMessage(config.ADMIN_CHANNEL_ID, adminMsg, { reply_markup: btn.reply_markup }).catch(() => {});
    userStates[uId] = null;
}

// ==================== شحن الرصيد ====================
function initCharge(ctx, userStates, uId, db) {
    if (!db.users[uId]) db.users[uId] = { balance_usd: 0 };
    const rate = db.exchange_rate || 14500;
    const usd = db.users[uId].balance_usd || 0;
    const msg = `💳 مركز المحفظة:\n💰 رصيدك: $${usd.toFixed(2)} | ${(usd * rate).toLocaleString()} ل.س\n📈 سعر الصرف: 1$ = ${rate.toLocaleString()} ل.س`;
    const btn = Markup.inlineKeyboard([
        [Markup.button.callback("💵 شحن بالدولار", "ch#usd")],
        [Markup.button.callback("🇸🇾 شحن بالليرة", "ch#syr")],
        [Markup.button.callback("🔙 القائمة الرئيسية", "main_menu")]
    ]);
    ctx.reply(msg, { reply_markup: btn });
}

function askAmount(ctx, data, uId, userStates) {
    const isUsd = data === "ch#usd";
    userStates[uId] = { action: 'await_charge_amount', isUsd };
    ctx.reply(`✍️ اكتب المبلغ (أرقام فقط):`);
}

async function handleChargeSteps(ctx, state, uId, userStates, db) {
    if (state.action === 'await_charge_amount') {
        const amount = parseFloat(ctx.message.text);
        if (isNaN(amount) || amount <= 0) return ctx.reply("❌ اكتب رقماً صحيحاً!");
        userStates[uId] = { action: 'await_proof', amount, isUsd: state.isUsd };
        return ctx.reply("📸 أرسل صورة إثبات الدفع:");
    }
    if (state.action === 'await_proof') {
        const currency = state.isUsd ? "$" : "ل.س";
        const cap = `🏦 طلب شحن جديد:\n👤 ${ctx.from.first_name}\n🆔 ${ctx.chat.id}\n💰 المبلغ: ${state.amount} ${currency}`;
        const btn = Markup.inlineKeyboard([
            [Markup.button.callback("✅ قبول", `pay_approve#${ctx.chat.id}#${state.amount}#${state.isUsd ? 'usd' : 'syr'}`)],
            [Markup.button.callback("❌ رفض", `pay_reject#${ctx.chat.id}`)]
        ]);
        if (ctx.message.photo) {
            await ctx.telegram.sendPhoto(config.ADMIN_CHANNEL_ID, ctx.message.photo.pop().file_id, { caption: cap, reply_markup: btn });
        } else {
            await ctx.telegram.sendMessage(config.ADMIN_CHANNEL_ID, cap + `\n📝 الإثبات: ${ctx.message.text}`, { reply_markup: btn });
        }
        ctx.reply("🚀 تم إرسال طلب الشحن للإدارة!");
        userStates[uId] = null;
    }
}

// ==================== الإعدادات والدعم ====================
function showSettings(ctx) {
    const backBtn = Markup.inlineKeyboard([[Markup.button.callback("🔙 القائمة الرئيسية", "main_menu")]]);
    ctx.reply(`⚙️ الإعدادات:\n👤 ${ctx.from.first_name}\n🆔 ${ctx.chat.id}`, { reply_markup: backBtn });
}

function showSupport(ctx) {
    const backBtn = Markup.inlineKeyboard([[Markup.button.callback("🔙 القائمة الرئيسية", "main_menu")]]);
    ctx.reply(`📞 الدعم الفني:\n@${config.DEVELOPER_USERNAME?.replace('@', '') || 'MrXT1_3'}`, { reply_markup: backBtn });
}

// ==================== المعالج الرئيسي ====================
module.exports = async function handleCallback(ctx, bot, db, userStates, saveDB) {
    const data = ctx.callbackQuery.data;
    const uId = String(ctx.from.id);
    await ctx.answerCbQuery().catch(() => {});

    // أزرار الإدارة
    if (data.startsWith("adm#")) {
        return handleAdmin(ctx, data, uId, userStates, db, bot);
    }

    // أزرار المتجر
    if (data.startsWith("shop_cat#") || data.startsWith("buy_item#") || data === "confirm_order" ||
        data.startsWith("send_code#") || data === "m#games" || data === "m#cards" || data === "m#phone" ||
        data.startsWith("order#")) {
        return handleShop(ctx, data, uId, db, userStates, saveDB, bot);
    }

    // إنشاء بوت
    if (data === "bot_order#start") {
        return initBotOrder(ctx, userStates, uId);
    }
    if (data.startsWith("srv#")) {
        return handleServerChoice(ctx, data, uId, userStates, bot);
    }
    if (data.startsWith("bot_dec#")) {
        const parts = data.split("#");
        const action = parts[1];
        const clientId = parts[2];
        if (action === "price") {
            userStates[uId] = { action: 'await_bot_price', targetCustomerId: clientId };
            return ctx.editMessageText(`✍️ اكتب السعر للمستخدم ${clientId}:`);
        }
        if (action === "desc") {
            userStates[uId] = { action: 'await_bot_desc_admin', targetCustomerId: clientId };
            return ctx.editMessageText(`✍️ اكتب وصف إضافي`);
        }
        if (action === "time") {
            userStates[uId] = { action: 'await_bot_time', targetCustomerId: clientId };
            return ctx.editMessageText(`✍️ اكتب الوقت المتوقع`);
        }
        if (action === "file") {
            userStates[uId] = { action: 'await_bot_file', targetCustomerId: clientId };
            return ctx.editMessageText(`📤 أرسل الملف`);
        }
    }

    // الشحن
    if (data.startsWith("ch#")) {
        return askAmount(ctx, data, uId, userStates);
    }
    if (data.startsWith("amt#") || data.startsWith("amts#")) {
        const amount = data.split("#")[1];
        userStates[uId] = { action: 'await_charge_amount', amount: parseFloat(amount), isUsd: data.startsWith("amt#") };
        return ctx.reply(`📸 أرسل صورة إثبات الدفع`);
    }
    if (data.startsWith("pay_approve#") || data.startsWith("pay_reject#")) {
        return handlePayment(ctx, data, uId, db, saveDB);
    }

    // استرجاع الأموال
    if (data.startsWith("ref_app#") || data.startsWith("ref_rej#")) {
        const parts = data.split("#");
        const targetId = parts[1];
        const amount = parseFloat(parts[2]) || 0;
        if (data.startsWith("ref_app#")) {
            if (db.users[targetId]) {
                db.users[targetId].balance_usd = (db.users[targetId].balance_usd || 0) - amount;
                saveDB(db);
                await ctx.editMessageText(`✅ تم استرجاع $${amount}`);
                await bot.telegram.sendMessage(targetId, `✅ تم استرجاع $${amount}`);
            }
        } else {
            await ctx.editMessageText(`❌ تم رفض الاسترجاع`);
            await bot.telegram.sendMessage(targetId, "❌ عذراً، تم رفض استرجاع الأموال.");
        }
        return;
    }
    if (data.startsWith("refund#")) {
        const currency = data.split("#")[1];
        userStates[uId] = { action: 'await_refund_amount', currency };
        const msg = currency === 'usd' ? "✍️ اكتب المبلغ بالدولار:" : "✍️ اكتب المبلغ بالليرة:";
        return ctx.reply(msg);
    }

    // العودة للقائمة
    if (data === "main_menu") {
        const mainMenu = Markup.keyboard([
            ['🏪 المتجر'],
            ['💳 المحفظة', '💰 استرجاع الأموال'],
            ['⚙️ الإعدادات', '📞 الدعم الفني']
        ]).resize();
        return ctx.editMessageText("🎯 القائمة الرئيسية", { reply_markup: mainMenu });
    }

    return ctx.reply("⚠️ هذا الزر غير مفعل حالياً.");
};
