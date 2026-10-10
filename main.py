import os
import logging
import asyncio
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from aiogram.types import Message

logging.basicConfig(level=logging.INFO)

TOKEN = os.getenv("BOT_TOKEN")
if not TOKEN:
    raise ValueError("BOT_TOKEN çevresel değişkeni bulunamadı!")

bot = Bot(token=TOKEN)
dp = Dispatcher()

muted_users = set()
warnings = {}

@dp.message(F.text & F.text.startswith(".mute"))
async def cmd_mute(message: Message):
    if not message.reply_to_message:
        await message.reply("⚠️ Lütfen susturmak istediğiniz kullanıcının mesajına yanıt vererek `.mute` yazın.")
        return
    
    target_user = message.reply_to_message.from_user
    muted_users.add(target_user.id)
    await message.reply(f"🔇 {target_user.full_name} başarıyla susturuldu.")

@dp.message(F.text & F.text.startswith(".unmute"))
async def cmd_unmute(message: Message):
    if not message.reply_to_message:
        await message.reply("⚠️ Lütfen susturmasını kaldırmak istediğiniz kişinin mesajına yanıt vererek `.unmute` yazın.")
        return
    
    target_user = message.reply_to_message.from_user
    if target_user.id in muted_users:
        muted_users.remove(target_user.id)
        await message.reply(f"🔊 {target_user.full_name} sesli/yazılı iletişimi açıldı.")
    else:
        await message.reply("ℹ️ Bu kullanıcı zaten susturulmamış.")

@dp.message(F.text & F.text.startswith(".uyari"))
async def cmd_warn(message: Message):
    if not message.reply_to_message:
        await message.reply("⚠️ Lütfen uyarmak istediğiniz kişinin mesajına yanıt vererek `.uyari` yazın.")
        return
    
    target_user = message.reply_to_message.from_user
    uid = target_user.id
    
    warnings[uid] = warnings.get(uid, 0) + 1
    count = warnings[uid]
    
    if count >= 3:
        warnings[uid] = 0
        await message.reply(f"🚨 {target_user.full_name} 3 kez uyarı sınırını aştı! Hesap raporlandı / kısıtlandı.")
    else:
        await message.reply(f"⚠️ {target_user.full_name} uyarıldı! (Toplam Uyarı: {count}/3)")

@dp.message(F.text & F.text.startswith(".spam"))
async def cmd_spam(message: Message):
    args = message.text.split(maxsplit=2)
    if len(args) < 3:
        await message.reply("⚠️ Kullanım şekli: `.spam <sayı> <mesaj>` (Örn: `.spam 100 mal`)", parse_mode="Markdown")
        return
    
    try:
        count = int(args[1])
        text_to_spam = args[2]
    except ValueError:
        await message.reply("⚠️ Geçerli bir sayı girmelisin! Örn: `.spam 10 mal`", parse_mode="Markdown")
        return
    
    if count > 50:
        count = 50
        await message.answer("ℹ️ Güvenlik nedeniyle spam sınırı maksimum 50 olarak ayarlandı.")

    try:
        await message.delete()
    except:
        pass

    for _ in range(count):
        await message.answer(text_to_spam)
        await asyncio.sleep(0.3)

@dp.message(F.photo)
async def handle_photo(message: Message):
    photo = message.photo[-1]
    file_id = photo.file_id
    if message.reply_to_message:
        await message.reply(f"📸 Fotoğraf yakalandı!\nFile ID: `{file_id}`", parse_mode="Markdown")

@dp.message()
async def block_muted(message: Message):
    if message.from_user and message.from_user.id in muted_users:
        try:
            await message.delete()
        except Exception:
            pass
        return

async def main():
    print("Bot başlatılıyor...")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
