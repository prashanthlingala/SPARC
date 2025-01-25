import sqlite3
from datetime import datetime
from typing import Dict, List, Optional
import json

class Database:
    def __init__(self, db_path: str = "campaign_craft.db"):
        self.db_path = db_path
        self.init_database()

    def get_connection(self):
        return sqlite3.connect(self.db_path)

    def check_schema_version(self, cursor):
        """Check if database schema needs updating"""
        try:
            cursor.execute("SELECT hashtags FROM generated_content LIMIT 1")
            return True
        except sqlite3.OperationalError:
            return False

    def init_database(self):
        """Initialize database tables"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            # Check if schema needs updating
            try:
                if not self.check_schema_version(cursor):
                    # Drop existing tables if they exist
                    cursor.execute("DROP TABLE IF EXISTS generated_content")
                    cursor.execute("DROP TABLE IF EXISTS analytics")
                    cursor.execute("DROP TABLE IF EXISTS campaigns")
                    cursor.execute("DROP TABLE IF EXISTS personas")
            except:
                pass

            # Create personas table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS personas (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    role TEXT NOT NULL,
                    experience TEXT,
                    technical_proficiency TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')

            # Create campaigns table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS campaigns (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    goal TEXT NOT NULL,
                    status TEXT DEFAULT 'draft',
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')

            # Create generated_content table with new columns
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS generated_content (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    campaign_id INTEGER,
                    persona_id INTEGER,
                    content_type TEXT NOT NULL,
                    tone TEXT NOT NULL,
                    content TEXT NOT NULL,
                    hashtags TEXT,
                    keywords TEXT,
                    twitter_content TEXT,
                    email_subject TEXT,
                    email_body TEXT,
                    tweet_url TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (campaign_id) REFERENCES campaigns (id),
                    FOREIGN KEY (persona_id) REFERENCES personas (id)
                )
            ''')

            # Create analytics table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS analytics (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    campaign_id INTEGER,
                    content_id INTEGER,
                    metric_name TEXT NOT NULL,
                    metric_value REAL NOT NULL,
                    recorded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (campaign_id) REFERENCES campaigns (id),
                    FOREIGN KEY (content_id) REFERENCES generated_content (id)
                )
            ''')

            conn.commit()

    # Persona Management
    def save_persona(self, persona: Dict) -> int:
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO personas (name, role, experience, technical_proficiency)
                VALUES (?, ?, ?, ?)
            ''', (
                persona.get('name'),
                persona.get('role'),
                persona.get('experience'),
                persona.get('technical_proficiency')
            ))
            conn.commit()
            return cursor.lastrowid

    def get_personas(self) -> List[Dict]:
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM personas')
            columns = [description[0] for description in cursor.description]
            return [dict(zip(columns, row)) for row in cursor.fetchall()]

    # Campaign Management
    def save_campaign(self, campaign: Dict) -> int:
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO campaigns (name, goal, status)
                VALUES (?, ?, ?)
            ''', (
                campaign.get('name'),
                campaign.get('goal'),
                campaign.get('status', 'draft')
            ))
            conn.commit()
            return cursor.lastrowid

    def get_campaigns(self) -> List[Dict]:
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM campaigns')
            columns = [description[0] for description in cursor.description]
            return [dict(zip(columns, row)) for row in cursor.fetchall()]

    # Content Management
    def save_generated_content(self, content: Dict) -> int:
        """Save generated content"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO generated_content 
                (campaign_id, persona_id, content_type, tone, content, hashtags, keywords)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (
                content.get('campaign_id'),
                content.get('persona_id'),
                content.get('content_type'),
                content.get('tone'),
                content.get('content'),
                json.dumps(content.get('hashtags', [])),
                json.dumps(content.get('keywords', []))
            ))
            conn.commit()
            return cursor.lastrowid

    def get_campaign_content(self, campaign_id: int) -> List[Dict]:
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT gc.*, p.name as persona_name 
                FROM generated_content gc
                LEFT JOIN personas p ON gc.persona_id = p.id
                WHERE campaign_id = ?
            ''', (campaign_id,))
            columns = [description[0] for description in cursor.description]
            return [dict(zip(columns, row)) for row in cursor.fetchall()]

    # Analytics
    def save_analytics(self, campaign_id: int, metric_name: str, metric_value: float, content_id: Optional[int] = None):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO analytics (campaign_id, content_id, metric_name, metric_value)
                VALUES (?, ?, ?, ?)
            ''', (campaign_id, content_id, metric_name, metric_value))
            conn.commit()

    def get_campaign_analytics(self, campaign_id: int) -> List[Dict]:
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT * FROM analytics 
                WHERE campaign_id = ?
                ORDER BY recorded_at DESC
            ''', (campaign_id,))
            columns = [description[0] for description in cursor.description]
            return [dict(zip(columns, row)) for row in cursor.fetchall()]

    # New method to update content
    def update_content(self, content_id: int, updates: Dict) -> bool:
        """Update content with new values"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            # Build update query dynamically based on provided updates
            set_clause = ", ".join([f"{k} = ?" for k in updates.keys()])
            set_clause += ", updated_at = CURRENT_TIMESTAMP"
            
            query = f'''
                UPDATE generated_content
                SET {set_clause}
                WHERE id = ?
            '''
            
            values = list(updates.values()) + [content_id]
            
            try:
                cursor.execute(query, values)
                conn.commit()
                return True
            except Exception as e:
                print(f"Error updating content: {str(e)}")
                return False 

    def update_persona(self, persona_id: int, updates: Dict) -> bool:
        """Update persona with new values"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            # Build update query dynamically based on provided updates
            set_clause = ", ".join([f"{k} = ?" for k in updates.keys()])
            
            query = f'''
                UPDATE personas
                SET {set_clause}
                WHERE id = ?
            '''
            
            values = list(updates.values()) + [persona_id]
            
            try:
                cursor.execute(query, values)
                conn.commit()
                return True
            except Exception as e:
                print(f"Error updating persona: {str(e)}")
                return False

    def delete_persona(self, persona_id: int) -> bool:
        """Delete persona from database"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            try:
                # First check if persona is referenced in generated_content
                cursor.execute('''
                    SELECT COUNT(*) FROM generated_content
                    WHERE persona_id = ?
                ''', (persona_id,))
                
                if cursor.fetchone()[0] > 0:
                    print("Cannot delete persona: Referenced in generated content")
                    return False
                
                # If not referenced, delete the persona
                cursor.execute('DELETE FROM personas WHERE id = ?', (persona_id,))
                conn.commit()
                return True
            except Exception as e:
                print(f"Error deleting persona: {str(e)}")
                return False 