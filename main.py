#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
DTM Test Bot - Telegram bot for educational testing
Supports 3 languages and 6 subjects with comprehensive testing system
"""

import os
import logging
import json
from datetime import datetime
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes
from database import DatabaseManager
from translations import TranslationManager
from admin import AdminManager
from config import Config
import random

# Configure logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

class DTMTestBot:
    def __init__(self):
        self.db = DatabaseManager()
        self.translations = TranslationManager()
        self.admin = AdminManager(self.db)
        self.config = Config()
        
        # Initialize database
        self.db.init_database()
        
        # Store current test sessions
        self.active_tests = {}
    
    async def start(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /start command"""
        if not update.effective_user:
            return
        user_id = update.effective_user.id
        username = update.effective_user.username or "Unknown"
        first_name = update.effective_user.first_name or ""
        
        # Register user if not exists
        self.db.register_user(user_id, username, first_name)
        
        # Check if user has selected language
        user_lang = self.db.get_user_language(user_id)
        
        if not user_lang:
            await self.show_language_selection(update, context)
        else:
            await self.show_main_menu(update, context, user_lang)
    
    async def show_language_selection(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Show language selection menu"""
        keyboard = [
            [InlineKeyboardButton("🇺🇿 O'zbek", callback_data="lang_uz")],
            [InlineKeyboardButton("🇷🇺 Русский", callback_data="lang_ru")],
            [InlineKeyboardButton("🇬🇧 English", callback_data="lang_en")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        welcome_text = (
            "🎓 DTM Test Botiga xush kelibsiz!\n"
            "🇷🇺 Добро пожаловать в DTM Test Bot!\n"
            "🇬🇧 Welcome to DTM Test Bot!\n\n"
            "Tilni tanlang / Выберите язык / Choose language:"
        )
        
        if update.message:
            await update.message.reply_text(welcome_text, reply_markup=reply_markup)
        elif update.callback_query:
            await update.callback_query.edit_message_text(welcome_text, reply_markup=reply_markup)
    
    async def show_main_menu(self, update: Update, context: ContextTypes.DEFAULT_TYPE, lang: str):
        """Show main menu"""
        t = self.translations.get_translation(lang)
        
        keyboard = [
            [InlineKeyboardButton(t["select_subject"], callback_data="select_subject")],
            [InlineKeyboardButton(t["my_results"], callback_data="my_results")],
            [InlineKeyboardButton(t["change_language"], callback_data="change_language")],
            [InlineKeyboardButton(t["help"], callback_data="help")]
        ]
        
        # Add admin panel for authorized users
        if update.effective_user:
            user_id = update.effective_user.id
            if self.admin.is_admin(user_id):
                keyboard.append([InlineKeyboardButton(t.get("admin_panel", "👨‍💼 Admin Panel"), callback_data="admin_panel")])
        
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        if update.message:
            await update.message.reply_text(t["welcome_message"], reply_markup=reply_markup)
        elif update.callback_query:
            await update.callback_query.edit_message_text(t["welcome_message"], reply_markup=reply_markup)
    
    async def show_subject_selection(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Show subject selection menu"""
        if not update.effective_user or not update.callback_query:
            return
        user_id = update.effective_user.id
        lang = self.db.get_user_language(user_id)
        t = self.translations.get_translation(lang)
        
        subjects = self.config.SUBJECTS
        keyboard = []
        
        for subject_key in subjects:
            subject_name = t.get(f"subject_{subject_key}", subject_key.title())
            keyboard.append([InlineKeyboardButton(subject_name, callback_data=f"subject_{subject_key}")])
        
        keyboard.append([InlineKeyboardButton(t["back_to_menu"], callback_data="back_to_menu")])
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.callback_query.edit_message_text(t["select_subject_text"], reply_markup=reply_markup)
    
    async def start_test(self, update: Update, context: ContextTypes.DEFAULT_TYPE, subject: str):
        """Start a test for selected subject"""
        if not update.effective_user or not update.callback_query:
            return
        user_id = update.effective_user.id
        lang = self.db.get_user_language(user_id)
        t = self.translations.get_translation(lang)
        
        # Get random questions for the subject
        questions = self.db.get_random_questions(subject, lang, 10)
        
        if not questions:
            await update.callback_query.answer(t["no_questions_available"])
            return
        
        # Store test session
        test_session = {
            'user_id': user_id,
            'subject': subject,
            'questions': questions,
            'current_question': 0,
            'answers': {},
            'start_time': datetime.now()
        }
        
        self.active_tests[user_id] = test_session
        
        # Show first question
        await self.show_question(update, context)
    
    async def show_question(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Show current question"""
        if not update.effective_user or not update.callback_query:
            return
        user_id = update.effective_user.id
        lang = self.db.get_user_language(user_id)
        t = self.translations.get_translation(lang)
        
        if user_id not in self.active_tests:
            await update.callback_query.answer(t["test_not_found"])
            return
        
        test_session = self.active_tests[user_id]
        current_q_idx = test_session['current_question']
        questions = test_session['questions']
        
        if current_q_idx >= len(questions):
            await self.finish_test(update, context)
            return
        
        question = questions[current_q_idx]
        question_num = current_q_idx + 1
        total_questions = len(questions)
        
        # Create answer options
        keyboard = []
        options = ['A', 'B', 'C', 'D']
        for i, option in enumerate(options):
            option_text = question[f'option_{option.lower()}']
            if option_text:
                keyboard.append([InlineKeyboardButton(f"{option}. {option_text}", callback_data=f"answer_{option}_{current_q_idx}")])
        
        keyboard.append([InlineKeyboardButton(t["cancel_test"], callback_data="cancel_test")])
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        question_text = (
            f"❓ {t['question']} {question_num}/{total_questions}\n\n"
            f"{question['question_text']}"
        )
        
        await update.callback_query.edit_message_text(question_text, reply_markup=reply_markup)
    
    async def handle_answer(self, update: Update, context: ContextTypes.DEFAULT_TYPE, answer: str, question_idx: int):
        """Handle user's answer"""
        if not update.effective_user:
            return
        user_id = update.effective_user.id
        
        if user_id not in self.active_tests:
            return
        
        test_session = self.active_tests[user_id]
        
        # Store answer
        test_session['answers'][question_idx] = answer
        test_session['current_question'] = question_idx + 1
        
        # Show next question
        await self.show_question(update, context)
    
    async def finish_test(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Finish test and show results"""
        if not update.effective_user or not update.callback_query:
            return
        user_id = update.effective_user.id
        lang = self.db.get_user_language(user_id)
        t = self.translations.get_translation(lang)
        
        if user_id not in self.active_tests:
            return
        
        test_session = self.active_tests[user_id]
        questions = test_session['questions']
        answers = test_session['answers']
        
        # Calculate results and prepare detailed analysis
        correct_count = 0
        total_questions = len(questions)
        test_answers = []
        
        for i, question in enumerate(questions):
            user_answer = answers.get(i, '')
            is_correct = user_answer.lower() == question['correct_answer'].lower()
            if is_correct:
                correct_count += 1
            
            # Store detailed answer for analysis
            test_answers.append({
                'question': question['question_text'],
                'user_answer': user_answer.upper(),
                'correct_answer': question['correct_answer'].upper(),
                'is_correct': is_correct,
                'option_a': question['option_a'],
                'option_b': question['option_b'],
                'option_c': question['option_c'],
                'option_d': question['option_d']
            })
        
        wrong_count = total_questions - correct_count
        percentage = round((correct_count / total_questions) * 100, 1)
        
        # Save result to database with detailed answers
        end_time = datetime.now()
        duration = int((end_time - test_session['start_time']).total_seconds())
        
        test_result_id = self.db.save_test_result(
            user_id=user_id,
            subject=test_session['subject'],
            correct_answers=correct_count,
            total_questions=total_questions,
            percentage=percentage,
            duration=duration,
            test_answers=test_answers
        )
        
        # Store test analysis in session for later access
        test_session['test_answers'] = test_answers
        test_session['test_result_id'] = test_result_id
        
        # Create result message
        subject_key = f"subject_{test_session['subject']}"
        subject_name = t.get(subject_key, test_session['subject'].title())
        duration_min = duration // 60
        duration_sec = duration % 60
        
        result_text = (
            f"📊 {t['test_completed']}\n\n"
            f"📚 {t['subject']}: {subject_name}\n"
            f"✅ {t['correct_answers']}: {correct_count}\n"
            f"❌ {t['wrong_answers']}: {wrong_count}\n"
            f"📈 {t['percentage']}: {percentage}%\n"
            f"⏱ {t['duration']}: {duration_min}:{duration_sec:02d}"
        )
        
        keyboard = [
            [InlineKeyboardButton(t["show_analysis"], callback_data="show_analysis")],
            [InlineKeyboardButton(t["back_to_menu"], callback_data="back_to_menu")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.callback_query.edit_message_text(result_text, reply_markup=reply_markup)
    
    async def show_analysis(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Show detailed test analysis"""
        if not update.effective_user or not update.callback_query:
            return
        user_id = update.effective_user.id
        lang = self.db.get_user_language(user_id)
        t = self.translations.get_translation(lang)
        
        # Get test analysis from active session
        test_answers = None
        if user_id in self.active_tests:
            test_answers = self.active_tests[user_id].get('test_answers')
            # Clear session after showing analysis
            del self.active_tests[user_id]
        
        if not test_answers:
            analysis_text = (
                f"📋 {t['test_analysis']}\n\n"
                f"{t.get('no_analysis_available', 'Test tahlili mavjud emas. Avval test topshiring.')}"
            )
        else:
            # Create detailed analysis
            analysis_text = f"📋 {t['test_analysis']}\n\n"
            
            correct_icon = "✅"
            wrong_icon = "❌"
            
            for i, answer in enumerate(test_answers, 1):
                icon = correct_icon if answer['is_correct'] else wrong_icon
                status = "To'g'ri" if answer['is_correct'] else "Noto'g'ri"
                
                question_text = answer['question'][:60] + "..." if len(answer['question']) > 60 else answer['question']
                
                analysis_text += (
                    f"{icon} {i}. {status}\n"
                    f"❓ {question_text}\n"
                    f"👤 Javobingiz: {answer['user_answer']}\n"
                    f"✓ To'g'ri: {answer['correct_answer']}\n\n"
                )
                
                # Limit message length for Telegram
                if len(analysis_text) > 3500:
                    analysis_text += f"... va boshqa {len(test_answers) - i} ta savol"
                    break
        
        keyboard = [[InlineKeyboardButton(t["back_to_menu"], callback_data="back_to_menu")]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.callback_query.edit_message_text(analysis_text, reply_markup=reply_markup)
    
    async def show_results(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Show user's test results"""
        if not update.effective_user or not update.callback_query:
            return
        user_id = update.effective_user.id
        lang = self.db.get_user_language(user_id)
        t = self.translations.get_translation(lang)
        
        results = self.db.get_user_results(user_id, limit=5)
        
        if not results:
            results_text = t["no_results_yet"]
        else:
            results_text = f"📊 {t['your_results']}\n\n"
            
            for i, result in enumerate(results, 1):
                subject_name = t.get(f"subject_{result['subject']}", result['subject'].title())
                date_str = datetime.fromisoformat(result['test_date']).strftime("%d.%m.%Y %H:%M")
                
                results_text += (
                    f"{i}. 📚 {subject_name}\n"
                    f"   📈 {result['percentage']}% ({result['correct_answers']}/{result['total_questions']})\n"
                    f"   📅 {date_str}\n\n"
                )
        
        keyboard = [[InlineKeyboardButton(t["back_to_menu"], callback_data="back_to_menu")]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.callback_query.edit_message_text(results_text, reply_markup=reply_markup)
    
    async def show_help(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Show help information"""
        if not update.effective_user or not update.callback_query:
            return
        user_id = update.effective_user.id
        lang = self.db.get_user_language(user_id)
        t = self.translations.get_translation(lang)
        
        keyboard = [[InlineKeyboardButton(t["back_to_menu"], callback_data="back_to_menu")]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.callback_query.edit_message_text(t["help_text"], reply_markup=reply_markup)
    
    async def callback_handler(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle callback queries"""
        if not update.callback_query or not update.effective_user:
            return
        query = update.callback_query
        await query.answer()
        
        data = query.data
        if not data:
            return
        user_id = update.effective_user.id
        
        # Language selection
        if data.startswith("lang_"):
            lang = data.split("_")[1]
            self.db.set_user_language(user_id, lang)
            await self.show_main_menu(update, context, lang)
        
        # Main menu navigation
        elif data == "select_subject":
            await self.show_subject_selection(update, context)
        
        elif data == "my_results":
            await self.show_results(update, context)
        
        elif data == "change_language":
            await self.show_language_selection(update, context)
        
        elif data == "help":
            await self.show_help(update, context)
        
        elif data == "back_to_menu":
            lang = self.db.get_user_language(user_id)
            await self.show_main_menu(update, context, lang)
        
        # Subject selection
        elif data.startswith("subject_"):
            subject = data.split("_", 1)[1]
            await self.start_test(update, context, subject)
        
        # Answer handling
        elif data.startswith("answer_"):
            parts = data.split("_")
            answer = parts[1]
            question_idx = int(parts[2])
            await self.handle_answer(update, context, answer, question_idx)
        
        # Test control
        elif data == "cancel_test":
            if user_id in self.active_tests:
                del self.active_tests[user_id]
            lang = self.db.get_user_language(user_id)
            await self.show_main_menu(update, context, lang)
        
        elif data == "show_analysis":
            await self.show_analysis(update, context)
        
        # Admin panel
        elif data == "admin_panel":
            await self.admin.show_admin_panel(update, context)
        
        elif data.startswith("admin_"):
            await self.admin.handle_admin_callback(update, context, data)

def main():
    """Main function to run the bot"""
    # Get bot token from environment
    token = os.getenv('TELEGRAM_BOT_TOKEN')
    if not token:
        logger.error("TELEGRAM_BOT_TOKEN environment variable not set!")
        return
    
    # Create bot instance
    bot = DTMTestBot()
    
    # Create application
    application = Application.builder().token(token).build()
    
    # Add handlers
    application.add_handler(CommandHandler("start", bot.start))
    application.add_handler(CallbackQueryHandler(bot.callback_handler))
    
    # Start bot
    logger.info("DTM Test Bot started successfully!")
    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == "__main__":
    main()
