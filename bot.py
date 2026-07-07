import pandas as pd
import telebot
import os

TOKEN = os.environ.get('TELEGRAM_TOKEN')
bot = telebot.TeleBot(TOKEN)

# Excel-ის წაკითხვა
df = pd.read_excel('udzravi_qoneba_databaze.xlsx')

@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.reply_to(message, "გამარჯობა! 👋\nდამიწერე რა გინდა: გასაქირავებელი, გასაყიდი, ვაკე, საბურთალო და ა.შ.")

@bot.message_handler(func=lambda message: True)
def search_posts(message):
    keyword = message.text.lower()
    results = df[df.apply(lambda row: keyword in str(row).lower(), axis=1)]
    
    if results.empty:
        bot.reply_to(message, "სამწუხაროდ ვერაფერი ვიპოვე 😔 სცადე სხვა სიტყვა")
    else:
        for index, row in results.head(3).iterrows():
            text = f"**{row['კატეგორია']}** - {row['ლოკაცია']}\n💰 {row['ფასი']}\n📝 {row['აღწერა']}\n🔗 {row['ლინკი']}"
            bot.send_message(message.chat.id, text, parse_mode='Markdown')

print("Bot is running...")
bot.polling()