// Главный класс приложения
class SlanglitApp {
    constructor() {
        this.currentDirection = 'to_formal';
        this.history = [];
        this.currentPage = 1;
        this.itemsPerPage = 8;
        this.userId = this.getUserId();
        this.apiBaseUrl = '/api';
        this.apiAvailable = false;
        
        this.init();
    }

    getUserId() {
        // 1. Пробуем Telegram Web App (автоматически)
        if (window.Telegram && window.Telegram.WebApp) {
            const tg = window.Telegram.WebApp;
            if (tg.initDataUnsafe && tg.initDataUnsafe.user) {
                const userId = tg.initDataUnsafe.user.id.toString();
                console.log('✅ Используем Telegram user_id:', userId);
                localStorage.setItem('slanglit_user_id', userId);
                localStorage.setItem('slanglit_user_source', 'telegram');
                return userId;
            }
        }
        
        // 2. Пробуем из localStorage (пользователь уже вводил)
        const savedUserId = localStorage.getItem('slanglit_user_id');
        const userSource = localStorage.getItem('slanglit_user_source');
        
        if (savedUserId && userSource === 'telegram') {
            console.log('✅ Используем сохраненный Telegram user_id:', savedUserId);
            return savedUserId;
        }
        
        // 3. Если есть web ID - удаляем его и запрашиваем Telegram ID
        if (savedUserId && savedUserId.startsWith('web_')) {
            console.log('🔄 Удаляем старый web ID и запрашиваем Telegram ID');
            localStorage.removeItem('slanglit_user_id');
            localStorage.removeItem('slanglit_user_source');
            return null;
        }
        
        // 4. Нет ID - будет запрошен у пользователя
        console.log('⚠️ User ID не найден, требуется ввод Telegram ID');
        return null;
    }

    async init() {
        // Telegram Web App интеграция
        if (window.Telegram && window.Telegram.WebApp) {
            this.tg = window.Telegram.WebApp;
            this.tg.ready();
            this.tg.expand();
        }
        
        // Проверяем соединение с API
        await this.checkApiConnection();
        
        // Если нет user_id - показываем экран ввода Telegram ID
        if (!this.userId) {
            this.showUserIdInput();
            return;
        }
        
        this.bindEvents();
        await this.loadHistory();
        this.renderHistory();
    }

    async checkApiConnection() {
    try {
        console.log('🔧 Проверяем подключение к API...');
        console.log('URL:', `${this.apiBaseUrl}/health`);
        
        const response = await fetch(`${this.apiBaseUrl}/health`, {
            method: 'GET',
            headers: {
                'Content-Type': 'application/json',
                'Accept': 'application/json'
            }
        });
        
        console.log('📊 Статус ответа:', response.status);
        console.log('📋 Заголовки:', Object.fromEntries(response.headers.entries()));
        
        // Сначала получим текст чтобы посмотреть что приходит
        const responseText = await response.text();
        console.log('📝 Тело ответа:', responseText);
        
        // Пробуем распарсить как JSON
        let data;
        try {
            data = JSON.parse(responseText);
        } catch (e) {
            console.error('❌ Ответ не JSON:', responseText.substring(0, 100));
            throw new Error('Сервер вернул HTML вместо JSON. Проверь что API запущен.');
        }
        
        if (response.ok && data.database === 'connected') {
            console.log('✅ API сервер доступен:', data);
            this.apiAvailable = true;
            return true;
        } else {
            throw new Error(data.message || 'API не доступен');
        }
    } catch (error) {
        console.error('❌ API сервер не доступен:', error);
        this.showError('Сервер переводов временно недоступен. Пожалуйста, попробуйте позже.');
        this.apiAvailable = false;
        return false;
    }
}

    showError(message) {
        const russianText = document.getElementById('russianText');
        const explanationContent = document.querySelector('.explanation-content');
        
        if (russianText) {
            russianText.textContent = 'Ошибка';
            russianText.style.color = '#ff6b6b';
        }
        if (explanationContent) {
            explanationContent.textContent = message;
        }
        
        setTimeout(() => {
            if (russianText) russianText.style.color = '';
        }, 5000);
    }

    showUserIdInput() {
        // Создаем временный контейнер для ввода ID
        const tempContainer = document.createElement('div');
        tempContainer.id = 'temp-user-id-input';
        tempContainer.innerHTML = `
            <div class="user-id-input-container">
                <div class="header">
                    <div class="app-title">Сленглит</div>
                    <div class="app-subtitle">мини-приложение</div>
                </div>
                
                <div class="translation-card">
                    <div class="card-label">ВВОД TELEGRAM ID</div>
                    <div style="text-align: center; padding: 20px;">
                        <h4>🔐 Требуется Telegram ID</h4>
                        <p>Для сохранения истории переводов введите ваш Telegram ID</p>
                        
                        <div style="background: #2a2f35; padding: 15px; border-radius: 8px; margin: 15px 0; border: 1px solid #44A3B9;">
                            <p><strong>📱 Как получить Telegram ID:</strong></p>
                            <p>1. Откройте <a href="https://t.me/slenglit_bot?start=start" target="_blank" style="color: #44A3B9; font-weight: bold;">бота в Telegram</a></p>
                            <p>2. Скопируйте ваш ID из сообщения бота</p>
                            <p>3. Введите его ниже</p>
                        </div>
                        
                        <input type="text" id="userIdInput" placeholder="Введите ваш Telegram ID (только цифры)" 
                               style="width: 100%; padding: 12px; margin: 10px 0; 
                                      border-radius: 8px; border: 2px solid #44A3B9;
                                      background: #343434; color: white; font-size: 14px;
                                      text-align: center; font-weight: bold;">
                        
                        <div style="display: flex; gap: 10px; margin-top: 15px;">
                            <button onclick="window.app.saveUserId()" 
                                    style="flex: 1; background: #44A3B9; color: white; border: none;
                                           padding: 12px 0; border-radius: 8px; cursor: pointer;
                                           font-size: 14px; font-weight: bold;">
                                ✅ Сохранить ID
                            </button>
                            
                            <button onclick="window.app.continueWithoutId()" 
                                    style="flex: 1; background: transparent; color: #989898; border: 1px solid #989898;
                                           padding: 12px 0; border-radius: 8px; cursor: pointer;
                                           font-size: 12px;">
                                ⚠️ Без истории
                            </button>
                        </div>
                        
                        <div style="margin-top: 15px; padding: 10px; background: #2a2f35; border-radius: 6px; font-size: 11px; color: #989898;">
                            <strong>Важно:</strong> Без Telegram ID переводы будут работать, но история не сохранится
                        </div>
                    </div>
                </div>
            </div>
        `;
        
        // Скрываем основные страницы и показываем временный контейнер
        document.getElementById('main-page').style.display = 'none';
        document.getElementById('history-page').style.display = 'none';
        document.body.appendChild(tempContainer);
        
        // Фокус на поле ввода
        setTimeout(() => {
            const input = document.getElementById('userIdInput');
            if (input) input.focus();
        }, 100);
    }

    saveUserId() {
        const input = document.getElementById('userIdInput');
        const userId = input.value.trim();
        
        if (!userId) {
            alert('❌ Пожалуйста, введите ваш Telegram ID');
            return;
        }
        
        if (!/^\d+$/.test(userId)) {
            alert('❌ Telegram ID должен содержать только цифры\n\nПример: 5159491775');
            return;
        }
        
        if (userId.length < 5) {
            alert('❌ Telegram ID слишком короткий');
            return;
        }
        
        // Сохраняем как Telegram ID
        localStorage.setItem('slanglit_user_id', userId);
        localStorage.setItem('slanglit_user_source', 'telegram');
        this.userId = userId;
        
        console.log('✅ Сохранен Telegram ID:', userId);
        this.continueWithApp();
    }

    continueWithoutId() {
        // Генерируем временный ID только для текущей сессии (не сохраняем в localStorage)
        const tempId = 'temp_' + Date.now();
        this.userId = tempId;
        
        console.log('⚠️ Используем временный ID без сохранения истории:', tempId);
        this.continueWithApp();
    }

    continueWithApp() {
        // Удаляем временный контейнер
        const tempContainer = document.getElementById('temp-user-id-input');
        if (tempContainer) {
            tempContainer.remove();
        }
        
        // Показываем основные страницы
        document.getElementById('main-page').style.display = 'flex';
        document.getElementById('history-page').style.display = 'none';
        
        // Обновляем интерфейс в зависимости от типа ID
        this.updateInterfaceForUserId();
        
        this.bindEvents();
        
        // Загружаем историю только если есть Telegram ID
        if (!this.userId.startsWith('temp_')) {
            this.loadHistory().then(() => this.renderHistory());
        } else {
            this.history = [];
        }
    }

    updateInterfaceForUserId() {
        const explanationContent = document.querySelector('.explanation-content');
        if (explanationContent) {
            if (this.userId.startsWith('temp_')) {
                explanationContent.innerHTML = 'Здесь появится объяснение термина<br><small style="color: #ff6b6b;">⚠️ История не сохраняется</small>';
            } else {
                explanationContent.innerHTML = 'Здесь появится объяснение термина<br><small style="color: #44A3B9;">✅ История сохраняется</small>';
            }
        }
    }

    bindEvents() {
        // Привязываем события к элементам которые точно существуют
        const bigTranslateBtn = document.getElementById('bigTranslateBtn');
        const slangInput = document.getElementById('slangInput');
        const langSwapBtn = document.getElementById('langSwapBtn');
        const translateNavBtn = document.getElementById('translateNavBtn');
        const historyNavBtn = document.getElementById('historyNavBtn');
        const translateNavBtnHistory = document.getElementById('translateNavBtnHistory');
        const historyNavBtnHistory = document.getElementById('historyNavBtnHistory');

        if (bigTranslateBtn) {
            bigTranslateBtn.onclick = () => this.showTranslation();
        }

        if (translateNavBtn) {
            translateNavBtn.onclick = () => this.showMain();
        }

        if (historyNavBtn) {
            historyNavBtn.onclick = () => this.showHistory();
        }

        if (translateNavBtnHistory) {
            translateNavBtnHistory.onclick = () => this.showMain();
        }

        if (historyNavBtnHistory) {
            historyNavBtnHistory.onclick = () => {}; // Уже в истории
        }

        if (langSwapBtn) {
            langSwapBtn.onclick = () => this.switchLanguage();
        }

        if (slangInput) {
            slangInput.onkeypress = (e) => {
                if (e.key === 'Enter') {
                    e.preventDefault();
                    this.showTranslation();
                }
            };
        }
    }

    async showTranslation() {
        const inputText = document.getElementById('slangInput').value.trim();
        const russianText = document.getElementById('russianText');
        const explanationContent = document.querySelector('.explanation-content');
        
        if (!inputText) {
            russianText.textContent = 'Введите текст для перевода';
            explanationContent.textContent = 'Начните вводить текст для перевода';
            return;
        }

        russianText.textContent = 'Переводим...';
        explanationContent.textContent = 'Обрабатываем запрос...';

        try {
            if (!this.apiAvailable) {
                throw new Error('API недоступен');
            }

            const response = await this.translateViaApi(inputText);
            
            russianText.textContent = response.translated_text;
            
            // Показываем информацию о сохранении истории
            if (this.userId.startsWith('temp_')) {
                explanationContent.textContent = response.explanation + '\n\n⚠️ Перевод не сохранен в историю';
            } else {
                explanationContent.textContent = response.explanation;
                await this.loadHistory();
            }
            
        } catch (error) {
            console.error('❌ Ошибка перевода:', error);
            this.showError('Не удалось выполнить перевод: ' + error.message);
        }
    }

    async translateViaApi(text) {
        // Для временных ID используем специальный маркер
        const userIdToSend = this.userId.startsWith('temp_') ? 'unknown_user' : this.userId;
        
        console.log('🔧 Отправляем запрос на перевод:', { text, direction: this.currentDirection, userId: userIdToSend });
        
        const response = await fetch(`${this.apiBaseUrl}/translate`, {
            method: 'POST',
            mode: 'cors',
            headers: {
                'Content-Type': 'application/json',
                'Accept': 'application/json'
            },
            body: JSON.stringify({
                text: text,
                direction: this.currentDirection,
                user_id: userIdToSend
            })
        });

        if (!response.ok) {
            const errorText = await response.text();
            console.error('❌ Ошибка API перевода:', response.status, errorText);
            throw new Error(`Ошибка перевода: ${response.status}`);
        }

        const data = await response.json();
        console.log('✅ Перевод получен:', data);
        return data;
    }

    switchLanguage() {
        const slangInput = document.getElementById('slangInput');
        const russianText = document.getElementById('russianText');
        const explanationContent = document.querySelector('.explanation-content');
        
        const leftLangText = document.getElementById('leftLangText');
        const rightLangText = document.getElementById('rightLangText');
        const leftCardLabel = document.getElementById('leftCardLabel');
        const rightCardLabel = document.getElementById('rightCardLabel');
        
        if (this.currentDirection === 'to_formal') {
            this.currentDirection = 'to_informal';
            leftLangText.textContent = 'русский';
            rightLangText.textContent = 'сленговый';
            leftCardLabel.textContent = 'РУССКИЙ';
            rightCardLabel.textContent = 'СЛЕНГ';
            slangInput.placeholder = 'Введите русское выражение...';
        } else {
            this.currentDirection = 'to_formal';
            leftLangText.textContent = 'сленговый';
            rightLangText.textContent = 'русский';
            leftCardLabel.textContent = 'СЛЕНГ';
            rightCardLabel.textContent = 'РУССКИЙ';
            slangInput.placeholder = 'Введите сленговое выражение...';
        }
        
        slangInput.value = '';
        russianText.textContent = 'Результат перевода...';
        
        if (this.userId.startsWith('temp_')) {
            explanationContent.innerHTML = 'Здесь появится объяснение термина<br><small style="color: #ff6b6b;">⚠️ История не сохраняется</small>';
        } else {
            explanationContent.innerHTML = 'Здесь появится объяснение термина<br><small style="color: #44A3B9;">✅ История сохраняется</small>';
        }
    }

    async showHistory() {
        document.getElementById('main-page').classList.remove('active');
        document.getElementById('history-page').classList.add('active');
        
        document.getElementById('translateNavBtn').classList.remove('active');
        document.getElementById('historyNavBtn').classList.add('active');
        document.getElementById('translateNavBtnHistory').classList.remove('active');
        document.getElementById('historyNavBtnHistory').classList.add('active');
        
        await this.loadHistory();
        this.renderHistory();
    }

    showMain() {
        document.getElementById('history-page').classList.remove('active');
        document.getElementById('main-page').classList.add('active');
        
        document.getElementById('translateNavBtn').classList.add('active');
        document.getElementById('historyNavBtn').classList.remove('active');
        document.getElementById('translateNavBtnHistory').classList.add('active');
        document.getElementById('historyNavBtnHistory').classList.remove('active');
    }

    async loadHistory() {
        // Для временных ID не загружаем историю
        if (this.userId.startsWith('temp_')) {
            this.history = [];
            return;
        }

        if (!this.userId || !this.apiAvailable) {
            this.history = [];
            return;
        }

        try {
            console.log('🔧 Загружаем историю для пользователя:', this.userId);
            
            const response = await fetch(`${this.apiBaseUrl}/history/${this.userId}?limit=100`, {
                method: 'GET',
                mode: 'cors',
                headers: {
                    'Accept': 'application/json'
                }
            });
            
            if (!response.ok) {
                throw new Error(`HTTP ${response.status}: Ошибка загрузки истории`);
            }
            
            const data = await response.json();
            console.log('✅ История загружена:', data);
            
            if (data.success) {
                this.history = data.translations.map(trans => ({
                    original: trans.direction === 'to_formal' ? trans.informal_text : trans.formal_text,
                    translation: trans.direction === 'to_formal' ? trans.formal_text : trans.informal_text,
                    explanation: trans.explanation,
                    created_at: trans.created_at
                }));
            }
        } catch (error) {
            console.error('❌ Ошибка загрузки истории:', error);
            this.history = [];
        }
    }

    renderHistory() {
        const historyItems = document.getElementById('historyItems');
        const pagination = document.getElementById('pagination');
        
        if (!historyItems) return;
        
        historyItems.innerHTML = '';
        pagination.innerHTML = '';
        
        if (this.history.length === 0) {
            let message = 'История переводов пуста';
            if (this.userId.startsWith('temp_')) {
                message = '📝 История недоступна<br><small>Введите Telegram ID для сохранения переводов</small>';
            } else if (!this.apiAvailable) {
                message = '❌ Не удалось загрузить историю';
            }
            
            historyItems.innerHTML = `
                <div class="history-item" style="text-align: center; color: var(--text-secondary); padding: 30px;">
                    ${message}
                </div>
            `;
            return;
        }
        
        const startIndex = (this.currentPage - 1) * this.itemsPerPage;
        const endIndex = startIndex + this.itemsPerPage;
        const currentItems = this.history.slice(startIndex, endIndex);
        
        currentItems.forEach((item) => {
            const historyItem = document.createElement('div');
            historyItem.className = 'history-item';
            historyItem.innerHTML = `
                <div class="history-pair">
                    <div class="history-original">${this.escapeHtml(item.original)}</div>
                    <div class="history-translation">${this.escapeHtml(item.translation)}</div>
                </div>
                <div class="history-explanation">${this.escapeHtml(item.explanation)}</div>
            `;
            
            historyItem.addEventListener('click', () => {
                this.loadHistoryItem(item);
            });
            
            historyItems.appendChild(historyItem);
        });
        
        const totalPages = Math.ceil(this.history.length / this.itemsPerPage);
        
        if (totalPages > 1) {
            pagination.classList.remove('hidden');
            for (let i = 1; i <= totalPages; i++) {
                const pageBtn = document.createElement('button');
                pageBtn.className = `page-btn ${i === this.currentPage ? 'active' : ''}`;
                pageBtn.textContent = i;
                pageBtn.addEventListener('click', () => {
                    this.currentPage = i;
                    this.renderHistory();
                });
                pagination.appendChild(pageBtn);
            }
        } else {
            pagination.classList.add('hidden');
        }
    }

    loadHistoryItem(item) {
        if (this.currentDirection === 'to_formal') {
            document.getElementById('slangInput').value = item.original;
        } else {
            document.getElementById('slangInput').value = item.translation;
        }
        
        this.showTranslation();
        this.showMain();
    }

    escapeHtml(text) {
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }
}

// Глобальные функции
function copyText(elementId) {
    const text = document.getElementById(elementId).textContent;
    navigator.clipboard.writeText(text).then(() => {
        console.log('Текст скопирован: ' + text);
    }).catch(err => {
        console.error('Ошибка копирования: ', err);
    });
}

function pasteText(elementId) {
    const input = document.getElementById(elementId);
    navigator.clipboard.readText().then(text => {
        input.value = text;
        const event = new Event('input', { bubbles: true });
        input.dispatchEvent(event);
    }).catch(err => {
        console.error('Ошибка вставки: ', err);
    });
}

// Инициализация приложения
document.addEventListener('DOMContentLoaded', () => {
    console.log('🚀 Инициализация SlanglitApp...');
    window.app = new SlanglitApp();
});