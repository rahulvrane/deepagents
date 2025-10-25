# Co-Scientist Agent System: Software Requirements & Setup

This document details all software requirements, API keys, and infrastructure needed to implement the Co-Scientist Agent System.

---

## Table of Contents

1. [Python Dependencies](#python-dependencies)
2. [API Keys & External Services](#api-keys--external-services)
3. [Infrastructure Requirements](#infrastructure-requirements)
4. [Development Tools](#development-tools)
5. [Setup Instructions](#setup-instructions)
6. [Cost Estimates](#cost-estimates)

---

## Python Dependencies

### Core Dependencies (Already in DeepAgents)

```toml
[tool.poetry.dependencies]
python = "^3.10"
langchain = ">=1.0.0,<2.0.0"
langchain-core = ">=1.0.0,<2.0.0"
langchain-anthropic = ">=1.0.0,<2.0.0"
langgraph = ">=0.2.0"
```

### NEW: Scientific Computing

```toml
# Data manipulation and analysis
numpy = "^1.24.0"
pandas = "^2.0.0"
scipy = "^1.10.0"

# Statistical analysis
scikit-learn = "^1.3.0"
statsmodels = "^0.14.0"

# Visualization
matplotlib = "^3.7.0"
seaborn = "^0.12.0"
plotly = "^5.14.0"              # Optional: Interactive plots
```

### NEW: Literature Search & PDF Processing

```toml
# PubMed/NCBI integration
biopython = "^1.81"             # BLAST, sequence tools, Entrez utilities
pubmed-parser = "^0.3.0"        # Alternative PubMed parser

# arXiv integration
arxiv = "^2.0.0"                # Official arXiv API wrapper

# Semantic Scholar
# No dedicated library - uses REST API directly via requests

# PDF processing
pymupdf = "^1.23.0"             # PyMuPDF - fast PDF parsing
pdfplumber = "^0.10.0"          # Alternative PDF parser with tables
pypdf2 = "^3.0.0"               # PDF manipulation

# OCR for scanned PDFs (optional)
pytesseract = "^0.3.10"         # Requires tesseract-ocr system package
pillow = "^10.0.0"              # Image processing
```

### NEW: Citation Management

```toml
bibtexparser = "^1.4.0"         # Parse and generate BibTeX
pybtex = "^0.24.0"              # Alternative BibTeX library
citeproc-py = "^0.6.0"          # Citation formatting (APA, MLA, etc.)
```

### NEW: Domain-Specific Tools

#### Bioinformatics
```toml
biopython = "^1.81"             # Already listed above
# For BLAST, need local BLAST+ installation OR use web BLAST
pysam = "^0.21.0"               # SAM/BAM file processing
pyvcf = "^0.6.8"                # VCF file processing (variants)
```

#### Chemistry
```toml
rdkit = "^2023.9.0"             # Cheminformatics (SMILES, molecular modeling)
# Note: RDKit can be tricky to install, use conda recommended
```

#### Physics/Math
```toml
sympy = "^1.12"                 # Symbolic mathematics
numba = "^0.58.0"               # JIT compilation for numerical code
```

### NEW: Sandboxing & Security

```toml
# Option 1: Docker-based (RECOMMENDED)
docker = "^7.0.0"               # Python Docker SDK

# Option 2: Python-based sandboxing (less secure)
RestrictedPython = "^6.2"       # Restricted Python execution

# Option 3: Subprocess isolation
# No additional dependencies - uses built-in subprocess module
```

### Optional: Enhanced Features

```toml
# Jupyter integration for interactive analysis
jupyterlab = "^4.0.0"
ipykernel = "^6.25.0"

# Natural language processing (for text analysis)
nltk = "^3.8.0"
spacy = "^3.7.0"

# Database backends for production
psycopg2-binary = "^2.9.0"      # PostgreSQL
redis = "^5.0.0"                # Redis for caching

# Progress bars and UI
tqdm = "^4.66.0"
rich = "^13.5.0"                # Terminal formatting

# Testing
pytest = "^7.4.0"
pytest-asyncio = "^0.21.0"
pytest-cov = "^4.1.0"
```

---

## API Keys & External Services

### Required for Core Functionality

#### 1. **Anthropic Claude API** (Already Required)
- **Purpose**: LLM for agent reasoning
- **Get Key**: https://console.anthropic.com/
- **Environment Variable**: `ANTHROPIC_API_KEY`
- **Cost**: Pay-per-token (see pricing section)
- **Free Tier**: No free tier, pay-as-you-go

```bash
export ANTHROPIC_API_KEY="sk-ant-..."
```

### Required for Literature Search

#### 2. **NCBI E-utilities API** (PubMed)
- **Purpose**: Search and retrieve biomedical literature
- **Get Key**: https://www.ncbi.nlm.nih.gov/account/
- **Environment Variable**: `NCBI_API_KEY` (optional but recommended)
- **Cost**: **FREE**
- **Rate Limits**:
  - Without key: 3 requests/second
  - With key: 10 requests/second
- **Notes**: API key not strictly required but highly recommended

```bash
export NCBI_API_KEY="your_ncbi_api_key"
export NCBI_EMAIL="your.email@example.com"  # Required for Entrez
```

**How to get:**
1. Create free NCBI account: https://www.ncbi.nlm.nih.gov/account/
2. Go to Settings → API Key Management
3. Create new API key

#### 3. **arXiv API**
- **Purpose**: Search and download preprints
- **Get Key**: **Not required** - completely free and open
- **Cost**: **FREE**
- **Rate Limits**: 1 request every 3 seconds (be respectful)
- **Notes**: No authentication needed

#### 4. **Semantic Scholar API**
- **Purpose**: Cross-disciplinary paper search
- **Get Key**: **Not required** for basic use, recommended for high volume
- **Get Key (Optional)**: https://www.semanticscholar.org/product/api
- **Environment Variable**: `SEMANTIC_SCHOLAR_API_KEY` (optional)
- **Cost**: **FREE**
- **Rate Limits**:
  - Without key: 100 requests/5 minutes
  - With key: Higher limits (varies)
- **Notes**: Works without key for moderate usage

```bash
export SEMANTIC_SCHOLAR_API_KEY="your_s2_api_key"  # Optional
```

### Optional Services

#### 5. **Tavily Search API** (Already used in examples)
- **Purpose**: Web search for general research
- **Get Key**: https://tavily.com/
- **Environment Variable**: `TAVILY_API_KEY`
- **Cost**: Free tier available, then paid
- **Free Tier**: 1,000 requests/month

```bash
export TAVILY_API_KEY="tvly-..."
```

#### 6. **Unpaywall API** (Open Access Papers)
- **Purpose**: Find free full-text PDFs
- **Get Key**: Email address only
- **Environment Variable**: `UNPAYWALL_EMAIL`
- **Cost**: **FREE**
- **Notes**: Just need to provide email

```bash
export UNPAYWALL_EMAIL="your.email@example.com"
```

#### 7. **CrossRef API** (Citation Data)
- **Purpose**: Retrieve citation metadata
- **Get Key**: **Not required** - free and open
- **Cost**: **FREE**
- **Rate Limits**: Be polite (1 request/second recommended)

#### 8. **AlphaFold API** (Protein Structure Prediction)
- **Purpose**: Predict protein 3D structures
- **Access**: Free through Google Cloud or AlphaFold DB
- **Cost**: **FREE** (for AlphaFold DB lookups)
- **Notes**: For predictions, may need Google Cloud account

#### 9. **PubChem API** (Chemical Compounds)
- **Purpose**: Chemical structure and property data
- **Get Key**: **Not required** - free NIH service
- **Cost**: **FREE**

### Infrastructure Services (Production Only)

#### 10. **PostgreSQL** (Long-term Memory)
- **Purpose**: Persistent storage for agent memory
- **Options**:
  - Self-hosted (free)
  - Supabase (free tier available)
  - AWS RDS (paid)
  - Neon (free tier available)
- **Environment Variable**: `DATABASE_URI`

```bash
export DATABASE_URI="postgresql://user:password@localhost:5432/coscientist"
```

#### 11. **Redis** (Caching)
- **Purpose**: Cache search results and computations
- **Options**:
  - Self-hosted (free)
  - Redis Cloud (free tier: 30MB)
  - AWS ElastiCache (paid)
- **Environment Variable**: `REDIS_URL`

```bash
export REDIS_URL="redis://localhost:6379"
```

---

## Infrastructure Requirements

### 1. Python Environment

**Version**: Python 3.10 or higher (3.11 recommended)

```bash
python --version
# Should be 3.10.x or higher
```

### 2. Code Execution Sandbox

For secure Python code execution, choose ONE:

#### Option A: Docker (RECOMMENDED)
- **Purpose**: Isolated, secure code execution
- **Installation**: Install Docker Desktop or Docker Engine
  - macOS: https://docs.docker.com/desktop/install/mac-install/
  - Linux: https://docs.docker.com/engine/install/
  - Windows: https://docs.docker.com/desktop/install/windows-install/

**Verify installation:**
```bash
docker --version
# Docker version 24.0.0 or higher
```

**Test Docker:**
```bash
docker run hello-world
```

#### Option B: RestrictedPython (LESS SECURE)
- **Purpose**: Python-based sandboxing
- **Installation**: `pip install RestrictedPython`
- **Limitations**: Less secure than Docker, not recommended for untrusted code
- **Use case**: Development/testing only

#### Option C: Subprocess with restrictions
- **Purpose**: Basic isolation using subprocess
- **Installation**: Built-in Python module
- **Limitations**: Minimal security, good for trusted environments only

### 3. BLAST+ (Optional - for Bioinformatics)

If using bioinformatics tools:

**Linux:**
```bash
sudo apt-get install ncbi-blast+
```

**macOS:**
```bash
brew install blast
```

**Windows:**
Download from: https://ftp.ncbi.nlm.nih.gov/blast/executables/blast+/LATEST/

**Verify:**
```bash
blastp -version
```

### 4. Tesseract OCR (Optional - for scanned PDFs)

If processing scanned PDFs:

**Linux:**
```bash
sudo apt-get install tesseract-ocr
```

**macOS:**
```bash
brew install tesseract
```

**Windows:**
Download from: https://github.com/UB-Mannheim/tesseract/wiki

**Verify:**
```bash
tesseract --version
```

### 5. LaTeX (Optional - for Scientific Writing)

If generating LaTeX documents:

**Linux:**
```bash
sudo apt-get install texlive-full
```

**macOS:**
```bash
brew install --cask mactex
```

**Windows:**
Install MiKTeX: https://miktex.org/download

---

## Development Tools

### Required

```bash
# Version control
git >= 2.30.0

# Package manager (choose one)
pip >= 23.0.0
poetry >= 1.5.0  # Recommended
uv >= 0.1.0      # Fastest option
```

### Recommended

```bash
# Code formatting
black >= 23.0.0
ruff >= 0.1.0

# Type checking
mypy >= 1.5.0

# Testing
pytest >= 7.4.0
pytest-cov >= 4.1.0
```

---

## Setup Instructions

### 1. Clone Repository

```bash
git clone https://github.com/rahulvrane/deepagents.git
cd deepagents
git checkout claude/customize-ai-agent-system-011CUSAiF45iLE9WLEcVz366
```

### 2. Set Up Python Environment

#### Option A: Using Poetry (Recommended)

```bash
# Install poetry if not already installed
curl -sSL https://install.python-poetry.org | python3 -

# Install dependencies
poetry install

# Activate virtual environment
poetry shell
```

#### Option B: Using pip + venv

```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Linux/macOS:
source venv/bin/activate
# On Windows:
venv\Scripts\activate

# Install dependencies
pip install -e .
pip install -r requirements-dev.txt
```

### 3. Install New Scientific Dependencies

Create or update `requirements-scientific.txt`:

```txt
# Core scientific computing
numpy>=1.24.0
pandas>=2.0.0
scipy>=1.10.0
scikit-learn>=1.3.0
statsmodels>=0.14.0

# Visualization
matplotlib>=3.7.0
seaborn>=0.12.0

# Literature search
biopython>=1.81
arxiv>=2.0.0
pymupdf>=1.23.0
pdfplumber>=0.10.0

# Citation management
bibtexparser>=1.4.0
pybtex>=0.24.0

# Symbolic math
sympy>=1.12

# Sandboxing
docker>=7.0.0

# Optional
jupyterlab>=4.0.0
```

Install:
```bash
pip install -r requirements-scientific.txt
```

**For RDKit (Chemistry):**
```bash
# RDKit is easier to install via conda
conda install -c conda-forge rdkit
```

### 4. Set Up Environment Variables

Create `.env` file in project root:

```bash
# Required
ANTHROPIC_API_KEY=sk-ant-...

# Literature search (recommended)
NCBI_API_KEY=your_ncbi_api_key
NCBI_EMAIL=your.email@example.com

# Optional
SEMANTIC_SCHOLAR_API_KEY=your_s2_key
TAVILY_API_KEY=tvly-...
UNPAYWALL_EMAIL=your.email@example.com

# Production (if using)
DATABASE_URI=postgresql://user:password@localhost:5432/coscientist
REDIS_URL=redis://localhost:6379
```

Load environment variables:
```bash
# Option 1: Use python-dotenv
pip install python-dotenv

# Option 2: Source manually
export $(cat .env | xargs)

# Option 3: Add to shell profile
echo 'export ANTHROPIC_API_KEY=sk-ant-...' >> ~/.bashrc
source ~/.bashrc
```

### 5. Set Up Docker (if using Docker sandbox)

```bash
# Pull Python image for code execution
docker pull python:3.11-slim

# Test Docker access
docker run --rm python:3.11-slim python --version
```

### 6. Verify Installation

```bash
# Run existing tests
pytest tests/

# Test scientific imports
python -c "import numpy, pandas, scipy, sklearn, matplotlib; print('Scientific libs OK')"
python -c "import Bio; print('Biopython OK')"
python -c "import arxiv; print('ArXiv OK')"
python -c "import pymupdf; print('PyMuPDF OK')"
python -c "import bibtexparser; print('BibTeX OK')"
```

### 7. Test API Access

Create `test_apis.py`:

```python
#!/usr/bin/env python3
"""Test API access for Co-Scientist components."""

import os
import requests

def test_anthropic():
    """Test Anthropic API key."""
    key = os.getenv("ANTHROPIC_API_KEY")
    if not key:
        print("❌ ANTHROPIC_API_KEY not set")
        return False
    if not key.startswith("sk-ant-"):
        print("❌ ANTHROPIC_API_KEY invalid format")
        return False
    print("✅ Anthropic API key configured")
    return True

def test_ncbi():
    """Test NCBI E-utilities access."""
    email = os.getenv("NCBI_EMAIL", "test@example.com")
    url = f"https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi"
    params = {
        "db": "pubmed",
        "term": "cancer",
        "retmax": 1,
        "retmode": "json",
        "email": email,
    }
    try:
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        print("✅ NCBI E-utilities accessible")
        return True
    except Exception as e:
        print(f"❌ NCBI E-utilities error: {e}")
        return False

def test_arxiv():
    """Test arXiv API access."""
    url = "http://export.arxiv.org/api/query"
    params = {"search_query": "all:electron", "max_results": 1}
    try:
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        print("✅ arXiv API accessible")
        return True
    except Exception as e:
        print(f"❌ arXiv API error: {e}")
        return False

def test_semantic_scholar():
    """Test Semantic Scholar API access."""
    url = "https://api.semanticscholar.org/graph/v1/paper/search"
    params = {"query": "machine learning", "limit": 1}
    headers = {}
    api_key = os.getenv("SEMANTIC_SCHOLAR_API_KEY")
    if api_key:
        headers["x-api-key"] = api_key
    try:
        response = requests.get(url, params=params, headers=headers, timeout=10)
        response.raise_for_status()
        print("✅ Semantic Scholar API accessible")
        return True
    except Exception as e:
        print(f"❌ Semantic Scholar API error: {e}")
        return False

if __name__ == "__main__":
    print("Testing API access...\n")
    results = [
        test_anthropic(),
        test_ncbi(),
        test_arxiv(),
        test_semantic_scholar(),
    ]
    print(f"\n{'='*50}")
    print(f"Results: {sum(results)}/{len(results)} APIs accessible")
    if all(results):
        print("✅ All required APIs are accessible!")
    else:
        print("⚠️  Some APIs are not accessible")
```

Run:
```bash
python test_apis.py
```

---

## Cost Estimates

### Development Phase

**Required Costs:**
- Anthropic Claude API: ~$20-50/month (depending on usage)
- Total: **$20-50/month**

**Optional/Free:**
- All literature search APIs: FREE
- NCBI/PubMed: FREE
- arXiv: FREE
- Semantic Scholar: FREE
- Development environment: FREE

### Production Phase

**Low Volume (<1000 queries/month):**
- Anthropic Claude API: ~$50-100/month
- Infrastructure (self-hosted): $0
- Total: **$50-100/month**

**Medium Volume (1000-10000 queries/month):**
- Anthropic Claude API: ~$200-500/month
- PostgreSQL (Supabase free tier): $0
- Redis (Redis Cloud free tier): $0
- Total: **$200-500/month**

**High Volume (>10000 queries/month):**
- Anthropic Claude API: ~$1000-5000/month
- PostgreSQL (managed): ~$50/month
- Redis (managed): ~$30/month
- Infrastructure: ~$100/month
- Total: **$1180-5180/month**

### Cost Optimization Tips

1. **Use prompt caching** (already in DeepAgents) - reduces costs by 90% for repeated prompts
2. **Aggressive filesystem use** - offload context to reduce token usage
3. **Subagent delegation** - isolate context, summarize results
4. **Cache literature searches** - avoid redundant API calls
5. **Batch operations** - group similar tasks
6. **Monitor usage** - track costs with Anthropic dashboard

---

## Minimum Viable Setup

To get started with minimal requirements:

### Essential Only

```bash
# Python packages
pip install langchain langchain-anthropic langgraph
pip install numpy pandas matplotlib
pip install biopython arxiv pymupdf bibtexparser

# API Keys
export ANTHROPIC_API_KEY=sk-ant-...
export NCBI_EMAIL=your.email@example.com

# That's it! You can start developing.
```

**What you get:**
- ✅ Literature search (PubMed, arXiv)
- ✅ Basic data analysis
- ✅ Simple visualizations
- ✅ Citation management
- ✅ DeepAgents core features

**What you don't get:**
- ❌ Secure code execution (no Docker)
- ❌ Advanced chemistry tools (no RDKit)
- ❌ Production database (no PostgreSQL)
- ❌ Caching (no Redis)

### Recommended Setup

Add for better experience:

```bash
# Additional packages
pip install scipy scikit-learn seaborn docker

# Set up Docker
docker pull python:3.11-slim

# Add more APIs
export SEMANTIC_SCHOLAR_API_KEY=your_key
```

**What you get:**
- ✅ Everything in essential
- ✅ Secure code execution
- ✅ Advanced statistics
- ✅ Better visualizations
- ✅ Faster literature search

---

## Quick Start Checklist

- [ ] Python 3.10+ installed
- [ ] Git installed
- [ ] Repository cloned
- [ ] Virtual environment created
- [ ] Core dependencies installed (`langchain`, `langgraph`, etc.)
- [ ] Scientific dependencies installed (`numpy`, `pandas`, etc.)
- [ ] Anthropic API key obtained and set
- [ ] NCBI email configured
- [ ] Optional: Docker installed
- [ ] Optional: Additional API keys configured
- [ ] Tests passing
- [ ] API access verified

---

## Troubleshooting

### Common Issues

**1. RDKit installation fails**
```bash
# Use conda instead of pip
conda install -c conda-forge rdkit
```

**2. PyMuPDF installation fails**
```bash
# Try pre-built wheel
pip install --upgrade pip
pip install pymupdf
```

**3. Docker permission denied (Linux)**
```bash
sudo usermod -aG docker $USER
# Log out and back in
```

**4. NCBI API rate limiting**
```bash
# Get API key for higher limits
# https://www.ncbi.nlm.nih.gov/account/
```

**5. ImportError for scientific packages**
```bash
# Reinstall in virtual environment
pip install --force-reinstall numpy pandas scipy
```

---

## Next Steps

Once setup is complete:

1. ✅ Verify all APIs work with `test_apis.py`
2. ✅ Run existing DeepAgents tests: `pytest tests/`
3. ✅ Review `IMPLEMENTATION_PLAN.md` for development roadmap
4. ✅ Start implementing Phase 1: Literature Search Middleware

---

## Summary

### Absolutely Required
- **Python 3.10+**
- **Anthropic API key** ($20-50/month)
- **NCBI email** (free)
- **Core packages**: numpy, pandas, matplotlib, biopython, arxiv

### Highly Recommended
- **Docker** (for secure code execution)
- **NCBI API key** (free, higher rate limits)
- **Additional packages**: scipy, scikit-learn, seaborn

### Optional
- **Semantic Scholar API key** (free)
- **RDKit** (for chemistry)
- **PostgreSQL** (production memory)
- **Redis** (caching)
- **BLAST+** (bioinformatics)
- **LaTeX** (document generation)

### Total Minimum Cost
**$20-50/month** for Anthropic API only
Everything else can be FREE!
