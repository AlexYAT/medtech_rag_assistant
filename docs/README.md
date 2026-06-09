# Documentation

Supplementary documentation for **AI Product Assistant MedTech — MVP RAG**.

## Overview

This prototype simulates an intelligent assistant for medical device specialists. It uses mock retrieval from `content.json` instead of real PDF parsing or vector search.

## RAG Scenarios

| Scenario | Handler | Purpose |
|----------|---------|---------|
| `technical_specs` | `technical_specs()` | Material, sizes, delivery system |
| `comparison` | `comparison()` | Side-by-side product comparison |
| `overview` | `overview()` | Product summary for sales and product teams |
| `faq` | `faq()` | Compatibility, contraindications, commercial facts |
| `rzn_check` | `rzn_check()` | Mock regulatory status via `RegulatoryRepository` |

## Data Model

Product records in `content.json` include:

- Core metadata: `product_name`, `manufacturer`, `product_group`, `document_type`
- Technical fields: `material`, `sizes`, `delivery_system`, `application_area`, `coating`
- Extended fields: `compatible_guidewires`, `documented_advantages`, `purpose`, `key_features`
- Regulatory fields: `rzn_number`, `rzn_status`

## Frontend

- Search and filters run entirely in the browser (`static/script.js`)
- RAG queries are sent to `POST /api/rag`
- Responses may include `answer`, `table`, `list`, `notice`, and `sources_by_product`

## Disclaimer

This is an educational MVP. It does not provide medical advice and should not be used for clinical decision making.
