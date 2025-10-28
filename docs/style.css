/* ========== VARIABLES & RESET ========== */
* {
    margin: 0;
    padding: 0;
    box-sizing: border-box;
}

:root {
    --bg-primary: #222526;
    --bg-secondary: #343434;
    --bg-card: #343434;
    --text-primary: #FFFFFF;
    --text-secondary: #989898;
    --text-accent: #44A3B9;
    --accent-primary: #44A3B9;
    --border-radius: 16px;
    --max-width: 800px;
}

body {
    background: linear-gradient(135deg, #1a1e23 0%, #2a2f35 100%);
    color: var(--text-primary);
    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, sans-serif;
    line-height: 1.5;
    min-height: 100vh;
    display: flex;
    justify-content: center;
    align-items: center;
    padding: 40px;
}

.app-container {
    width: 100%;
    max-width: var(--max-width);
    background: var(--bg-primary);
    border-radius: 24px;
    overflow: hidden;
    box-shadow: 0 20px 60px rgba(0, 0, 0, 0.5);
    min-height: 800px;
    height: 800px;
    display: flex;
    flex-direction: column;
    border: 1px solid #3a3a3a;
}

/* ========== PAGES ========== */
.page {
    display: none;
    padding: 40px;
    flex: 1;
    flex-direction: column;
    overflow: hidden;
}

.page.active {
    display: flex;
}

/* ========== HEADER ========== */
.header {
    padding: 0 0 30px;
    text-align: center;
    flex-shrink: 0;
}

.app-title {
    font-size: 36px;
    font-weight: 700;
    margin-bottom: 8px;
    background: linear-gradient(135deg, #44A3B9 0%, #5bc2d8 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
}

.app-subtitle {
    font-size: 18px;
    color: var(--text-secondary);
    font-weight: 500;
}

/* ========== LANGUAGE SWITCH ========== */
.language-switch {
    display: flex;
    align-items: center;
    justify-content: center;
    gap: 20px;
    margin: 0 0 30px;
    padding: 20px;
    background: var(--bg-card);
    border-radius: var(--border-radius);
    flex-shrink: 0;
    border: 1px solid #444;
}

.lang-text {
    font-size: 20px;
    font-weight: 600;
    color: var(--text-primary);
    width: 120px;
    text-align: center;
}

.lang-swap-btn {
    background: var(--accent-primary);
    color: white;
    border: none;
    border-radius: 12px;
    width: 60px;
    height: 60px;
    display: flex;
    align-items: center;
    justify-content: center;
    cursor: pointer;
    font-size: 28px;
    font-weight: bold;
    flex-shrink: 0;
    transition: all 0.3s ease;
    box-shadow: 0 4px 12px rgba(68, 163, 185, 0.3);
}

.lang-swap-btn:hover {
    background: #3a92a5;
    transform: scale(1.08);
    box-shadow: 0 6px 16px rgba(68, 163, 185, 0.4);
}

/* ========== TRANSLATION CARDS ========== */
.translation-card {
    background: var(--bg-card);
    margin: 0 0 20px;
    padding: 30px;
    border-radius: var(--border-radius);
    flex-shrink: 0;
    border: 1px solid #444;
    transition: transform 0.2s ease;
}

.translation-card:hover {
    transform: translateY(-2px);
}

.card-label {
    font-size: 16px;
    color: var(--text-accent);
    margin-bottom: 16px;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 1px;
}

.translation-text {
    font-size: 22px;
    color: var(--text-primary);
    font-weight: 600;
    line-height: 1.4;
    min-height: 32px;
    word-break: break-word;
    padding: 8px 0;
}

/* ========== BIG TRANSLATE BUTTON ========== */
.big-translate-btn {
    width: 100%;
    background: linear-gradient(135deg, #44A3B9 0%, #5bc2d8 100%);
    color: white;
    border: none;
    border-radius: var(--border-radius);
    padding: 24px;
    font-size: 20px;
    font-weight: 700;
    cursor: pointer;
    margin: 30px 0;
    flex-shrink: 0;
    transition: all 0.3s ease;
    box-shadow: 0 6px 20px rgba(68, 163, 185, 0.3);
    text-transform: uppercase;
    letter-spacing: 0.5px;
}

.big-translate-btn:hover {
    transform: translateY(-2px);
    box-shadow: 0 8px 25px rgba(68, 163, 185, 0.4);
}

/* ========== EXPLANATION CARD ========== */
.explanation-card {
    background: var(--bg-card);
    margin: 0 0 30px;
    padding: 30px;
    border-radius: var(--border-radius);
    flex-grow: 1;
    display: flex;
    flex-direction: column;
    min-height: 180px;
    border: 1px solid #444;
}

.explanation-title {
    font-size: 18px;
    font-weight: 700;
    color: var(--text-primary);
    margin-bottom: 16px;
    text-transform: uppercase;
    letter-spacing: 0.5px;
}

.explanation-content {
    font-size: 18px;
    color: var(--text-secondary);
    line-height: 1.6;
    flex-grow: 1;
    word-break: break-word;
}

/* ========== NAVIGATION BUTTONS ========== */
.nav-buttons {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 20px;
    position: absolute;
    bottom: 40px;
    left: 40px;
    right: 40px;
    background: var(--bg-primary);
    padding: 10px 0;
    z-index: 100;
}

.nav-btn {
    background: var(--bg-card);
    color: var(--text-primary);
    border: 1px solid #444;
    border-radius: var(--border-radius);
    padding: 20px 24px;
    font-size: 18px;
    font-weight: 600;
    cursor: pointer;
    transition: all 0.3s ease;
}

.nav-btn:hover {
    background: #3d3d3d;
    transform: translateY(-1px);
}

.nav-btn.active {
    background: linear-gradient(135deg, #44A3B9 0%, #5bc2d8 100%);
    color: white;
    border-color: #44A3B9;
    box-shadow: 0 4px 12px rgba(68, 163, 185, 0.3);
}

.nav-btn.active:hover {
    transform: translateY(-1px);
    box-shadow: 0 6px 16px rgba(68, 163, 185, 0.4);
}

/* ========== HISTORY SECTION ========== */
.history-container {
    flex-grow: 1;
    display: flex;
    flex-direction: column;
    padding-bottom: 30px;
    overflow: hidden;
}

.history-items {
    display: flex;
    flex-direction: column;
    gap: 16px;
    flex-grow: 1;
    margin-bottom: 30px;
    overflow-y: auto;
    max-height: 520px;
    padding-right: 12px;
}

/* Scrollbar styling */
.history-items::-webkit-scrollbar {
    width: 8px;
}

.history-items::-webkit-scrollbar-track {
    background: var(--bg-secondary);
    border-radius: 4px;
}

.history-items::-webkit-scrollbar-thumb {
    background: var(--accent-primary);
    border-radius: 4px;
}

.history-items::-webkit-scrollbar-thumb:hover {
    background: #3a92a5;
}

.history-item {
    background: var(--bg-card);
    border-radius: var(--border-radius);
    padding: 24px;
    cursor: pointer;
    transition: all 0.3s ease;
    flex-shrink: 0;
    border: 1px solid #444;
}

.history-item:hover {
    background: #3d3d3d;
    transform: translateY(-2px);
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.2);
}

.history-pair {
    display: flex;
    justify-content: space-between;
    align-items: flex-start;
    margin-bottom: 12px;
}

.history-original {
    font-size: 20px;
    font-weight: 700;
    color: var(--text-primary);
}

.history-translation {
    font-size: 20px;
    color: var(--text-accent);
    font-weight: 700;
}

.history-explanation {
    font-size: 16px;
    color: var(--text-secondary);
    line-height: 1.5;
    overflow: hidden;
    text-overflow: ellipsis;
    display: -webkit-box;
    -webkit-line-clamp: 2;
    -webkit-box-orient: vertical;
}

.pagination {
    display: flex;
    justify-content: center;
    gap: 10px;
    margin-top: auto;
    padding: 24px 0 10px;
    flex-shrink: 0;
}

.page-btn {
    background: var(--bg-card);
    color: var(--text-primary);
    border: 1px solid #444;
    border-radius: 10px;
    width: 44px;
    height: 44px;
    display: flex;
    align-items: center;
    justify-content: center;
    cursor: pointer;
    font-size: 18px;
    font-weight: 600;
    transition: all 0.3s ease;
}

.page-btn:hover {
    background: #3d3d3d;
    transform: scale(1.05);
}

.page-btn.active {
    background: var(--accent-primary);
    border-color: var(--accent-primary);
    box-shadow: 0 4px 12px rgba(68, 163, 185, 0.3);
}

/* Кнопки ввода/копирования */
.action-buttons {
    display: flex;
    gap: 12px;
    margin-top: 16px;
}

.action-btn {
    background: transparent;
    border: 1px solid var(--text-secondary);
    color: var(--text-secondary);
    border-radius: 10px;
    padding: 12px 18px;
    font-size: 16px;
    cursor: pointer;
    display: flex;
    align-items: center;
    gap: 8px;
    transition: all 0.3s ease;
    font-weight: 500;
}

.action-btn:hover {
    border-color: var(--accent-primary);
    color: var(--accent-primary);
    transform: translateY(-1px);
}

.action-btn svg {
    width: 18px;
    height: 18px;
    fill: currentColor;
}

/* Поле ввода */
.input-field {
    width: 100%;
    background: transparent;
    border: 1px solid var(--text-secondary);
    border-radius: 10px;
    padding: 16px;
    font-size: 20px;
    color: var(--text-primary);
    font-family: inherit;
    resize: none;
    min-height: 60px;
    transition: all 0.3s ease;
    font-weight: 500;
}

.input-field:focus {
    outline: none;
    border-color: var(--accent-primary);
    box-shadow: 0 0 0 2px rgba(68, 163, 185, 0.2);
}

.input-field::placeholder {
    color: var(--text-secondary);
}

/* Скрываем пагинацию когда не нужна */
.pagination.hidden {
    display: none;
}

/* Адаптация для мобильных */
@media (max-width: 768px) {
    body {
        padding: 20px;
        align-items: stretch;
    }
    
    .app-container {
        max-width: 100%;
        height: 100vh;
        border-radius: 0;
        box-shadow: none;
        min-height: auto;
    }
    
    .page {
        padding: 20px 16px 80px;
    }
    
    .nav-buttons {
        bottom: 20px;
        left: 16px;
        right: 16px;
    }
    
    .app-title {
        font-size: 28px;
    }
    
    .app-subtitle {
        font-size: 16px;
    }
    
    .lang-text {
        font-size: 16px;
        width: 100px;
    }
    
    .lang-swap-btn {
        width: 50px;
        height: 50px;
        font-size: 24px;
    }
    
    .translation-text,
    .input-field {
        font-size: 18px;
    }
    
    .explanation-content {
        font-size: 16px;
    }
    
    .big-translate-btn {
        font-size: 18px;
        padding: 20px;
    }
}

/* Safe areas for iOS */
@supports (padding: max(0px)) {
    body {
        padding-left: max(0px, env(safe-area-inset-left));
        padding-right: max(0px, env(safe-area-inset-right));
        padding-bottom: max(0px, env(safe-area-inset-bottom));
    }
}