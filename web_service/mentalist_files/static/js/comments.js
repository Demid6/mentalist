document.addEventListener('DOMContentLoaded', function () {
    const commentsList = document.getElementById('comments-list');
    const usernameInput = document.getElementById('comment-username');
    const textInput     = document.getElementById('comment-text');
    const submitBtn     = document.getElementById('submit-comment');

    let knownIds = new Set();

    // ── Загрузка и рендер ────────────────────────────────────────────────────

    async function loadComments() {
        try {
            const res  = await fetch('/api/comments/');
            const data = await res.json();
            if (data.success) renderComments(data.comments);
        } catch (e) {
            console.error('Ошибка загрузки:', e);
        }
    }

    function renderComments(comments) {
        if (!comments.length) {
            commentsList.innerHTML =
                '<div class="no-comments">Пока нет версий по делу. Добавьте первую гипотезу.</div>';
            knownIds.clear();
            return;
        }

        const noMsg = commentsList.querySelector('.no-comments');
        if (noMsg) { commentsList.innerHTML = ''; knownIds.clear(); }

        comments.forEach(function (c) {
            if (knownIds.has(c.id)) return;
            knownIds.add(c.id);

            const div = document.createElement('div');
            div.className = 'comment-item new';
            div.dataset.id = c.id;
            div.innerHTML =
                '<div class="comment-header">' +
                    '<span class="comment-username">' + esc(c.username) + '</span>' +
                    '<span class="comment-date">'     + esc(c.created_at) + '</span>' +
                '</div>' +
                '<div class="comment-text">' + esc(c.text) + '</div>';

            commentsList.insertBefore(div, commentsList.firstChild);
        });
    }

    // ── Отправка ─────────────────────────────────────────────────────────────

    async function addComment() {
        const username = usernameInput.value.trim();
        const text     = textInput.value.trim();

        if (!username) { showNote('Укажите позывной', false); return; }
        if (!text)     { showNote('Опишите гипотезу по делу', false); return; }

        submitBtn.disabled    = true;
        submitBtn.textContent = 'Передача...';

        try {
            const res  = await fetch('/api/comments/add/', {
                method:  'POST',
                headers: { 'Content-Type': 'application/json' },
                body:    JSON.stringify({ username, text }),
            });
            const data = await res.json();

            if (data.success) {
                textInput.value = '';
                showNote('Версия добавлена в архив CBI', true);
                loadComments();
            } else {
                showNote(data.message || 'Ошибка', false);
            }
        } catch (e) {
            showNote('Ошибка соединения', false);
        } finally {
            submitBtn.disabled    = false;
            submitBtn.textContent = 'Передать в архив';
        }
    }

    submitBtn.addEventListener('click', addComment);
    textInput.addEventListener('keydown', function (e) {
        if (e.key === 'Enter' && !e.shiftKey) { e.preventDefault(); addComment(); }
    });

    // ── Polling каждые 3 секунды (как в референсном проекте) ─────────────────
    loadComments();
    setInterval(loadComments, 3000);

    // ── Утилиты ──────────────────────────────────────────────────────────────

    function esc(str) {
        const d = document.createElement('div');
        d.textContent = str;
        return d.innerHTML;
    }

    function showNote(msg, ok) {
        const old = document.querySelector('.notification');
        if (old) old.remove();
        const n = document.createElement('div');
        n.className = 'notification ' + (ok ? 'success' : 'error');
        n.innerHTML = '<div class="notification-content"><span>' + esc(msg) + '</span></div>';
        document.body.appendChild(n);
        setTimeout(() => n.classList.add('show'), 10);
        setTimeout(() => { n.classList.remove('show'); setTimeout(() => n.remove(), 300); }, 3500);
    }
});
