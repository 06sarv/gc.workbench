# Genetic Counselling Workbench

A comprehensive web application for genetic counselors featuring AI-powered variant analysis, batch VCF processing, and an intelligent RAG assistant.

## Features

- **AI Copilot**: RAG-powered chatbot with domain validation for genetics queries only
- **Single Variant Analysis**: HGVS/rsID analysis with ClinGen, MyVariant, VEP, ClinVar integration
- **VCF Batch Processing**: Upload and analyze VCF files (.vcf, .vcf.gz) with automatic patient de-identification

## Quick Start

```bash
# Install dependencies
pip install -r requirements.txt

# Set up environment variable
echo "GEMINI_API_KEY=your_key_here" > .env

# Run application
streamlit run app.py
```

Visit `http://localhost:8501`

## Technology Stack

- **Frontend**: Streamlit with custom professional UI
- **AI**: Google Gemini API
- **RAG**: ChromaDB vector store
- **APIs**: ClinGen Allele Registry, MyVariant.info, Ensembl VEP, ClinVar
- **Python**: 3.8+

## Deployment

### Streamlit Cloud (Recommended)

1. Push code to GitHub
2. Go to [share.streamlit.io](https://share.streamlit.io)
3. Connect your repository
4. Add `GEMINI_API_KEY` in Secrets
5. Deploy!

### Local

```bash
pip install -r requirements.txt
export GEMINI_API_KEY="your_key"
streamlit run app.py
```

## Environment Variables

| Variable | Description | Required |
|----------|-------------|----------|
| `GEMINI_API_KEY` | Google Gemini API key | Yes |

## License

See [LICENSE](LICENSE) file.

---

**Research & Educational Use Only** • Patient Data De-identified
