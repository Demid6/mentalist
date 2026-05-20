document.addEventListener('DOMContentLoaded', function() {
    const form = document.getElementById('loginForm');

    function validateUsername(input) {
        const errorElement = document.getElementById('username-error');
        const value = input.value.trim();

        if (!value) {
            errorElement.textContent = 'Введите логин';
            return false;
        }
        if (value.length < 3) {
            errorElement.textContent = 'Логин должен быть минимум 3 символа';
            return false;
        }
        errorElement.textContent = '';
        return true;
    }

    function validatePassword(input) {
        const errorElement = document.getElementById('password-error');
        const value = input.value;

        if (!value) {
            errorElement.textContent = 'Введите пароль';
            return false;
        }
        if (value.length < 6) {
            errorElement.textContent = 'Пароль должен быть минимум 6 символов';
            return false;
        }
        errorElement.textContent = '';
        return true;
    }

    function showNotification(message, isSuccess) {
        const oldNotification = document.querySelector('.notification');
        if (oldNotification) {
            oldNotification.remove();
        }

        const notification = document.createElement('div');
        notification.className = `notification ${isSuccess ? 'success' : 'error'}`;
        notification.innerHTML = `
            <div class="notification-content">
                <span class="notification-message">${message}</span>
            </div>
        `;

        document.body.appendChild(notification);
        setTimeout(() => notification.classList.add('show'), 10);
        setTimeout(() => {
            notification.classList.remove('show');
            setTimeout(() => notification.remove(), 300);
        }, 3000);
    }

    document.getElementById('username').addEventListener('input', function() {
        validateUsername(this);
    });
    document.getElementById('password').addEventListener('input', function() {
        validatePassword(this);
    });

    form.addEventListener('submit', async function(event) {
        event.preventDefault();

        const isUsernameValid = validateUsername(document.getElementById('username'));
        const isPasswordValid = validatePassword(document.getElementById('password'));

        if (!isUsernameValid || !isPasswordValid) {
            showNotification('Проверьте логин и пароль', false);
            return;
        }

        const submitBtn = document.getElementById('submit-btn');
        const originalText = submitBtn.textContent;
        submitBtn.textContent = 'Вход...';
        submitBtn.disabled = true;

        try {
            const response = await fetch('/api/login/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    username: document.getElementById('username').value.trim(),
                    password: document.getElementById('password').value,
                }),
            });

            const result = await response.json();
            if (result.success) {
                showNotification(result.message, true);
                setTimeout(() => {
                    window.location.href = result.redirect_url || '/academy/';
                }, 500);
            } else {
                showNotification(result.message, false);
            }
        } catch (error) {
            showNotification('Ошибка соединения с сервером', false);
        } finally {
            submitBtn.textContent = originalText;
            submitBtn.disabled = false;
        }
    });
});
