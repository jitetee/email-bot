"""Telegram bot for managing bulk email campaigns."""
import asyncio
import logging
from pathlib import Path
from typing import Optional

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application, CommandHandler, MessageHandler,
    CallbackQueryHandler, ContextTypes, ConversationHandler,
    filters
)

from config import TELEGRAM_BOT_TOKEN, EMAIL_LIST_FILE, TEMPLATES_DIR
from template_engine import EmailTemplate
from email_sender import BulkEmailSender

# Conversation states
SELECT_TEMPLATE, CONFIRM_SEND, CUSTOM_SUBJECT, CUSTOM_BODY = range(4)

# Setup logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)


class EmailBot:
    """Telegram bot for email campaign management."""
    
    def __init__(self):
        self.template_engine = EmailTemplate(TEMPLATES_DIR)
        self.email_sender = BulkEmailSender()
        self.current_template: Optional[dict] = None
        self.current_subject: Optional[str] = None
        self.current_body: Optional[str] = None
    
    async def start(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Handle /start command."""
        welcome_text = """
📧 *Email Campaign Bot*

I can help you send bulk promotional emails with custom templates.

*Commands:*
/list - List available templates
/send - Start a new email campaign
/preview - Preview a template
/emails - View email list stats
/help - Show this help message

*Features:*
✅ HTML email templates
✅ Custom variables ($name, $company, etc.)
✅ Image attachments
✅ Rate limiting (avoid spam filters)
✅ Progress tracking
✅ Detailed logging

Ready to start? Use /send to begin!
        """
        await update.message.reply_text(welcome_text, parse_mode='Markdown')
    
    async def help_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Handle /help command."""
        help_text = """
*📧 Email Bot Help*

*Setup:*
1. Configure your SMTP settings in config.py
2. Add emails to data/email_list.txt
3. Set your Telegram bot token

*Sending Campaigns:*
1. Use /send to start
2. Choose a template
3. Customize variables
4. Confirm and send

*Template Variables:*
- $name - Recipient name
- $company - Your company name
- $offer - Special offer text
- $link - Call-to-action URL

*Rate Limits:*
- Default: 50 emails per batch
- 60s delay between batches
- 0.5s delay between emails

Stay compliant with email regulations!
        """
        await update.message.reply_text(help_text, parse_mode='Markdown')
    
    async def list_templates(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Handle /list command - show available templates."""
        templates = self.template_engine.list_templates()
        
        if not templates:
            await update.message.reply_text("No templates found. Using default template.")
            return
        
        text = "📋 *Available Templates:*\n\n"
        for i, template in enumerate(templates, 1):
            text += f"{i}. `{template}`\n"
        
        text += "\nUse /send to select a template and start sending."
        await update.message.reply_text(text, parse_mode='Markdown')
    
    async def email_stats(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Handle /emails command - show email list stats."""
        if not EMAIL_LIST_FILE.exists():
            await update.message.reply_text("❌ Email list file not found!")
            return
        
        emails = self.email_sender.load_email_list(EMAIL_LIST_FILE)
        
        text = f"""
📊 *Email List Statistics*

📁 File: `{EMAIL_LIST_FILE.name}`
📧 Total emails: *{len(emails)}*

*Sample emails:*
"""
        for email in emails[:5]:
            text += f"  • `{email}`\n"
        
        if len(emails) > 5:
            text += f"  ... and {len(emails) - 5} more"
        
        await update.message.reply_text(text, parse_mode='Markdown')
    
    async def send_start(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        """Start the send conversation."""
        templates = self.template_engine.list_templates()
        
        keyboard = []
        for template in templates:
            keyboard.append([InlineKeyboardButton(f"📄 {template}", callback_data=f"template_{template}")])
        keyboard.append([InlineKeyboardButton("⚙️ Default Template", callback_data="template_default")])
        keyboard.append([InlineKeyboardButton("❌ Cancel", callback_data="cancel")])
        
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.message.reply_text(
            "📧 *Select a Template*\n\nChoose an email template to use:",
            reply_markup=reply_markup,
            parse_mode='Markdown'
        )
        
        return SELECT_TEMPLATE
    
    async def template_selected(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        """Handle template selection."""
        query = update.callback_query
        await query.answer()
        
        if query.data == "cancel":
            await query.edit_message_text("Campaign cancelled.")
            return ConversationHandler.END
        
        template_name = query.data.replace("template_", "")
        self.current_template = self.template_engine.load_template(template_name)
        
        # Show preview and ask for confirmation
        preview_text = f"""
📋 *Template Preview*

*Subject:* {self.current_template['subject']}

*Body:* (HTML content loaded)

Ready to send to {self.email_sender.load_email_list(EMAIL_LIST_FILE).__len__() if EMAIL_LIST_FILE.exists() else 0} recipients?
        """
        
        keyboard = [
            [InlineKeyboardButton("✏️ Customize Subject", callback_data="customize_subject")],
            [InlineKeyboardButton("✅ Send Now", callback_data="confirm_send")],
            [InlineKeyboardButton("❌ Cancel", callback_data="cancel")]
        ]
        
        await query.edit_message_text(
            preview_text,
            reply_markup=InlineKeyboardMarkup(keyboard),
            parse_mode='Markdown'
        )
        
        return CONFIRM_SEND
    
    async def confirm_send(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        """Handle send confirmation."""
        query = update.callback_query
        await query.answer()
        
        if query.data == "cancel":
            await query.edit_message_text("Campaign cancelled.")
            return ConversationHandler.END
        
        if query.data == "customize_subject":
            await query.edit_message_text(
                "✏️ Send me your custom subject line,\nor type /cancel to go back."
            )
            return CUSTOM_SUBJECT
        
        # Start sending
        await query.edit_message_text("🚀 Starting email campaign...")
        
        # Load emails
        if not EMAIL_LIST_FILE.exists():
            await query.edit_message_text("❌ Email list file not found!")
            return ConversationHandler.END
        
        emails = self.email_sender.load_email_list(EMAIL_LIST_FILE)
        
        # Send in background
        asyncio.create_task(
            self._send_campaign(query, emails)
        )
        
        return ConversationHandler.END
    
    async def _send_campaign(self, query, emails: list) -> None:
        """Send campaign in background."""
        async def progress(current: int, total: int, status: str):
            if current % 10 == 0 or current == total:
                try:
                    await query.edit_message_text(
                        f"📊 Progress: {current}/{total}\n"
                        f"✅ Sent: {self.email_sender.stats['sent']}\n"
                        f"❌ Failed: {self.email_sender.stats['failed']}\n"
                        f"Status: {status}"
                    )
                except:
                    pass
        
        # Run blocking send in executor
        loop = asyncio.get_event_loop()
        await loop.run_in_executor(
            None,
            lambda: self.email_sender.send_bulk(
                emails,
                self.current_template['subject'],
                self.current_template['body'],
                progress_callback=progress
            )
        )
        
        stats = self.email_sender.get_stats()
        await query.edit_message_text(
            f"✅ *Campaign Complete!*\n\n"
            f"📊 Results:\n"
            f"• Total: {stats['total']}\n"
            f"• Sent: {stats['sent']}\n"
            f"• Failed: {stats['failed']}\n"
            f"• Duration: {stats['end_time'] - stats['start_time']}",
            parse_mode='Markdown'
        )
    
    async def custom_subject(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        """Handle custom subject input."""
        self.current_subject = update.message.text
        self.current_template['subject'] = self.current_subject
        
        await update.message.reply_text(
            f"✅ Subject updated to: {self.current_subject}\n\n"
            "Ready to send?",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("✅ Send Now", callback_data="confirm_send")],
                [InlineKeyboardButton("❌ Cancel", callback_data="cancel")]
            ])
        )
        
        return CONFIRM_SEND
    
    async def cancel(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        """Cancel conversation."""
        await update.message.reply_text("Operation cancelled.")
        return ConversationHandler.END
    
    async def error_handler(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Handle errors."""
        logger.error(f"Update {update} caused error: {context.error}")
        if update and update.effective_message:
            await update.effective_message.reply_text(
                f"❌ Error: {context.error}"
            )
    
    def run(self) -> None:
        """Start the bot."""
        # Create application
        application = Application.builder().token(TELEGRAM_BOT_TOKEN).build()
        
        # Create conversation handler
        conv_handler = ConversationHandler(
            entry_points=[CommandHandler('send', self.send_start)],
            states={
                SELECT_TEMPLATE: [
                    CallbackQueryHandler(self.template_selected)
                ],
                CONFIRM_SEND: [
                    CallbackQueryHandler(self.confirm_send)
                ],
                CUSTOM_SUBJECT: [
                    MessageHandler(filters.TEXT & ~filters.COMMAND, self.custom_subject)
                ],
            },
            fallbacks=[CommandHandler('cancel', self.cancel)],
        )
        
        # Add handlers
        application.add_handler(conv_handler)
        application.add_handler(CommandHandler('start', self.start))
        application.add_handler(CommandHandler('help', self.help_command))
        application.add_handler(CommandHandler('list', self.list_templates))
        application.add_handler(CommandHandler('emails', self.email_stats))
        application.add_handler(CommandHandler('cancel', self.cancel))
        
        # Error handler
        application.add_error_handler(self.error_handler)
        
        # Start bot
        logger.info("Starting bot...")
        application.run_polling(allowed_updates=Update.ALL_TYPES)


def main():
    """Main entry point."""
    bot = EmailBot()
    bot.run()


if __name__ == '__main__':
    main()
