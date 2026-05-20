document.addEventListener('DOMContentLoaded', function() {
    const form = document.getElementById('registrationForm');

    // Валидация имени
    function validateNameField(input, errorElementId) {
        const errorElement = document.getElementById(errorElementId);
        const value = input.value.trim();
        const pattern = /^[А-ЯA-Z][а-яa-z]+$/;

        if (value === '') {
            errorElement.textContent = 'Поле обязательно для заполнения';
            return false;
        } else if (!pattern.test(value)) {
            errorElement.textContent = 'Должно начинаться с заглавной буквы, затем только строчные буквы';
            return false;
        } else {
            errorElement.textContent = '';
            return true;
        }
    }

    // Валидация логина
    function validateUsername(input) {
        const errorElement = document.getElementById('username-error');
        const value = input.value.trim();

        if (value === '') {
            errorElement.textContent = 'Позывной обязателен';
            return false;
        } else if (value.length < 3) {
            errorElement.textContent = 'Логин должен быть минимум 3 символа';
            return false;
        } else if (value.length > 20) {
            errorElement.textContent = 'Логин должен быть максимум 20 символов';
            return false;
        } else {
            errorElement.textContent = '';
            return true;
        }
    }

    // Валидация пароля
    function validatePassword(input) {
        const errorElement = document.getElementById('password-error');
        const value = input.value;

        if (value === '') {
            errorElement.textContent = 'Пароль обязателен';
            return false;
        } else if (value.length < 6) {
            errorElement.textContent = 'Пароль должен быть минимум 6 символов';
            return false;
        } else {
            errorElement.textContent = '';
            return true;
        }
    }

    // Проверка совпадения паролей
    function validatePasswordMatch() {
        const password = document.getElementById('password').value;
        const confirmPassword = document.getElementById('confirm-password').value;
        const errorElement = document.getElementById('confirm-password-error');

        if (password !== confirmPassword) {
            errorElement.textContent = 'Пароли не совпадают';
            return false;
        } else {
            errorElement.textContent = '';
            return true;
        }
    }

    // Валидация email
    function validateEmail(input) {
        const errorElement = document.getElementById('email-error');
        const value = input.value.trim();
        const emailPattern = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;

        if (value !== '' && !emailPattern.test(value)) {
            errorElement.textContent = 'Введите корректный email';
            return false;
        } else {
            errorElement.textContent = '';
            return true;
        }
    }

    // Валидация телефона
    function validatePhone(input) {
        const errorElement = document.getElementById('phone-error');
        const value = input.value.trim();
        const phonePattern = /^\+7-[0-9]{3}-[0-9]{3}-[0-9]{2}-[0-9]{2}$/;

        if (value !== '' && !phonePattern.test(value)) {
            errorElement.textContent = 'Формат: +7-999-999-99-99';
            return false;
        } else {
            errorElement.textContent = '';
            return true;
        }
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

        setTimeout(() => {
            notification.classList.add('show');
        }, 10);

        setTimeout(() => {
            notification.classList.remove('show');
            setTimeout(() => {
                notification.remove();
            }, 300);
        }, 3000);
    }

    document.getElementById('firstname').addEventListener('input', function() {
        validateNameField(this, 'firstname-error');
    });

    document.getElementById('lastname').addEventListener('input', function() {
        validateNameField(this, 'lastname-error');
    });

    document.getElementById('username').addEventListener('input', function() {
        validateUsername(this);
    });

    document.getElementById('password').addEventListener('input', function() {
        validatePassword(this);
        validatePasswordMatch();
    });

    document.getElementById('confirm-password').addEventListener('input', function() {
        validatePasswordMatch();
    });

    document.getElementById('email').addEventListener('input', function() {
        validateEmail(this);
    });

    document.getElementById('phone').addEventListener('input', function() {
        validatePhone(this);
    });

    form.addEventListener('submit', async function(event) {
        event.preventDefault();
        const isFirstnameValid = validateNameField(document.getElementById('firstname'), 'firstname-error');
        const isLastnameValid = validateNameField(document.getElementById('lastname'), 'lastname-error');
        const isUsernameValid = validateUsername(document.getElementById('username'));
        const isPasswordValid = validatePassword(document.getElementById('password'));
        const isPasswordMatch = validatePasswordMatch();
        const isEmailValid = validateEmail(document.getElementById('email'));
        const isPhoneValid = validatePhone(document.getElementById('phone'));

        if (isFirstnameValid && isLastnameValid && isUsernameValid && isPasswordValid &&
            isPasswordMatch && isEmailValid && isPhoneValid) {

            const submitBtn = document.getElementById('submit-btn');
            const originalText = submitBtn.textContent;
            submitBtn.textContent = 'Проверка доступа...';
            submitBtn.disabled = true;

            const formData = {
                username: document.getElementById('username').value.trim(),
                password: document.getElementById('password').value,
                firstname: document.getElementById('firstname').value.trim(),
                lastname: document.getElementById('lastname').value.trim(),
                email: document.getElementById('email').value.trim(),
                phone: document.getElementById('phone').value.trim()
            };

            try {
                const response = await fetch('/api/register/', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify(formData)
                });

                const result = await response.json();

                if (result.success) {
                    showNotification(result.message, true);
                    form.reset();
                    setTimeout(() => {
                        window.location.href = result.redirect_url || '/academy/';
                    }, 600);
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
            showNotification('Исправьте ошибки в анкете агента', false);
        }
    });
});