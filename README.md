# AI Product Assistant MedTech — MVP RAG

AI Product Assistant MedTech is a prototype RAG assistant for medical devices and consumables.

The project demonstrates:

- product information retrieval;
- compatibility lookup;
- product overview generation;
- product comparison;
- regulatory status check;
- source-based answers from manufacturer documentation.

---

## MVP Features

- Search and filtering
- Product cards
- Mock RAG assistant
- Technical specifications
- Product comparison
- Product overview
- FAQ examples
- Regulatory status check

---

## Demo Scenarios

| # | Scenario | Description |
|---|----------|-------------|
| 1 | 📏 Eluvia Dimensions | Available stent sizes with source reference |
| 2 | 🔗 Sterling PTA Compatibility | Compatible guidewires with IFU verification notice |
| 3 | 📄 Sterling PTA Overview | Purpose, key features, and application area |
| 4 | 💼 Eluvia Advantages | Documented facts for commercial proposals (IFU only) |
| 5 | ⚖️ Compare Eluvia vs EverFlex | Side-by-side comparison table with per-product sources |
| 6 | ⚠️ EverFlex Contraindications | Contraindications with manufacturer document notice |
| 7 | 🏛 Eluvia Regulatory Status | Registration number and status via Regulatory Repository |

---

## Project Structure

```text
medtech_rag_assistant/
├── app.py
├── content.json
├── requirements.txt
├── .env.example
├── .gitignore
├── templates/index.html
├── static/style.css
├── static/script.js
├── README.md
├── LICENSE
└── docs/
```

---

## Local Run

### Prerequisites

- Python 3.10+
- pip

### Install and start

```bash
cd "D:\Work\Intensiv 3.0\Project\medtech_rag_assistant"
pip install -r requirements.txt
python app.py
```

Open in your browser:

```text
http://127.0.0.1:5000
```

---

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/` | Web interface |
| `GET` | `/api/products` | All products from `content.json` |
| `GET` | `/api/filters` | Filter options (manufacturer, group, document type) |
| `POST` | `/api/rag` | RAG assistant query |
| `POST` | `/api/generate-content` | OpenAI content generation |
| `POST` | `/api/publish-vk` | Publish edited content to VK group |

Example RAG request:

```json
{
  "question": "Compare Eluvia and EverFlex."
}
```

---

## Test Data

`content.json` contains three demo products:

| Product | Manufacturer | Type |
|---------|--------------|------|
| Eluvia | Boston Scientific | Drug-eluting stent |
| EverFlex | Medtronic | Self-expanding stent |
| Sterling PTA | Boston Scientific | Balloon catheter |

---

## GitHub Publication

```bash
git init
git add .
git commit -m "Add AI Product Assistant MedTech MVP RAG prototype"
```

Optional — push to remote:

```bash
git branch -M main
git remote add origin <your-repo-url>
git push -u origin main
```

---

## Lesson 02 — Content Generator with OpenAI API

### What was added

- **Content Generator** section on the main page for generating work texts for MedTech managers, product specialists, and sales teams
- `POST /api/generate-content` endpoint powered by OpenAI API
- Product data from `content.json` is passed to the model as context
- Generated text includes source URL and manufacturer document verification notice

### Supported content types

1. Commercial description (`commercial_description`)
2. Catalog description (`catalog_description`)
3. Technical description for physicians (`technical_doctor`)
4. Client email (`client_email`)
5. Social media post (`social_post`)

### Supported tones

1. Expert (`expert`)
2. Business (`business`)
3. Brief (`brief`)
4. Friendly (`friendly`)

### OpenAI API configuration

The API key is stored in a local `.env` file and is **not** published to GitHub.

Create environment from example:

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```

Create `.env` from `.env.example`:

```bash
copy .env.example .env
```

Fill in your credentials:

```env
OPENAI_API_KEY=your_real_key_here
OPENAI_MODEL=gpt-4o-mini
```

### Run

```bash
python app.py
```

Open:

```text
http://127.0.0.1:5000
```

If `.env` is missing or `OPENAI_API_KEY` is not set, the application still runs — Content Generator returns a clear configuration message.

---

## Lesson 03 — VK Publishing Integration

### What was added

- Editable textarea for generated content before publishing
- **Copy** button for generated/edited text
- **Опубликовать в VK** button with explicit user confirmation
- `POST /api/publish-vk` endpoint using VK API `wall.post`
- Success and error status messages after publishing attempt
- Educational disclaimer before VK publishing

### Required environment variables

```env
VK_ACCESS_TOKEN=your_vk_access_token_here
VK_GROUP_ID=your_vk_group_id_here
VK_API_VERSION=5.199
```

### VK configuration

1. Create a VK community (group) for testing.
2. Obtain a community access token with `wall` permission.
3. Add variables to local `.env` (never commit `.env` to GitHub).

Setup example:

```bash
copy .env.example .env
```

Fill in:

```env
OPENAI_API_KEY=...
OPENAI_MODEL=gpt-4o-mini
VK_ACCESS_TOKEN=...
VK_GROUP_ID=...
VK_API_VERSION=5.199
```

### Run locally

```bash
python app.py
```

Open:

```text
http://127.0.0.1:5000
```

### Important notes

- `.env` is not committed to GitHub
- Review generated text and sources before publishing to VK
- If `VK_ACCESS_TOKEN` or `VK_GROUP_ID` is missing, the app still runs and returns a friendly configuration error
- VK token is never exposed in UI, logs, or API error messages

---

## MVP Limitations

- Data is stored in `content.json` (no real PDF documents)
- RAG is rule-based retrieval without LLM or vector database
- Document URLs are placeholders (`example.com`)
- Regulatory check is a mock via `RegulatoryRepository`

---

## Disclaimer

This project is an educational MVP prototype.

It does not provide medical advice and should not be used for clinical decision making.

---

## License

MIT License — see [LICENSE](LICENSE) for details.

Copyright (c) 2026 Alexandr Yatugin
