# 🇮🇳 GovEase — Your Rights, One Search Away

> India has 700+ government schemes — scholarships, pensions, housing loans, crop insurance. Most go unclaimed because people don't know they qualify. **GovEase fixes that.**

🔗 **Live Demo:** [http://govease-sankar.s3-website-us-east-1.amazonaws.com](http://govease-sankar.s3-website-us-east-1.amazonaws.com)

---

## The Problem

Every year, lakhs of crores in government welfare funds go unclaimed. A farmer in Tamil Nadu doesn't know about PM-KISAN. A first-generation college student misses a full-ride scholarship. A senior citizen skips a pension they're entitled to.

The information exists — scattered across hundreds of government portals, buried in PDFs, written in bureaucratic language. **Nobody has time to search through all of them.**

## The Solution

GovEase asks you 7 simple questions — age, gender, income, state, category, occupation, and education — and instantly matches you with every government scheme you're eligible for.

No signup. No data stored. Just results.

### How it works

1. **You fill a short profile** — takes 30 seconds
2. **AI scans 47 high-impact schemes** — covering education, health, agriculture, employment, housing, women & child welfare, SC/ST/OBC welfare, and senior citizens
3. **You get personalized results** — ranked by relevance, with benefits, required documents, and direct apply links
4. **AI summary** — Bedrock (Amazon Nova Lite) writes a plain-English recommendation of what to apply for first

---

## Architecture

```
┌─────────────┐     ┌───────────────┐     ┌──────────────┐     ┌───────────┐
│   Frontend   │────▶│  API Gateway   │────▶│    Lambda     │────▶│ DynamoDB  │
│  (S3 static) │     │  REST POST     │     │  govease-     │     │ 47 schemes│
│              │◀────│  /v1/match     │◀────│  match        │     │           │
└─────────────┘     └───────────────┘     │              │────▶│ Bedrock   │
                                           │              │◀────│ Nova Lite │
                                           └──────────────┘     └───────────┘

```

| Layer | Service | Purpose |
| --- | --- | --- |
| **Frontend** | Amazon S3 (Static Website Hosting) | Dark tricolor UI — form + results display |
| **API** | Amazon API Gateway (REST) | POST /v1/match — accepts user profile |
| **Backend** | AWS Lambda (Python 3.12) | Eligibility filtering + AI summary generation |
| **Database** | Amazon DynamoDB | 47 government schemes with eligibility criteria |
| **AI** | Amazon Bedrock (Nova Lite v1) | Natural language recommendation summary |

---

## Tech Stack

- **Frontend:** Vanilla HTML/CSS/JS — Space Grotesk + DM Sans typography, dark theme with India tricolor accents
- **Backend:** Python 3.12 on AWS Lambda
- **AI Model:** Amazon Nova Lite v1 via Bedrock
- **Database:** DynamoDB (on-demand, pay-per-request)
- **Hosting:** S3 static website hosting
- **API:** REST API via API Gateway with Lambda proxy integration
- **No frameworks. No npm. No build step.** One HTML file, one Lambda function, one DynamoDB table.

---

## Scheme Coverage

**47 schemes** across **10 categories:**

| Category | Count | Examples |
| --- | --- | --- |
| Education | 12 | PM Vidyalaxmi, Post Matric Scholarship SC, CSSS, NMMSS |
| Health | 6 | Ayushman Bharat (PMJAY), JSY, PMSMA |
| Agriculture | 6 | PM-KISAN, PMFBY, KCC, Soil Health Card |
| Women & Child | 5 | Sukanya Samriddhi, PMMVY, Beti Bachao Beti Padhao |
| Employment | 5 | PMKVY, MUDRA, PMEGP, MGNREGA |
| Housing | 4 | PMAY-Urban, PMAY-Gramin |
| SC/ST/OBC Welfare | 4 | Stand Up India, VCF-SC |
| Senior Citizen | 3 | IGNOAPS, PMVVY |
| Finance | 1 | PM Jan Dhan Yojana |
| Rural Development | 1 | DDU-GKY |

Covers **44 central** + **3 state-specific** (Karnataka, Madhya Pradesh, Tamil Nadu) schemes.

---

## Project Structure

```
govease/
├── index.html                  # Frontend — single-file dark tricolor UI
├── govease_schemes.json        # 47 government schemes dataset
├── seed_dynamodb.py            # Script to load schemes into DynamoDB
├── lambda_function.py          # Lambda backend — matching + Bedrock AI
└── README.md

```

---

## Run Locally

**Prerequisites:** AWS CLI configured, Python 3.12+, boto3

```bash
# 1. Clone
git clone https://github.com/Sankar2316/govease.git
cd govease

# 2. Create DynamoDB table
aws dynamodb create-table \
  --table-name GovEase-Schemes \
  --attribute-definitions AttributeName=scheme_id,AttributeType=S \
  --key-schema AttributeName=scheme_id,KeyType=HASH \
  --billing-mode PAY_PER_REQUEST \
  --region us-east-1

# 3. Seed data
python seed_dynamodb.py

# 4. Open frontend
open index.html

```

---

## What I Learned

- First time using **Amazon Bedrock** for AI-powered matching and natural language summaries
- Built a complete **serverless full-stack app** — zero servers, zero cost when idle
- Learned how **DynamoDB scan + filter** works at scale with batch operations
- Understood **API Gateway + Lambda proxy integration** end-to-end
- Designed a **dark-theme UI with India tricolor identity** from scratch

---

## What's Next

- [x] Add more schemes (state-specific schemes for all 28 states)
- [x] Hindi / Tamil / regional language support
- [x] WhatsApp chatbot integration for rural users
- [x] Document checklist generator per scheme
- [x] Deadline alerts and application tracking

---

## Hackathon

**First Commit** — Event 01 of the Bharat Builds TourWeMakeDevs × AWS · September 17–20, 2026Track: **Ship It** (deployed on AWS with a live URL)

---

Built by **Sankar** · Team CloudNova
