#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Admin panel functionality for DTM Test Bot
Handles admin operations including statistics and question management
"""

import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from database import DatabaseManager
from translations import TranslationManager

logger = logging.getLogger(__name__)

class AdminManager:
    def __init__(self, db: DatabaseManager):
        self.db = db
        self.translations = TranslationManager()
        
        # Get super admin ID from config
        from config import Config
        self.SUPER_ADMIN_ID = Config.SUPER_ADMIN_ID
        
        # Add super admin to database
        self.db.add_admin(self.SUPER_ADMIN_ID)
    
    def is_admin(self, user_id: int) -> bool:
        """Check if user is admin"""
        return user_id == self.SUPER_ADMIN_ID or self.db.is_admin(user_id)
    
    async def show_admin_panel(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Show admin panel main menu"""
        if not update.effective_user or not update.callback_query:
            return
        user_id = update.effective_user.id
        
        if not self.is_admin(user_id):
            await update.callback_query.answer("❌ Sizda admin huquqlari yo'q!")
            return
        
        lang = self.db.get_user_language(user_id)
        t = self.translations.get_translation(lang)
        
        keyboard = [
            [InlineKeyboardButton("📊 Statistika", callback_data="admin_statistics")],
            [InlineKeyboardButton("📝 Savollar statistikasi", callback_data="admin_questions_stats")],
            [InlineKeyboardButton("➕ Savol qo'shish", callback_data="admin_add_question")],
            [InlineKeyboardButton("👥 Foydalanuvchilar", callback_data="admin_users")],
            [InlineKeyboardButton("🔙 Orqaga", callback_data="back_to_menu")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        admin_text = (
            "👨‍💼 Admin Panel\n\n"
            "Kerakli bo'limni tanlang:"
        )
        
        await update.callback_query.edit_message_text(admin_text, reply_markup=reply_markup)
    
    async def show_statistics(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Show bot statistics"""
        if not update.effective_user or not update.callback_query:
            return
        user_id = update.effective_user.id
        
        if not self.is_admin(user_id):
            return
        
        stats = self.db.get_user_statistics()
        
        if not stats:
            stats_text = "❌ Statistika ma'lumotlarini olishda xatolik yuz berdi."
        else:
            stats_text = (
                f"📊 Bot Statistikasi\n\n"
                f"👥 Jami foydalanuvchilar: {stats.get('total_users', 0)}\n"
                f"📝 Jami testlar: {stats.get('total_tests', 0)}\n"
                f"📈 O'rtacha ball: {stats.get('average_score', 0)}%\n\n"
                f"📚 Fanlar bo'yicha:\n"
            )
            
            subject_stats = stats.get('subject_statistics', {})
            for subject, count in subject_stats.items():
                stats_text += f"• {subject.title()}: {count} test\n"
        
        keyboard = [[InlineKeyboardButton("🔙 Admin panelga", callback_data="admin_panel")]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.callback_query.edit_message_text(stats_text, reply_markup=reply_markup)
    
    async def show_questions_statistics(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Show questions statistics by subject and language"""
        if not update.effective_user or not update.callback_query:
            return
        user_id = update.effective_user.id
        
        if not self.is_admin(user_id):
            return
        
        subjects = ['mathematics', 'history', 'english', 'biology', 'chemistry', 'law']
        languages = ['uz', 'ru', 'en']
        
        stats_text = "📝 Savollar Statistikasi\n\n"
        
        total_questions = 0
        for subject in subjects:
            stats_text += f"📚 {subject.title()}:\n"
            subject_total = 0
            
            for lang in languages:
                count = self.db.get_questions_count(subject, lang)
                stats_text += f"  • {lang.upper()}: {count} savol\n"
                subject_total += count
            
            stats_text += f"  Jami: {subject_total} savol\n\n"
            total_questions += subject_total
        
        stats_text += f"🔢 Umumiy savollar soni: {total_questions}"
        
        keyboard = [[InlineKeyboardButton("🔙 Admin panelga", callback_data="admin_panel")]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.callback_query.edit_message_text(stats_text, reply_markup=reply_markup)
    
    async def show_users_list(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Show users list (simplified)"""
        if not update.effective_user or not update.callback_query:
            return
        user_id = update.effective_user.id
        
        if not self.is_admin(user_id):
            return
        
        stats = self.db.get_user_statistics()
        total_users = stats.get('total_users', 0)
        total_tests = stats.get('total_tests', 0)
        
        users_text = (
            f"👥 Foydalanuvchilar\n\n"
            f"Jami ro'yxatdan o'tganlar: {total_users}\n"
            f"Jami o'tkazilgan testlar: {total_tests}\n\n"
            f"Batafsil ma'lumot uchun ma'lumotlar bazasiga murojaat qiling."
        )
        
        keyboard = [[InlineKeyboardButton("🔙 Admin panelga", callback_data="admin_panel")]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.callback_query.edit_message_text(users_text, reply_markup=reply_markup)
    
    async def handle_admin_callback(self, update: Update, context: ContextTypes.DEFAULT_TYPE, callback_data: str):
        """Handle admin panel callbacks"""
        if not update.effective_user or not update.callback_query:
            return
        user_id = update.effective_user.id
        
        if not self.is_admin(user_id):
            await update.callback_query.answer("❌ Sizda admin huquqlari yo'q!")
            return
        
        if callback_data == "admin_statistics":
            await self.show_statistics(update, context)
        
        elif callback_data == "admin_questions_stats":
            await self.show_questions_statistics(update, context)
        
        elif callback_data == "admin_add_question":
            await self.show_add_question_info(update, context)
        
        elif callback_data == "admin_users":
            await self.show_users_list(update, context)
        
        elif callback_data == "admin_panel":
            await self.show_admin_panel(update, context)
    
    async def show_add_question_info(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Show information about adding questions"""
        if not update.callback_query:
            return
        info_text = (
            "➕ Savol qo'shish\n\n"
            "Hozircha savollar to'g'ridan-to'g'ri ma'lumotlar bazasiga "
            "qo'shilishi kerak.\n\n"
            "Keyingi versiyalarda bot orqali savol qo'shish "
            "funksiyasi qo'shiladi.\n\n"
            "Ma'lumotlar bazasi fayli: data/dtm_test.db\n"
            "Jadval nomi: questions"
        )
        
        keyboard = [[InlineKeyboardButton("🔙 Admin panelga", callback_data="admin_panel")]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.callback_query.edit_message_text(info_text, reply_markup=reply_markup)
