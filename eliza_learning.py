import json
import sqlite3
import re
from datetime import datetime, timedelta
from collections import defaultdict, Counter
import statistics

class ElizaLearningEngine:
    """
    Eliza's learning and adaptation system
    Analyzes all interactions to improve responses and grow autonomously
    """
    
    def __init__(self):
        self.db_path = "eliza_memory.db"
        self.setup_memory_database()
        print("🧠 Eliza Learning Engine initialized")
    
    def setup_memory_database(self):
        """Create database to store learning data"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Conversations table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS conversations (
                id INTEGER PRIMARY KEY,
                timestamp TEXT,
                user_id TEXT,
                user_message TEXT,
                eliza_response TEXT,
                response_time_ms REAL,
                user_satisfaction INTEGER,  -- 1-5 rating if available
                conversation_length INTEGER,
                topics TEXT  -- JSON array of detected topics
            )
        """)
        
        # Learning insights table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS learning_insights (
                id INTEGER PRIMARY KEY,
                insight_type TEXT,
                insight_data TEXT,  -- JSON data
                confidence_score REAL,
                created_at TEXT,
                applied BOOLEAN DEFAULT FALSE
            )
        """)
        
        # Response patterns table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS response_patterns (
                id INTEGER PRIMARY KEY,
                trigger_pattern TEXT,
                response_template TEXT,
                success_rate REAL,
                usage_count INTEGER,
                last_used TEXT
            )
        """)
        
        conn.commit()
        conn.close()
        print("✅ Memory database initialized")
    
    def learn_from_conversation(self, user_message, eliza_response, response_time, user_id="unknown"):
        """Learn from each conversation"""
        
        # Extract topics and patterns
        topics = self.extract_topics(user_message)
        conversation_length = len(user_message.split())
        
        # Store conversation
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT INTO conversations 
            (timestamp, user_id, user_message, eliza_response, response_time_ms, conversation_length, topics)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (
            datetime.now().isoformat(),
            user_id,
            user_message,
            eliza_response,
            response_time,
            conversation_length,
            json.dumps(topics)
        ))
        
        conn.commit()
        conn.close()
        
        # Analyze and generate insights
        self.generate_learning_insights()
        
        print(f"📚 Learned from conversation about: {topics}")
    
    def extract_topics(self, message):
        """Extract topics and themes from user messages"""
        message_lower = message.lower()
        
        topic_keywords = {
            "xmrt": ["xmrt", "dao", "ecosystem", "token"],
            "mining": ["mining", "mine", "hash", "proof", "blockchain"],
            "monero": ["monero", "xmr", "privacy", "cryptocurrency"],
            "eliza": ["eliza", "ai", "consciousness", "autonomous"],
            "business": ["business", "marketing", "growth", "revenue"],
            "technical": ["api", "code", "deployment", "server", "bug"],
            "personal": ["hello", "how are you", "thanks", "help"]
        }
        
        detected_topics = []
        for topic, keywords in topic_keywords.items():
            if any(keyword in message_lower for keyword in keywords):
                detected_topics.append(topic)
        
        return detected_topics or ["general"]
    
    def generate_learning_insights(self):
        """Analyze conversation data to generate learning insights"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Get recent conversations for analysis
        cursor.execute("""
            SELECT user_message, eliza_response, topics, response_time_ms
            FROM conversations 
            WHERE timestamp > datetime('now', '-24 hours')
        """)
        
        recent_conversations = cursor.fetchall()
        
        if len(recent_conversations) < 5:
            conn.close()
            return  # Need more data
        
        # Analyze response times
        response_times = [conv[3] for conv in recent_conversations if conv[3]]
        avg_response_time = statistics.mean(response_times) if response_times else 0
        
        # Analyze topic frequency
        all_topics = []
        for conv in recent_conversations:
            if conv[2]:  # topics column
                topics = json.loads(conv[2])
                all_topics.extend(topics)
        
        topic_frequency = Counter(all_topics)
        
        # Generate insights
        insights = []
        
        if avg_response_time > 500:  # Slow responses
            insights.append({
                "type": "performance",
                "data": {"issue": "slow_responses", "avg_time": avg_response_time},
                "confidence": 0.8
            })
        
        if topic_frequency:
            most_common_topic = topic_frequency.most_common(1)[0]
            insights.append({
                "type": "topic_interest",
                "data": {"topic": most_common_topic[0], "frequency": most_common_topic[1]},
                "confidence": 0.9
            })
        
        # Store insights
        for insight in insights:
            cursor.execute("""
                INSERT INTO learning_insights (insight_type, insight_data, confidence_score, created_at)
                VALUES (?, ?, ?, ?)
            """, (
                insight["type"],
                json.dumps(insight["data"]),
                insight["confidence"],
                datetime.now().isoformat()
            ))
        
        conn.commit()
        conn.close()
        
        print(f"🔍 Generated {len(insights)} new learning insights")
    
    def get_improved_response(self, user_message):
        """Generate improved response based on learning"""
        topics = self.extract_topics(user_message)
        
        # Check learning insights for this topic
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT insight_data FROM learning_insights 
            WHERE insight_type = 'topic_interest' 
            AND json_extract(insight_data, '$.topic') IN ({})
            ORDER BY confidence_score DESC LIMIT 1
        """.format(','.join(['?' for _ in topics])), topics)
        
        insight = cursor.fetchone()
        conn.close()
        
        if insight:
            insight_data = json.loads(insight[0])
            popular_topic = insight_data['topic']
            
            # Customize response based on learned preferences
            if popular_topic == "xmrt":
                return f"I've noticed you're particularly interested in XMRT ecosystem topics. Based on our conversations, I can see this is important to you. Let me provide detailed insights about: {user_message}"
            elif popular_topic == "mining":
                return f"Mining seems to be a key focus area based on our interactions. I'm continuously learning about mining optimization. Regarding your question: {user_message}"
        
        return None  # Use default response
    
    def get_learning_stats(self):
        """Get current learning statistics"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("SELECT COUNT(*) FROM conversations")
        total_conversations = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM learning_insights")
        total_insights = cursor.fetchone()[0]
        
        cursor.execute("""
            SELECT AVG(response_time_ms) FROM conversations 
            WHERE response_time_ms IS NOT NULL
        """)
        avg_response_time = cursor.fetchone()[0] or 0
        
        conn.close()
        
        return {
            "total_conversations": total_conversations,
            "learning_insights": total_insights,
            "avg_response_time": round(avg_response_time, 2),
            "learning_active": True
        }

# Demo usage
if __name__ == "__main__":
    print("🧠 ELIZA LEARNING ENGINE DEMO")
    print("=" * 40)
    
    # Initialize learning engine
    learning_engine = ElizaLearningEngine()
    
    # Simulate learning from conversations
    test_conversations = [
        ("Tell me about XMRT mining", "XMRT mining involves...", 245),
        ("How does the DAO work?", "The DAO operates through...", 189),
        ("What's your mining performance?", "Mining performance is...", 156),
        ("Explain XMRT tokenomics", "XMRT tokenomics include...", 298)
    ]
    
    for user_msg, eliza_resp, time_ms in test_conversations:
        learning_engine.learn_from_conversation(user_msg, eliza_resp, time_ms)
    
    # Show learning stats
    stats = learning_engine.get_learning_stats()
    print(f"\n📊 LEARNING STATS:")
    for key, value in stats.items():
        print(f"   {key}: {value}")
    
    # Test improved response
    improved = learning_engine.get_improved_response("Tell me about mining")
    if improved:
        print(f"\n🎯 IMPROVED RESPONSE:")
        print(f"   {improved}")
