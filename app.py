import json
import os
from pathlib import Path

from dotenv import load_dotenv
from flask import Flask, jsonify, render_template, request
from openai import OpenAI

load_dotenv()

app = Flask(__name__)

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-4o-mini")

CONTENT_TYPE_LABELS = {
    "commercial_description": "Коммерческое описание",
    "catalog_description": "Краткое описание для каталога",
    "technical_doctor": "Техническое описание для врача",
    "client_email": "Email клиенту",
    "social_post": "Пост для соцсетей",
}

TONE_LABELS = {
    "expert": "Экспертный",
    "business": "Деловой",
    "brief": "Краткий",
    "friendly": "Дружелюбный",
}

CONTENT_FOOTER_WARNING = (
    "Проверьте критически важные параметры по оригинальному документу производителя."
)

CONTENT_PATH = Path(__file__).parent / "content.json"

DEMO_QUESTIONS = [
    "Какие размеры доступны для стента Eluvia?",
    "Какие проводники подходят для баллонного катетера Sterling PTA?",
    "Подготовь краткий обзор баллонного катетера Sterling PTA.",
    "Сформируй основные преимущества Eluvia для коммерческого предложения.",
    "Сравни Eluvia и EverFlex.",
    "Какие противопоказания указаны для EverFlex?",
    "Проверь регистрационный статус Eluvia.",
]


def load_content():
    with open(CONTENT_PATH, encoding="utf-8") as f:
        return json.load(f)


def find_product(products, name):
    name_lower = name.lower()
    for product in products:
        if product["product_name"].lower() == name_lower:
            return product
    return None


def retrieve_product(products, name):
    product = find_product(products, name)
    if not product:
        return None, []
    return product, [product["source_url"]]


class RegulatoryRepository:
    """Mock regulatory data repository for RZN registration checks."""

    def __init__(self, products):
        self._registry = {
            p["product_name"].lower(): {
                "rzn_number": p["rzn_number"],
                "rzn_status": p["rzn_status"],
                "manufacturer": p["manufacturer"],
            }
            for p in products
        }

    def check(self, product_name):
        entry = self._registry.get(product_name.lower())
        if not entry:
            return None
        return {
            "product_name": product_name,
            "rzn_number": entry["rzn_number"],
            "rzn_status": entry["rzn_status"],
            "manufacturer": entry["manufacturer"],
        }


def technical_specs(products, question):
    product_name = _extract_product_name(question, products)
    if not product_name:
        return {
            "scenario": "technical_specs",
            "answer": "Укажите название изделия для получения технических характеристик.",
            "sources": [],
        }

    product, sources = retrieve_product(products, product_name)
    if not product:
        return {
            "scenario": "technical_specs",
            "answer": f"Изделие «{product_name}» не найдено в базе данных.",
            "sources": [],
        }

    question_lower = question.lower()
    if "размер" in question_lower:
        table = {
            "headers": ["№", "Диаметр × Длина"],
            "rows": [
                [str(index + 1), size] for index, size in enumerate(product["sizes"])
            ],
        }
        answer = (
            f"Для стента **{product['product_name']}** "
            f"в документации производителя указаны следующие размеры:"
        )
        return {
            "scenario": "technical_specs",
            "answer": answer,
            "sources": sources,
            "table": table,
        }

    sizes = ", ".join(product["sizes"])
    answer = (
        f"**{product['product_name']}** — технические характеристики:\n\n"
        f"- **Материал:** {product['material']}\n"
        f"- **Размеры:** {sizes}\n"
        f"- **Система доставки:** {product['delivery_system']}"
    )
    return {"scenario": "technical_specs", "answer": answer, "sources": sources}


def comparison(products, question):
    product_a_name = "Eluvia"
    product_b_name = "EverFlex"

    product_a, sources_a = retrieve_product(products, product_a_name)
    product_b, sources_b = retrieve_product(products, product_b_name)

    if not product_a or not product_b:
        return {
            "scenario": "comparison",
            "answer": "Не удалось выполнить сравнение: одно или оба изделия не найдены.",
            "sources": [],
            "table": None,
        }

    table = {
        "headers": ["Параметр", product_a_name, product_b_name],
        "rows": [
            ["Производитель", product_a["manufacturer"], product_b["manufacturer"]],
            ["Тип изделия", product_a["product_group"], product_b["product_group"]],
            [
                "Область применения",
                product_a.get("application_area", "—"),
                product_b.get("application_area", "—"),
            ],
            [
                "Наличие покрытия",
                product_a.get("coating", "—"),
                product_b.get("coating", "—"),
            ],
            [
                "Система доставки",
                product_a["delivery_system"],
                product_b["delivery_system"],
            ],
        ],
    }

    answer = (
        f"Сравнительная таблица **{product_a_name}** и **{product_b_name}** "
        f"на основе документации производителей."
    )

    return {
        "scenario": "comparison",
        "answer": answer,
        "sources": list(dict.fromkeys(sources_a + sources_b)),
        "sources_by_product": [
            {"product": product_a_name, "url": product_a["source_url"]},
            {"product": product_b_name, "url": product_b["source_url"]},
        ],
        "table": table,
    }


def overview(products, question):
    product_name = _extract_product_name(question, products)
    if not product_name:
        return {
            "scenario": "overview",
            "answer": "Укажите название изделия для получения обзора.",
            "sources": [],
        }

    product, sources = retrieve_product(products, product_name)
    if not product:
        return {
            "scenario": "overview",
            "answer": f"Изделие «{product_name}» не найдено в базе данных.",
            "sources": [],
        }

    purpose = product.get("purpose", product["description"])
    features = product.get("key_features", [])
    application = product.get("application_area", "—")

    features_text = "\n".join(f"- {feature}" for feature in features) if features else "—"

    answer = (
        f"**{product['product_name']}** ({product['manufacturer']})\n\n"
        f"**Назначение:** {purpose}\n\n"
        f"**Основные особенности:**\n{features_text}\n\n"
        f"**Область применения:** {application}"
    )
    return {"scenario": "overview", "answer": answer, "sources": sources}


def faq(products, question):
    product_name = _extract_product_name(question, products)
    question_lower = question.lower()

    if "проводник" in question_lower or (
        "совместим" in question_lower and "sterling" in question_lower
    ):
        return _compatibility_faq(products, product_name or "Sterling PTA")

    if "преимущест" in question_lower or "коммерческ" in question_lower:
        return _commercial_faq(products, product_name or "Eluvia")

    if "противопоказан" in question_lower:
        if not product_name:
            product_name = "EverFlex"
        product, sources = retrieve_product(products, product_name)
        if not product:
            return {
                "scenario": "faq",
                "answer": f"Изделие «{product_name}» не найдено.",
                "sources": [],
            }
        answer = (
            f"**Противопоказания для {product['product_name']}** "
            f"(по данным IFU):\n\n{product['contraindications']}"
        )
        return {
            "scenario": "faq",
            "answer": answer,
            "sources": sources,
            "notice": (
                "Проверьте критически важные параметры "
                "по оригинальному документу производителя."
            ),
        }

    for demo_q in DEMO_QUESTIONS:
        if demo_q.lower() in question_lower or question_lower in demo_q.lower():
            return faq(products, demo_q)

    return {
        "scenario": "faq",
        "answer": (
            "Выберите один из рабочих сценариев в разделе "
            "«Примеры рабочих сценариев» или задайте вопрос об изделии."
        ),
        "sources": [],
    }


def _compatibility_faq(products, product_name):
    product, sources = retrieve_product(products, product_name)
    if not product or "compatible_guidewires" not in product:
        return {
            "scenario": "faq",
            "answer": f"Данные о совместимости для «{product_name}» не найдены.",
            "sources": [],
        }

    guidewires = product["compatible_guidewires"]
    item_list = [
        f"{wire['name']} ({wire['manufacturer']}) — {wire['notes']}"
        for wire in guidewires
    ]

    answer = (
        f"Для баллонного катетера **{product['product_name']}** "
        f"в IFU указаны следующие совместимые проводники:"
    )
    return {
        "scenario": "faq",
        "answer": answer,
        "list": item_list,
        "sources": sources,
        "notice": (
            "Перед применением проверьте совместимость "
            "по инструкции производителя (IFU)."
        ),
    }


def _commercial_faq(products, product_name):
    product, sources = retrieve_product(products, product_name)
    if not product:
        return {
            "scenario": "faq",
            "answer": f"Изделие «{product_name}» не найдено.",
            "sources": [],
        }

    facts = product.get("documented_advantages", [])
    answer = (
        f"Документированные характеристики **{product['product_name']}** "
        f"для коммерческого предложения (только факты из IFU):"
    )
    return {
        "scenario": "faq",
        "answer": answer,
        "list": facts,
        "sources": sources,
        "notice": (
            "Ответ сформирован исключительно на основе документации производителя. "
            "Маркетинговые утверждения без источника не добавляются."
        ),
    }


def rzn_check(products, question):
    repo = RegulatoryRepository(products)
    product_name = _extract_product_name(question, products)

    if not product_name:
        return {
            "scenario": "rzn_check",
            "answer": "Укажите название изделия для проверки регистрации в РЗН.",
            "sources": [],
            "rzn": None,
        }

    result = repo.check(product_name)
    if not result:
        return {
            "scenario": "rzn_check",
            "answer": f"Регистрационные данные для «{product_name}» не найдены.",
            "sources": [],
            "rzn": None,
        }

    answer = (
        f"**{result['product_name']}**\n\n"
        f"- **Производитель:** {result['manufacturer']}\n"
        f"- **Регистрационный номер:** {result['rzn_number']}\n"
        f"- **Статус регистрации:** {result['rzn_status']}"
    )
    return {
        "scenario": "rzn_check",
        "answer": answer,
        "sources": ["Regulatory Repository (демо)"],
        "rzn": result,
    }


def _extract_product_name(question, products):
    question_lower = question.lower()
    for product in products:
        if product["product_name"].lower() in question_lower:
            return product["product_name"]
    return None


def detect_scenario(question):
    q = question.lower()

    if any(
        kw in q
        for kw in ("рзн", "регистрац", "удостоверен", "номер ру", "регистрационный статус")
    ):
        return "rzn_check"
    if any(kw in q for kw in ("сравни", "сравнение", " vs ")):
        if "eluvia" in q and "everflex" in q:
            return "comparison"
    if "проводник" in q or ("совместим" in q and "sterling" in q):
        return "faq"
    if "преимущест" in q or "коммерческ" in q:
        return "faq"
    if "противопоказан" in q:
        return "faq"
    if any(kw in q for kw in ("обзор", "overview", "кратк", "описание", "подготовь")):
        return "overview"
    if any(kw in q for kw in ("размер", "материал", "характеристик", "delivery", "доставк")):
        return "technical_specs"

    return "overview"


SCENARIO_HANDLERS = {
    "technical_specs": technical_specs,
    "comparison": comparison,
    "overview": overview,
    "faq": faq,
    "rzn_check": rzn_check,
}


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/api/products")
def api_products():
    return jsonify(load_content())


@app.route("/api/rag", methods=["POST"])
def api_rag():
    data = request.get_json(silent=True) or {}
    question = (data.get("question") or "").strip()

    if not question:
        return jsonify({"error": "Вопрос не может быть пустым."}), 400

    products = load_content()
    scenario = data.get("scenario") or detect_scenario(question)
    handler = SCENARIO_HANDLERS.get(scenario, overview)
    result = handler(products, question)

    return jsonify(result)


def build_product_context(product):
    return {
        "product_name": product.get("product_name"),
        "manufacturer": product.get("manufacturer"),
        "product_group": product.get("product_group"),
        "description": product.get("description"),
        "application_area": product.get("application_area"),
        "purpose": product.get("purpose"),
        "key_features": product.get("key_features"),
        "documented_advantages": product.get("documented_advantages"),
        "compatible_guidewires": product.get("compatible_guidewires"),
        "source_url": product.get("source_url"),
    }


def build_content_prompt(product, content_type, tone):
    product_data = build_product_context(product)
    content_label = CONTENT_TYPE_LABELS[content_type]
    tone_label = TONE_LABELS[tone]

    system_prompt = (
        "You are a medical device content assistant for MedTech sales and product teams. "
        "Generate text ONLY based on the provided product data from manufacturer documentation. "
        "Rules:\n"
        "- Do NOT invent medical properties, clinical outcomes, or indications not in the data.\n"
        "- Do NOT provide medical advice or treatment recommendations.\n"
        "- If data is insufficient for a section, explicitly state the limitation.\n"
        "- Write in Russian.\n"
        "- Do not add source URL or disclaimer — they will be appended separately."
    )

    user_prompt = (
        f"Content type: {content_label}\n"
        f"Tone: {tone_label}\n\n"
        f"Product data (JSON):\n{json.dumps(product_data, ensure_ascii=False, indent=2)}\n\n"
        f"Generate the requested {content_label.lower()} in {tone_label.lower()} tone."
    )

    return system_prompt, user_prompt


def generate_content_with_openai(product, content_type, tone):
    system_prompt, user_prompt = build_content_prompt(product, content_type, tone)
    client = OpenAI(api_key=OPENAI_API_KEY)

    response = client.chat.completions.create(
        model=OPENAI_MODEL,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
        temperature=0.5,
    )

    generated = response.choices[0].message.content.strip()
    source_url = product.get("source_url", "")

    return (
        f"{generated}\n\n"
        f"Источник: {source_url}\n\n"
        f"{CONTENT_FOOTER_WARNING}"
    )


@app.route("/api/generate-content", methods=["POST"])
def api_generate_content():
    data = request.get_json(silent=True) or {}
    product_name = (data.get("product_name") or "").strip()
    content_type = (data.get("content_type") or "").strip()
    tone = (data.get("tone") or "").strip()

    if not product_name or not content_type or not tone:
        return jsonify({"status": "error", "message": "Missing required fields."}), 400

    if content_type not in CONTENT_TYPE_LABELS:
        return jsonify({"status": "error", "message": "Invalid content_type."}), 400

    if tone not in TONE_LABELS:
        return jsonify({"status": "error", "message": "Invalid tone."}), 400

    if not OPENAI_API_KEY:
        return jsonify({
            "status": "error",
            "message": (
                "OpenAI API key is not configured. "
                "Create .env file based on .env.example."
            ),
        })

    products = load_content()
    product = find_product(products, product_name)
    if not product:
        return jsonify({
            "status": "error",
            "message": f"Product '{product_name}' not found.",
        }), 404

    try:
        generated_text = generate_content_with_openai(product, content_type, tone)
        return jsonify({
            "status": "success",
            "product_name": product_name,
            "content_type": content_type,
            "tone": tone,
            "generated_text": generated_text,
            "source_url": product.get("source_url", ""),
        })
    except Exception as exc:
        return jsonify({"status": "error", "message": str(exc)})


@app.route("/api/filters")
def api_filters():
    products = load_content()
    manufacturers = sorted({p["manufacturer"] for p in products})
    groups = sorted({p["product_group"] for p in products})
    doc_types = sorted({p["document_type"] for p in products})
    return jsonify(
        {
            "manufacturers": manufacturers,
            "product_groups": groups,
            "document_types": doc_types,
        }
    )


if __name__ == "__main__":
    app.run(debug=True, host="127.0.0.1", port=5000)
