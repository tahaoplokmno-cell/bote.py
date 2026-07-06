const { Telegraf, Markup } = require('telegraf');
const fs = require('fs');

// ==================== الإعدادات ====================
const config = {
    BOT_TOKEN: "8700905522:AAE30w5iFr8jmhIRf_eE0EpSAmk6j1lMfn8",
    ADMIN_CHANNEL_ID: "-1004479419959",
    ADMIN_ID: "8243108672",
    ADMIN_PASSWORD: "T13AHA990POL",
    DEVELOPER_USERNAME: "@MrXT1_3"
};

// ==================== قاعدة البيانات ====================
const DB_FILE = './database.json';
function loadDB() {
    try { if (fs.existsSync(DB_FILE)) return JSON.parse(fs.readFileSync(DB_FILE)); } catch(e) {}
    return {
        users: {},
        banned: {},
        muted: {},
        exchange_rate: 14500,
        admin_notes: "",
        bot_maintenance: false,
        custom_store: {
            games: {
                "🎮 ببجي موبايل": ["60 شدة - 1.20$", "325 شدة - 5.00$", "660 شدة - 10.00$", "1800 شدة - 25.00$"],
                "🔥 فري فاير": ["100 دايموند - 2.00$", "200 دايموند - 4.00$", "400 دايموند - 7.00$"],
                "🎮 روبلوكس": ["100 روبوكس - 1.50$", "500 روبوكس - 6.00$", "1000 روبوكس - 11.00$"],
                "🎟️ بطاقات ستيم": ["فئة 5$ - 5.50$", "فئة 10$ - 11.00$"],
                "🎟️ بطاقات إكس بوكس": ["فئة 10$ - 10.50$", "فئة 25$ - 26.00$"]
            }
        },
        orders: [],
        bot_orders: [],
        installments: [],
        products: []
    };
}
function saveDB(d) { fs.writeFileSync(DB_FILE, JSON.stringify(d, null, 2)); }

// ==================== البوت ====================
const bot = new Telegraf(config.BOT_TOKEN);
let db = loadDB();
let userStates = {};
const save = () => saveDB(db);

// ===== القوائم =====
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

const walletMenu = Markup.inlineKeyboard([
    [Markup.button.callback("💵 شحن بالدولار", "charge#usd")],
    [Markup.button.callback("🇸🇾 شحن بالليرة", "charge#syr")],
    [Markup.button.callback("🔙 القائمة الرئيسية", "main_menu")]
]);

const refundMenu = Markup.inlineKeyboard([
    [Markup.button.callback("💵 استرجاع بالدولار", "refund#usd")],
    [Markup.button.callback("🇸🇾 استرجاع بالليرة", "refund#syr")],
    [Markup.button.callback("🔙 القائمة الرئيسية", "main_menu")]
]);

// ===== لوحة الإدارة =====
const adminPanel = Markup.inlineKeyboard([
    [Markup.button.callback("📊 الإحصائيات", "adm#stats")],
    [Markup.button.callback("📢 إرسال إعلان", "adm#broadcast")],
    [Markup.button.callback("💰 إدارة المحفظة", "adm#wallet")],
    [Markup.button.callback("👥 المستخدمين", "adm#users")],
    [Markup.button.callback("🎮 إدارة المتجر", "adm#store")],
    [Markup.button.callback("🔙 القائمة الرئيسية", "main_menu")]
]);

// ===== الأوامر =====
bot.command('admin', ctx => {
    userStates[String(ctx.chat.id)] = { action: 'await_password' };
    ctx.reply("🔐 اكتب كلمة السر:");
});

bot.command('panel', ctx => {
    const uId = String(ctx.chat.id);
    if (userStates[uId]?.action === 'admin_dashboard' || uId === config.ADMIN_ID) {
        return ctx.reply("🛸 **لوحة التحكم**", { reply_markup: adminPanel });
    }
    ctx.reply("❌ ليس لديك صلاحية.");
});

bot.start(async (ctx) => {
    const uId = String(ctx.chat.id);
    if (db.banned?.[uId]) return ctx.reply("🚫 أنت محظور.");
    if (!db.users[uId]) {
        db.users[uId] = { name: ctx.from.first_name, balance_usd: 0, joined: new Date().toISOString() };
        save();
    }
    const rate = db.exchange_rate || 14500;
    const usd = db.users[uId].balance_usd || 0;
    ctx.reply(
        `👑 **بوت شام إن جيم** 👑\n` +
        `━━━━━━━━━━━━━━━━━━━━\n` +
        `👤 مرحباً: ${ctx.from.first_name}\n` +
        `💰 رصيدك: $${usd.toFixed(2)} | ${(usd * rate).toLocaleString()} ل.س\n` +
        `📈 سعر الصرف: 1$ = ${rate.toLocaleString()} ل.س`,
        { reply_markup: mainMenu }
    );
});

bot.hears('🏪 المتجر', ctx => ctx.reply("🛍️ اختر القسم:", storeMenu));
bot.hears('💳 المحفظة', ctx => ctx.reply("💳 **المحفظة**", { reply_markup: walletMenu }));
bot.hears('💰 استرجاع الأموال', ctx => ctx.reply("💰 **استرجاع الأموال**", { reply_markup: refundMenu }));
bot.hears('⚙️ الإعدادات', ctx => ctx.reply(`⚙️ **الإعدادات**\n👤 ${ctx.from.first_name}\n🆔 ${ctx.chat.id}`));
bot.hears('📞 الدعم الفني', ctx => ctx.reply(`📞 **الدعم الفني**\n${config.DEVELOPER_USERNAME}`));

bot.hears('🤖 إنشاء بوت', ctx => {
    userStates[String(ctx.chat.id)] = { action: 'await_bot_desc' };
    ctx.reply("🤖 **إنشاء بوت**\n✍️ اكتب مواصفات البوت الذي تريده:");
});

// ===== معالج الكولباك =====
bot.on('callback_query', async (ctx) => {
    const data = ctx.callbackQuery.data;
    const uId = String(ctx.from.id);
    await ctx.answerCbQuery().catch(() => {});

    // ===== أزرار الإدارة =====
    if (data.startsWith("adm#")) {
        const action = data.split('#')[1];
        if (action === "stats") {
            const totalUsers = Object.keys(db.users || {}).length;
            const totalBalance = Object.values(db.users || {}).reduce((s, u) => s + (u.balance_usd || 0), 0);
            return ctx.editMessageText(
                `📊 **الإحصائيات**\n` +
                `👥 المستخدمين: ${totalUsers}\n` +
                `💰 إجمالي الرصيد: $${totalBalance.toFixed(2)}`,
                { reply_markup: Markup.inlineKeyboard([[Markup.button.callback("🔙 رجوع", "adm#back")]]) }
            );
        }
        if (action === "back") {
            return ctx.editMessageText("🛸 **لوحة التحكم**", { reply_markup: adminPanel });
        }
        if (action === "broadcast") {
            userStates[uId] = { action: 'await_broadcast' };
            return ctx.editMessageText("✍️ اكتب الرسالة التي تريد إرسالها لجميع المستخدمين:");
        }
        if (action === "wallet") {
            return ctx.editMessageText("💰 **إدارة المحفظة**\nاختر الإجراء:",
                Markup.inlineKeyboard([
                    [Markup.button.callback("➕ إضافة رصيد", "adm#add_balance")],
                    [Markup.button.callback("🔙 رجوع", "adm#back")]
                ])
            );
        }
        if (action === "add_balance") {
            userStates[uId] = { action: 'await_add_balance' };
            return ctx.editMessageText("✍️ اكتب: `آيدي_المستخدم|المبلغ` (مثال: 8243108672|10)");
        }
        if (action === "users") {
            const users = db.users || {};
            let list = "👥 **المستخدمين**\n";
            let count = 0;
            for (const id in users) {
                count++;
                list += `${count}. ${users[id].name} (${id}) - $${users[id].balance_usd || 0}\n`;
                if (count >= 20) { list += `\n... و ${Object.keys(users).length - 20} آخرين`; break; }
            }
            return ctx.editMessageText(list);
        }
        if (action === "store") {
            const games = db.custom_store.games || {};
            let list = "🛒 **الأقسام**\n";
            for (const cat in games) {
                list += `📂 ${cat} (${games[cat].length} منتج)\n`;
            }
            return ctx.editMessageText(list);
        }
        return ctx.reply("🔐 هذا زر خاص بالأدمن.");
    }

    // ===== أزرار المتجر =====
    if (data === "m#games") {
        const games = db.custom_store.games;
        const keys = Object.keys(games);
        if (keys.length === 0) return ctx.reply("⚠️ لا توجد ألعاب!");
        const buttons = keys.map(g => [Markup.button.callback(g, `cat#${g}`)]);
        buttons.push([Markup.button.callback("🔙 القائمة الرئيسية", "main_menu")]);
        return ctx.editMessageText("🎮 **اختر اللعبة:**", { reply_markup: Markup.inlineKeyboard(buttons) });
    }

    if (data.startsWith("cat#")) {
        const catName = data.split('#')[1];
        const list = db.custom_store.games[catName] || [];
        if (list.length === 0) return ctx.reply(`⚠️ لا توجد عروض في ${catName}!`);
        const buttons = list.map(item => {
            const price = parseFloat(item.split('-')[1]) || 0;
            return Markup.button.callback(item, `buy#${catName}#${item}#${price}`);
        });
        let rows = [];
        for (let i = 0; i < buttons.length; i += 2) rows.push(buttons.slice(i, i + 2));
        rows.push([Markup.button.callback("🔙 رجوع للألعاب", "m#games")]);
        rows.push([Markup.button.callback("🔙 القائمة الرئيسية", "main_menu")]);
        return ctx.editMessageText(`🛒 **عروض ${catName}**`, { reply_markup: Markup.inlineKeyboard(rows) });
    }

    if (data.startsWith("buy#")) {
        const parts = data.split('#');
        const cat = parts[1], item = parts[2], price = parseFloat(parts[3]);
        const userBal = db.users[uId]?.balance_usd || 0;
        if (userBal < price) return ctx.reply(`❌ رصيدك ($${userBal.toFixed(2)}) لا يكفي!`);
        userStates[uId] = { cat, item, price, action: 'await_game_id' };
        return ctx.reply(`✍️ اكتب الآيدي (ID) الخاص بك:`);
    }

    if (data === "confirm_order") {
        const state = userStates[uId];
        if (!state || state.action !== 'confirmed') return ctx.reply("❌ لا يوجد طلب مؤكد.");
        const userBal = db.users[uId]?.balance_usd || 0;
        if (userBal < state.price) return ctx.reply(`❌ رصيدك غير كافٍ!`);
        db.users[uId].balance_usd = userBal - state.price;
        save();
        userStates[uId] = null;
        await ctx.editMessageText(`✅ **تم الشراء بنجاح!**\n🎁 ${state.item}\n💰 $${state.price}`);
        await ctx.telegram.sendMessage(config.ADMIN_CHANNEL_ID,
            `🛒 **طلب شراء جديد**\n👤 ${ctx.from.first_name}\n🆔 ${uId}\n🎁 ${state.item}\n💰 $${state.price}\n🆔 الآيدي: ${state.gameId || 'غير محدد'}`
        ).catch(() => {});
        return;
    }

    if (data === "m#cards") {
        const buttons = [
            [Markup.button.callback("🎮 بطاقات ستيم", "cat#🎟️ بطاقات ستيم")],
            [Markup.button.callback("🎮 بطاقات إكس بوكس", "cat#🎟️ بطاقات إكس بوكس")],
            [Markup.button.callback("🔙 القائمة الرئيسية", "main_menu")]
        ];
        return ctx.editMessageText("🎟️ **اختر البطاقة:**", { reply_markup: Markup.inlineKeyboard(buttons) });
    }

    if (data === "m#phone") {
        const buttons = [
            [Markup.button.callback("📱 سيريتل", "phone#syr")],
            [Markup.button.callback("📱 إم تي إن", "phone#mtn")],
            [Markup.button.callback("🔙 القائمة الرئيسية", "main_menu")]
        ];
        return ctx.editMessageText("📱 **اختر شبكة الهاتف:**", { reply_markup: Markup.inlineKeyboard(buttons) });
    }

    if (data.startsWith("phone#")) {
        const type = data.split('#')[1];
        userStates[uId] = { action: 'await_phone', cardType: type };
        return ctx.reply(`✍️ اكتب رقم الهاتف (${type.toUpperCase()}):`);
    }

    // ===== شحن الرصيد =====
    if (data.startsWith("charge#")) {
        const currency = data.split('#')[1];
        userStates[uId] = { action: 'await_charge_amount', currency };
        return ctx.reply(`✍️ اكتب المبلغ ${currency === 'usd' ? 'بالدولار' : 'بالليرة السورية'}:`);
    }

    // ===== استرجاع الأموال =====
    if (data.startsWith("refund#")) {
        const currency = data.split('#')[1];
        userStates[uId] = { action: 'await_refund_amount', currency };
        return ctx.reply(`✍️ اكتب المبلغ ${currency === 'usd' ? 'بالدولار' : 'بالليرة السورية'}:`);
    }

    // ===== طلب بوت =====
    if (data === "bot_order#start") {
        userStates[uId] = { action: 'await_bot_desc' };
        return ctx.reply("🤖 **إنشاء بوت**\n✍️ اكتب مواصفات البوت الذي تريده:");
    }

    // ===== أزرار طلب البوت من الأدمن =====
    if (data.startsWith("bot#")) {
        const parts = data.split('#');
        const action = parts[1];
        const clientId = parts[2];
        if (action === "price") {
            userStates[uId] = { action: 'await_bot_price', targetCustomerId: clientId };
            return ctx.editMessageText(`✍️ اكتب السعر للمستخدم ${clientId}:`);
        }
        if (action === "desc") {
            userStates[uId] = { action: 'await_bot_desc_admin', targetCustomerId: clientId };
            return ctx.editMessageText(`✍️ اكتب وصف إضافي للمستخدم ${clientId}:`);
        }
        if (action === "time") {
            userStates[uId] = { action: 'await_bot_time', targetCustomerId: clientId };
            return ctx.editMessageText(`✍️ اكتب الوقت المتوقع للمستخدم ${clientId}:`);
        }
        if (action === "file") {
            userStates[uId] = { action: 'await_bot_file', targetCustomerId: clientId };
            return ctx.editMessageText(`📤 أرسل الملف للمستخدم ${clientId}:`);
        }
    }

    // ===== العودة للقائمة =====
    if (data === "main_menu") {
        return ctx.editMessageText("🎯 **القائمة الرئيسية**", { reply_markup: mainMenu });
    }

    return ctx.reply("⚠️ هذا الزر غير مفعل حالياً.");
});

// ===== معالج النصوص =====
bot.on('text', async (ctx) => {
    const uId = String(ctx.chat.id);
    const state = userStates[uId];
    if (!state) return;

    // ===== كلمة السر =====
    if (state.action === 'await_password') {
        if (ctx.message.text === config.ADMIN_PASSWORD) {
            userStates[uId] = { action: 'admin_dashboard' };
            return ctx.reply("✅ تم التحقق! اكتب /panel.");
        }
        userStates[uId] = null;
        return ctx.reply("❌ كلمة سر خاطئة!");
    }

    // ===== إرسال إعلان =====
    if (state.action === 'await_broadcast') {
        userStates[uId] = null;
        ctx.reply("🚀 جاري الإرسال...");
        const users = db.users || {};
        let count = 0;
        for (const id in users) {
            try {
                await bot.telegram.sendMessage(id, `📢 **إعلان**\n\n${ctx.message.text}`).catch(() => {});
                count++;
            } catch(e) {}
        }
        return ctx.reply(`✅ تم إرسال الإعلان إلى ${count} مستخدم.`);
    }

    // ===== إضافة رصيد (أدمن) =====
    if (state.action === 'await_add_balance') {
        const parts = ctx.message.text.split('|');
        if (parts.length !== 2) return ctx.reply("❌ الصيغة غير صحيحة! استخدم: `آيدي_المستخدم|المبلغ`");
        const targetId = parts[0].trim();
        const amount = parseFloat(parts[1].trim());
        if (isNaN(amount) || amount <= 0) return ctx.reply("❌ المبلغ غير صحيح!");
        if (!db.users[targetId]) return ctx.reply("❌ المستخدم غير موجود!");
        db.users[targetId].balance_usd = (db.users[targetId].balance_usd || 0) + amount;
        save();
        userStates[uId] = null;
        await ctx.reply(`✅ تم إضافة $${amount} إلى ${db.users[targetId].name}`);
        await bot.telegram.sendMessage(targetId, `🎉 تم إضافة $${amount} إلى محفظتك!`).catch(() => {});
        return;
    }

    // ===== كتابة الآيدي =====
    if (state.action === 'await_game_id') {
        userStates[uId] = { ...state, action: 'confirmed', gameId: ctx.message.text };
        const confirmBtn = Markup.inlineKeyboard([
            [Markup.button.callback("✔️ تأكيد الشراء", "confirm_order")]
        ]);
        return ctx.reply(`🎯 **تأكيد الطلب**\n🎁 ${state.item}\n💰 $${state.price}\n🆔 ${ctx.message.text}`, { reply_markup: confirmBtn });
    }

    // ===== شحن الرصيد =====
    if (state.action === 'await_charge_amount') {
        const amount = parseFloat(ctx.message.text);
        if (isNaN(amount) || amount <= 0) return ctx.reply("❌ اكتب رقماً صحيحاً!");
        const rate = db.exchange_rate || 14500;
        const usdAmount = state.currency === 'usd' ? amount : amount / rate;
        if (!db.users[uId]) db.users[uId] = { balance_usd: 0 };
        db.users[uId].balance_usd = (db.users[uId].balance_usd || 0) + usdAmount;
        save();
        userStates[uId] = null;
        return ctx.reply(`✅ تم شحن ${amount} ${state.currency === 'usd' ? '$' : 'ل.س'} إلى محفظتك!`);
    }

    // ===== استرجاع الأموال =====
    if (state.action === 'await_refund_amount') {
        const amount = parseFloat(ctx.message.text);
        if (isNaN(amount) || amount <= 0) return ctx.reply("❌ اكتب رقماً صحيحاً!");
        const rate = db.exchange_rate || 14500;
        const usdAmount = state.currency === 'usd' ? amount : amount / rate;
        const userBal = db.users[uId]?.balance_usd || 0;
        if (userBal < usdAmount) return ctx.reply(`❌ رصيدك غير كافٍ!`);
        db.users[uId].balance_usd = userBal - usdAmount;
        save();
        userStates[uId] = null;
        const adminMsg = `💰 **طلب استرجاع أموال**\n👤 ${ctx.from.first_name}\n🆔 ${uId}\n💵 المبلغ: $${usdAmount.toFixed(2)}`;
        await ctx.telegram.sendMessage(config.ADMIN_CHANNEL_ID, adminMsg).catch(() => {});
        return ctx.reply(`✅ تم استرجاع $${usdAmount.toFixed(2)} إلى محفظتك!`);
    }

    // ===== شحن رصيد الهاتف =====
    if (state.action === 'await_phone') {
        userStates[uId] = { ...state, phone: ctx.message.text, action: 'await_phone_amount' };
        return ctx.reply(`✍️ اكتب المبلغ المراد شحنه:`);
    }

    if (state.action === 'await_phone_amount') {
        const amount = parseFloat(ctx.message.text);
        if (isNaN(amount) || amount <= 0) return ctx.reply("❌ اكتب رقماً صحيحاً!");
        const rate = db.exchange_rate || 14500;
        const usdAmount = amount / rate;
        const userBal = db.users[uId]?.balance_usd || 0;
        if (userBal < usdAmount) return ctx.reply(`❌ رصيدك غير كافٍ!`);
        db.users[uId].balance_usd = userBal - usdAmount;
        save();
        userStates[uId] = null;
        const msg = `✅ تم شحن ${amount} ل.س إلى ${state.phone} (${state.cardType.toUpperCase()})`;
        await ctx.reply(msg);
        await ctx.telegram.sendMessage(config.ADMIN_CHANNEL_ID,
            `📱 **طلب شحن هاتف**\n👤 ${ctx.from.first_name}\n📞 ${state.phone}\n📶 ${state.cardType.toUpperCase()}\n💰 ${amount} ل.س`
        ).catch(() => {});
        return;
    }

    // ===== إنشاء بوت =====
    if (state.action === 'await_bot_desc') {
        userStates[uId] = { desc: ctx.message.text, action: 'await_bot_contact' };
        return ctx.reply("✍️ أرسل رقم تواصلك أو Username:");
    }

    if (state.action === 'await_bot_contact') {
        userStates[uId] = { ...state, contact: ctx.message.text, action: 'await_bot_server' };
        const serverBtn = Markup.inlineKeyboard([
            [Markup.button.callback("🔥 سيرفر قوي", "srv#strong")],
            [Markup.button.callback("💤 سيرفر عادي", "srv#normal")]
        ]);
        return ctx.reply("🖥️ **اختر نوع السيرفر:**", serverBtn);
    }

    if (data.startsWith("srv#")) {
        const srvType = data.split('#')[1];
        const state = userStates[uId];
        if (!state) return ctx.reply("❌ انتهت الجلسة.");
        const srvName = srvType === 'strong' ? '🔥 قوي 24 ساعة' : '💤 عادي 12-18 ساعة';
        ctx.reply("🚀 جاري الإرسال للإدارة...");
        const adminMsg = `🤖 **طلب بوت جديد**\n👤 ${ctx.from.first_name}\n🆔 ${uId}\n💬 ${state.contact}\n📝 ${state.desc}\n🖥️ ${srvName}`;
        const btn = Markup.inlineKeyboard([
            [Markup.button.callback("💰 السعر", `bot#price#${uId}`)],
            [Markup.button.callback("📝 الوصف", `bot#desc#${uId}`)],
            [Markup.button.callback("⏰ الوقت", `bot#time#${uId}`)],
            [Markup.button.callback("📂 ملف", `bot#file#${uId}`)]
        ]);
        await ctx.telegram.sendMessage(config.ADMIN_CHANNEL_ID, adminMsg, { reply_markup: btn }).catch(() => {});
        userStates[uId] = null;
        return;
    }

    // ===== طلب بوت (السعر، الوصف، الوقت، الملف) =====
    if (state.action === 'await_bot_price' && ctx.message.text) {
        const clientId = state.targetCustomerId;
        if (clientId) {
            await bot.telegram.sendMessage(clientId, `💰 **السعر:** ${ctx.message.text}`).catch(() => {});
            ctx.reply(`✅ تم إرسال السعر`);
        }
        userStates[uId] = null;
        return;
    }
    if (state.action === 'await_bot_desc_admin' && ctx.message.text) {
        const clientId = state.targetCustomerId;
        if (clientId) {
            await bot.telegram.sendMessage(clientId, `📝 **وصف إضافي:** ${ctx.message.text}`).catch(() => {});
            ctx.reply(`✅ تم إرسال الوصف`);
        }
        userStates[uId] = null;
        return;
    }
    if (state.action === 'await_bot_time' && ctx.message.text) {
        const clientId = state.targetCustomerId;
        if (clientId) {
            await bot.telegram.sendMessage(clientId, `⏰ **الوقت:** ${ctx.message.text}`).catch(() => {});
            ctx.reply(`✅ تم إرسال الوقت`);
        }
        userStates[uId] = null;
        return;
    }
    if (state.action === 'await_bot_file' && (ctx.message.document || ctx.message.text)) {
        const clientId = state.targetCustomerId;
        if (clientId) {
            if (ctx.message.document) {
                await bot.telegram.sendDocument(clientId, ctx.message.document.file_id, { caption: "📂 ملف البوت" }).catch(() => {});
            } else {
                await bot.telegram.sendMessage(clientId, `📂 **الملف:** ${ctx.message.text}`).catch(() => {});
            }
            ctx.reply(`✅ تم إرسال الملف`);
        }
        userStates[uId] = null;
        return;
    }
});

// ===== التشغيل =====
bot.launch().then(() => console.log("🚀 البوت شغال")).catch(err => console.error("❌ خطأ:", err));
