import uuid
import telebot
import sqlite3
from telebot.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton
import threading
import time
import subprocess
import threading
from bomber_free import run_bomber_directly
import threading
bot = telebot.TeleBot("8171266389:AAFW0-0XRt4IzaPL27HUHzx8dse0Bcj39oU")#توکن ربات
admins = [8244066327]#چت ایدی 
admin_user_name = "V1TOW"#یوزر نیم خودتون بدون @
conn = sqlite3.connect('users_.db', check_same_thread=False)
cursor = conn.cursor()
cursor.execute('''CREATE TABLE IF NOT EXISTS users(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER,
    username TEXT,
    first_name TEXT,
    phone TEXT,
    banned INTEGER DEFAULT 0,
    permiom_user INTEGER DEFAULT 0,
    premium_until INTEGER DEFAULT 0
)''')
conn.commit()
try:
    cursor.execute("ALTER TABLE users ADD COLUMN active_bomber INTEGER DEFAULT 0")
    conn.commit()
except sqlite3.OperationalError:
    pass
try:
    cursor.execute("ALTER TABLE users ADD COLUMN active_bombers_count INTEGER DEFAULT 0")
    conn.commit()
except sqlite3.OperationalError:
    pass

user_panel = ReplyKeyboardMarkup(resize_keyboard=True)
user_panel.add("بمبر 💣💣")
user_panel.add("ℹ️اطلاعات من", "🛒خرید پریمیوم")
user_panel.add("راهنما و سوالات تکراری❓")

back_to_bomber = ReplyKeyboardMarkup(resize_keyboard=True)
back_to_bomber.add("بازگشت به بخش بمبر 🔙🔙")
def help_panel():
    markup = ReplyKeyboardMarkup()
    markup.add("اس ام اس بمبر چیست❓", "آموزش استفاده از ربات📚")
    markup.add("انواع بمبر ها چه کاری میکنند❓", "فرق اشتراک پریمیوم با عادی چیست❓")
    markup.add("بازگشت به منوی اصلی 🔙")
    return markup
def bomber_panel():
    markup = ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add("اس ام اس بمبر عادی 💣💣", "اس ام اس بمبر پریمیوم 💣💣")
    markup.add("ایمیل بمبر (به زودی )📥📥", "کال بمبر (به زودی)📞📞")
    markup.add("بازگشت 🔙")
    return markup

admin_link_button = InlineKeyboardMarkup()
admin_link_button.add(InlineKeyboardButton(text="ادمین ربات 📭", url=f"https://t.me/{admin_user_name}"))

def time_keyboard():
    markup = InlineKeyboardMarkup()
    markup.add(
        InlineKeyboardButton("15 روز 📅", callback_data="15day"),
        InlineKeyboardButton("30 روز 📅", callback_data="30day"),
        InlineKeyboardButton("60 روز 📅", callback_data="60day"),
    )
    return markup

@bot.message_handler(commands=['start'])
def start(message):
    user_id = message.from_user.id
    cursor.execute("SELECT * FROM users WHERE user_id=?", (user_id,))
    user = cursor.fetchone()
    if user:
        if user[5] == 1:
            bot.send_message(message.chat.id, "⛔ شما بن شده‌اید و نمی‌توانید ادامه دهید.")
            return
        bot.send_message(message.chat.id, "👋 خوش اومدی دوباره!", reply_markup=user_panel)
    else:
        cursor.execute("INSERT INTO users(user_id, username, first_name) VALUES(?,?,?)",
                       (user_id, message.from_user.username or "-", message.from_user.first_name or "-"))
        conn.commit()
        markup = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
        markup.add(KeyboardButton("📱 ارسال شماره تلفن", request_contact=True))
        bot.send_message(message.chat.id, "👋 خوش اومدی! لطفاً شماره‌ت رو ارسال کن:", reply_markup=markup)

@bot.message_handler(content_types=['contact'])
def contact_handler(message):
    if message.contact:
        user_id = message.from_user.id
        phone = message.contact.phone_number
        username = message.from_user.username or "-"
        first_name = message.from_user.first_name or "-"
        cursor.execute("SELECT user_id FROM users WHERE user_id=?", (user_id,))
        result = cursor.fetchone()

        if result:
            cursor.execute("UPDATE users SET phone=?, username=?, first_name=? WHERE user_id=?",
                           (phone, username, first_name, user_id))
        else:
            cursor.execute("INSERT INTO users(user_id, username, first_name, phone) VALUES(?,?,?,?)",
                           (user_id, username, first_name, phone))
        conn.commit()
        bot.send_message(message.chat.id, f"📱 شماره‌ات ثبت شد ✅\n{phone}")
        bot.send_message(message.chat.id, "برای ادامه از منوی زیر استفاده کن 👇", reply_markup=user_panel)

@bot.message_handler(commands=['panel'])
def admin_panel(message):
    if message.from_user.id not in admins:
        bot.send_message(message.chat.id, "⛔ دسترسی نداری.")
        return
    markup = InlineKeyboardMarkup()
    markup.add(
        InlineKeyboardButton("✉️ پیام همگانی", callback_data="broadcast"),
        InlineKeyboardButton("🚫 بن", callback_data="ban"),
        InlineKeyboardButton("✅ رفع بن", callback_data="unban")
    )
    markup.add(
        InlineKeyboardButton("👀 آخرین کاربران", callback_data="last10"),
        InlineKeyboardButton("🔍 جستجو", callback_data="search")
    )
    markup.add(
        InlineKeyboardButton("⭐ افزودن پریمیوم", callback_data="add_user"),
        InlineKeyboardButton("❌ حذف پریمیوم", callback_data="remove_premium")
    )
    bot.send_message(message.chat.id, "📋 پنل مدیریت", reply_markup=markup)

premium_users = {}
@bot.callback_query_handler(func=lambda call: True)
def callback(call):
    if call.from_user.id not in admins:
        return
    data = call.data
    if data == "broadcast":
        bot.send_message(call.message.chat.id, "📨 پیام همگانی را بنویس:")
        bot.register_next_step_handler(call.message, broadcast_message)
    elif data == "ban":
        bot.send_message(call.message.chat.id, "🚫 آیدی عددی کاربر را ارسال کن:")
        bot.register_next_step_handler(call.message, ban_user)
    elif data == "unban":
        bot.send_message(call.message.chat.id, "✅ آیدی عددی کاربر برای رفع بن را بفرست:")
        bot.register_next_step_handler(call.message, unban_user)
    elif data == "last10":
        cursor.execute("SELECT user_id, username, phone FROM users ORDER BY id DESC LIMIT 10")
        users = cursor.fetchall()
        text = "\n".join([f"👤 @{u[1]} ({u[0]}) 📱 {u[2]}" for u in users]) or "هیچ کاربری یافت نشد."
        bot.send_message(call.message.chat.id, text)
    elif data == "search":
        bot.send_message(call.message.chat.id, "🔍 آیدی عددی، یوزرنیم یا پیام فوروارد را بفرست:")
        bot.register_next_step_handler(call.message, search_user)
    elif data == "add_user":
        bot.send_message(call.message.chat.id, "آیدی عددی کاربر را بفرست تا پریمیوم شود:")
        bot.register_next_step_handler(call.message, store_uid_for_premium)
    elif data == "remove_premium":
        bot.send_message(call.message.chat.id, "آیدی عددی کاربر را بفرست تا پریمیومش حذف شود:")
        bot.register_next_step_handler(call.message, remove_premium)
    elif data in ["15day", "30day", "60day"]:
        set_premium_time_callback(call)
@bot.message_handler(func=lambda message: True)
def callbackinfo(message):
    user_id = message.from_user.id
    mt = message.text

    if mt == "بمبر 💣💣":
        bot.send_message(message.chat.id, "به بخش بمبر خوش اومدی 💣 از دکمه‌های زیر استفاده کن 👇", reply_markup=bomber_panel())
        return

    elif mt == "🛒خرید پریمیوم":
        bot.send_message(message.chat.id, "برای خرید اشتراک پریمیوم با ادمین در ارتباط باش 💬", reply_markup=admin_link_button)
        return

    elif mt == "ℹ️اطلاعات من":
        cursor.execute(
            "SELECT id, user_id, username, first_name, phone, permiom_user, premium_until, active_bombers_count FROM users WHERE user_id=?",
            (user_id,)
        )
        row = cursor.fetchone()
        if not row:
            bot.send_message(message.chat.id, "❌ کاربری پیدا نشد.")
            return
        premium_status = '✅ فعال' if row[5] == 1 else '❌ غیرفعال'
        active_bombers = row[7]  # تعداد بمبرهای فعال

        texxt = (
            f"ℹ️ اطلاعات حساب شما:\n"
            f"🆔 شناسه: {row[1]}\n"
            f"💬 یوزرنیم: @{row[2]}\n"
            f"📱 شماره: {row[4]}\n"
            f"⭐ وضعیت پریمیوم: {premium_status}\n"
            f"💣 بمبرهای فعال: {active_bombers}/{'5' if row[5] == 1 else '1'}"
        )
        bot.send_message(message.chat.id, texxt)
        return

    elif mt == "اس ام اس بمبر پریمیوم 💣💣":
        cursor.execute("SELECT permiom_user FROM users WHERE user_id=?", (user_id,))
        result = cursor.fetchone()
        if result and result[0] == 1:
            bot.send_message(message.chat.id, "🔥 به بمبر پریمیوم خوش اومدی! لطفا شماره مورد نظر رو با +98 ارسال کنید:\n+989120000000\n⏱️ مدت زمان: 5 دقیقه", reply_markup=back_to_bomber)
            bot.register_next_step_handler(message, bomber_premium)
        else:
            bot.send_message(message.chat.id, "⛔ فقط کاربران پریمیوم می‌تونن از این بخش استفاده کنن.", reply_markup=user_panel)
        return

    elif mt == "اس ام اس بمبر عادی 💣💣":
        bot.send_message(message.chat.id, "به اس ام اس بمبر عادی خوش امدید 💣\n لطفا شماره مورد نظر رو با +98 ارسال کنید برای مثال :\n+989120000000\n توجه داشته باشید با اس ام اس بمبر عادی فقط 60 ثانیه فعال میمونه 6️⃣0️⃣", reply_markup=back_to_bomber)
        bot.register_next_step_handler(message , bomber_free)
        return

    elif mt in ["ایمیل بمبر (به زودی )📥📥", "کال بمبر (به زودی)📞📞"]:
        bot.send_message(message.chat.id, "🕒 این قابلیت به زودی اضافه می‌شود!", reply_markup=back_to_bomber)
        return

    elif mt == "بازگشت به بخش بمبر 🔙🔙":
        bot.send_message(message.chat.id, "به بخش بمبر برگشتی 💣", reply_markup=bomber_panel())
        return

    elif mt == "بازگشت 🔙":
        bot.send_message(message.chat.id, "🔙 به منوی اصلی بازگشتی!", reply_markup=user_panel)
        return

    elif mt == "راهنما و سوالات تکراری❓":
        bot.send_message(message.chat.id, "از منوی زیر استفاده کنید🔧", reply_markup=help_panel())
        return

    # بخش راهنمای ریپلای
    elif mt == "اس ام اس بمبر چیست❓":
        text = """📱 **اس ام اس بمبر چیست؟**

اس ام اس بمبر یک ابزار است که با ارسال پیامک‌های متعدد به شماره هدف، باعث ایجاد مزاحمت می‌شود. این ابزار معمولاً برای تست امنیتی یا موارد آموزشی استفاده می‌شود.

⚠️ **توجه**: استفاده نادرست از این ابزار ممکن است مشکلات قانونی به همراه داشته باشد."""
        bot.send_message(message.chat.id, text, parse_mode='Markdown', reply_markup=help_panel())

    elif mt == "آموزش استفاده از ربات📚":
        text = """📚 **آموزش استفاده از ربات**

1. ابتدا با دستور /start ربات را فعال کنید
2. شماره تلفن خود را ثبت نمایید
3. از منوی اصلی گزینه «بمبر» را انتخاب کنید
4. نوع بمبر مورد نظر را انتخاب کنید
5. شماره هدف را با فرمت +98 وارد کنید
6. منتظر پایان عملیات باشید

⏱️ **مدت زمان**: بمبر عادی 60 ثانیه فعال می‌ماند"""
        bot.send_message(message.chat.id, text, parse_mode='Markdown', reply_markup=help_panel())

    elif mt == "انواع بمبر ها چه کاری میکنند❓":
        text = """💣 **انواع بمبرها و کارایی آنها**

• **اس ام اس بمبر**: ارسال پیامک به شماره هدف
• **ایمیل بمبر**: ارسال ایمیل‌های متعدد (به زودی)
• **کال بمبر**: تماس‌های متعدد (به زودی)

🎯 **کاربردها**: تست امنیتی، آموزش، آگاهی از آسیب‌پذیری‌ها"""
        bot.send_message(message.chat.id, text, parse_mode='Markdown', reply_markup=help_panel())

    elif mt == "فرق اشتراک پریمیوم با عادی چیست❓":
        text = """⭐ **مقایسه پریمیوم و عادی**

🆓 **عادی**:
• مدت زمان: 60 ثانیه
• سرویس‌های محدود
• فقط ۱ بمبر همزمان

💎 **پریمیوم**:
• مدت زمان: 300 ثانیه
• سرویس‌های بیشتر
• ۵ بمبر همزمان
• اولویت در اجرا
• پشتیبانی ویژه

💬 برای خرید با ادمین تماس بگیرید."""
        bot.send_message(message.chat.id, text, parse_mode='Markdown', reply_markup=help_panel())

    elif mt == "بازگشت به منوی اصلی 🔙":
        bot.send_message(message.chat.id, "🔙 به منوی اصلی بازگشتی!", reply_markup=user_panel)
        return
def can_start_bomber(user_id):
    cursor.execute("SELECT permiom_user, active_bombers_count FROM users WHERE user_id=?", (user_id,))
    result = cursor.fetchone()
    if not result:
        return False
    premium_status, active_count = result[0], result[1]
    if premium_status == 1:
        return active_count < 5
    else:
        return active_count < 1

def increment_bomber_count(user_id):
    cursor.execute("UPDATE users SET active_bombers_count = active_bombers_count + 1 WHERE user_id=?", (user_id,))
    conn.commit()

def decrement_bomber_count(user_id):
    cursor.execute("UPDATE users SET active_bombers_count = active_bombers_count - 1 WHERE user_id=?", (user_id,))
    conn.commit()

def bomber_free(message):
    user_id = message.from_user.id
    if not can_start_bomber(user_id):
        cursor.execute("SELECT permiom_user FROM users WHERE user_id=?", (user_id,))
        user = cursor.fetchone()
        if user and user[0] == 1:
            bot.send_message(message.chat.id, "⚠️ شما در حال حاضر ۵ بمبر فعال دارید! منتظر پایان یکی از آنها باشید.", reply_markup=bomber_panel())
        else:
            bot.send_message(message.chat.id, "⚠️ هنوز عملیات قبلی‌ت تموم نشده!", reply_markup=bomber_panel())
        return

    phone = message.text.strip()
    if not phone.startswith("+98") or len(phone) != 13 or not phone[1:].isdigit():
        bot.send_message(message.chat.id, "⚠️ لطفاً شماره معتبر وارد کن.\nفرمت درست: +98912xxxxxxx", reply_markup=back_to_bomber)
        return

    bot.send_message(message.chat.id, f"🚀 بمبر برای شماره {phone} شروع شد...")
    increment_bomber_count(user_id)

    def run_bomber_wrapper():
        try:
            import bomber_free
            bomber_free.run_bomber_directly(phone)
        except Exception:
            pass
        finally:
            decrement_bomber_count(user_id)
            bot.send_message(message.chat.id, f"✅ بمبر برای {phone} پایان یافت", reply_markup=bomber_panel())

    threading.Thread(target=run_bomber_wrapper, daemon=True).start()

def bomber_premium(message):
    user_id = message.from_user.id
    if not can_start_bomber(user_id):
        bot.send_message(message.chat.id, "⚠️ شما در حال حاضر ۵ بمبر فعال دارید! منتظر پایان یکی از آنها باشید.", reply_markup=bomber_panel())
        return

    phone = message.text.strip()
    if not phone.startswith("+98") or len(phone) != 13 or not phone[1:].isdigit():
        bot.send_message(message.chat.id, "⚠️ لطفاً شماره معتبر وارد کن.\nفرمت درست: +98912xxxxxxx", reply_markup=back_to_bomber)
        return

    bot.send_message(message.chat.id, f"🚀 بمبر پریمیوم برای شماره {phone} شروع شد...")
    increment_bomber_count(user_id)

    def run_premium_bomber_wrapper():
        try:
            import bomber_premium
            bomber_premium.run_premium_bomber(phone)
        except Exception:
            pass
        finally:
            decrement_bomber_count(user_id)
            bot.send_message(message.chat.id, f"✅ بمبر پریمیوم برای {phone} پایان یافت", reply_markup=bomber_panel())
def is_bomber_active(user_id):
    cursor.execute("SELECT active_bomber FROM users WHERE user_id=?", (user_id,))
    row = cursor.fetchone()
    return row and row[0] == 1

def set_bomber_status(user_id, status):
    cursor.execute("UPDATE users SET active_bomber=? WHERE user_id=?", (1 if status else 0, user_id))
    conn.commit()

def bomber_free(message):
    user_id = message.from_user.id

    if is_bomber_active(user_id):
        bot.send_message(message.chat.id, "⚠️ هنوز عملیات قبلی‌ت تموم نشده!")
        return

    phone = message.text.strip()
    if not phone.startswith("+98") or len(phone) != 13 or not phone[1:].isdigit():
        bot.send_message(message.chat.id, "⚠️ لطفاً شماره معتبر وارد کن.\nفرمت درست: +98912xxxxxxx", reply_markup=back_to_bomber)
        return

    msg = bot.send_message(message.chat.id, f"🚀 بمبر برای شماره {phone} شروع شد...")
    set_bomber_status(user_id, True)

    def run_bomber():
        try:
            import bomber_free
            bomber_free.run_bomber_directly(phone)
        except Exception as e:
            print(f"Bomber error: {e}")
        finally:
            set_bomber_status(user_id, False)
            bot.send_message(message.chat.id, f"✅ بمبر برای {phone} پایان یافت")

    threading.Thread(target=run_bomber, daemon=True).start()

def start_progress(chat_id, msg_id, phone, user_id):
    total_time = 60
    step = 2

    try:
        set_bomber_status(user_id, True)
        start_time = time.time()

        while True:
            elapsed_time = time.time() - start_time
            if elapsed_time >= total_time:
                break

            percent = int((elapsed_time / total_time) * 100)
            bar = "▓" * (percent // 10) + "░" * (10 - percent // 10)

            try:
                bot.edit_message_text(
                    chat_id=chat_id,
                    message_id=msg_id,
                    text=f"💣 بمبر فعال است برای شماره {phone}\n[{bar}] {percent}%\n⏰ زمان باقی‌مانده: {int(total_time - elapsed_time)} ثانیه"
                )
            except:
                pass
            time.sleep(step)

    except Exception as e:
        print(f"Error in progress: {e}")
    finally:
        set_bomber_status(user_id, False)
        try:
            bot.edit_message_text(
                chat_id=chat_id,
                message_id=msg_id,
                text=f"✅ بمبر برای شماره {phone} تموم شد!"
            )
        except:
            pass
def broadcast_message(message):
    text = message.text
    cursor.execute("SELECT user_id FROM users WHERE banned=0")
    users = cursor.fetchall()
    for u in users:
        try:
            bot.send_message(u[0], text)
        except:
            pass
    bot.send_message(message.chat.id, "✅ پیام برای همه ارسال شد.")

def ban_user(message):
    try:
        uid = int(message.text)
        cursor.execute("UPDATE users SET banned=1 WHERE user_id=?", (uid,))
        conn.commit()
        bot.send_message(message.chat.id, f"🚫 کاربر {uid} بن شد.")
    except:
        bot.send_message(message.chat.id, "❌ آیدی معتبر نیست.")

def unban_user(message):
    try:
        uid = int(message.text)
        cursor.execute("UPDATE users SET banned=0 WHERE user_id=?", (uid,))
        conn.commit()
        bot.send_message(message.chat.id, f"✅ کاربر {uid} رفع بن شد.")
    except:
        bot.send_message(message.chat.id, "❌ آیدی معتبر نیست.")

def search_user(message):
    if message.forward_from:
        uid = message.forward_from.id
        cursor.execute("SELECT * FROM users WHERE user_id=?", (uid,))
    elif message.text.startswith("@"):
        username = message.text[1:]
        cursor.execute("SELECT * FROM users WHERE username=?", (username,))
    elif message.text.isdigit():
        cursor.execute("SELECT * FROM users WHERE user_id=?", (int(message.text),))
    else:
        bot.send_message(message.chat.id, "⚠️ فرمت نادرست.")
        return
    user = cursor.fetchone()
    if user:
        bot.send_message(message.chat.id, f"👤 @{user[2]} ({user[1]})\n📱 {user[4]}\n⭐ پریمیوم: {'✅' if user[6] else '❌'}")
    else:
        bot.send_message(message.chat.id, "❌ کاربر یافت نشد.")

def store_uid_for_premium(message):
    try:
        uid = int(message.text)
        chat_id = message.chat.id
        premium_users[chat_id] = uid
        bot.send_message(chat_id, f"📆 مدت اشتراک برای کاربر {uid} را انتخاب کن:", reply_markup=time_keyboard())
    except:
        bot.send_message(message.chat.id, "❌ آیدی معتبر نیست.")

def set_premium_time_callback(call):
    import time as t
    chat_id = call.message.chat.id
    if chat_id not in premium_users:
        bot.answer_callback_query(call.id, "⚠️ ابتدا کاربر را انتخاب کن.")
        return
    uid = premium_users.pop(chat_id)
    now = int(t.time())
    days = {"15day": 15, "30day": 30, "60day": 60}[call.data]
    premium_until = now + days * 24 * 3600
    cursor.execute("UPDATE users SET permiom_user=1, premium_until=? WHERE user_id=?", (premium_until, uid))
    conn.commit()
    bot.edit_message_text(f"✅ کاربر {uid} پریمیوم شد تا {days} روز.", chat_id, call.message.message_id)
    try:
        bot.send_message(uid, f"⭐ اشتراک پریمیوم شما فعال شد به مدت {days} روز ✅")
    except:
        pass

def remove_premium(message):
    try:
        uid = int(message.text)
        cursor.execute("UPDATE users SET permiom_user=0, premium_until=0 WHERE user_id=?", (uid,))
        conn.commit()
        bot.send_message(message.chat.id, f"❌ پریمیوم کاربر {uid} حذف شد.")
    except:
        bot.send_message(message.chat.id, "❌ آیدی معتبر نیست.")

def check_premium():
    while True:
        now = int(time.time())
        cursor.execute("SELECT user_id FROM users WHERE permiom_user=1 AND premium_until<=?", (now,))
        expired = cursor.fetchall()
        for u in expired:
            cursor.execute("UPDATE users SET permiom_user=0, premium_until=0 WHERE user_id=?", (u[0],))
            conn.commit()
            try:
                bot.send_message(u[0], "⏰ اشتراک پریمیوم شما به پایان رسید.")
            except:
                pass
        time.sleep(60)

threading.Thread(target=check_premium, daemon=True).start()
print("Bot is running...")
bot.infinity_polling()