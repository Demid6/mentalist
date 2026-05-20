import os
import sqlite3
from datetime import datetime
import requests
from flask import Flask, request, jsonify, render_template_string
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

TELEGRAM_BOT_TOKEN = os.environ.get('TELEGRAM_BOT_TOKEN', '')
TELEGRAM_CHAT_ID = os.environ.get('TELEGRAM_CHAT_ID', '')


def send_to_telegram(name, email, message):
    if not TELEGRAM_BOT_TOKEN or not TELEGRAM_CHAT_ID:
        return False
    text = (
        f"\U0001F4EC <b>Новое сообщение</b>\n\n"
        f"<b>Имя:</b> {name}\n"
        f"<b>Email:</b> {email}\n\n"
        f"<b>Сообщение:</b>\n{message}"
    )
    try:
        resp = requests.post(
            f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage",
            json={'chat_id': TELEGRAM_CHAT_ID, 'text': text, 'parse_mode': 'HTML'},
            timeout=5,
        )
        return resp.ok
    except requests.RequestException as e:
        print(f"⚠️  Telegram error: {e}")
        return False

# === РАБОТА С БАЗОЙ ДАННЫХ ===

def get_db():
    """Подключение к базе данных SQLite"""
    conn = sqlite3.connect('notifications.db')
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    """Создание таблицы уведомлений при первом запуске"""
    conn = get_db()
    conn.execute('''
        CREATE TABLE IF NOT EXISTS notifications (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT NOT NULL,
            message TEXT NOT NULL,
            sent_to_telegram INTEGER DEFAULT 0,
            created_at TEXT NOT NULL
        )
    ''')
    conn.commit()
    conn.close()
    print("✅ База данных notifications.db инициализирована")

init_db()

# === HTML ШАБЛОН ===

HTML_TEMPLATE = '''
<!DOCTYPE html>
<html>
<head>
    <title>📬 Сервис уведомлений</title>
    <meta charset="UTF-8">
    <style>
        * { box-sizing: border-box; }
        body {
            font-family: 'Segoe UI', Arial, sans-serif;
            max-width: 800px;
            margin: 50px auto;
            padding: 20px;
            background: #f5f5f5;
        }
        h1 { color: #333; border-bottom: 3px solid #2196F3; padding-bottom: 10px; }
        .form-container {
            background: white;
            padding: 20px;
            border-radius: 10px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
            margin-bottom: 30px;
        }
        input, textarea {
            width: 100%;
            padding: 12px;
            margin: 10px 0;
            border: 2px solid #ddd;
            border-radius: 8px;
            font-size: 14px;
            font-family: inherit;
        }
        input:focus, textarea:focus {
            outline: none;
            border-color: #2196F3;
        }
        button {
            background: linear-gradient(135deg, #2196F3 0%, #1976D2 100%);
            color: white;
            padding: 12px 25px;
            border: none;
            border-radius: 8px;
            cursor: pointer;
            font-size: 16px;
            transition: all 0.3s ease;
        }
        button:hover { transform: translateY(-2px); box-shadow: 0 5px 15px rgba(33,150,243,0.4); }
        .notification-item {
            background: white;
            border-left: 4px solid #2196F3;
            padding: 15px;
            margin-bottom: 10px;
            border-radius: 8px;
            box-shadow: 0 1px 3px rgba(0,0,0,0.1);
        }
        .name { font-weight: bold; color: #2196F3; font-size: 16px; }
        .email { color: #666; font-size: 13px; margin-left: 10px; }
        .date { font-size: 11px; color: #999; display: block; margin-top: 5px; }
        .message { margin-top: 10px; color: #333; background: #f9f9f9; padding: 10px; border-radius: 5px; }
        .status { font-size: 11px; color: #4CAF50; margin-left: 10px; }
        .no-notifications { text-align: center; color: #999; padding: 40px; }
    </style>
</head>
<body>
    <h1>📬 Футбольный портал — Обратная связь</h1>
    
    <div class="form-container">
        <h3>✉️ Отправить сообщение</h3>
        <input type="text" id="name" placeholder="Ваше имя *">
        <input type="email" id="email" placeholder="Email *">
        <textarea id="message" placeholder="Ваше сообщение *" rows="3"></textarea>
        <button onclick="sendMessage()">📨 Отправить сообщение</button>
    </div>
    
    <h2>📋 История сообщений</h2>
    <div id="notifications"></div>
    
    <script>
        async function loadNotifications() {
            try {
                const response = await fetch('/notifications');
                const data = await response.json();
                const container = document.getElementById('notifications');
                
                if (!data.notifications || data.notifications.length === 0) {
                    container.innerHTML = '<div class="no-notifications">📭 Нет отправленных сообщений</div>';
                    return;
                }
                
                container.innerHTML = data.notifications.map(n => `
                    <div class="notification-item">
                        <div>
                            <span class="name">👤 ${escapeHtml(n.name)}</span>
                            <span class="email">📧 ${escapeHtml(n.email)}</span>
                            <span class="status">${n.sent_to_telegram ? '✅ Отправлено' : '⏳ В очереди'}</span>
                        </div>
                        <div class="message">💬 ${escapeHtml(n.message)}</div>
                        <div class="date">📅 ${n.created_at}</div>
                    </div>
                `).join('');
            } catch (error) {
                console.error('Ошибка загрузки:', error);
            }
        }
        
        function escapeHtml(text) {
            const div = document.createElement('div');
            div.textContent = text;
            return div.innerHTML;
        }
        
        async function sendMessage() {
            const name = document.getElementById('name').value.trim();
            const email = document.getElementById('email').value.trim();
            const message = document.getElementById('message').value.trim();
            
            if (!name) return alert('❌ Введите ваше имя');
            if (!email) return alert('❌ Введите email');
            if (!message) return alert('❌ Введите сообщение');
            
            const now = new Date();
            const created_at = `${now.getDate().toString().padStart(2,'0')}.${(now.getMonth()+1).toString().padStart(2,'0')}.${now.getFullYear()} ${now.getHours().toString().padStart(2,'0')}:${now.getMinutes().toString().padStart(2,'0')}`;
            
            try {
                const response = await fetch('/notifications', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({name, email, message, created_at})
                });
                
                const result = await response.json();
                
                if (result.success) {
                    alert('✅ Сообщение отправлено!');
                    document.getElementById('name').value = '';
                    document.getElementById('email').value = '';
                    document.getElementById('message').value = '';
                    loadNotifications();
                } else {
                    alert('❌ Ошибка: ' + result.message);
                }
            } catch (error) {
                alert('❌ Ошибка отправки');
            }
        }
        
        loadNotifications();
        setInterval(loadNotifications, 5000);
    </script>
</body>
</html>
'''

# === API ЭНДПОИНТЫ ===

@app.route('/')
def index():
    """Главная страница сервиса уведомлений"""
    return render_template_string(HTML_TEMPLATE)

@app.route('/notifications', methods=['GET'])
def get_notifications():
    """Получить все уведомления (в формате JSON)"""
    conn = get_db()
    notifications = conn.execute('SELECT * FROM notifications ORDER BY id DESC LIMIT 50').fetchall()
    conn.close()
    return jsonify({'notifications': [dict(row) for row in notifications]})

@app.route('/notifications', methods=['POST'])
def add_notification():
    """Добавить новое уведомление"""
    data = request.json
    name = data.get('name', '').strip()
    email = data.get('email', '').strip()
    message = data.get('message', '').strip()
    created_at = data.get('created_at') or datetime.now().strftime('%d.%m.%Y %H:%M')
    
    if not name or not email or not message:
        return jsonify({'success': False, 'message': 'Заполните все поля'}), 400
    
    sent = send_to_telegram(name, email, message)

    conn = get_db()
    conn.execute(
        'INSERT INTO notifications (name, email, message, sent_to_telegram, created_at) VALUES (?, ?, ?, ?, ?)',
        (name, email, message, 1 if sent else 0, created_at)
    )
    conn.commit()
    conn.close()

    status = "✅ отправлено в Telegram" if sent else "⚠️  Telegram недоступен"
    print(f"📬 Новое сообщение от {name} ({email}): {message[:50]}... — {status}")

    return jsonify({'success': True, 'message': 'Сообщение сохранено', 'telegram_sent': sent})

if __name__ == '__main__':
    print("🚀 Сервис уведомлений запущен на http://0.0.0.0:8002")
    app.run(host='0.0.0.0', port=8002, debug=True)