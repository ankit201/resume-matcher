# 🏗️ System Architecture

## High-Level Architecture

```
┌─────────────────────────────────────────────────────────────────────────┐
│                         PRESENTATION LAYER                               │
│                                                                          │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐│
│  │  Live Demo   │  │  Executive   │  │    Bias      │  │    Batch     ││
│  │  (Single     │  │  Dashboard   │  │  Analysis    │  │  Processing  ││
│  │  Resume)     │  │  (5 Views)   │  │  (Fairness)  │  │  (Bulk)      ││
│  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘│
│         │                 │                  │                 │        │
│         └─────────────────┴──────────────────┴─────────────────┘        │
│                                  │                                       │
│                            Streamlit UI                                  │
└──────────────────────────────────┬───────────────────────────────────────┘
                                   │
                                   │ HTTP/REST
                                   │
┌──────────────────────────────────▼───────────────────────────────────────┐
│                        INTELLIGENCE LAYER                                 │
│                                                                          │
│  ┌────────────────────────────────────────────────────────────────────┐ │
│  │                      Orchestration                                  │ │
│  │  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐            │ │
│  │  │  Matcher     │  │   Scoring    │  │   Bias       │            │ │
│  │  │  (Main)      │◄─┤   Engine     │◄─┤   Detector   │            │ │
│  │  └──────────────┘  └──────────────┘  └──────────────┘            │ │
│  └────────────────────────────────────────────────────────────────────┘ │
│                                  │                                       │
│  ┌────────────────────────────────────────────────────────────────────┐ │
│  │                     Multi-LLM System                                │ │
│  │  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐            │ │
│  │  │   OpenAI     │  │   Gemini     │  │  Anthropic   │            │ │
│  │  │   GPT-4      │  │  2.0 Flash   │  │  Claude 3.5  │            │ │
│  │  │              │  │              │  │              │            │ │
│  │  │  (Matching)  │  │  (Parsing)   │  │  (Optional)  │            │ │
│  │  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘            │ │
│  │         │                 │                  │                     │ │
│  │         └─────────────────┴──────────────────┘                     │ │
│  │                           │                                         │ │
│  │                    LLM Factory                                      │ │
│  │                  (Adapter Pattern)                                  │ │
│  └────────────────────────────────────────────────────────────────────┘ │
│                                  │                                       │
│  ┌────────────────────────────────────────────────────────────────────┐ │
│  │                    AI/ML Components                                 │ │
│  │  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐            │ │
│  │  │  Semantic    │  │   LLM Deep   │  │  Analytics   │            │ │
│  │  │  Matcher     │  │   Matcher    │  │  & ROI       │            │ │
│  │  │              │  │              │  │              │            │ │
│  │  │ (Embeddings) │  │ (5-Dim)      │  │ (Dashboards) │            │ │
│  │  └──────────────┘  └──────────────┘  └──────────────┘            │ │
│  └────────────────────────────────────────────────────────────────────┘ │
└──────────────────────────────────────┬───────────────────────────────────┘
                                       │
┌──────────────────────────────────────▼───────────────────────────────────┐
│                           DATA LAYER                                      │
│                                                                          │
│  ┌────────────────────────────────────────────────────────────────────┐ │
│  │                       Parsers                                       │ │
│  │  ┌──────────────┐           ┌──────────────┐                      │ │
│  │  │   Resume     │           │  Job Desc    │                      │ │
│  │  │   Parser     │           │   Parser     │                      │ │
│  │  │              │           │              │                      │ │
│  │  │ (Gemini PDF) │           │ (LLM-based)  │                      │ │
│  │  └──────────────┘           └──────────────┘                      │ │
│  └────────────────────────────────────────────────────────────────────┘ │
│                                  │                                       │
│  ┌────────────────────────────────────────────────────────────────────┐ │
│  │                    Data Models                                      │ │
│  │  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐            │ │
│  │  │  Parsed      │  │  Match       │  │  Bias        │            │ │
│  │  │  Resume      │  │  Result      │  │  Flag        │            │ │
│  │  │              │  │              │  │              │            │ │
│  │  │ (Pydantic)   │  │ (Pydantic)   │  │ (Pydantic)   │            │ │
│  │  └──────────────┘  └──────────────┘  └──────────────┘            │ │
│  └────────────────────────────────────────────────────────────────────┘ │
│                                  │                                       │
│  ┌────────────────────────────────────────────────────────────────────┐ │
│  │                   Configuration                                     │ │
│  │  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐            │ │
│  │  │  Settings    │  │  Environment │  │  YAML        │            │ │
│  │  │  (Pydantic)  │  │  (.env)      │  │  Config      │            │ │
│  │  └──────────────┘  └──────────────┘  └──────────────┘            │ │
│  └────────────────────────────────────────────────────────────────────┘ │
└───────────────────────────────────────────────────────────────────────────┘
```

---

## Component Details

### 1. Presentation Layer (Streamlit UI)

```
┌─────────────────────────────────────────┐
│          app.py (Main)                  │
│  - Landing page                         │
│  - Navigation sidebar                   │
│  - System status                        │
│  - Quick stats                          │
└────────────┬────────────────────────────┘
             │
    ┌────────┴────────┬─────────┬─────────┐
    │                 │         │         │
┌───▼────┐    ┌───────▼──┐  ┌──▼──────┐ ┌▼────────┐
│ Live   │    │Executive │  │  Bias   │ │ Batch   │
│ Demo   │    │Dashboard │  │Analysis │ │Process  │
└────────┘    └──────────┘  └─────────┘ └─────────┘
```

**Responsibilities:**
- User interface and interaction
- File upload and display
- Real-time progress feedback
- Results visualization
- Export functionality

---

### 2. Intelligence Layer

#### 2.1 Multi-LLM System (Factory Pattern)

```
┌─────────────────────────────────────────┐
│        LLMFactory (factory.py)          │
│  - create_adapter(provider: str)        │
│  - get_default_adapter()                │
│  - get_parsing_adapter()                │
└────────────┬────────────────────────────┘
             │
    ┌────────┴─────────┬──────────────┐
    │                  │              │
┌───▼────────────┐ ┌──▼───────────┐ ┌▼──────────────┐
│ OpenAI Adapter │ │Gemini Adapter│ │Anthropic      │
│ (openai_...)   │ │(gemini_...)  │ │Adapter        │
│                │ │              │ │(anthropic_...)│
│ GPT-4 Turbo    │ │2.0 Flash Exp │ │Claude 3.5     │
│ - Matching     │ │- PDF Parsing │ │- Optional     │
│ - Deep Analysis│ │- Structuring │ │- Comparison   │
└────────────────┘ └──────────────┘ └───────────────┘
         │                 │                │
         └─────────────────┴────────────────┘
                          │
                ┌─────────▼──────────┐
                │  BaseLLMAdapter    │
                │  (base.py)         │
                │                    │
                │  - generate()      │
                │  - structured()    │
                │  - cost tracking   │
                │  - retry logic     │
                └────────────────────┘
```

**Key Features:**
- Unified interface across all LLMs
- Automatic retry with exponential backoff
- Token counting and cost tracking
- Structured output with JSON mode
- Easy to add new LLM providers

#### 2.2 Matching Pipeline

```
┌─────────────────────────────────────────────────────────┐
│           ResumeMatcher (matcher.py)                    │
│                Main Orchestrator                        │
└────────────┬────────────────────────────────────────────┘
             │
             ▼
┌─────────────────────────────────────────────────────────┐
│        ScoringEngine (scoring_engine.py)                │
│              Pipeline Orchestration                     │
└────────┬────────────────────────────────────────────────┘
         │
         ├──► 1. Parse Resume (ResumeParser)
         │       └─► Gemini Native PDF Upload
         │
         ├──► 2. Parse Job Description (JobDescriptionParser)
         │       └─► LLM Structured Extraction
         │
         ├──► 3. Semantic Filtering (SemanticMatcher)
         │       ├─► Generate embeddings
         │       ├─► Compute similarity
         │       └─► Filter candidates (threshold: 0.7)
         │
         ├──► 4. Deep LLM Analysis (LLMMatcher)
         │       ├─► Technical Skills (30%)
         │       ├─► Experience (30%)
         │       ├─► Education (15%)
         │       ├─► Cultural Fit (15%)
         │       └─► Growth Potential (10%)
         │
         ├──► 5. Bias Detection (BiasDetector)
         │       ├─► Age indicators
         │       ├─► Gender markers
         │       ├─► Ethnic identifiers
         │       ├─► Disability references
         │       ├─► Family status
         │       └─► Religious affiliations
         │
         └──► 6. Final Scoring & Recommendation
                ├─► Weighted combination
                ├─► Confidence score
                └─► Recommendation level
```

#### 2.3 Five-Dimensional Analysis

```
┌─────────────────────────────────────────┐
│    LLMMatcher (llm_matcher.py)          │
│      5-Dimensional Evaluation           │
└────────────┬────────────────────────────┘
             │
    ┌────────┼────────┬─────────┬─────────┐
    │        │        │         │         │
┌───▼────┐ ┌▼─────┐ ┌▼──────┐ ┌▼──────┐ ┌▼────────┐
│Tech    │ │Exper │ │Educ   │ │Culture│ │Growth   │
│Skills  │ │ience │ │ation  │ │Fit    │ │Potential│
│        │ │      │ │       │ │       │ │         │
│ 30%    │ │ 30%  │ │ 15%   │ │ 15%   │ │ 10%     │
└────────┘ └──────┘ └───────┘ └───────┘ └─────────┘

Each dimension returns:
┌─────────────────────────────┐
│ ScoreDimension              │
│ - score: float (0-1)        │
│ - weight: float             │
│ - reasoning: str            │
│ - evidence: List[str]       │
│ - gaps: List[str]           │
│ - recommendations: List[str]│
└─────────────────────────────┘
```

---

### 3. Data Layer

#### 3.1 Parsers (Gemini Native PDF)

```
┌──────────────────────────────────────────┐
│    ResumeParser (parsers.py)             │
└────────────┬─────────────────────────────┘
             │
   ┌─────────┴──────────┐
   │                    │
┌──▼──────────────┐  ┌──▼──────────────┐
│  PDF Parser     │  │ DOCX/TXT Parser │
│  (Gemini)       │  │ (Text extract)  │
│                 │  │                 │
│ 1. Upload PDF   │  │ 1. Read text    │
│ 2. Gemini       │  │ 2. Send to LLM  │
│    processes    │  │ 3. Structure    │
│ 3. Returns      │  │                 │
│    structured   │  │                 │
└─────────────────┘  └─────────────────┘
         │                    │
         └────────┬───────────┘
                  │
       ┌──────────▼──────────┐
       │   ParsedResume      │
       │   (Pydantic Model)  │
       │                     │
       │ - contact_info      │
       │ - summary           │
       │ - education         │
       │ - work_experience   │
       │ - skills            │
       │ - certifications    │
       │ - languages         │
       │ - total_exp_years   │
       │ - metadata          │
       └─────────────────────┘
```

**Gemini Native PDF Advantages:**
- 95% accuracy vs 70-80% with text extraction
- Preserves formatting and structure
- Understands tables and columns
- Handles visual elements
- No preprocessing needed

#### 3.2 Data Models (Pydantic v2)

```
models.py
│
├── ParsedResume
│   ├── ContactInfo
│   ├── Education[]
│   ├── WorkExperience[]
│   ├── Certification[]
│   └── Skills[]
│
├── ParsedJobDescription
│   ├── JobRequirement[]
│   └── ExperienceLevel (Enum)
│
├── MatchResult
│   ├── ScoreDimension[]
│   ├── SkillMatch[]
│   └── BiasFlag[]
│
└── Validation
    ├── Field validators
    ├── Type checking
    └── Business rules
```

---

## Design Patterns Used

### 1. Factory Pattern (LLM Adapters)

```python
# Creation
adapter = LLMFactory.create_adapter("openai")  # Returns OpenAIAdapter
adapter = LLMFactory.create_adapter("gemini")  # Returns GeminiAdapter

# Usage - same interface for all
response = adapter.generate(prompt="...", system_prompt="...")
```

**Benefits:**
- Easy to add new LLM providers
- Centralized configuration
- Consistent interface
- Testability

### 2. Strategy Pattern (Scoring)

```python
# Configurable weights (must sum to 1.0)
weights = {
    "technical_skills": 0.30,
    "experience": 0.30,
    "education": 0.15,
    "cultural_fit": 0.15,
    "growth_potential": 0.10
}

# Different strategies for different roles
senior_engineer_weights = {...}
junior_engineer_weights = {...}
```

**Benefits:**
- Flexible scoring based on role
- Easy A/B testing
- Customizable per client
- Validated configuration

### 3. Repository Pattern (Data Access)

```python
# Abstraction over data storage
class MatchRepository:
    def save_result(self, result: MatchResult) -> str
    def get_result(self, id: str) -> MatchResult
    def list_results(self, filters: Dict) -> List[MatchResult]
```

**Benefits:**
- Easy to switch storage (file, DB, S3)
- Testability with mocks
- Separation of concerns

---

## Data Flow

### Single Resume Matching

```
1. User uploads PDF
   │
   ▼
2. ResumeParser.parse_file()
   ├─► Upload to Gemini
   └─► Extract structured data → ParsedResume
   │
   ▼
3. User enters Job Description
   │
   ▼
4. JobDescriptionParser.parse_text()
   └─► LLM extraction → ParsedJobDescription
   │
   ▼
5. ScoringEngine.score_candidate()
   │
   ├─► SemanticMatcher.compute_similarity()
   │   └─► Embeddings + Cosine similarity → 0.75
   │
   ├─► LLMMatcher.evaluate_match()
   │   ├─► Dimension 1: Technical Skills → 0.85
   │   ├─► Dimension 2: Experience → 0.78
   │   ├─► Dimension 3: Education → 0.90
   │   ├─► Dimension 4: Cultural Fit → 0.70
   │   └─► Dimension 5: Growth → 0.82
   │   └─► Weighted avg → 0.81
   │
   ├─► BiasDetector.detect_bias()
   │   └─► 2 flags detected (age, gender)
   │
   └─► Final MatchResult
       ├─► overall_score: 0.81
       ├─► recommendation: "good_match"
       ├─► confidence: 0.89
       └─► bias_detected: True
   │
   ▼
6. Display results in UI
   ├─► Score visualization
   ├─► Dimensional breakdown
   ├─► Skills analysis
   ├─► Bias flags
   └─► Export options
```

### Batch Processing

```
1. Upload N resumes + 1 JD
   │
   ▼
2. For each resume:
   ├─► Parse with Gemini
   ├─► Match against JD
   ├─► Detect bias
   └─► Store result
   │
   ▼
3. Aggregate results
   ├─► Sort by score
   ├─► Apply threshold filter
   └─► Generate statistics
   │
   ▼
4. Display ranked results
   ├─► Top N candidates
   ├─► Score distribution
   ├─► Comparison table
   └─► Export options
```

---

## Scalability Considerations

### Current Architecture
- **Single resume:** ~10-12 seconds
- **Batch (50 resumes):** ~10-15 minutes
- **Cost:** $0.12-0.18 per resume

### Optimization Strategies

```
┌─────────────────────────────────────┐
│     Scaling Approaches              │
├─────────────────────────────────────┤
│ 1. Async Processing                 │
│    - Python asyncio                 │
│    - Concurrent LLM calls           │
│    - 3-5x faster                    │
│                                     │
│ 2. Caching                          │
│    - Cache embeddings               │
│    - Cache JD parsing               │
│    - Redis/Memcached                │
│                                     │
│ 3. Queue System                     │
│    - Celery + RabbitMQ              │
│    - Background workers             │
│    - Progress tracking              │
│                                     │
│ 4. Database                         │
│    - PostgreSQL/MongoDB             │
│    - Vector store (Pinecone)        │
│    - Historical analysis            │
│                                     │
│ 5. Kubernetes                       │
│    - Horizontal scaling             │
│    - Load balancing                 │
│    - Auto-scaling                   │
└─────────────────────────────────────┘
```

---

## Security & Compliance

### Data Protection

```
┌──────────────────────────────────────┐
│      Security Layers                 │
├──────────────────────────────────────┤
│ 1. API Key Management                │
│    - Environment variables           │
│    - Never committed to git          │
│    - Rotation policy                 │
│                                      │
│ 2. Data Encryption                   │
│    - At rest: AES-256                │
│    - In transit: TLS 1.3             │
│    - Key management: Vault           │
│                                      │
│ 3. PII Protection                    │
│    - Detect sensitive data           │
│    - Anonymization option            │
│    - GDPR compliance                 │
│                                      │
│ 4. Audit Trail                       │
│    - Log all decisions               │
│    - Immutable records               │
│    - Compliance reporting            │
│                                      │
│ 5. Access Control                    │
│    - Role-based access (RBAC)        │
│    - Authentication required         │
│    - Authorization checks            │
└──────────────────────────────────────┘
```

---

## Monitoring & Observability

```
┌────────────────────────────────────────┐
│         Monitoring Stack               │
├────────────────────────────────────────┤
│ Application Metrics                    │
│ ├─► Requests/second                    │
│ ├─► Response time (p50, p95, p99)      │
│ ├─► Error rate                         │
│ └─► Success rate                       │
│                                        │
│ LLM Metrics                            │
│ ├─► API call count                     │
│ ├─► Token usage                        │
│ ├─► Cost tracking                      │
│ └─► Latency by provider                │
│                                        │
│ Business Metrics                       │
│ ├─► Resumes processed                  │
│ ├─► Match score distribution           │
│ ├─► Bias flags detected                │
│ └─► Time to shortlist                  │
│                                        │
│ Tools (Future)                         │
│ ├─► Prometheus (metrics)               │
│ ├─► Grafana (dashboards)               │
│ ├─► Sentry (error tracking)            │
│ └─► DataDog (APM)                      │
└────────────────────────────────────────┘
```

---

## Testing Strategy

```
┌─────────────────────────────────────┐
│          Test Pyramid               │
│         /\                          │
│        /  \  E2E Tests              │
│       /────\                        │
│      /      \  Integration Tests    │
│     /────────\                      │
│    /          \  Unit Tests         │
│   /────────────\                    │
└─────────────────────────────────────┘

Unit Tests (70%)
├─► Parsers: PDF extraction, validation
├─► Matchers: Scoring logic, weights
├─► Models: Pydantic validation
└─► Utils: Helper functions

Integration Tests (20%)
├─► LLM adapters with real APIs
├─► Parser with sample PDFs
├─► End-to-end matching pipeline
└─► Bias detection with fixtures

E2E Tests (10%)
├─► Streamlit UI flows
├─► Batch processing
├─► Export functionality
└─► Error scenarios
```

---

<div align="center">

## 🏗️ Architecture Summary

**Clean, Modular, Production-Ready**

Three-layer architecture with clear separation of concerns  
Multi-LLM system with factory pattern for flexibility  
Comprehensive bias detection and compliance features  
Scalable design ready for enterprise deployment  

</div>
