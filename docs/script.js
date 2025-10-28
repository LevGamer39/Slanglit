// Главный класс приложения
class SlanglitApp {
    constructor() {
        this.currentDirection = 'slang_to_russian';
        this.init();
    }

    init() {
        // Telegram Web App интеграция
        if (window.Telegram && window.Telegram.WebApp) {
            this.tg = window.Telegram.WebApp;
            this.tg.ready();
            this.tg.expand();
        }
        
        this.bindEvents();
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
    }

    showTranslation() {
        // Здесь будет логика перевода
        console.log('Перевод...');
    }

    switchLanguage() {
        // Сохраняем текущие тексты
        const slangText = document.getElementById('slangText').textContent;
        const russianText = document.getElementById('russianText').textContent;
        
        // Получаем элементы текста в переключателе языка
        const langTexts = document.querySelectorAll('.lang-text');
        const leftLang = langTexts[0];
        const rightLang = langTexts[1];
        
        if (this.currentDirection === 'slang_to_russian') {
            // Меняем на русский → сленг
            this.currentDirection = 'russian_to_slang';
            
            // Меняем местами тексты в переключателе языка
            const temp = leftLang.textContent;
            leftLang.textContent = rightLang.textContent;
            rightLang.textContent = temp;
            
            // Меняем заголовки карточек
            document.querySelectorAll('.card-label')[0].textContent = 'РУССКИЙ';
            document.querySelectorAll('.card-label')[1].textContent = 'СЛЕНГ';
            
            // Меняем тексты местами
            document.getElementById('slangText').textContent = russianText;
            document.getElementById('russianText').textContent = slangText;
        } else {
            // Меняем на сленг → русский
            this.currentDirection = 'slang_to_russian';
            
            // Меняем местами тексты в переключателе языка
            const temp = leftLang.textContent;
            leftLang.textContent = rightLang.textContent;
            rightLang.textContent = temp;
            
            // Меняем заголовки карточек
            document.querySelectorAll('.card-label')[0].textContent = 'СЛЕНГ';
            document.querySelectorAll('.card-label')[1].textContent = 'РУССКИЙ';
            
            // Меняем тексты местами
            document.getElementById('slangText').textContent = russianText;
            document.getElementById('russianText').textContent = slangText;
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
}

// Инициализация приложения
document.addEventListener('DOMContentLoaded', () => {
    new SlanglitApp();
});