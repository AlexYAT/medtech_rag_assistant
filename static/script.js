let allProducts = [];

const searchInput = document.getElementById("searchInput");
const filterManufacturer = document.getElementById("filterManufacturer");
const filterGroup = document.getElementById("filterGroup");
const filterDocType = document.getElementById("filterDocType");
const cardsContainer = document.getElementById("cardsContainer");
const resultsCount = document.getElementById("resultsCount");
const noResults = document.getElementById("noResults");

const ragInput = document.getElementById("ragInput");
const ragSubmit = document.getElementById("ragSubmit");
const ragResponse = document.getElementById("ragResponse");
const ragScenario = document.getElementById("ragScenario");
const ragAnswer = document.getElementById("ragAnswer");
const ragList = document.getElementById("ragList");
const ragTable = document.getElementById("ragTable");
const ragNotice = document.getElementById("ragNotice");
const ragSources = document.getElementById("ragSources");

const SCENARIO_LABELS = {
    technical_specs: "Technical Specs",
    comparison: "Comparison",
    overview: "Overview",
    faq: "FAQ",
    rzn_check: "RZN Check",
};

async function init() {
    try {
        const [productsRes, filtersRes] = await Promise.all([
            fetch("/api/products"),
            fetch("/api/filters"),
        ]);

        allProducts = await productsRes.json();
        const filters = await filtersRes.json();

        populateSelect(filterManufacturer, filters.manufacturers);
        populateSelect(filterGroup, filters.product_groups);
        populateSelect(filterDocType, filters.document_types);

        renderCards(allProducts);
        bindEvents();
    } catch (err) {
        console.error("Init error:", err);
        cardsContainer.innerHTML =
            '<p style="color:#f85149">Ошибка загрузки данных. Убедитесь, что сервер запущен.</p>';
    }
}

function populateSelect(select, options) {
    options.forEach((opt) => {
        const el = document.createElement("option");
        el.value = opt;
        el.textContent = opt;
        select.appendChild(el);
    });
}

function bindEvents() {
    searchInput.addEventListener("input", applyFilters);
    filterManufacturer.addEventListener("change", applyFilters);
    filterGroup.addEventListener("change", applyFilters);
    filterDocType.addEventListener("change", applyFilters);

    ragSubmit.addEventListener("click", () => askRag(ragInput.value));
    ragInput.addEventListener("keydown", (e) => {
        if (e.key === "Enter") askRag(ragInput.value);
    });

    document.querySelectorAll(".demo-btn").forEach((btn) => {
        btn.addEventListener("click", () => {
            const question = btn.dataset.question;
            ragInput.value = question;
            askRag(question);
        });
    });
}

function applyFilters() {
    const query = searchInput.value.toLowerCase().trim();
    const manufacturer = filterManufacturer.value;
    const group = filterGroup.value;
    const docType = filterDocType.value;

    const filtered = allProducts.filter((p) => {
        const matchesSearch =
            !query ||
            p.product_name.toLowerCase().includes(query) ||
            p.manufacturer.toLowerCase().includes(query) ||
            p.product_group.toLowerCase().includes(query) ||
            p.document_type.toLowerCase().includes(query) ||
            p.description.toLowerCase().includes(query);

        const matchesManufacturer = !manufacturer || p.manufacturer === manufacturer;
        const matchesGroup = !group || p.product_group === group;
        const matchesDocType = !docType || p.document_type === docType;

        return matchesSearch && matchesManufacturer && matchesGroup && matchesDocType;
    });

    renderCards(filtered);
}

function renderCards(products) {
    cardsContainer.innerHTML = "";

    const count = products.length;
    resultsCount.textContent = `${count} ${pluralize(count, "изделие", "изделия", "изделий")}`;

    if (count === 0) {
        noResults.classList.remove("hidden");
        return;
    }

    noResults.classList.add("hidden");

    products.forEach((product, index) => {
        const card = document.createElement("article");
        card.className = "card";
        card.style.animationDelay = `${index * 0.08}s`;

        card.innerHTML = `
            <h3 class="card__title">${escapeHtml(product.product_name)}</h3>
            <div class="card__meta">
                <span class="card__tag">${escapeHtml(product.manufacturer)}</span>
                <span class="card__tag">${escapeHtml(product.product_group)}</span>
                <span class="card__tag card__tag--accent">${escapeHtml(product.document_type)}</span>
            </div>
            <p class="card__description">${escapeHtml(product.description)}</p>
            <a class="card__link" href="${escapeHtml(product.source_url)}" target="_blank" rel="noopener">
                Открыть материал
                <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                    <path d="M18 13v6a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V8a2 2 0 0 1 2-2h6"/>
                    <polyline points="15 3 21 3 21 9"/><line x1="10" y1="14" x2="21" y2="3"/>
                </svg>
            </a>
        `;

        cardsContainer.appendChild(card);
    });
}

async function askRag(question) {
    const trimmed = question.trim();
    if (!trimmed) return;

    ragSubmit.classList.add("loading");
    ragSubmit.textContent = "Обработка...";

    try {
        const res = await fetch("/api/rag", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ question: trimmed }),
        });

        const data = await res.json();

        if (!res.ok) {
            showRagError(data.error || "Ошибка запроса");
            return;
        }

        showRagResponse(data);
    } catch (err) {
        console.error("RAG error:", err);
        showRagError("Не удалось получить ответ от сервера.");
    } finally {
        ragSubmit.classList.remove("loading");
        ragSubmit.textContent = "Спросить";
    }
}

function showRagResponse(data) {
    ragResponse.classList.remove("hidden");
    ragScenario.textContent = SCENARIO_LABELS[data.scenario] || data.scenario;
    ragAnswer.innerHTML = formatAnswer(data.answer);

    if (data.list && data.list.length > 0) {
        ragList.classList.remove("hidden");
        ragList.innerHTML =
            "<ul style='margin-top:0.75rem;padding-left:1.25rem;list-style:disc;'>" +
            data.list.map((item) => `<li>${formatAnswer(item)}</li>`).join("") +
            "</ul>";
    } else {
        ragList.classList.add("hidden");
        ragList.innerHTML = "";
    }

    if (data.table) {
        ragTable.classList.remove("hidden");
        ragTable.innerHTML = buildTable(data.table);
    } else {
        ragTable.classList.add("hidden");
        ragTable.innerHTML = "";
    }

    if (data.notice) {
        ragNotice.classList.remove("hidden");
        ragNotice.innerHTML = `
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <path d="M12 9v4m0 4h.01M10.29 3.86 1.82 18a2 2 0 0 0 1.71 3h16.94a2 2 0 0 0 1.71-3L13.71 3.86a2 2 0 0 0-3.42 0z"/>
            </svg>
            <span>${escapeHtml(data.notice)}</span>
        `;
    } else {
        ragNotice.classList.add("hidden");
        ragNotice.innerHTML = "";
    }

    if (data.sources_by_product && data.sources_by_product.length > 0) {
        ragSources.innerHTML = `
            <h4>Источники</h4>
            ${data.sources_by_product
                .map(
                    (s) =>
                        `<div><strong>${escapeHtml(s.product)}:</strong> ` +
                        `<a href="${escapeHtml(s.url)}" target="_blank" rel="noopener">${escapeHtml(s.url)}</a></div>`
                )
                .join("")}
        `;
    } else if (data.sources && data.sources.length > 0) {
        ragSources.innerHTML = `
            <h4>Источники</h4>
            ${data.sources
                .map((url) => {
                    const isLink = url.startsWith("http");
                    return isLink
                        ? `<a href="${escapeHtml(url)}" target="_blank" rel="noopener">${escapeHtml(url)}</a>`
                        : `<span>${escapeHtml(url)}</span>`;
                })
                .join("")}
        `;
    } else {
        ragSources.innerHTML = "";
    }

    ragResponse.scrollIntoView({ behavior: "smooth", block: "nearest" });
}

function showRagError(message) {
    ragResponse.classList.remove("hidden");
    ragScenario.textContent = "Ошибка";
    ragAnswer.textContent = message;
    ragList.classList.add("hidden");
    ragTable.classList.add("hidden");
    ragNotice.classList.add("hidden");
    ragSources.innerHTML = "";
}

function buildTable(table) {
    const headerRow = table.headers.map((h) => `<th>${escapeHtml(h)}</th>`).join("");
    const bodyRows = table.rows
        .map((row) => `<tr>${row.map((cell) => `<td>${escapeHtml(cell)}</td>`).join("")}</tr>`)
        .join("");

    return `<table class="rag-table"><thead><tr>${headerRow}</tr></thead><tbody>${bodyRows}</tbody></table>`;
}

function formatAnswer(text) {
    return escapeHtml(text).replace(/\*\*(.+?)\*\*/g, "<strong>$1</strong>");
}

function escapeHtml(str) {
    const div = document.createElement("div");
    div.textContent = str;
    return div.innerHTML;
}

function pluralize(n, one, few, many) {
    const mod10 = n % 10;
    const mod100 = n % 100;
    if (mod100 >= 11 && mod100 <= 19) return many;
    if (mod10 === 1) return one;
    if (mod10 >= 2 && mod10 <= 4) return few;
    return many;
}

init();
