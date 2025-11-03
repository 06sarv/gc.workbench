# Genetic Counselling Workbench

A comprehensive web application for genetic counselors featuring AI-powered variant analysis, batch VCF processing, and an intelligent RAG assistant.

## Features

- **AI Copilot**: RAG-powered chatbot with domain validation
- **Single Variant Analysis**: HGVS/rsID analysis with ClinGen, MyVariant, VEP, ClinVar
- **VCF Batch Processing**: Upload and analyze VCF files with automatic de-identification

## Quick Start

```bash
# Install dependencies
pip install -r requirements.txt

# Set up environment
echo "GEMINI_API_KEY=your_key_here" > .env

# Run application
streamlit run app.py
```

Visit `http://localhost:8501`

## Technology Stack

- Streamlit, Python 3.13+
- Google Gemini AI
- ChromaDB (RAG)
- ClinGen, MyVariant.info, Ensembl VEP APIs

## Documentation

See [TESTING_GUIDE.md](TESTING_GUIDE.md) for comprehensive testing instructions.

## License

See [LICENSE](LICENSE) file.

---

**Research & Educational Use Only** • Patient Data De-identified
