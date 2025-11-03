from typing import List, Dict
from rag.vectorstore import GenomicsVectorStore
import os

INTRO_PROMPT = """You are a genomics-savvy assistant for genetic counselors.
Use retrieved evidence snippets to craft clear, clinically responsible answers.
Always cite sources by their `source_id`. Distinguish between variant interpretation guidance and general counseling info."""

GENETICS_KEYWORDS = [
    # Variant identifiers
    "variant", "mutation", "snp", "indel", "deletion", "insertion", "duplication",
    "rs", "hgvs", "clingen", "clinvar", "dbsnp",
    # Genes and genomics
    "gene", "chromosome", "allele", "genotype", "phenotype", "genome", "exon", "intron",
    "transcript", "protein", "amino acid", "nucleotide", "codon",
    # Medical genetics
    "pathogenic", "benign", "vus", "significance", "inheritance", "hereditary",
    "carrier", "penetrance", "expressivity", "genetic counseling",
    # Specific conditions/genes (examples)
    "brca", "cf", "sickle cell", "hemophilia", "huntington", "duchenne",
    # Analysis terms
    "frequency", "gnomad", "exac", "population", "consequence", "impact",
    "sift", "polyphen", "cadd", "revel", "vep", "annotation"
]

class RAGChatbot:
    def __init__(self, llm_provider="gemini"):
        self.vstore = GenomicsVectorStore()
        self.llm_provider = llm_provider
        self.gemini_client = None
    
    def is_genetics_related(self, query: str) -> bool:
        """Check if query is related to genetics/genomics domain."""
        query_lower = query.lower()
        
        # Check for genetics keywords
        keyword_match = any(keyword in query_lower for keyword in GENETICS_KEYWORDS)
        
        # Check for HGVS or rsID patterns
        hgvs_pattern = any(pattern in query_lower for pattern in ["nm_", "nc_", "ng_", "np_", "p.", "c.", "g."])
        rsid_pattern = "rs" in query_lower and any(char.isdigit() for char in query)
        
        return keyword_match or hgvs_pattern or rsid_pattern

    def _get_gemini_client(self):
        if self.gemini_client is None:
            import google.generativeai as genai
            api_key = os.getenv("GEMINI_API_KEY")
            if not api_key:
                raise ValueError("GEMINI_API_KEY environment variable not set")
            genai.configure(api_key=api_key)
            self.gemini_client = genai
        return self.gemini_client

    def build_prompt(self, query: str, retrieved_docs: List[Dict]):
        context = "\n\n---\n\n".join(
            f"[{doc['metadata'].get('source_id', 'unknown')}]\n{doc['content']}"
            for doc in retrieved_docs
        )
        return f"""{INTRO_PROMPT}

User question: {query}

Retrieved context:
{context}

Answer guidelines:
- Start with a short summary.
- Cite sources inline using [source_id].
- If the question is outside provided context, acknowledge and offer general guidance."""

    def chat(self, query: str):
        # Domain validation check
        if not self.is_genetics_related(query):
            return (
                "⚠️ **Out of Scope Query Detected**\n\n"
                "I'm specifically designed to assist genetic counselors with genetics and genomics-related questions. "
                "Your query doesn't appear to be related to:\n"
                "- Genetic variants (HGVS notation, rsIDs, SNPs)\n"
                "- Genes and chromosomes\n"
                "- Clinical significance and disease associations\n"
                "- Genetic counseling topics\n\n"
                "Please ask questions related to genetic variants, inheritance patterns, clinical genomics, "
                "or genetic counseling practices.",
                []
            )
        
        docs = self.vstore.similarity_search(query, k=6)
        prompt = self.build_prompt(query, docs)

        try:
            if self.llm_provider == "gemini":
                genai = self._get_gemini_client()
                model = genai.GenerativeModel('gemini-2.5-flash')
                response = model.generate_content(prompt)
                answer = response.text
            elif self.llm_provider == "openai":
                from openai import OpenAI
                client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
                response = client.chat.completions.create(
                    model="gpt-4o-mini",
                    messages=[
                        {"role": "system", "content": "You are a clinical genomics assistant."},
                        {"role": "user", "content": prompt}
                    ],
                    temperature=0.2,
                    max_tokens=800
                )
                answer = response.choices[0].message.content
            else:
                raise NotImplementedError("Only Gemini and OpenAI are supported.")
        except Exception as e:
            error_msg = str(e)
            if "429" in error_msg or "ResourceExhausted" in error_msg:
                return (
                    "⚠️ **Rate Limit Exceeded**\n\n"
                    "The AI service is currently experiencing high demand. Please:\n"
                    "1. Wait 30-60 seconds before trying again\n"
                    "2. Try a more specific query to reduce processing time\n"
                    "3. If the issue persists, check your API quota at the provider's console\n\n"
                    f"Technical details: {error_msg}",
                    docs
                )
            raise

        return answer, docs
