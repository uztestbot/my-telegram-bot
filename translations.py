#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Translation management for DTM Test Bot
Handles multi-language support for the bot interface
"""

import json
import os
import logging

logger = logging.getLogger(__name__)

class TranslationManager:
    def __init__(self, translations_dir: str = "translations"):
        self.translations_dir = translations_dir
        self.translations = {}
        self.load_translations()
    
    def load_translations(self):
        """Load all translation files"""
        languages = ['uz', 'ru', 'en']
        
        for lang in languages:
            file_path = os.path.join(self.translations_dir, f"{lang}.json")
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    self.translations[lang] = json.load(f)
                logger.info(f"Loaded {lang} translations")
            except FileNotFoundError:
                logger.warning(f"Translation file not found: {file_path}")
                self.translations[lang] = {}
            except json.JSONDecodeError as e:
                logger.error(f"Error parsing {file_path}: {e}")
                self.translations[lang] = {}
    
    def get_translation(self, language: str) -> dict:
        """Get translations for specific language"""
        return self.translations.get(language, self.translations.get('uz', {}))
    
    def get_text(self, language: str, key: str, default: str = "") -> str:
        """Get specific translation text"""
        translations = self.get_translation(language)
        return translations.get(key, default)
    
    def reload_translations(self):
        """Reload translation files"""
        self.load_translations()
