## Order Status Vector API (with optional Gemini)

This is a small demo API that:

- **Creates dummy order data** in memory.
- **Builds a simple vector index** (TF‑IDF + cosine similarity) over the order descriptions.
- **Exposes an HTTP endpoint** to query order status using natural‑language text.
- **Optionally calls Google Gemini** (if configured) to generate a friendly explanation of the status.

### 1. Setup

```bash
cd /home/dev/Azure_learning/Email-Processor-WorkFlow-RAG-api
python -m venv myenv
source myenv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
```

### 2. Configure Gemini (optional but recommended)

Do **not** hard‑code your API key in code. Instead, export it as an environment variable:

```bash
export GEMINI_API_KEY="YOUR_GEMINI_API_KEY_HERE"
```

> Note: Never commit your real key to Git or share it in public places.

If `GEMINI_API_KEY` is not set or `google-generativeai` is not installed, the API will still work; it will just return `gemini_answer: null` in responses.

### 3. Run the API

```bash
uvicorn app:app --reload --host 0.0.0.0 --port 8000
```

The app will be available at `http://localhost:8000`.

Health check:

```bash
curl http://localhost:8000/health
```

### 4. Query order status

Endpoint: `POST /order-status`

Request body:

```json
{
  "query": "What is the status of order ORD-1001 for Alice?"
}
```

Example using `curl`:

```bash
curl -X POST "http://localhost:8000/order-status" \
  -H "Content-Type: application/json" \
  -d '{"query": "What is the status of order 1002 for Bob?"}'
```

Example response (shape):

```json
{
  "query": "What is the status of order 1002 for Bob?",
  "best_match": {
    "order": {
      "order_id": "ORD-1002",
      "customer_name": "Bob Smith",
      "items": ["MacBook Air M3"],
      "status": "Processing",
      "description": "..."
    },
    "score": 0.87
  },
  "top_k": [
    {
      "order": { "...": "..." },
      "score": 0.87
    }
  ],
  "gemini_answer": "Short natural-language explanation here, if Gemini is configured."
}
```

The **vector database** here is an in‑memory TF‑IDF matrix built from the dummy order corpus. You can later replace it with a real vector database (e.g. Pinecone, Chroma, PostgreSQL pgvector) by swapping out the `search_orders` implementation in `app.py`.



