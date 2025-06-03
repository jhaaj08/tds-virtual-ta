# TDS Virtual TA

An intelligent API-powered Teaching Assistant that automatically answers student questions for the **Tools in Data Science (TDS)** course offered by **IIT Madras Online Degree**.

This project was built for the October 2025 TDS Virtual TA assignment.

---

## What It Does

- Accepts a **student question** (with optional image).
- Searches through:
  - **TDS Jan 2025 course content** (as of April 15, 2025)
  - **Discourse forum posts** (from Jan 1 – Apr 14, 2025)
- Uses an **LLM** to generate accurate, context-aware answers.
- Returns:
  - An `answer` string
  - A list of supporting `links` to relevant Discourse posts

---

## Example API Usage

```bash
curl -X POST https://<your-api-url>/api/ \
  -H "Content-Type: application/json" \
  -d '{
    "question": "Should I use gpt-4o-mini or gpt-3.5-turbo?",
    "image": ""
  }'

Expected Response

{
  "answer": "You must use `gpt-3.5-turbo-0125`, even if AI Proxy only supports `gpt-4o-mini`. Use the OpenAI API directly.",
  "links": [
    {
      "url": "https://discourse.onlinedegree.iitm.ac.in/t/ga5-question-8-clarification/155939/4",
      "text": "Use the model that’s mentioned in the question."
    },
    {
      "url": "https://discourse.onlinedegree.iitm.ac.in/t/ga5-question-8-clarification/155939/3",
      "text": "You just have to use a tokenizer to get the number of tokens and multiply by the given rate."
    }
  ]
}


⸻

How to Run Locally

1. Clone the repo

git clone https://github.com/yourusername/tds-virtual-ta.git
cd tds-virtual-ta

2. Install dependencies

pip install -r requirements.txt

3. Set environment variables

Create a .env file:

OPENAI_API_KEY=your-openai-key

4. Run the app

uvicorn main:app --reload


⸻

Project Structure

.
├── api/                    # FastAPI route(s)
├── scraper/                # Discourse scraper script
├── data/                   # Raw + cleaned data
├── models/                 # Embedding + retrieval
├── utils/                  # Helpers (OCR, etc.)
├── main.py                 # App entry point
├── requirements.txt
├── README.md
└── LICENSE


⸻

Deployment

The API is publicly deployed at:

https:///api

Use promptfoo for evaluation:

npx -y promptfoo eval --config project-tds-virtual-ta-promptfoo.yaml


⸻

Bonus Feature

Includes a script to scrape Discourse forum posts from any course and date range:

python scraper/scrape_discourse.py --start 2025-01-01 --end 2025-04-14 --base-url "https://discourse.onlinedegree.iitm.ac.in/c/tds"


⸻

License

MIT License. See LICENSE file.

⸻

👤 Author

Ajit Kumar
IIT Madras 
