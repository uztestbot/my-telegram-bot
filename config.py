#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Configuration file for DTM Test Bot
Contains all bot settings and constants
"""

import os

class Config:
    """Configuration class for DTM Test Bot"""
    
    # Bot settings
    BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN', 'your_bot_token_here')
    
    # Database settings
    DATABASE_PATH = "data/dtm_test.db"
    
    # Supported languages
    SUPPORTED_LANGUAGES = ['uz', 'ru', 'en']
    DEFAULT_LANGUAGE = 'uz'
    
    # Subjects available for testing
    SUBJECTS = [
        'mathematics',
        'history', 
        'english',
        'biology',
        'chemistry',
        'law'
    ]
    
    # Test settings
    QUESTIONS_PER_TEST = 10
    RESULTS_HISTORY_LIMIT = 5
    
    # Admin settings - sizning Telegram user ID raqamingizni kiriting
    SUPER_ADMIN_ID = int(os.getenv('SUPER_ADMIN_ID', '123456789'))
    
    # File paths
    TRANSLATIONS_DIR = "translations"
    DATA_DIR = "data"
    
    # Bot messages limits
    MAX_MESSAGE_LENGTH = 4096
    MAX_CAPTION_LENGTH = 1024
    
    @classmethod
    def get_database_path(cls) -> str:
        """Get database file path"""
        # Ensure data directory exists
        os.makedirs(cls.DATA_DIR, exist_ok=True)
        return cls.DATABASE_PATH
    
    @classmethod
    def get_translations_path(cls, language: str) -> str:
        """Get translation file path for specific language"""
        os.makedirs(cls.TRANSLATIONS_DIR, exist_ok=True)
        return os.path.join(cls.TRANSLATIONS_DIR, f"{language}.json")
