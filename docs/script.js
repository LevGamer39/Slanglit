// Главный класс приложения
class SlanglitApp {
    constructor() {
        this.currentDirection = 'slang_to_russian';
        this.history = [];
        this.currentPage = 1;
        this.itemsPerPage = 8;
        
        // Словарь для перевода
        this.dictionary = {
            'краш': { translation: 'симпатия', explanation: 'Человек, который вам нравится' },
            'кринж': { translation: 'стыдно', explanation: 'Чувство неловкости за чьи-то действия' },
            'рофл': { translation: 'шутка', explanation: 'Что-то смешное, веселье' },
            'го': { translation: 'пойдем', explanation: 'Призыв к действию, предложение начать' },
            'афк': { translation: 'отошел', explanation: 'Временно отсутствует у компьютера' },
            'имба': { translation: 'очень круто', explanation: 'Что-то выдающееся, превосходное' },
            'чилить': { translation: 'расслабляться', explanation: 'Проводить время бездельничая' },
            'хейтить': { translation: 'ненавидеть', explanation: 'Проявлять негативное отношение' },
            'скипнуть': { translation: 'пропустить', explanation: 'Не обращать внимания, пролистать' },
            'залипать': { translation: 'увлекаться', explanation: 'Сильно погружаться в процесс' },
            'шазамить': { translation: 'узнавать песню', explanation: 'Использовать приложение для распознавания музыки' },
            'красавчик': { translation: 'молодец', explanation: 'Выражение одобрения' },
            'лайтовый': { translation: 'очень лёгкий, простой', explanation: 'Лайтовый (от англ.: light - "лёгкий")\nЧасто употребляется в отношении какой-либо очень простой задачи, быстровыполнимой' },
            'хейтер': { translation: 'недоброжелатель', explanation: 'Человек, который постоянно критикует и осуждает' },
            'флекс': { translation: 'хвастовство', explanation: 'Демонстрация своих достижений или богатства' },
            'рил': { translation: 'реально', explanation: 'По-настоящему, действительно' },
            'пруф': { translation: 'доказательство', explanation: 'Подтверждение, свидетельство' },
            'сасный': { translation: 'привлекательный', explanation: 'Симпатичный, стильный' }
        };
        
        this.init();
    }

    init() {
        // Telegram Web App интеграция
        if (window.Telegram && window.Telegram.WebApp) {
            this.tg = window.Telegram.WebApp;
            this.tg.ready();
            this.tg.expand();
        }
        
        this.loadHistory();
        this.bindEvents();
        this.renderHistory();
    }

    bindEvents() {
        // Большая кнопка перевода
        document.getElementById('bigTranslateBtn').addEventListener('click', () => {
            this.showTranslation();
        });

        // Кнопки навигации на главной
        document.getElementById('translateNavBtn').addEventListener('click', () => {
            this.showMain();
        });

        document.getElementById('historyNavBtn').addEventListener('click', () => {
            this.showHistory();
        });

        // Кнопки навигации на истории
        document.getElementById('translateNavBtnHistory').addEventListener('click', () => {
            this.showMain();
        });

        document.getElementById('historyNavBtnHistory').addEventListener('click', () => {
            // Уже в истории, ничего не делаем
        });

        // Кнопка смены языка
        document.getElementById('langSwapBtn').addEventListener('click', () => {
            this.switchLanguage();
        });

        // Обработчик ввода текста - автоперевод при вводе
        document.getElementById('slangInput').addEventListener('input', (e) => {
            this.handleInputChange(e.target.value);
        });

        // Обработчик Enter для текстового поля
        document.getElementById('slangInput').addEventListener('keypress', (e) => {
            if (e.key === 'Enter') {
                e.preventDefault();
                this.showTranslation();
            }
        });
    }

    handleInputChange(text) {
        // Автоматический перевод при вводе (можно отключить если мешает)
        if (text.length > 2) {
            // this.showTranslation(); // Раскомментировать для автоперевода
        }
    }

    showTranslation() {
        const inputText = document.getElementById('slangInput').value.trim();
        if (!inputText) {
            document.getElementById('russianText').textContent = 'Введите текст для перевода';
            document.querySelector('.explanation-content').textContent = 'Начните вводить сленговое выражение или русское слово';
            return;
        }

        let translation = '';
        let explanation = '';

        if (this.currentDirection === 'slang_to_russian') {
            // Перевод сленга на русский
            const normalizedInput = inputText.toLowerCase();
            if (this.dictionary[normalizedInput]) {
                translation = this.dictionary[normalizedInput].translation;
                explanation = this.dictionary[normalizedInput].explanation;
            } else {
                translation = 'Перевод не найден';
                explanation = 'Попробуйте другое выражение или проверьте правильность написания';
            }
        } else {
            // Перевод русского на сленг
            const normalizedInput = inputText.toLowerCase();
            let found = false;
            
            for (const [slang, data] of Object.entries(this.dictionary)) {
                if (data.translation.toLowerCase().includes(normalizedInput) || 
                    normalizedInput.includes(data.translation.toLowerCase())) {
                    translation = slang;
                    explanation = data.explanation;
                    found = true;
                    break;
                }
            }
            
            if (!found) {
                translation = 'Сленговый аналог не найден';
                explanation = 'Попробуйте другое слово или переключите направление перевода';
            }
        }

        // Обновляем интерфейс
        document.getElementById('russianText').textContent = translation;
        document.querySelector('.explanation-content').textContent = explanation;

        // Добавляем в историю если перевод найден
        if (translation !== 'Перевод не найден' && translation !== 'Сленговый аналог не найден') {
            this.addToHistory(
                this.currentDirection === 'slang_to_russian' ? inputText : translation,
                this.currentDirection === 'slang_to_russian' ? translation : inputText,
                explanation
            );
        }
    }

    switchLanguage() {
        const slangInput = document.getElementById('slangInput');
        const russianText = document.getElementById('russianText');
        
        // Получаем элементы текста в переключателе языка
        const leftLangText = document.getElementById('leftLangText');
        const rightLangText = document.getElementById('rightLangText');
        
        if (this.currentDirection === 'slang_to_russian') {
            // Меняем на русский → сленг
            this.currentDirection = 'russian_to_slang';
            
            // Меняем местами тексты в переключателе языка
            leftLangText.textContent = 'русский';
            rightLangText.textContent = 'сленговый';
            
            // Меняем заголовки карточек
            document.getElementById('leftCardLabel').textContent = 'РУССКИЙ';
            document.getElementById('rightCardLabel').textContent = 'СЛЕНГ';
            
            // Меняем placeholder
            slangInput.placeholder = 'Введите русское выражение...';
        } else {
            // Меняем на сленг → русский
            this.currentDirection = 'slang_to_russian';
            
            // Меняем местами тексты в переключателе языка
            leftLangText.textContent = 'сленговый';
            rightLangText.textContent = 'русский';
            
            // Меняем заголовки карточек
            document.getElementById('leftCardLabel').textContent = 'СЛЕНГ';
            document.getElementById('rightCardLabel').textContent = 'РУССКИЙ';
            
            // Меняем placeholder
            slangInput.placeholder = 'Введите сленговое выражение...';
        }
        
        // Очищаем результаты при смене направления
        slangInput.value = '';
        russianText.textContent = 'Результат перевода...';
        document.querySelector('.explanation-content').textContent = 'Здесь появится объяснение термина';
    }

    showHistory() {
        document.getElementById('main-page').classList.remove('active');
        document.getElementById('history-page').classList.add('active');
        
        // Обновляем состояние кнопок навигации
        document.getElementById('translateNavBtn').classList.remove('active');
        document.getElementById('historyNavBtn').classList.add('active');
        document.getElementById('translateNavBtnHistory').classList.remove('active');
        document.getElementById('historyNavBtnHistory').classList.add('active');
        
        // Перерисовываем историю
        this.renderHistory();
    }

    showMain() {
        document.getElementById('history-page').classList.remove('active');
        document.getElementById('main-page').classList.add('active');
        
        // Обновляем состояние кнопок навигации
        document.getElementById('translateNavBtn').classList.add('active');
        document.getElementById('historyNavBtn').classList.remove('active');
        document.getElementById('translateNavBtnHistory').classList.add('active');
        document.getElementById('historyNavBtnHistory').classList.remove('active');
    }

    loadHistory() {
        // Пробуем загрузить историю из localStorage
        const savedHistory = localStorage.getItem('slanglitHistory');
        if (savedHistory) {
            this.history = JSON.parse(savedHistory);
        } else {
            // Заглушка с примерами
            this.history = [
                { original: "краш", translation: "симпатия", explanation: "Человек, который вам нравится" },
                { original: "кринж", translation: "стыдно", explanation: "Чувство неловкости за чьи-то действия" },
                { original: "рофл", translation: "шутка", explanation: "Что-то смешное, веселье" },
                { original: "го", translation: "пойдем", explanation: "Призыв к действию, предложение начать" }
            ];
        }
    }

    addToHistory(original, translation, explanation) {
        this.history.unshift({ 
            original, 
            translation, 
            explanation: explanation.split('\n')[0] // Берем только первую строку для истории
        });
        
        // Ограничиваем историю 50 элементами
        if (this.history.length > 50) {
            this.history = this.history.slice(0, 50);
        }
        
        // Сохраняем в localStorage
        localStorage.setItem('slanglitHistory', JSON.stringify(this.history));
        
        this.renderHistory();
    }

    renderHistory() {
        const historyItems = document.getElementById('historyItems');
        const pagination = document.getElementById('pagination');
        
        // Очищаем контейнеры
        historyItems.innerHTML = '';
        pagination.innerHTML = '';
        
        if (this.history.length === 0) {
            historyItems.innerHTML = `
                <div class="history-item" style="text-align: center; color: var(--text-secondary);">
                    История переводов пуста
                </div>
            `;
            return;
        }
        
        // Рассчитываем элементы для текущей страницы
        const startIndex = (this.currentPage - 1) * this.itemsPerPage;
        const endIndex = startIndex + this.itemsPerPage;
        const currentItems = this.history.slice(startIndex, endIndex);
        
        // Рендерим элементы истории
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
            
            // Добавляем обработчик клика
            historyItem.addEventListener('click', () => {
                this.loadHistoryItem(item);
            });
            
            historyItems.appendChild(historyItem);
        });
        
        // Рендерим пагинацию только если нужно
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
        // В зависимости от текущего направления загружаем соответствующим образом
        if (this.currentDirection === 'slang_to_russian') {
            document.getElementById('slangInput').value = item.original;
        } else {
            document.getElementById('slangInput').value = item.translation;
        }
        
        // Выполняем перевод
        this.showTranslation();
        
        // Переходим на главную страницу
        this.showMain();
    }

    escapeHtml(text) {
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }
}

// Функция копирования текста
function copyText(elementId) {
    const text = document.getElementById(elementId).textContent;
    navigator.clipboard.writeText(text).then(() => {
        // Можно добавить уведомление о успешном копировании
        console.log('Текст скопирован: ' + text);
    }).catch(err => {
        console.error('Ошибка копирования: ', err);
    });
}

// Функция вставки текста
function pasteText(elementId) {
    const input = document.getElementById(elementId);
    navigator.clipboard.readText().then(text => {
        input.value = text;
        // Триггерим событие изменения
        const event = new Event('input', { bubbles: true });
        input.dispatchEvent(event);
    }).catch(err => {
        console.error('Ошибка вставки: ', err);
    });
}

// Инициализация приложения
document.addEventListener('DOMContentLoaded', () => {
    new SlanglitApp();
});