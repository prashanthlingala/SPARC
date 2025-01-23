import sqlite3
from typing import Dict, List, Optional
import json
from datetime import datetime

class DatabaseManager:
    def __init__(self, db_path: str = "database/campaign_craft.db"):
        self.db_path = db_path
        self.init_db()
    
    def init_db(self):
        """Initialize database tables"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Create personas table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS personas (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    role TEXT NOT NULL,
                    experience TEXT NOT NULL,
                    technical_proficiency TEXT NOT NULL,
                    content_style TEXT NOT NULL,
                    pain_points TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Create content table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS generated_content (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    campaign_goal TEXT NOT NULL,
                    content_type TEXT NOT NULL,
                    tone TEXT NOT NULL,
                    content TEXT NOT NULL,
                    persona_id INTEGER,
                    hashtags TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (persona_id) REFERENCES personas (id)
                )
            """)
            
            conn.commit()
    
    def save_persona(self, persona: Dict) -> int:
        """Save persona to database"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO personas (
                    role, experience, technical_proficiency, 
                    content_style, pain_points
                ) VALUES (?, ?, ?, ?, ?)
            """, (
                persona['role'],
                persona['experience'],
                persona['technical_proficiency'],
                json.dumps(persona['content_style']),
                persona['pain_points']
            ))
            conn.commit()
            return cursor.lastrowid
    
    def get_personas(self) -> List[Dict]:
        """Get all personas from database"""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM personas ORDER BY created_at DESC")
            rows = cursor.fetchall()
            
            return [{
                'id': row['id'],
                'role': row['role'],
                'experience': row['experience'],
                'technical_proficiency': row['technical_proficiency'],
                'content_style': json.loads(row['content_style']),
                'pain_points': row['pain_points'],
                'created_at': row['created_at']
            } for row in rows]
    
    def save_content(self, content_data: Dict) -> int:
        """Save generated content to database"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO generated_content (
                    campaign_goal, content_type, tone, content,
                    persona_id, hashtags
                ) VALUES (?, ?, ?, ?, ?, ?)
            """, (
                content_data['campaign_goal'],
                content_data['content_type'],
                content_data['tone'],
                content_data['content'],
                content_data['persona_id'],
                json.dumps(content_data.get('hashtags', []))
            ))
            conn.commit()
            return cursor.lastrowid
    
    def get_content_history(self) -> List[Dict]:
        """Get content generation history"""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute("""
                SELECT c.*, p.role as persona_role 
                FROM generated_content c
                LEFT JOIN personas p ON c.persona_id = p.id
                ORDER BY c.created_at DESC
            """)
            rows = cursor.fetchall()
            
            return [{
                'id': row['id'],
                'campaign_goal': row['campaign_goal'],
                'content_type': row['content_type'],
                'tone': row['tone'],
                'content': row['content'],
                'persona_role': row['persona_role'],
                'hashtags': json.loads(row['hashtags']),
                'created_at': row['created_at']
            } for row in rows] 