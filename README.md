# Genetic Counselling Workbench

**Live Demo**: [https://genetic-workbench.streamlit.app](https://genetic-workbench.streamlit.app)

A production-grade web application for genetic counselors featuring AI-powered variant analysis, batch VCF processing, and an intelligent RAG (Retrieval-Augmented Generation) assistant. Built with Python, Streamlit, and integrated with 5 major genomics APIs.

---

## Architecture Overview

```
chatbot-gc-main/
├── app.py                      # Main Streamlit application (1738 lines)
├── core/                       # Core business logic
│   ├── query_router.py        # Intelligent query classification (HGVS/rsID/gene)
│   ├── api_clients.py         # External API integrations
│   └── disease_correlation.py # Disease-gene association logic
├── analysis/                   # Variant analysis pipeline
│   ├── vcf_parser.py          # VCF/VCF.gz file parser
│   ├── variant_analyser.py    # Single variant analysis orchestration
│   └── variant_analysis.py    # Batch variant processing
├── rag/                        # RAG chatbot system
│   ├── chatbot.py             # RAG implementation with domain validation
│   ├── ingest.py              # Document ingestion pipeline
│   ├── vectorstore.py         # ChromaDB vector database interface
│   └── documents.yaml         # Knowledge base source URLs
├── ui/                         # UI components
│   ├── components.py          # Reusable UI widgets
│   ├── layout.py              # Page layout structure
│   └── styling.py             # CSS styling injection
└── data/knowledge_base/        # ChromaDB persistent storage
```

---

## Core Modules

### 1. **Query Router** (`core/query_router.py`)
- **Purpose**: Classifies user input into query types
- **Flow**:
  1. Accepts raw text input (e.g., "NM_000277.2:c.1521_1523del", "rs429358")
  2. Uses regex patterns to detect:
     - **HGVS notation**: `NM_`, `NC_`, `ENST`, with position/change syntax
     - **rsID**: `rs` followed by digits
     - **Gene symbols**: Alphanumeric gene names
  3. Returns query type + normalized format
- **Output**: `{"type": "hgvs", "query": "NM_000277.2:c.1521_1523del"}`

### 2. **API Clients** (`core/api_clients.py`)
Implements REST API integrations with error handling and retry logic:

#### **ClinGen Allele Registry**
- Endpoint: `https://reg.clinicalgenome.org/allele`
- Input: HGVS variant (e.g., `NM_000277.2:c.1521_1523del`)
- Returns: Canonical allele ID, molecular consequence, gene context

#### **MyVariant.info**
- Endpoint: `https://myvariant.info/v1/variant/{hgvs}`
- Input: HGVS or rsID
- Returns: ClinVar data (clinical significance, review status), dbSNP info, CADD scores

#### **Ensembl VEP (Variant Effect Predictor)**
- Endpoint: `https://rest.ensembl.org/vep/human/hgvs/{variant}`
- Input: HGVS notation
- Returns: Transcript consequences, SIFT/PolyPhen predictions, protein impact

#### **ClinVar**
- Endpoint: `https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi`
- Input: Variant query
- Returns: ClinVar variation ID, clinical significance, condition associations

**Error Handling**: All clients implement:
- Rate limit detection (429 errors)
- Retry with exponential backoff
- URL encoding for special characters (e.g., `>`, `*`, parentheses)

### 3. **Variant Analyzer** (`analysis/variant_analyser.py`)

#### **VariantDataFetcher**
Orchestrates parallel API calls:
```python
fetch_variant_data(hgvs_id):
    ├── query_clingen(hgvs_id)      # Canonical allele
    ├── query_myvariant(hgvs_id)    # Population frequency
    ├── query_vep(hgvs_id)          # Functional prediction
    └── query_clinvar(hgvs_id)      # Clinical significance
    
    Returns consolidated JSON with all data sources
```

#### **VariantAnalyzer**
- Processes single variants through full pipeline
- Formats data for Streamlit display (DataFrames, styled cards)
- Handles missing data gracefully (shows "N/A" for unavailable fields)

### 4. **VCF Parser** (`analysis/vcf_parser.py`)
- **Input**: `.vcf` or `.vcf.gz` files
- **Processing**:
  1. Detects file compression (gzip handling)
  2. Skips header lines (`##`)
  3. Parses tab-delimited variant records
  4. Extracts: CHROM, POS, ID (rsID), REF, ALT, QUAL, FILTER, INFO, FORMAT
- **Output**: Pandas DataFrame with structured variant data
- **Privacy**: Strips patient-identifying columns (sample names)

### 5. **RAG Chatbot** (`rag/chatbot.py`)

#### **Architecture**:
```
User Query
    ↓
Domain Validation (genetics keywords only)
    ↓
Vector Search (ChromaDB)
    ↓
Retrieve Top-K Documents (K=5)
    ↓
Context Building (concatenate retrieved docs)
    ↓
Google Gemini API (with context + query)
    ↓
Response
```

#### **Domain Validation**:
```python
is_genetics_related(query):
    Keywords = ["variant", "gene", "mutation", "HGVS", "genetic", 
                "chromosome", "allele", "genotype", "inheritance", ...]
    
    if any(keyword in query.lower()):
        return True
    else:
        return False  # Reject non-genetics queries
```

#### **Vector Store** (`rag/vectorstore.py`):
- **Database**: ChromaDB with persistent storage (`data/knowledge_base/`)
- **Embeddings**: Sentence-Transformers (`all-MiniLM-L6-v2`)
- **Indexing**:
  1. Scrapes genetic counseling articles from `documents.yaml`
  2. Chunks documents into 512-token segments
  3. Generates embeddings
  4. Stores in ChromaDB with metadata (source URL, chunk ID)
- **Retrieval**: Cosine similarity search on query embeddings

---

## Application Flow

### **Tab 1: AI Copilot**
```
User Input
    ↓
Domain Validation Check
    ↓ (Pass)
RAG Chatbot Query
    ↓
Vector Search (5 documents)
    ↓
Gemini API Call (with context)
    ↓
Display Response (chat bubbles with gradient styling)
```

**Features**:
- Chat history persistence (session state)
- Automatic context building from past messages
- Rate limit handling (shows retry message)
- Domain restriction (only genetics queries accepted)

### **Tab 2: Single Variant Analysis**
```
User Input (HGVS or rsID)
    ↓
Query Router Classification
    ↓
Parallel API Calls:
    ├── ClinGen (gene context)
    ├── MyVariant (population data)
    ├── VEP (functional prediction)
    └── ClinVar (clinical significance)
    ↓
Data Consolidation
    ↓
Display Results:
    ├── Clinical Significance Card (color-coded)
    ├── Gene Information Table
    ├── Population Frequency Chart
    ├── Functional Predictions Table
    └── External Links (ClinVar, gnomAD, UCSC)
```

**Sidebar Settings**:
- Display format examples (HGVS, rsID, gene)
- Frequency threshold slider (filters variants by MAF)
- Collapsible by default, only visible in Tab 2

### **Tab 3: VCF Batch Processing**
```
File Upload (.vcf / .vcf.gz / .txt / .doc / .docx / .pdf)
    ↓
VCF Parser (extracts variants)
    ↓
Patient De-identification (strips sample columns)
    ↓
Batch Processing Loop:
    For each variant:
        ├── Convert to HGVS (if rsID)
        ├── Query APIs (same as Tab 2)
        └── Append to results DataFrame
    ↓
Display Summary Table (sortable, filterable)
    ↓
Download as CSV (de-identified)
```

**Privacy Features**:
- Removes patient names from filenames (e.g., `JohnDoe.vcf` → `uploaded_variants.vcf`)
- Strips FORMAT and sample genotype columns
- Only retains: CHROM, POS, ID, REF, ALT, QUAL, FILTER, INFO

---

## Data Flow Diagram

```
┌─────────────────┐
│   User Input    │
└────────┬────────┘
         │
    ┌────▼────┐
    │ Router  │ (Query Classification)
    └────┬────┘
         │
    ┌────▼─────────────────────────┐
    │  Parallel API Orchestration  │
    └────┬─────────────────────────┘
         │
    ┌────▼────┐  ┌────▼────┐  ┌────▼────┐  ┌────▼────┐
    │ ClinGen │  │MyVariant│  │   VEP   │  │ ClinVar │
    └────┬────┘  └────┬────┘  └────┬────┘  └────┬────┘
         │            │            │            │
         └────────────┴─────┬──────┴────────────┘
                            │
                     ┌──────▼──────┐
                     │ Consolidate │
                     └──────┬──────┘
                            │
                     ┌──────▼──────┐
                     │  Display UI │
                     └─────────────┘
```

---

## Features

- **AI Copilot**: RAG-powered chatbot with domain validation for genetics queries only
- **Single Variant Analysis**: HGVS/rsID analysis with ClinGen, MyVariant, VEP, ClinVar integration
- **VCF Batch Processing**: Upload and analyze VCF files (.vcf, .vcf.gz) with automatic patient de-identification


## Technology Stack

| Component | Technology | Purpose |
|-----------|-----------|---------|
| **Frontend** | Streamlit 1.28+ | Interactive web UI with custom CSS |
| **AI Model** | Google Gemini API | LLM for RAG responses |
| **Vector DB** | ChromaDB 0.4.18 | Semantic search for knowledge base |
| **Embeddings** | Sentence-Transformers | Document vectorization |
| **APIs** | ClinGen, MyVariant, VEP, ClinVar | Genomic data sources |
| **File Parsing** | Pandas, gzip | VCF file processing |
| **Deployment** | Streamlit Cloud | Production hosting |
| **Python** | 3.8+ | Core language |




## License

See [LICENSE](LICENSE) file.

---

**Research & Educational Use Only** • Patient Data De-identified


---

<div align="center">
 
