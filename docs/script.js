// Главный класс приложения
class SlanglitApp {
    constructor() {
        this.currentDirection = 'slang_to_russian';
        this.history = [];
        this.currentPage = 1;
        this.itemsPerPage = 8;
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
            // Уже на главной, ничего не делаем
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

        // Обработчик ввода текста
        document.getElementById('slangInput').addEventListener('input', (e) => {
            this.handleInputChange(e.target.value);
        });
    }

    handleInputChange(text) {
        // Здесь можно добавить логику автоперевода или другие действия
        console.log('Введен текст:', text);
    }

    showTranslation() {
        const inputText = document.getElementById('slangInput').value;
        if (inputText.trim()) {
            // Здесь будет логика перевода
            console.log('Перевод текста:', inputText);
            // В реальном приложении здесь будет вызов API перевода
            
            // Добавляем в историю
            this.addToHistory(inputText, "переведенный текст", "описание перевода");
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
    }

    showHistory() {
        document.getElementById('main-page').classList.remove('active');
        document.getElementById('history-page').classList.add('active');
        
        // Обновляем состояние кнопок навигации
        document.getElementById('translateNavBtn').classList.remove('active');
        document.getElementById('historyNavBtn').classList.add('active');
        document.getElementById('translateNavBtnHistory').classList.remove('active');
        document.getElementById('historyNavBtnHistory').classList.add('active');
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
        // В реальном приложении здесь будет загрузка из localStorage или API
        this.history = [
            { original: "краш", translation: "симпатия", explanation: "Человек, который вам нравится" },
            { original: "кринж", translation: "стыдно", explanation: "Чувство неловкости" },
            { original: "рофл", translation: "шутка", explanation: "Что-то смешное" },
            { original: "го", translation: "пойдем", explanation: "Призыв к действию" },
            { original: "афк", translation: "отошел", explanation: "Временно отсутствует у компьютера" },
            { original: "имба", translation: "очень круто", explanation: "Что-то выдающееся, превосходное" },
            { original: "чилить", translation: "расслабляться", explanation: "Проводить время бездельничая" },
            { original: "хейтить", translation: "ненавидеть", explanation: "Проявлять негативное отношение" },
            { original: "скипнуть", translation: "пропустить", explanation: "Не обращать внимания, пролистать" },
            { original: "залипать", translation: "увлекаться", explanation: "Сильно погружаться в процесс" },
            { original: "шазамить", translation: "узнавать песню", explanation: "Использовать приложение для распознавания музыки" },
            { original: "красавчик", translation: "молодец", explanation: "Выражение одобрения" }
        ];
    }

    addToHistory(original, translation, explanation) {
        this.history.unshift({ original, translation, explanation });
        if (this.history.length > 50) { // Ограничиваем историю
            this.history = this.history.slice(0, 50);
        }
        this.renderHistory();
    }

    renderHistory() {
        const historyItems = document.getElementById('historyItems');
        const pagination = document.getElementById('pagination');
        
        // Очищаем контейнеры
        historyItems.innerHTML = '';
        pagination.innerHTML = '';
        
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
                    <div class="history-original">${item.original}</div>
                    <div class="history-translation">${item.translation}</div>
                </div>
                <div class="history-explanation">${item.explanation}</div>
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
        // Загружаем элемент истории в переводчик
        document.getElementById('slangInput').value = item.original;
        document.getElementById('russianText').textContent = item.translation;
        
        // Обновляем справку
        document.querySelector('.explanation-content').textContent = item.explanation;
        
        // Переходим на главную страницу
        this.showMain();
    }
}

// Функция копирования текста
function copyText(elementId) {
    const text = document.getElementById(elementId).textContent;
    navigator.clipboard.writeText(text).then(() => {
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