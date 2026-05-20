document.addEventListener('DOMContentLoaded', function() {
    const form = document.getElementById('feedbackForm');

    //валидации email
    function validateEmail(input) {
        const errorElement = document.getElementById('email-error');
        const value = input.value.trim();
        const emailPattern = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;

        if (value === '') {
            errorElement.textContent = 'Контактный email обязателен';
            return false;
        } else if (!emailPattern.test(value)) {
            errorElement.textContent = 'Введите корректный email';
            return false;
        } else {
            errorElement.textContent = '';
            return true;
        }
    }

    //валидации имени
    function validateName(input) {
        const errorElement = document.getElementById('name-error');
        const value = input.value.trim();

        if (value === '') {
            errorElement.textContent = 'Позывной обязателен';
            return false;
        } else if (value.length < 2) {
            errorElement.textContent = 'Имя должно содержать минимум 2 символа';
            return false;
        } else {
            errorElement.textContent = '';
            return true;
        }
    }

    //валидации сообщения
    function validateMessage(input) {
        const errorElement = document.getElementById('message-error');
        const value = input.value.trim();

        if (value === '') {
            errorElement.textContent = 'Наводка обязательна';
            return false;
        } else if (value.length < 10) {
            errorElement.textContent = 'Наводка должна содержать минимум 10 символов';
            return false;
        } else {
            errorElement.textContent = '';
            return true;
        }
    }

    document.getElementById('name').addEventListener('input', function() {
        validateName(this);
    });

    document.getElementById('email').addEventListener('input', function() {
        validateEmail(this);
    });

    document.getElementById('message').addEventListener('input', function() {
        validateMessage(this);
    });

    //показ уведомления
    function showNotification(message, isSuccess) {
        const oldNotification = document.querySelector('.notification');
        if (oldNotification) oldNotification.remove();

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

    form.addEventListener('submit', async function(event) {
        event.preventDefault();

        const isNameValid = validateName(document.getElementById('name'));
        const isEmailValid = validateEmail(document.getElementById('email'));
        const isMessageValid = validateMessage(document.getElementById('message'));

        if (isNameValid && isEmailValid && isMessageValid) {
            const submitBtn = document.getElementById('submit-btn');
            const originalText = submitBtn.textContent;
            submitBtn.textContent = 'Передача в CBI...';
            submitBtn.disabled = true;

            const formData = {
                name: document.getElementById('name').value.trim(),
                email: document.getElementById('email').value.trim(),
                message: document.getElementById('message').value.trim()
            };

            try {
                const response = await fetch('/api/feedback/', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify(formData)
                });

                const result = await response.json();

                if (result.success) {
                    showNotification(result.message, true);
                    form.reset();
                } else {
                    showNotification(result.message, false);
                }
            } catch (error) {
                showNotification('Ошибка соединения с сервером', false);
            } finally {
                submitBtn.textContent = originalText;
                submitBtn.disabled = false;
            }
        } else {
            showNotification('Проверьте поля перед отправкой наводки', false);
        }
    });
});