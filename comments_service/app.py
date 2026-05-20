import sqlite3
from datetime import datetime
from flask import Flask, request, jsonify, render_template_string
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

# === РАБОТА С БАЗОЙ ДАННЫХ ===

def get_db():
    """Подключение к базе данных SQLite"""
    conn = sqlite3.connect('comments.db')
    conn.row_factory = sqlite3.Row  # Чтобы возвращать словари
    return conn

def init_db():
    """Создание таблицы комментариев при первом запуске"""
    conn = get_db()
    conn.execute('''
        CREATE TABLE IF NOT EXISTS comments (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL,
            text TEXT NOT NULL,
            created_at TEXT NOT NULL
        )
    ''')
    conn.commit()
    conn.close()
    print("✅ База данных comments.db инициализирована")

# Инициализируем БД при запуске
init_db()

# === HTML ШАБЛОН ===

HTML_TEMPLATE = '''
<!DOCTYPE html>
<html>
<head>
    <title>📝 Сервис комментариев</title>
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
        h1 { color: #333; border-bottom: 3px solid #4CAF50; padding-bottom: 10px; }
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
            border-color: #4CAF50;
        }
        button {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 12px 25px;
            border: none;
            border-radius: 8px;
            cursor: pointer;
            font-size: 16px;
            transition: all 0.3s ease;
        }
        button:hover { transform: translateY(-2px); box-shadow: 0 5px 15px rgba(102,126,234,0.4); }
        .comment {
            background: white;
            border-bottom: 1px solid #eee;
            padding: 15px;
            margin-bottom: 10px;
            border-radius: 8px;
            box-shadow: 0 1px 3px rgba(0,0,0,0.1);
        }
        .username { font-weight: bold; color: #4CAF50; font-size: 16px; }
        .date { font-size: 11px; color: #999; margin-left: 10px; }
        .text { margin-top: 8px; color: #333; line-height: 1.5; }
        .no-comments { text-align: center; color: #999; padding: 40px; }
    </style>
</head>
<body>
    <h1>⚽ Футбольный портал — Комментарии</h1>
    
    <div class="form-container">
        <h3>✏️ Написать комментарий</h3>
        <input type="text" id="username" placeholder="Ваше имя *">
        <textarea id="text" placeholder="Ваш комментарий *" rows="3"></textarea>
        <button onclick="addComment()">📤 Отправить комментарий</button>
    </div>
    
    <h2>💬 Комментарии пользователей</h2>
    <div id="comments"></div>
    
    <script>
        async function loadComments() {
            try {
                const response = await fetch('/comments');
                const data = await response.json();
                const container = document.getElementById('comments');
                
                if (!data.comments || data.comments.length === 0) {
                    container.innerHTML = '<div class="no-comments">😢 Пока нет комментариев. Будьте первым!</div>';
                    return;
                }
                
                container.innerHTML = data.comments.map(c => `
                    <div class="comment">
                        <div>
                            <span class="username">⚽ ${escapeHtml(c.username)}</span>
                            <span class="date">📅 ${c.created_at || ''}</span>
                        </div>
                        <div class="text">${escapeHtml(c.text)}</div>
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
        
        async function addComment() {
            const username = document.getElementById('username').value.trim();
            const text = document.getElementById('text').value.trim();
            
            if (!username) return alert('❌ Введите ваше имя');
            if (!text) return alert('❌ Введите комментарий');
            
            const now = new Date();
            const created_at = `${now.getDate().toString().padStart(2,'0')}.${(now.getMonth()+1).toString().padStart(2,'0')}.${now.getFullYear()} ${now.getHours().toString().padStart(2,'0')}:${now.getMinutes().toString().padStart(2,'0')}`;
            
            try {
                await fetch('/comments', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({username, text, created_at})
                });
                
                document.getElementById('text').value = '';
                loadComments();
            } catch (error) {
                alert('❌ Ошибка отправки');
            }
        }
        
        // Загружаем комментарии при загрузке страницы
        loadComments();
        
        // Обновляем каждые 5 секунд (для всех пользователей)
        setInterval(loadComments, 5000);
    </script>
</body>
</html>
'''

# === API ЭНДПОИНТЫ ===

@app.route('/')
def index():
    """Главная страница сервиса комментариев"""
    return render_template_string(HTML_TEMPLATE)

@app.route('/comments', methods=['GET'])
def get_comments():
    """Получить все комментарии (в формате JSON)"""
    conn = get_db()
    comments = conn.execute('SELECT * FROM comments ORDER BY id DESC LIMIT 100').fetchall()
    conn.close()
    return jsonify({'comments': [dict(row) for row in comments]})

@app.route('/comments', methods=['POST'])
def add_comment():
    """Добавить новый комментарий"""
    data = request.json
    username = data.get('username', '').strip()
    text = data.get('text', '').strip()
    created_at = data.get('created_at') or datetime.now().strftime('%d.%m.%Y %H:%M')
    
    if not username or not text:
        return jsonify({'success': False, 'message': 'Заполните все поля'}), 400
    
    conn = get_db()
    conn.execute(
        'INSERT INTO comments (username, text, created_at) VALUES (?, ?, ?)',
        (username, text, created_at)
    )
    conn.commit()
    conn.close()
    
    return jsonify({'success': True, 'message': 'Комментарий добавлен'})

if __name__ == '__main__':
    print("🚀 Сервис комментариев запущен на http://0.0.0.0:8001")
    app.run(host='0.0.0.0', port=8001, debug=True)