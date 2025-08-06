#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Database management for DTM Test Bot
Handles all database operations including user management, questions, and results
"""

import sqlite3
import json
import random
from datetime import datetime
from typing import List, Dict, Optional, Tuple
import logging

logger = logging.getLogger(__name__)

class DatabaseManager:
    def __init__(self, db_path: str = "data/dtm_test.db"):
        self.db_path = db_path
        self.init_database()
    
    def get_connection(self) -> sqlite3.Connection:
        """Get database connection"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn
    
    def init_database(self):
        """Initialize database with required tables"""
        conn = None
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            # Users table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS users (
                    user_id INTEGER PRIMARY KEY,
                    username TEXT,
                    first_name TEXT,
                    language TEXT DEFAULT 'uz',
                    registration_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    is_admin BOOLEAN DEFAULT 0
                )
            ''')
            
            # Questions table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS questions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    subject TEXT NOT NULL,
                    language TEXT NOT NULL,
                    question_text TEXT NOT NULL,
                    option_a TEXT NOT NULL,
                    option_b TEXT NOT NULL,
                    option_c TEXT NOT NULL,
                    option_d TEXT NOT NULL,
                    correct_answer TEXT NOT NULL,
                    difficulty_level INTEGER DEFAULT 1,
                    created_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Test results table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS test_results (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER NOT NULL,
                    subject TEXT NOT NULL,
                    correct_answers INTEGER NOT NULL,
                    total_questions INTEGER NOT NULL,
                    percentage REAL NOT NULL,
                    duration INTEGER NOT NULL,
                    test_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES users (user_id)
                )
            ''')
            
            # Admin users table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS admin_users (
                    user_id INTEGER PRIMARY KEY,
                    added_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES users (user_id)
                )
            ''')
            
            # Detailed test answers table for analysis
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS test_answers (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    test_result_id INTEGER NOT NULL,
                    question_text TEXT NOT NULL,
                    user_answer TEXT NOT NULL,
                    correct_answer TEXT NOT NULL,
                    is_correct INTEGER NOT NULL,
                    option_a TEXT NOT NULL,
                    option_b TEXT NOT NULL,
                    option_c TEXT NOT NULL,
                    option_d TEXT NOT NULL,
                    FOREIGN KEY (test_result_id) REFERENCES test_results (id)
                )
            ''')
            
            conn.commit()
            
            # Insert sample questions if table is empty
            self._insert_sample_questions()
            
            logger.info("Database initialized successfully")
            
        except Exception as e:
            logger.error(f"Error initializing database: {e}")
        finally:
            if conn:
                conn.close()
    
    def _insert_sample_questions(self):
        """Insert sample questions for testing"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        # Check if questions already exist
        cursor.execute("SELECT COUNT(*) FROM questions")
        count = cursor.fetchone()[0]
        
        if count > 0:
            conn.close()
            return
        
        # Sample questions for each subject and language - 10 questions each
        sample_questions = {
            'mathematics': {
                'uz': [
                    {
                        'question': "2 + 2 ning qiymati nechaga teng?",
                        'options': {'a': '3', 'b': '4', 'c': '5', 'd': '6'},
                        'correct': 'b'
                    },
                    {
                        'question': "10 × 5 ning natijasi qancha?",
                        'options': {'a': '45', 'b': '50', 'c': '55', 'd': '60'},
                        'correct': 'b'
                    },
                    {
                        'question': "√16 ning qiymati nechaga teng?",
                        'options': {'a': '2', 'b': '3', 'c': '4', 'd': '8'},
                        'correct': 'c'
                    },
                    {
                        'question': "15 - 7 ning natijasi nechchi?",
                        'options': {'a': '6', 'b': '7', 'c': '8', 'd': '9'},
                        'correct': 'c'
                    },
                    {
                        'question': "3² ning qiymati nechaga teng?",
                        'options': {'a': '6', 'b': '9', 'c': '12', 'd': '15'},
                        'correct': 'b'
                    },
                    {
                        'question': "72 ÷ 8 ning natijasi qancha?",
                        'options': {'a': '8', 'b': '9', 'c': '10', 'd': '11'},
                        'correct': 'b'
                    },
                    {
                        'question': "Uchburchakning ichki burchaklari yig'indisi necha gradus?",
                        'options': {'a': '90°', 'b': '180°', 'c': '270°', 'd': '360°'},
                        'correct': 'b'
                    },
                    {
                        'question': "0.5 ning kasr ko'rinishi qanday?",
                        'options': {'a': '1/3', 'b': '1/2', 'c': '2/3', 'd': '3/4'},
                        'correct': 'b'
                    },
                    {
                        'question': "Doiraning diametri 10 sm bo'lsa, radiusi necha sm?",
                        'options': {'a': '3 sm', 'b': '4 sm', 'c': '5 sm', 'd': '6 sm'},
                        'correct': 'c'
                    },
                    {
                        'question': "25% ning o'nli kasr ko'rinishi qanday?",
                        'options': {'a': '0.20', 'b': '0.25', 'c': '0.30', 'd': '0.35'},
                        'correct': 'b'
                    }
                ],
                'ru': [
                    {
                        'question': "Чему равно значение 2 + 2?",
                        'options': {'a': '3', 'b': '4', 'c': '5', 'd': '6'},
                        'correct': 'b'
                    },
                    {
                        'question': "Каков результат 10 × 5?",
                        'options': {'a': '45', 'b': '50', 'c': '55', 'd': '60'},
                        'correct': 'b'
                    },
                    {
                        'question': "Чему равно √16?",
                        'options': {'a': '2', 'b': '3', 'c': '4', 'd': '8'},
                        'correct': 'c'
                    },
                    {
                        'question': "Каков результат 15 - 7?",
                        'options': {'a': '6', 'b': '7', 'c': '8', 'd': '9'},
                        'correct': 'c'
                    },
                    {
                        'question': "Чему равно 3²?",
                        'options': {'a': '6', 'b': '9', 'c': '12', 'd': '15'},
                        'correct': 'b'
                    },
                    {
                        'question': "Каков результат 72 ÷ 8?",
                        'options': {'a': '8', 'b': '9', 'c': '10', 'd': '11'},
                        'correct': 'b'
                    },
                    {
                        'question': "Сколько градусов составляет сумма углов треугольника?",
                        'options': {'a': '90°', 'b': '180°', 'c': '270°', 'd': '360°'},
                        'correct': 'b'
                    },
                    {
                        'question': "Как записать 0.5 в виде дроби?",
                        'options': {'a': '1/3', 'b': '1/2', 'c': '2/3', 'd': '3/4'},
                        'correct': 'b'
                    },
                    {
                        'question': "Если диаметр круга 10 см, то каков радиус?",
                        'options': {'a': '3 см', 'b': '4 см', 'c': '5 см', 'd': '6 см'},
                        'correct': 'c'
                    },
                    {
                        'question': "Как записать 25% в виде десятичной дроби?",
                        'options': {'a': '0.20', 'b': '0.25', 'c': '0.30', 'd': '0.35'},
                        'correct': 'b'
                    }
                ],
                'en': [
                    {
                        'question': "What is the value of 2 + 2?",
                        'options': {'a': '3', 'b': '4', 'c': '5', 'd': '6'},
                        'correct': 'b'
                    },
                    {
                        'question': "What is the result of 10 × 5?",
                        'options': {'a': '45', 'b': '50', 'c': '55', 'd': '60'},
                        'correct': 'b'
                    },
                    {
                        'question': "What is the value of √16?",
                        'options': {'a': '2', 'b': '3', 'c': '4', 'd': '8'},
                        'correct': 'c'
                    },
                    {
                        'question': "What is the result of 15 - 7?",
                        'options': {'a': '6', 'b': '7', 'c': '8', 'd': '9'},
                        'correct': 'c'
                    },
                    {
                        'question': "What is the value of 3²?",
                        'options': {'a': '6', 'b': '9', 'c': '12', 'd': '15'},
                        'correct': 'b'
                    },
                    {
                        'question': "What is the result of 72 ÷ 8?",
                        'options': {'a': '8', 'b': '9', 'c': '10', 'd': '11'},
                        'correct': 'b'
                    },
                    {
                        'question': "What is the sum of interior angles of a triangle?",
                        'options': {'a': '90°', 'b': '180°', 'c': '270°', 'd': '360°'},
                        'correct': 'b'
                    },
                    {
                        'question': "What is 0.5 as a fraction?",
                        'options': {'a': '1/3', 'b': '1/2', 'c': '2/3', 'd': '3/4'},
                        'correct': 'b'
                    },
                    {
                        'question': "If a circle's diameter is 10 cm, what is its radius?",
                        'options': {'a': '3 cm', 'b': '4 cm', 'c': '5 cm', 'd': '6 cm'},
                        'correct': 'c'
                    },
                    {
                        'question': "What is 25% as a decimal?",
                        'options': {'a': '0.20', 'b': '0.25', 'c': '0.30', 'd': '0.35'},
                        'correct': 'b'
                    }
                ]
            },
            'history': {
                'uz': [
                    {
                        'question': "O'zbekiston mustaqillik sanasi qachon?",
                        'options': {'a': '1990-yil', 'b': '1991-yil', 'c': '1992-yil', 'd': '1993-yil'},
                        'correct': 'b'
                    },
                    {
                        'question': "Amir Temur qachon tug'ilgan?",
                        'options': {'a': '1336-yil', 'b': '1340-yil', 'c': '1350-yil', 'd': '1360-yil'},
                        'correct': 'a'
                    },
                    {
                        'question': "Samarqand shahrini kim va qachon asos solgan?",
                        'options': {'a': 'Makedoniyalik Iskandar', 'b': 'Amir Temur', 'c': 'Afrosiyob', 'd': 'Qutayba ibn Muslim'},
                        'correct': 'c'
                    },
                    {
                        'question': "Buyuk Ipak yo'li qaysi hududdan o'tgan?",
                        'options': {'a': 'Xorazm', 'b': 'Samarqand', 'c': 'Buxoro', 'd': 'Barcha javoblar to\'g\'ri'},
                        'correct': 'd'
                    },
                    {
                        'question': "Mirzo Ulug'bek qanday fan bilan shug'ullangan?",
                        'options': {'a': 'Tibbiyot', 'b': 'Astronomiya', 'c': 'Falsafa', 'd': 'Adabiyot'},
                        'correct': 'b'
                    },
                    {
                        'question': "Boburnoma asarining muallifi kim?",
                        'options': {'a': 'Zahiriddin Muhammad Bobur', 'b': 'Alisher Navoiy', 'c': 'Hofiz Sherozi', 'd': 'Jomiy'},
                        'correct': 'a'
                    },
                    {
                        'question': "O'rta Osiyoga arab bosqinchilari qachon kelgan?",
                        'options': {'a': '7-asr', 'b': '8-asr', 'c': '9-asr', 'd': '10-asr'},
                        'correct': 'a'
                    },
                    {
                        'question': "Xorazm shahlar sulolasi qachon hukmronlik qilgan?",
                        'options': {'a': '11-12 asrlar', 'b': '12-13 asrlar', 'c': '13-14 asrlar', 'd': '14-15 asrlar'},
                        'correct': 'b'
                    },
                    {
                        'question': "Buxoro xonligi qachon tuzilgan?",
                        'options': {'a': '15-asr', 'b': '16-asr', 'c': '17-asr', 'd': '18-asr'},
                        'correct': 'b'
                    },
                    {
                        'question': "Turkiston general-gubernatorligi qachon tashkil etilgan?",
                        'options': {'a': '1865-yil', 'b': '1867-yil', 'c': '1868-yil', 'd': '1870-yil'},
                        'correct': 'b'
                    }
                ],
                'ru': [
                    {
                        'question': "Когда была объявлена независимость Узбекистана?",
                        'options': {'a': '1990 год', 'b': '1991 год', 'c': '1992 год', 'd': '1993 год'},
                        'correct': 'b'
                    },
                    {
                        'question': "Когда родился Амир Темур?",
                        'options': {'a': '1336 год', 'b': '1340 год', 'c': '1350 год', 'd': '1360 год'},
                        'correct': 'a'
                    },
                    {
                        'question': "Кто и когда основал город Самарканд?",
                        'options': {'a': 'Александр Македонский', 'b': 'Амир Темур', 'c': 'Афросиаб', 'd': 'Кутайба ибн Муслим'},
                        'correct': 'c'
                    },
                    {
                        'question': "Через какие территории проходил Великий шелковый путь?",
                        'options': {'a': 'Хорезм', 'b': 'Самарканд', 'c': 'Бухара', 'd': 'Все ответы верны'},
                        'correct': 'd'
                    },
                    {
                        'question': "Какой наукой занимался Мирзо Улугбек?",
                        'options': {'a': 'Медицина', 'b': 'Астрономия', 'c': 'Философия', 'd': 'Литература'},
                        'correct': 'b'
                    },
                    {
                        'question': "Кто автор произведения \"Бабурнаме\"?",
                        'options': {'a': 'Захириддин Мухаммад Бабур', 'b': 'Алишер Навои', 'c': 'Хафиз Ширази', 'd': 'Джами'},
                        'correct': 'a'
                    },
                    {
                        'question': "Когда арабские завоеватели пришли в Среднюю Азию?",
                        'options': {'a': '7 век', 'b': '8 век', 'c': '9 век', 'd': '10 век'},
                        'correct': 'a'
                    },
                    {
                        'question': "Когда правила династия Хорезмшахов?",
                        'options': {'a': '11-12 века', 'b': '12-13 века', 'c': '13-14 века', 'd': '14-15 века'},
                        'correct': 'b'
                    },
                    {
                        'question': "Когда было образовано Бухарское ханство?",
                        'options': {'a': '15 век', 'b': '16 век', 'c': '17 век', 'd': '18 век'},
                        'correct': 'b'
                    },
                    {
                        'question': "Когда было создано Туркестанское генерал-губернаторство?",
                        'options': {'a': '1865 год', 'b': '1867 год', 'c': '1868 год', 'd': '1870 год'},
                        'correct': 'b'
                    }
                ],
                'en': [
                    {
                        'question': "When was Uzbekistan's independence declared?",
                        'options': {'a': '1990', 'b': '1991', 'c': '1992', 'd': '1993'},
                        'correct': 'b'
                    },
                    {
                        'question': "When was Amir Temur born?",
                        'options': {'a': '1336', 'b': '1340', 'c': '1350', 'd': '1360'},
                        'correct': 'a'
                    },
                    {
                        'question': "Who founded the city of Samarkand?",
                        'options': {'a': 'Alexander the Great', 'b': 'Amir Temur', 'c': 'Afrosiab', 'd': 'Qutayba ibn Muslim'},
                        'correct': 'c'
                    },
                    {
                        'question': "Which territories did the Great Silk Road pass through?",
                        'options': {'a': 'Khorezm', 'b': 'Samarkand', 'c': 'Bukhara', 'd': 'All answers are correct'},
                        'correct': 'd'
                    },
                    {
                        'question': "What science did Mirzo Ulugbek study?",
                        'options': {'a': 'Medicine', 'b': 'Astronomy', 'c': 'Philosophy', 'd': 'Literature'},
                        'correct': 'b'
                    },
                    {
                        'question': "Who is the author of \"Baburnama\"?",
                        'options': {'a': 'Zahiriddin Muhammad Babur', 'b': 'Alisher Navoi', 'c': 'Hafiz Shirazi', 'd': 'Jami'},
                        'correct': 'a'
                    },
                    {
                        'question': "When did Arab conquerors come to Central Asia?",
                        'options': {'a': '7th century', 'b': '8th century', 'c': '9th century', 'd': '10th century'},
                        'correct': 'a'
                    },
                    {
                        'question': "When did the Khwarezmshah dynasty rule?",
                        'options': {'a': '11-12 centuries', 'b': '12-13 centuries', 'c': '13-14 centuries', 'd': '14-15 centuries'},
                        'correct': 'b'
                    },
                    {
                        'question': "When was the Bukhara Khanate established?",
                        'options': {'a': '15th century', 'b': '16th century', 'c': '17th century', 'd': '18th century'},
                        'correct': 'b'
                    },
                    {
                        'question': "When was the Turkestan Governor-Generalship created?",
                        'options': {'a': '1865', 'b': '1867', 'c': '1868', 'd': '1870'},
                        'correct': 'b'
                    }
                ]
            },
            'english': {
                'uz': [
                    {
                        'question': "\"Hello\" so'zining ma'nosi nima?",
                        'options': {'a': 'Salom', 'b': 'Xayr', 'c': 'Rahmat', 'd': 'Kechirasiz'},
                        'correct': 'a'
                    },
                    {
                        'question': "\"Book\" so'zi qanday tarjima qilinadi?",
                        'options': {'a': 'Daftar', 'b': 'Kitob', 'c': 'Qalam', 'd': 'Stol'},
                        'correct': 'b'
                    },
                    {
                        'question': "\"Good morning\" iborasi qanday ma'no beradi?",
                        'options': {'a': 'Xayrli kech', 'b': 'Xayrli tong', 'c': 'Xayrli kun', 'd': 'Xayrli tun'},
                        'correct': 'b'
                    },
                    {
                        'question': "\"Cat\" so'zining ko'plik shakli qanday?",
                        'options': {'a': 'Cats', 'b': 'Cates', 'c': 'Caties', 'd': 'Catses'},
                        'correct': 'a'
                    },
                    {
                        'question': "\"I am a student\" jumlasida qaysi so'z ot hisoblanadi?",
                        'options': {'a': 'I', 'b': 'am', 'c': 'a', 'd': 'student'},
                        'correct': 'd'
                    },
                    {
                        'question': "\"Beautiful\" so'zining antonimi qaysi?",
                        'options': {'a': 'Pretty', 'b': 'Ugly', 'c': 'Nice', 'd': 'Good'},
                        'correct': 'b'
                    },
                    {
                        'question': "\"Can\" modal fe'li qanday ma'no bildiradi?",
                        'options': {'a': 'Majburiyat', 'b': 'Imkoniyat', 'c': 'Ehtimollik', 'd': 'Taklif'},
                        'correct': 'b'
                    },
                    {
                        'question': "\"Where\" so'zi qaysi tur savol so'zi?",
                        'options': {'a': 'Joy', 'b': 'Vaqt', 'c': 'Sabab', 'd': 'Usul'},
                        'correct': 'a'
                    },
                    {
                        'question': "\"Yesterday\" so'zining ma'nosi nima?",
                        'options': {'a': 'Bugun', 'b': 'Ertaga', 'c': 'Kecha', 'd': 'Hozir'},
                        'correct': 'c'
                    },
                    {
                        'question': "\"Read\" fe'lining o'tgan zamon shakli qanday?",
                        'options': {'a': 'Readed', 'b': 'Red', 'c': 'Read', 'd': 'Reading'},
                        'correct': 'c'
                    }
                ],
                'ru': [
                    {
                        'question': "Что означает слово \"Hello\"?",
                        'options': {'a': 'Привет', 'b': 'Пока', 'c': 'Спасибо', 'd': 'Извините'},
                        'correct': 'a'
                    },
                    {
                        'question': "Как переводится слово \"Book\"?",
                        'options': {'a': 'Тетрадь', 'b': 'Книга', 'c': 'Ручка', 'd': 'Стол'},
                        'correct': 'b'
                    },
                    {
                        'question': "Что означает выражение \"Good morning\"?",
                        'options': {'a': 'Добрый вечер', 'b': 'Доброе утро', 'c': 'Добрый день', 'd': 'Спокойной ночи'},
                        'correct': 'b'
                    },
                    {
                        'question': "Какая форма множественного числа у слова \"Cat\"?",
                        'options': {'a': 'Cats', 'b': 'Cates', 'c': 'Caties', 'd': 'Catses'},
                        'correct': 'a'
                    },
                    {
                        'question': "В предложении \"I am a student\" какое слово является существительным?",
                        'options': {'a': 'I', 'b': 'am', 'c': 'a', 'd': 'student'},
                        'correct': 'd'
                    },
                    {
                        'question': "Какой антоним у слова \"Beautiful\"?",
                        'options': {'a': 'Pretty', 'b': 'Ugly', 'c': 'Nice', 'd': 'Good'},
                        'correct': 'b'
                    },
                    {
                        'question': "Что выражает модальный глагол \"Can\"?",
                        'options': {'a': 'Обязанность', 'b': 'Возможность', 'c': 'Вероятность', 'd': 'Предложение'},
                        'correct': 'b'
                    },
                    {
                        'question': "\"Where\" - это вопросительное слово о чем?",
                        'options': {'a': 'Место', 'b': 'Время', 'c': 'Причина', 'd': 'Способ'},
                        'correct': 'a'
                    },
                    {
                        'question': "Что означает слово \"Yesterday\"?",
                        'options': {'a': 'Сегодня', 'b': 'Завтра', 'c': 'Вчера', 'd': 'Сейчас'},
                        'correct': 'c'
                    },
                    {
                        'question': "Какая форма прошедшего времени у глагола \"Read\"?",
                        'options': {'a': 'Readed', 'b': 'Red', 'c': 'Read', 'd': 'Reading'},
                        'correct': 'c'
                    }
                ],
                'en': [
                    {
                        'question': "What is the plural form of 'child'?",
                        'options': {'a': 'childs', 'b': 'children', 'c': 'childes', 'd': 'child'},
                        'correct': 'b'
                    },
                    {
                        'question': "Which word is a synonym for 'happy'?",
                        'options': {'a': 'sad', 'b': 'angry', 'c': 'joyful', 'd': 'tired'},
                        'correct': 'c'
                    },
                    {
                        'question': "What is the past tense of 'go'?",
                        'options': {'a': 'goed', 'b': 'went', 'c': 'gone', 'd': 'going'},
                        'correct': 'b'
                    },
                    {
                        'question': "Which article is used before vowel sounds?",
                        'options': {'a': 'a', 'b': 'an', 'c': 'the', 'd': 'any'},
                        'correct': 'b'
                    },
                    {
                        'question': "What type of word is 'quickly'?",
                        'options': {'a': 'noun', 'b': 'verb', 'c': 'adjective', 'd': 'adverb'},
                        'correct': 'd'
                    },
                    {
                        'question': "Which sentence is in present continuous tense?",
                        'options': {'a': 'I read books', 'b': 'I am reading', 'c': 'I read yesterday', 'd': 'I will read'},
                        'correct': 'b'
                    },
                    {
                        'question': "What is the opposite of 'big'?",
                        'options': {'a': 'large', 'b': 'huge', 'c': 'small', 'd': 'tall'},
                        'correct': 'c'
                    },
                    {
                        'question': "Which word is a preposition?",
                        'options': {'a': 'under', 'b': 'blue', 'c': 'run', 'd': 'happy'},
                        'correct': 'a'
                    },
                    {
                        'question': "What does 'library' mean?",
                        'options': {'a': 'school', 'b': 'place for books', 'c': 'hospital', 'd': 'shop'},
                        'correct': 'b'
                    },
                    {
                        'question': "Which is the correct spelling?",
                        'options': {'a': 'recieve', 'b': 'receive', 'c': 'receve', 'd': 'receeve'},
                        'correct': 'b'
                    }
                ]
            },
            'biology': {
                'uz': [
                    {
                        'question': "Inson tanasida nechta suyak bor?",
                        'options': {'a': '200', 'b': '206', 'c': '210', 'd': '220'},
                        'correct': 'b'
                    },
                    {
                        'question': "Fotosintez jarayoni qayerda sodir bo'ladi?",
                        'options': {'a': 'Ildizda', 'b': 'Poyada', 'c': 'Bargda', 'd': 'Gullarda'},
                        'correct': 'c'
                    },
                    {
                        'question': "DNK ning to'liq nomi qanday?",
                        'options': {'a': 'Deoksiribo nukleik kislota', 'b': 'Deoksi nukleik asid', 'c': 'Dioksi nukleik kislota', 'd': 'Dinukleik kislota'},
                        'correct': 'a'
                    },
                    {
                        'question': "Yurak qancha kameradan iborat?",
                        'options': {'a': '2', 'b': '3', 'c': '4', 'd': '5'},
                        'correct': 'c'
                    },
                    {
                        'question': "Og'iz bo'shlig'ida ovqat hazmi qaysi ferment yordamida boshlanadi?",
                        'options': {'a': 'Pepsin', 'b': 'Amilaza', 'c': 'Lipaza', 'd': 'Tripsin'},
                        'correct': 'b'
                    },
                    {
                        'question': "Hujayra bo'linishining qaysi fazasida xromosomalar yadroning markazida joylashadi?",
                        'options': {'a': 'Profaza', 'b': 'Metafaza', 'c': 'Anafaza', 'd': 'Telofaza'},
                        'correct': 'b'
                    },
                    {
                        'question': "Inson organizmida qaysi organ glyukoza zaxirasini saqlaydi?",
                        'options': {'a': 'Yurak', 'b': 'Jigar', 'c': 'Buyrak', 'd': 'Miya'},
                        'correct': 'b'
                    },
                    {
                        'question': "Quyosh nuridan vitamin D hosil bo'lishi uchun qaysi organ javobgar?",
                        'options': {'a': 'Teri', 'b': 'Jigar', 'c': 'Buyrak', 'd': 'Miya'},
                        'correct': 'a'
                    },
                    {
                        'question': "Nafas olish jarayonida kislorod qaysi organella tomonidan ishlatiladi?",
                        'options': {'a': 'Ribosoma', 'b': 'Mitoxondriya', 'c': 'Xloroplast', 'd': 'Lizosoma'},
                        'correct': 'b'
                    },
                    {
                        'question': "Genetik ma'lumot RNA dan protein sinteziga qaysi jarayon orqali o'tkaziladi?",
                        'options': {'a': 'Replikatsiya', 'b': 'Transkriptsiya', 'c': 'Translatsiya', 'd': 'Mutatsiya'},
                        'correct': 'c'
                    }
                ],
                'ru': [
                    {
                        'question': "Сколько костей в человеческом теле?",
                        'options': {'a': '200', 'b': '206', 'c': '210', 'd': '220'},
                        'correct': 'b'
                    },
                    {
                        'question': "Где происходит процесс фотосинтеза?",
                        'options': {'a': 'В корнях', 'b': 'В стебле', 'c': 'В листьях', 'd': 'В цветах'},
                        'correct': 'c'
                    },
                    {
                        'question': "Что означает аббревиатура ДНК?",
                        'options': {'a': 'Дезоксирибонуклеиновая кислота', 'b': 'Дезокси нуклеиновая кислота', 'c': 'Диокси нуклеиновая кислота', 'd': 'Динуклеиновая кислота'},
                        'correct': 'a'
                    },
                    {
                        'question': "Из скольких камер состоит сердце человека?",
                        'options': {'a': '2', 'b': '3', 'c': '4', 'd': '5'},
                        'correct': 'c'
                    },
                    {
                        'question': "Какой фермент начинает переваривание пищи в ротовой полости?",
                        'options': {'a': 'Пепсин', 'b': 'Амилаза', 'c': 'Липаза', 'd': 'Трипсин'},
                        'correct': 'b'
                    },
                    {
                        'question': "В какой фазе деления клетки хромосомы располагаются в центре ядра?",
                        'options': {'a': 'Профаза', 'b': 'Метафаза', 'c': 'Анафаза', 'd': 'Телофаза'},
                        'correct': 'b'
                    },
                    {
                        'question': "Какой орган в организме человека хранит запасы глюкозы?",
                        'options': {'a': 'Сердце', 'b': 'Печень', 'c': 'Почки', 'd': 'Мозг'},
                        'correct': 'b'
                    },
                    {
                        'question': "Какой орган отвечает за образование витамина D под воздействием солнечного света?",
                        'options': {'a': 'Кожа', 'b': 'Печень', 'c': 'Почки', 'd': 'Мозг'},
                        'correct': 'a'
                    },
                    {
                        'question': "Какая органелла использует кислород в процессе дыхания?",
                        'options': {'a': 'Рибосома', 'b': 'Митохондрия', 'c': 'Хлоропласт', 'd': 'Лизосома'},
                        'correct': 'b'
                    },
                    {
                        'question': "Каким процессом генетическая информация передается от РНК к белку?",
                        'options': {'a': 'Репликация', 'b': 'Транскрипция', 'c': 'Трансляция', 'd': 'Мутация'},
                        'correct': 'c'
                    }
                ],
                'en': [
                    {
                        'question': "How many bones are in the human body?",
                        'options': {'a': '200', 'b': '206', 'c': '210', 'd': '220'},
                        'correct': 'b'
                    },
                    {
                        'question': "Where does photosynthesis occur?",
                        'options': {'a': 'Roots', 'b': 'Stem', 'c': 'Leaves', 'd': 'Flowers'},
                        'correct': 'c'
                    },
                    {
                        'question': "What does DNA stand for?",
                        'options': {'a': 'Deoxyribonucleic acid', 'b': 'Deoxy nucleic acid', 'c': 'Dioxy nucleic acid', 'd': 'Dinucleic acid'},
                        'correct': 'a'
                    },
                    {
                        'question': "How many chambers does the human heart have?",
                        'options': {'a': '2', 'b': '3', 'c': '4', 'd': '5'},
                        'correct': 'c'
                    },
                    {
                        'question': "Which enzyme begins food digestion in the mouth?",
                        'options': {'a': 'Pepsin', 'b': 'Amylase', 'c': 'Lipase', 'd': 'Trypsin'},
                        'correct': 'b'
                    },
                    {
                        'question': "In which phase of cell division do chromosomes line up in the center?",
                        'options': {'a': 'Prophase', 'b': 'Metaphase', 'c': 'Anaphase', 'd': 'Telophase'},
                        'correct': 'b'
                    },
                    {
                        'question': "Which organ stores glucose reserves in the human body?",
                        'options': {'a': 'Heart', 'b': 'Liver', 'c': 'Kidneys', 'd': 'Brain'},
                        'correct': 'b'
                    },
                    {
                        'question': "Which organ produces vitamin D when exposed to sunlight?",
                        'options': {'a': 'Skin', 'b': 'Liver', 'c': 'Kidneys', 'd': 'Brain'},
                        'correct': 'a'
                    },
                    {
                        'question': "Which organelle uses oxygen in cellular respiration?",
                        'options': {'a': 'Ribosome', 'b': 'Mitochondria', 'c': 'Chloroplast', 'd': 'Lysosome'},
                        'correct': 'b'
                    },
                    {
                        'question': "What process transfers genetic information from RNA to protein?",
                        'options': {'a': 'Replication', 'b': 'Transcription', 'c': 'Translation', 'd': 'Mutation'},
                        'correct': 'c'
                    }
                ]
            },
            'chemistry': {
                'uz': [
                    {
                        'question': "Suvning kimyoviy formulasi qanday?",
                        'options': {'a': 'H2O', 'b': 'CO2', 'c': 'O2', 'd': 'H2SO4'},
                        'correct': 'a'
                    },
                    {
                        'question': "Kislorodning atom raqami nechchi?",
                        'options': {'a': '6', 'b': '7', 'c': '8', 'd': '9'},
                        'correct': 'c'
                    },
                    {
                        'question': "Karbonat angidridning formulasi qanday?",
                        'options': {'a': 'CO', 'b': 'CO2', 'c': 'C2O', 'd': 'C2O2'},
                        'correct': 'b'
                    },
                    {
                        'question': "Tuzning (NaCl) tarkibidagi elementlar qaysilar?",
                        'options': {'a': 'Natriy va Karbon', 'b': 'Natriy va Xlor', 'c': 'Azot va Xlor', 'd': 'Natriy va Kalsiy'},
                        'correct': 'b'
                    },
                    {
                        'question': "Mendeleyev jadvalidagi birinchi element qaysi?",
                        'options': {'a': 'Geliy', 'b': 'Vodorod', 'c': 'Litiy', 'd': 'Berilliy'},
                        'correct': 'b'
                    },
                    {
                        'question': "Kislota va ishqor aralashganda qanday jarayon yuz beradi?",
                        'options': {'a': 'Oksidlanish', 'b': 'Qaytarilish', 'c': 'Neytrallanish', 'd': 'Elektroliz'},
                        'correct': 'c'
                    },
                    {
                        'question': "Oltingugurtning kimyoviy belgisi qanday?",
                        'options': {'a': 'S', 'b': 'Si', 'c': 'Sc', 'd': 'Se'},
                        'correct': 'a'
                    },
                    {
                        'question': "pH shkala nechta birlikdan iborat?",
                        'options': {'a': '10', 'b': '12', 'c': '14', 'd': '16'},
                        'correct': 'c'
                    },
                    {
                        'question': "Organik kimyoning asosiy elementi qaysi?",
                        'options': {'a': 'Kislorod', 'b': 'Vodorod', 'c': 'Karbon', 'd': 'Azot'},
                        'correct': 'c'
                    },
                    {
                        'question': "Avogadro sonining qiymati taxminan nechchi?",
                        'options': {'a': '6.02×10²²', 'b': '6.02×10²³', 'c': '6.02×10²⁴', 'd': '6.02×10²⁵'},
                        'correct': 'b'
                    }
                ],
                'ru': [
                    {
                        'question': "Какова химическая формула воды?",
                        'options': {'a': 'H2O', 'b': 'CO2', 'c': 'O2', 'd': 'H2SO4'},
                        'correct': 'a'
                    },
                    {
                        'question': "Каков атомный номер кислорода?",
                        'options': {'a': '6', 'b': '7', 'c': '8', 'd': '9'},
                        'correct': 'c'
                    },
                    {
                        'question': "Какова формула углекислого газа?",
                        'options': {'a': 'CO', 'b': 'CO2', 'c': 'C2O', 'd': 'C2O2'},
                        'correct': 'b'
                    },
                    {
                        'question': "Какие элементы входят в состав поваренной соли (NaCl)?",
                        'options': {'a': 'Натрий и Углерод', 'b': 'Натрий и Хлор', 'c': 'Азот и Хлор', 'd': 'Натрий и Кальций'},
                        'correct': 'b'
                    },
                    {
                        'question': "Какой элемент первый в таблице Менделеева?",
                        'options': {'a': 'Гелий', 'b': 'Водород', 'c': 'Литий', 'd': 'Бериллий'},
                        'correct': 'b'
                    },
                    {
                        'question': "Какой процесс происходит при смешивании кислоты и щелочи?",
                        'options': {'a': 'Окисление', 'b': 'Восстановление', 'c': 'Нейтрализация', 'd': 'Электролиз'},
                        'correct': 'c'
                    },
                    {
                        'question': "Какой химический символ у серы?",
                        'options': {'a': 'S', 'b': 'Si', 'c': 'Sc', 'd': 'Se'},
                        'correct': 'a'
                    },
                    {
                        'question': "Из скольких единиц состоит шкала pH?",
                        'options': {'a': '10', 'b': '12', 'c': '14', 'd': '16'},
                        'correct': 'c'
                    },
                    {
                        'question': "Какой основной элемент органической химии?",
                        'options': {'a': 'Кислород', 'b': 'Водород', 'c': 'Углерод', 'd': 'Азот'},
                        'correct': 'c'
                    },
                    {
                        'question': "Каково приблизительное значение числа Авогадро?",
                        'options': {'a': '6.02×10²²', 'b': '6.02×10²³', 'c': '6.02×10²⁴', 'd': '6.02×10²⁵'},
                        'correct': 'b'
                    }
                ],
                'en': [
                    {
                        'question': "What is the chemical formula of water?",
                        'options': {'a': 'H2O', 'b': 'CO2', 'c': 'O2', 'd': 'H2SO4'},
                        'correct': 'a'
                    },
                    {
                        'question': "What is the atomic number of oxygen?",
                        'options': {'a': '6', 'b': '7', 'c': '8', 'd': '9'},
                        'correct': 'c'
                    },
                    {
                        'question': "What is the formula for carbon dioxide?",
                        'options': {'a': 'CO', 'b': 'CO2', 'c': 'C2O', 'd': 'C2O2'},
                        'correct': 'b'
                    },
                    {
                        'question': "Which elements make up table salt (NaCl)?",
                        'options': {'a': 'Sodium and Carbon', 'b': 'Sodium and Chlorine', 'c': 'Nitrogen and Chlorine', 'd': 'Sodium and Calcium'},
                        'correct': 'b'
                    },
                    {
                        'question': "Which element is first in the periodic table?",
                        'options': {'a': 'Helium', 'b': 'Hydrogen', 'c': 'Lithium', 'd': 'Beryllium'},
                        'correct': 'b'
                    },
                    {
                        'question': "What process occurs when acid and base are mixed?",
                        'options': {'a': 'Oxidation', 'b': 'Reduction', 'c': 'Neutralization', 'd': 'Electrolysis'},
                        'correct': 'c'
                    },
                    {
                        'question': "What is the chemical symbol for sulfur?",
                        'options': {'a': 'S', 'b': 'Si', 'c': 'Sc', 'd': 'Se'},
                        'correct': 'a'
                    },
                    {
                        'question': "How many units does the pH scale have?",
                        'options': {'a': '10', 'b': '12', 'c': '14', 'd': '16'},
                        'correct': 'c'
                    },
                    {
                        'question': "What is the main element of organic chemistry?",
                        'options': {'a': 'Oxygen', 'b': 'Hydrogen', 'c': 'Carbon', 'd': 'Nitrogen'},
                        'correct': 'c'
                    },
                    {
                        'question': "What is the approximate value of Avogadro's number?",
                        'options': {'a': '6.02×10²²', 'b': '6.02×10²³', 'c': '6.02×10²⁴', 'd': '6.02×10²⁵'},
                        'correct': 'b'
                    }
                ]
            },
            'law': {
                'uz': [
                    {
                        'question': "O'zbekiston Respublikasining Konstitutsiyasi qachon qabul qilingan?",
                        'options': {'a': '1991-yil', 'b': '1992-yil', 'c': '1993-yil', 'd': '1994-yil'},
                        'correct': 'b'
                    },
                    {
                        'question': "Fuqaro huquqlari qaysi hujjatda belgilab qo'yilgan?",
                        'options': {'a': 'Konstitutsiyada', 'b': 'Qonunda', 'c': 'Farmonida', 'd': 'Qarorida'},
                        'correct': 'a'
                    },
                    {
                        'question': "O'zbekiston Respublikasining Prezidenti necha yilga saylanadi?",
                        'options': {'a': '4 yil', 'b': '5 yil', 'c': '6 yil', 'd': '7 yil'},
                        'correct': 'b'
                    },
                    {
                        'question': "O'zbekiston Respublikasining Oliy Majlisi nechta palatadan iborat?",
                        'options': {'a': '1 palata', 'b': '2 palata', 'c': '3 palata', 'd': '4 palata'},
                        'correct': 'b'
                    },
                    {
                        'question': "Fuqarolik huquqiyat qobiliyati qachon boshlanadi?",
                        'options': {'a': "Tug'ilgandan", 'b': '16 yoshdan', 'c': '18 yoshdan', 'd': '21 yoshdan'},
                        'correct': 'a'
                    },
                    {
                        'question': "Saylov huquqi qanday yoshdan boshlanadi?",
                        'options': {'a': '16 yosh', 'b': '17 yosh', 'c': '18 yosh', 'd': '21 yosh'},
                        'correct': 'c'
                    },
                    {
                        'question': "Jinoyat javobgarligiga tortish qanday yoshdan boshlanadi?",
                        'options': {'a': '14 yosh', 'b': '16 yosh', 'c': '18 yosh', 'd': '21 yosh'},
                        'correct': 'b'
                    },
                    {
                        'question': "Nikoh tuzish uchun minimal yosh nechchi?",
                        'options': {'a': '16 yosh', 'b': '17 yosh', 'c': '18 yosh', 'd': '19 yosh'},
                        'correct': 'c'
                    },
                    {
                        'question': "O'zbekiston Respublikasining davlat tili qaysi?",
                        'options': {'a': 'Rus tili', 'b': "O'zbek tili", 'c': 'Ingliz tili', 'd': 'Arab tili'},
                        'correct': 'b'
                    },
                    {
                        'question': "Konstitutsiyaga o'zgartirishlar kiritish huquqi kimga tegishli?",
                        'options': {'a': 'Prezidentga', 'b': 'Oliy Majlisga', 'c': 'Bosh vazirga', 'd': 'Sudga'},
                        'correct': 'b'
                    }
                ],
                'ru': [
                    {
                        'question': "Когда была принята Конституция Республики Узбекистан?",
                        'options': {'a': '1991 год', 'b': '1992 год', 'c': '1993 год', 'd': '1994 год'},
                        'correct': 'b'
                    },
                    {
                        'question': "В каком документе установлены права граждан?",
                        'options': {'a': 'В Конституции', 'b': 'В Законе', 'c': 'В Указе', 'd': 'В Постановлении'},
                        'correct': 'a'
                    },
                    {
                        'question': "На сколько лет избирается Президент Республики Узбекистан?",
                        'options': {'a': '4 года', 'b': '5 лет', 'c': '6 лет', 'd': '7 лет'},
                        'correct': 'b'
                    },
                    {
                        'question': "Из скольких палат состоит Олий Мажлис Республики Узбекистан?",
                        'options': {'a': '1 палата', 'b': '2 палаты', 'c': '3 палаты', 'd': '4 палаты'},
                        'correct': 'b'
                    },
                    {
                        'question': "С какого момента начинается гражданская правоспособность?",
                        'options': {'a': 'С рождения', 'b': 'С 16 лет', 'c': 'С 18 лет', 'd': 'С 21 года'},
                        'correct': 'a'
                    },
                    {
                        'question': "С какого возраста начинается избирательное право?",
                        'options': {'a': '16 лет', 'b': '17 лет', 'c': '18 лет', 'd': '21 год'},
                        'correct': 'c'
                    },
                    {
                        'question': "С какого возраста начинается уголовная ответственность?",
                        'options': {'a': '14 лет', 'b': '16 лет', 'c': '18 лет', 'd': '21 год'},
                        'correct': 'b'
                    },
                    {
                        'question': "Каков минимальный возраст для заключения брака?",
                        'options': {'a': '16 лет', 'b': '17 лет', 'c': '18 лет', 'd': '19 лет'},
                        'correct': 'c'
                    },
                    {
                        'question': "Какой язык является государственным в Республике Узбекистан?",
                        'options': {'a': 'Русский', 'b': 'Узбекский', 'c': 'Английский', 'd': 'Арабский'},
                        'correct': 'b'
                    },
                    {
                        'question': "Кому принадлежит право внесения изменений в Конституцию?",
                        'options': {'a': 'Президенту', 'b': 'Олий Мажлису', 'c': 'Премьер-министру', 'd': 'Суду'},
                        'correct': 'b'
                    }
                ],
                'en': [
                    {
                        'question': "When was the Constitution of Uzbekistan adopted?",
                        'options': {'a': '1991', 'b': '1992', 'c': '1993', 'd': '1994'},
                        'correct': 'b'
                    },
                    {
                        'question': "In which document are civil rights established?",
                        'options': {'a': 'Constitution', 'b': 'Law', 'c': 'Decree', 'd': 'Resolution'},
                        'correct': 'a'
                    },
                    {
                        'question': "For how many years is the President of Uzbekistan elected?",
                        'options': {'a': '4 years', 'b': '5 years', 'c': '6 years', 'd': '7 years'},
                        'correct': 'b'
                    },
                    {
                        'question': "How many chambers does the Oliy Majlis of Uzbekistan have?",
                        'options': {'a': '1 chamber', 'b': '2 chambers', 'c': '3 chambers', 'd': '4 chambers'},
                        'correct': 'b'
                    },
                    {
                        'question': "When does civil legal capacity begin?",
                        'options': {'a': 'From birth', 'b': 'From 16 years', 'c': 'From 18 years', 'd': 'From 21 years'},
                        'correct': 'a'
                    },
                    {
                        'question': "From what age does voting right begin?",
                        'options': {'a': '16 years', 'b': '17 years', 'c': '18 years', 'd': '21 years'},
                        'correct': 'c'
                    },
                    {
                        'question': "From what age does criminal responsibility begin?",
                        'options': {'a': '14 years', 'b': '16 years', 'c': '18 years', 'd': '21 years'},
                        'correct': 'b'
                    },
                    {
                        'question': "What is the minimum age for marriage?",
                        'options': {'a': '16 years', 'b': '17 years', 'c': '18 years', 'd': '19 years'},
                        'correct': 'c'
                    },
                    {
                        'question': "What is the official language of Uzbekistan?",
                        'options': {'a': 'Russian', 'b': 'Uzbek', 'c': 'English', 'd': 'Arabic'},
                        'correct': 'b'
                    },
                    {
                        'question': "Who has the right to amend the Constitution?",
                        'options': {'a': 'President', 'b': 'Oliy Majlis', 'c': 'Prime Minister', 'd': 'Court'},
                        'correct': 'b'
                    }
                ]
            }
        }
        
        # Insert questions
        for subject, languages in sample_questions.items():
            for lang, questions in languages.items():
                for q in questions:
                    cursor.execute('''
                        INSERT INTO questions 
                        (subject, language, question_text, option_a, option_b, option_c, option_d, correct_answer)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                    ''', (
                        subject, lang, q['question'],
                        q['options']['a'], q['options']['b'], q['options']['c'], q['options']['d'],
                        q['correct']
                    ))
        
        conn.commit()
        conn.close()
        logger.info("Sample questions inserted successfully")
    
    def register_user(self, user_id: int, username: str, first_name: str):
        """Register a new user"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
                INSERT OR IGNORE INTO users (user_id, username, first_name)
                VALUES (?, ?, ?)
            ''', (user_id, username, first_name))
            conn.commit()
        except Exception as e:
            logger.error(f"Error registering user {user_id}: {e}")
        finally:
            conn.close()
    
    def get_user_language(self, user_id: int) -> str:
        """Get user's selected language"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute("SELECT language FROM users WHERE user_id = ?", (user_id,))
            result = cursor.fetchone()
            return result['language'] if result else 'uz'
        except Exception as e:
            logger.error(f"Error getting user language for {user_id}: {e}")
            return 'uz'
        finally:
            conn.close()
    
    def set_user_language(self, user_id: int, language: str):
        """Set user's language preference"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
                UPDATE users SET language = ? WHERE user_id = ?
            ''', (language, user_id))
            conn.commit()
        except Exception as e:
            logger.error(f"Error setting language for user {user_id}: {e}")
        finally:
            conn.close()
    
    def get_random_questions(self, subject: str, language: str, count: int = 10) -> List[Dict]:
        """Get random questions for a subject and language"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
                SELECT * FROM questions 
                WHERE subject = ? AND language = ?
                ORDER BY RANDOM()
                LIMIT ?
            ''', (subject, language, count))
            
            questions = []
            for row in cursor.fetchall():
                questions.append(dict(row))
            
            return questions
        except Exception as e:
            logger.error(f"Error getting random questions: {e}")
            return []
        finally:
            conn.close()
    
    def save_test_result(self, user_id: int, subject: str, correct_answers: int, 
                        total_questions: int, percentage: float, duration: int, 
                        test_answers: List[Dict] = None) -> int:
        """Save test result to database with detailed answers"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            # Save main test result
            cursor.execute('''
                INSERT INTO test_results 
                (user_id, subject, correct_answers, total_questions, percentage, duration)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (user_id, subject, correct_answers, total_questions, percentage, duration))
            
            test_result_id = cursor.lastrowid
            
            # Save detailed answers for analysis
            if test_answers:
                for answer in test_answers:
                    cursor.execute('''
                        INSERT INTO test_answers 
                        (test_result_id, question_text, user_answer, correct_answer, 
                         is_correct, option_a, option_b, option_c, option_d)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                    ''', (
                        test_result_id,
                        answer['question'],
                        answer['user_answer'],
                        answer['correct_answer'],
                        1 if answer['is_correct'] else 0,
                        answer['option_a'],
                        answer['option_b'],
                        answer['option_c'],
                        answer['option_d']
                    ))
            
            conn.commit()
            return test_result_id
        except Exception as e:
            logger.error(f"Error saving test result: {e}")
            return 0
        finally:
            conn.close()
    
    def get_user_results(self, user_id: int, limit: int = 5) -> List[Dict]:
        """Get user's test results"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
                SELECT * FROM test_results 
                WHERE user_id = ?
                ORDER BY test_date DESC
                LIMIT ?
            ''', (user_id, limit))
            
            results = []
            for row in cursor.fetchall():
                results.append(dict(row))
            
            return results
        except Exception as e:
            logger.error(f"Error getting user results: {e}")
            return []
        finally:
            conn.close()
    
    def get_user_statistics(self) -> Dict:
        """Get overall user statistics for admin"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            # Total users
            cursor.execute("SELECT COUNT(*) as total_users FROM users")
            total_users = cursor.fetchone()['total_users']
            
            # Total tests taken
            cursor.execute("SELECT COUNT(*) as total_tests FROM test_results")
            total_tests = cursor.fetchone()['total_tests']
            
            # Average score
            cursor.execute("SELECT AVG(percentage) as avg_score FROM test_results")
            avg_score = cursor.fetchone()['avg_score'] or 0
            
            # Tests by subject
            cursor.execute('''
                SELECT subject, COUNT(*) as count 
                FROM test_results 
                GROUP BY subject
            ''')
            subject_stats = {row['subject']: row['count'] for row in cursor.fetchall()}
            
            return {
                'total_users': total_users,
                'total_tests': total_tests,
                'average_score': round(avg_score, 1),
                'subject_statistics': subject_stats
            }
        except Exception as e:
            logger.error(f"Error getting user statistics: {e}")
            return {}
        finally:
            conn.close()
    
    def add_admin(self, user_id: int) -> bool:
        """Add user as admin"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute("INSERT OR IGNORE INTO admin_users (user_id) VALUES (?)", (user_id,))
            cursor.execute("UPDATE users SET is_admin = 1 WHERE user_id = ?", (user_id,))
            conn.commit()
            return True
        except Exception as e:
            logger.error(f"Error adding admin {user_id}: {e}")
            return False
        finally:
            conn.close()
    
    def is_admin(self, user_id: int) -> bool:
        """Check if user is admin"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute("SELECT is_admin FROM users WHERE user_id = ?", (user_id,))
            result = cursor.fetchone()
            return bool(result['is_admin']) if result else False
        except Exception as e:
            logger.error(f"Error checking admin status for {user_id}: {e}")
            return False
        finally:
            conn.close()
    
    def add_question(self, subject: str, language: str, question_text: str,
                    option_a: str, option_b: str, option_c: str, option_d: str,
                    correct_answer: str, difficulty_level: int = 1) -> bool:
        """Add a new question to database"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
                INSERT INTO questions 
                (subject, language, question_text, option_a, option_b, option_c, option_d, correct_answer, difficulty_level)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (subject, language, question_text, option_a, option_b, option_c, option_d, correct_answer, difficulty_level))
            conn.commit()
            return True
        except Exception as e:
            logger.error(f"Error adding question: {e}")
            return False
        finally:
            conn.close()
    
    def get_questions_count(self, subject: str = "", language: str = "") -> int:
        """Get count of questions by subject and/or language"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            if subject and language:
                cursor.execute("SELECT COUNT(*) as count FROM questions WHERE subject = ? AND language = ?", 
                             (subject, language))
            elif subject:
                cursor.execute("SELECT COUNT(*) as count FROM questions WHERE subject = ?", (subject,))
            elif language:
                cursor.execute("SELECT COUNT(*) as count FROM questions WHERE language = ?", (language,))
            else:
                cursor.execute("SELECT COUNT(*) as count FROM questions")
            
            return cursor.fetchone()['count']
        except Exception as e:
            logger.error(f"Error getting questions count: {e}")
            return 0
        finally:
            conn.close()
