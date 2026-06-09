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
