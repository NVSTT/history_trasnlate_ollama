const tg = window.Telegram.WebApp;
tg.expand(); // Растягиваем Web App на весь экран

let currentPage = "menu"; // Текущая страница
let currentTextId = null; // ID текущего текста

async function navigateTo(page) {
    currentPage = page;
    sessionStorage.setItem('currentPage', page);
    document.getElementById('content').innerHTML = '';

    if (page === "menu") showMainMenu();
    if (page === "new_text") showNewTextForm();
    if (page === "search") showSearch();
    if (page === "documents") await showTexts();
    if (page === "question") showQuestionForm(currentTextId);
}

async function apiRequest(url, method = 'GET', body = null) {
    const headers = { 'Content-Type': 'application/json' };

    if (body) console.log("Отправка запроса:", url, body);

    const response = await fetch(url, {
        method,
        headers,
        body: method !== 'GET' ? JSON.stringify(body) : null
    });

    if (!response.ok) {
        const errorText = await response.text();
        console.error("Ошибка API:", errorText);
        throw new Error(errorText);
    }

    return response.json();
}

// 🚀 Главное меню
function showMainMenu() {
    document.getElementById('content').innerHTML = `
        <div class="card">
            <h2>Старорусские тексты</h2>
            <button onclick="navigateTo('new_text')">📝 Новый текст</button>
            <button onclick="navigateTo('documents')">📚 Мои тексты</button>
            <button onclick="navigateTo('question')">❓ Задать вопрос</button>
            <button onclick="navigateTo('search')">🔍 Поиск</button>
        </div>`;
}

// Показываем главное меню при загрузке страницы
document.addEventListener("DOMContentLoaded", () => {
    showMainMenu();
});


// 🚀 Экран ввода нового текста
function showNewTextForm() {
    document.getElementById('content').innerHTML = `
        <div class="card">
            <h3>Новый текст</h3>
            <textarea id="original-text" placeholder="Введите старорусский текст"></textarea>
            <button onclick="processText()">Обработать</button>
            <button onclick="navigateTo('menu')">Назад</button>
        </div>`;
}

// 🚀 Отправка текста в API для перевода
async function processText() {
    const text = document.getElementById('original-text').value;
    if (!text) return tg.showAlert('Введите текст');

    showLoader();
    try {
        const response = await apiRequest('/api/translate/', 'POST', { text });
        document.getElementById('content').innerHTML = `
            <div class="card">
                <h3>Результат</h3>
                <h4>Оригинал:</h4><p>${text}</p>
                <h4>Перевод:</h4><p>${response.translation}</p>
                <h4>Суммаризация:</h4><p>${response.summary}</p>
                <h4>Ключевые слова:</h4><p>${response.keywords.join(', ')}</p>
                <button onclick="navigateTo('menu')">В главное меню</button>
            </div>`;
    } catch (error) {
        tg.showAlert('Ошибка обработки: ' + error.message);
    }
}

// 🚀 Экран поиска
function showSearch() {
    document.getElementById('content').innerHTML = `
        <div class="card">
            <h3>Поиск</h3>
            <input type="text" id="search-input" class="search-input" placeholder="Введите запрос">
            <button onclick="performSearch()">🔍 Искать</button>
            <button onclick="navigateTo('menu')">Назад</button>
            <div id="search-results"></div>
        </div>`;
}

// 🚀 Выполнение поиска в API
async function performSearch() {
    const query = document.getElementById('search-input').value;
    if (!query) return;

    document.getElementById('search-results').innerHTML = `<div class="loader"></div>`;
    try {
        // Используем новый эндпоинт для семантического поиска
        const response = await apiRequest('/api/search/', 'POST', { query, top_k: 5 });
        
        let resultsHtml = response.results.length
            ? response.results.map(doc => `
                <div class="text-card">
                    <p>
                      <strong>${doc.title} (${doc.year})</strong>
                      <span style="font-size: 0.9em; color: #666;">(Сходство: ${(doc.similarity * 100).toFixed(2)}%)</span>
                    </p>
                    <p>${doc.summary.slice(0, 100)}...</p>
                    <button onclick="showTextDetail(${doc.id})">Открыть</button>
                </div>`).join('')
            : '<p>Ничего не найдено</p>';

        document.getElementById('search-results').innerHTML = resultsHtml;
    } catch (error) {
        showError('Ошибка поиска: ' + error.message);
    }
}



function showError(message) {
    if (window.Telegram?.WebApp?.version && parseFloat(window.Telegram.WebApp.version) >= 6.1) {
        window.Telegram.WebApp.showAlert(message);
    } else {
        alert(message);  // Обычный alert для браузера или старых версий Telegram
    }
}

// 🚀 Экран списка документов
async function showTexts() {
    showLoader();
    try {
        const response = await apiRequest('/api/documents/', 'GET');
        console.log("Документы загружены:", response);
        document.getElementById('content').innerHTML = `
            <div class="card">
                <h3>Документы</h3>
                ${response.results.map(doc => `
                    <div class="text-card">
                        <p><strong>${doc.title} (${doc.year})</strong></p>
                        <p>${doc.summary.slice(0, 100)}...</p>
                        <button onclick="showTextDetail(${doc.id})">Открыть</button>
                    </div>`).join('')}
                <button onclick="navigateTo('menu')">Назад</button>
            </div>`;
    } catch (error) {
        console.error("Ошибка загрузки документов:", error);
        showError('Ошибка загрузки документов: ' + error.message);
    }
}

// 🚀 Детальный просмотр документа
async function showTextDetail(textId) {
    showLoader();
    try {
        const response = await apiRequest(`/api/documents/${textId}`, 'GET');
        currentTextId = textId;

        document.getElementById('content').innerHTML = `
            <div class="card">
                <h3>${response.title} (${response.year})</h3>
                <h4>Оригинал:</h4><p>${response.original_text}</p>
                <h4>Перевод:</h4><p>${response.modern_translation}</p>
                <h4>Суммаризация:</h4><p>${response.summary}</p>
                <button onclick="navigateTo('question')">Задать вопрос</button>
                <button onclick="navigateTo('documents')">Назад</button>
            </div>`;
    } catch (error) {
        tg.showAlert('Ошибка загрузки документа: ' + error.message);
    }
}

// 🚀 Форма вопросов
function showQuestionForm() {
    document.getElementById('content').innerHTML = `
        <div class="card">
            <h3>Задать вопрос</h3>
            <textarea id="question-input" placeholder="Введите вопрос"></textarea>
            <button onclick="submitQuestion()">Отправить</button>
            <button onclick="navigateTo('menu')">Назад</button>
        </div>`;
}

// 🚀 Отправка вопроса к API
async function submitQuestion() {
    const question = document.getElementById('question-input').value;
    if (!question || !currentTextId) return tg.showAlert("Выберите документ!");

    showLoader();
    try {
        const response = await apiRequest('/api/questions/', 'POST', { text_id: currentTextId, question });
        document.getElementById('content').innerHTML = `
            <div class="card">
                <h3>Ответ</h3>
                <p>${response.answer}</p>
                <button onclick="navigateTo('menu')">В главное меню</button>
            </div>`;
    } catch (error) {
        tg.showAlert('Ошибка: ' + error.message);
    }
}

// 🚀 Показать загрузчик
function showLoader() {
    document.getElementById('content').innerHTML = `<div class="loader"></div>`;
}

// 🚀 Восстановление состояния после обновления
document.addEventListener("DOMContentLoaded", () => {
    const lastPage = sessionStorage.getItem('currentPage') || "menu";
    navigateTo(lastPage);
});
