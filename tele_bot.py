from telegram import Update
from telegram.constants import ChatAction
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
import aiohttp
import base64
import os
from dotenv import load_dotenv

load_dotenv()
TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

# Command Handlers

# reply on /start
# Update contains info about incoming msg and context provides context for the callback
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
  await update.message.reply_text("Hello, I will tell you whether what you heard is fake news or not. Send me what you heard with /verify")
  
# reply on /help
async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
  await update.message.reply_text("add /verify to the text you want to send")
  
# do on /clear
async def clear(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Clear any stored conversation data for this user
    if context.user_data:
        context.user_data.clear()
        
    await update.message.reply_text("Chat context has been cleared.")

# reply with results on /verify {text}
async def verify_news(update: Update, context: ContextTypes.DEFAULT_TYPE):
  # if message is preceeded with /verify
  if context.args:
    message = " ".join(context.args)
    
  # if message is replied to using /verify 
  elif update.message.reply_to_message:
    message = update.message.reply_to_message.text
  
  else:
    await update.message.reply_text("Provide text to verify")
    return
  
  # Show typing
  await context.bot.send_chat_action(
    chat_id=update.effective_chat.id, 
    action=ChatAction.TYPING
  )
  
  # Backend looks for List[str]
  messages = [message]
  
  try:
    async with aiohttp.ClientSession() as session:
      async with session.post("http://localhost:3000/tele", json=messages) as response:
        if response.status == 200:
          
          # Get results
          results = await response.json()
          
          # Reply user
          await update.message.reply_text(results['text'])
          
          # Process audio file
          if 'audio' in results and results["audio"]:
            # Decode base64 to bianry
            audio_binary = base64.b64decode(results['audio'])
            
            # Write to file
            with open('results.mp3', 'wb') as f:
              f.write(audio_binary)
            
            # Send audio to user
            await context.bot.send_voice(
              chat_id=update.effective_chat.id,
              voice=open('results.mp3', 'rb')
            )

        else:
          await update.message.reply_text("Sorry, something went wrong")
          
  except Exception as e:
    await update.message.reply_text(f'Error connecting to server: {str(e)}')     
    
    
# Run bot
def main():
  # Create application and give token
  application = Application.builder().token(TOKEN).build()
  
  # Add commands
  application.add_handler(CommandHandler("start", start))
  application.add_handler(CommandHandler("help", help_command))
  application.add_handler(CommandHandler("clear", clear))
  application.add_handler(CommandHandler("verify", verify_news))
  
  # Run bot until CTRL + C
  application.run_polling(allowed_updates=Update.ALL_TYPES)
  
  
if __name__ == '__main__':
  main()