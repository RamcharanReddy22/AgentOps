from groq import Groq
from config import GROQ_API_KEY, MODEL, MAX_TOKENS
from rag.vector_store import search_documents

client = Groq(api_key=GROQ_API_KEY)

SYSTEM_PROMPT = (
    "You are an expert market research analyst. "
    "You will be given a query and relevant document excerpts from uploaded reports. "
    "IMPORTANT: Always look through ALL provided document excerpts carefully. "
    "If ANY excerpt contains the answer, use those EXACT figures and cite as 'Source: Uploaded Report'. "
    "Never say data is unavailable if it exists in the excerpts. "
    "Prioritize document data over general knowledge always."
)

def run_researcher(query: str) -> str:
    # Search with more results to catch relevant pages
    doc_results = search_documents(query, n_results=5)
    has_docs = doc_results and doc_results[0] != "No relevant documents found."

    user_content = f"Query: {query}\n\n"

    if has_docs:
        user_content += "=== DOCUMENT EXCERPTS (use these for exact figures) ===\n\n"
        for i, doc in enumerate(doc_results):
            user_content += f"Excerpt {i+1}:\n{doc}\n\n"
        user_content += "=== END OF DOCUMENTS ===\n\n"
        user_content += (
            "Using the above document excerpts, answer the query with exact figures. "
            "Look through ALL excerpts carefully before answering. "
            "Cite exact numbers from the documents."
        )
    else:
        user_content += "No documents uploaded. Use your general knowledge."

    response = client.chat.completions.create(
        model=MODEL,
        max_tokens=MAX_TOKENS,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_content}
        ]
    )
    return response.choices[0].message.content
