# Continuum - Supply Chain Risk Sentinel

A comprehensive, AI-powered supply chain risk monitoring and decision support system that leverages large language models, graph analysis, and advanced simulation to detect risks, analyze impacts, and recommend actionable mitigation strategies in real-time.

## Demo
<img width="1906" height="920" alt="image" src="https://github.com/user-attachments/assets/01aa3cf4-80a4-4d8b-add7-3e8bf6d014d7" />
<img width="1906" height="927" alt="image" src="https://github.com/user-attachments/assets/8b8b7c1f-6410-45dd-aaa4-1c7baeb6520c" />
<img width="1914" height="922" alt="image" src="https://github.com/user-attachments/assets/84bf38f2-a5e8-4981-8ea2-7533bbe37546" />
<img width="1914" height="912" alt="image" src="https://github.com/user-attachments/assets/736114ef-c394-4a43-98ec-70416da61107" />
<img width="1919" height="925" alt="image" src="https://github.com/user-attachments/assets/9fad11f7-4daf-41c3-b5e4-840702352c30" />



## Table of Contents

- [Overview](#overview)
- [Key Features](#key-features)
- [System Requirements](#system-requirements)
- [Quick Start](#quick-start)
- [Installation](#installation)
- [Architecture](#architecture)
- [Project Structure](#project-structure)
- [Core Components](#core-components)
- [Usage](#usage)
- [Docker Deployment](#docker-deployment)
- [Data Persistence](#data-persistence)
- [Configuration](#configuration)
- [Development](#development)
- [Troubleshooting](#troubleshooting)
- [Contributing](#contributing)
- [Support](#support)
- [License](#license)

## Overview

Continuum is an enterprise-grade supply chain risk management platform designed to monitor supplier networks, detect emerging risks from news and market data, simulate potential disruptions, and recommend strategic decisions to minimize supply chain vulnerability.

The system operates as a continuous monitoring agent that analyzes supplier relationships, identifies geopolitical and operational risks, calculates potential business impacts through scenario simulation, and provides confidence-scored recommendations for immediate action.

### Problem Statement

Modern supply chains are increasingly vulnerable to:
- Geopolitical disruptions (trade restrictions, sanctions)
- Natural disasters affecting production capacity
- Material shortages and commodity price volatility
- Supplier financial instability
- Logistics and transportation delays
- Regulatory changes affecting operations

Traditional risk management relies on manual monitoring and reactive responses. Continuum enables proactive, data-driven decision-making through continuous AI-powered analysis.

### Solution

Continuum automates supply chain risk detection and response through:
1. Real-time news and market data ingestion
2. Intelligent risk identification using LLM analysis
3. Supply chain graph modeling for impact propagation
4. Monte Carlo simulation of disruption scenarios
5. Confidence-scored action recommendations
6. Historical analysis and trend tracking
7. Interactive dashboard for risk visualization

## Key Features

### Risk Detection and Analysis

- Continuous monitoring of news sources and market data
- AI-powered risk extraction using language models
- Multi-factor severity scoring (0-1 scale)
- Risk categorization and tagging
- Confidence levels for detected risks
- Geographic and supplier-level impact mapping

### Supply Chain Modeling

- Dynamic graph representation of supplier networks
- Relationship tracking and dependency analysis
- Node and edge weight calculations
- Impact propagation through connected nodes
- Critical path identification
- Bottleneck detection and analysis

### Impact Simulation

- Monte Carlo-based disruption scenario generation
- Lead time delay calculations (days)
- Service impact estimation (percentage of capacity)
- Multiple scenario analysis (5+ concurrent scenarios)
- Worst-case impact identification
- Recovery time estimation

### Decision Support

- Multi-factor confidence calculation
- Real-world decision logic with material criticality
- Geopolitical risk integration
- Action library with 7 strategic recommendations
- Urgency-based prioritization
- Confidence-scored action recommendations
- Lead time validation for implementation

### Historical Analysis

- Automatic timestamped JSON persistence
- Complete cycle storage (all agent outputs)
- Cycle browsing and comparison
- Risk trend tracking
- Decision history audit trail
- CSV export for reporting

### Interactive Dashboard

- Real-time metrics and KPIs
- Supplier bubble chart visualization
- News timeline visualization
- Scenario comparison charts
- Supply chain graph network visualization
- Tabbed interface for organized data presentation
- History tab with cycle management
- Responsive design for multiple screen sizes

### Professional Containerization

- Docker multi-stage build optimization
- Docker Compose orchestration
- Volume-based data persistence
- Health check monitoring
- Production-ready configuration
- Optional background monitoring service

## System Requirements

### Minimum Requirements

- Python 3.13 or higher
- 4 GB RAM
- 500 MB disk space for application and data
- macOS, Linux, or Windows (with WSL2 or native Docker)

### Recommended Requirements

- Python 3.13.3 (current version)
- 8 GB RAM
- 2 GB disk space
- SSD for faster I/O
- Docker 20.10+ for containerized deployment
- Docker Compose 2.0+ for orchestration

### External Dependencies

- OpenAI API (for LLM analysis) - Optional, uses transformers library as fallback
- Internet connection for news fetching
- No database required - JSON file-based persistence

## Quick Start

### Using Docker (Recommended)

```bash
# 1. Clone or navigate to project directory
cd "path/to/- Continuum"

# 2. Start services
docker-compose up -d

# 3. Open dashboard in browser
# Access http://localhost:8501
```

### Native Python Installation

```bash
# 1. Install Python 3.13+
# Available at https://www.python.org/downloads/

# 2. Install dependencies
pip install -r requirements.txt

# 3. Run dashboard
streamlit run dashboard/app.py

# 4. In separate terminal, run background monitor
python main.py
```

### First Run Steps

1. Open http://localhost:8501 (or appropriate host:port)
2. Click "Run New Analysis" button
3. Wait for all 5 agents to complete
4. View results in Overview, Supply Chain Graph, Risks & Decisions, and Advanced Visuals tabs
5. Navigate to History tab to see saved analysis
6. Export results as CSV if needed

## Installation

### Prerequisites

- Python 3.13+ (verify with `python --version`)
- pip (comes with Python)
- For Docker: Docker Desktop 20.10+ ([download](https://www.docker.com/products/docker-desktop))

### Step-by-Step Installation

#### Option A: Docker Installation (Recommended)

```bash
# Navigate to project root
cd "path/to/- Continuum"

# Verify Docker setup
bash verify_docker_setup.sh          # Linux/Mac
# OR
verify_docker_setup.bat              # Windows

# Build and start
docker-compose up -d

# Verify startup
docker-compose ps
```

#### Option B: Native Python Installation

```bash
# 1. Clone or extract project
cd "path/to/- Continuum"

# 2. Create virtual environment (recommended)
python -m venv venv

# 3. Activate virtual environment
# On Linux/Mac:
source venv/bin/activate
# On Windows:
venv\Scripts\activate

# 4. Install dependencies
pip install -r requirements.txt

# 5. Create data directories
mkdir -p data/history logs

# 6. Start dashboard in terminal 1
streamlit run dashboard/app.py

# 7. Start background monitor in terminal 2
python main.py
```

### Dependency Installation Details

Key dependencies installed:

```
streamlit==1.41.1              # Dashboard framework
plotly==5.18.0                 # Interactive visualizations
pandas==2.3.3                  # Data manipulation
networkx==3.6.1                # Graph structures
pyvis==0.3.2                   # Network visualization
langgraph==1.0.5               # LLM orchestration
langchain-core==1.2.6          # LLM utilities
openai==2.14.0                 # LLM API client
transformers==4.45.2           # Local LLM fallback
torch==2.5.0                   # Neural network framework
feedparser==6.0.11             # News feed parsing
python-dotenv==1.0.1           # Environment configuration
scikit-learn==1.8.0            # Machine learning utilities
```

See `requirements.txt` for complete list with versions.

### Post-Installation Verification

```bash
# Python check
python -c "import streamlit; print(streamlit.__version__)"

# Docker check (if using Docker)
docker --version
docker-compose --version

# Port availability
# Ensure 8501 is not in use:
lsof -i :8501          # Linux/Mac
netstat -ano | findstr :8501  # Windows
```

## Architecture

### System Design

Continuum follows a modular agent-based architecture with a central memory system for state sharing:

```
Continuous Monitoring Loop
    |
    v
Ingestion Agent --> News sources, supplier data
    |
    v
Graph Agent --> Supply chain network modeling
    |
    v
Risk Agent --> News analysis, risk detection
    |
    v
Simulation Agent --> Scenario modeling, impact calculation
    |
    v
Decision Agent --> Recommendation generation
    |
    v
Data Persistence --> JSON storage with timestamps
    |
    v
Dashboard UI --> Streamlit presentation layer
```

### Data Flow

1. **Ingestion**: Fetches supplier data and news articles
2. **Graph Construction**: Builds supply chain network from relationships
3. **Risk Detection**: Analyzes news for supply chain threats
4. **Impact Simulation**: Models disruption scenarios and propagation
5. **Decision Making**: Generates context-aware recommendations
6. **Persistence**: Auto-saves complete cycle to timestamped JSON
7. **Visualization**: Presents results interactively in dashboard

### Key Design Patterns

- **Agent Pattern**: Each component responsible for specific analysis phase
- **Memory Singleton**: Shared state across agents
- **Pipeline Pattern**: Sequential processing through stages
- **Producer-Consumer**: Agents produce data consumed by next stage
- **Persistence Pattern**: Transparent auto-save on completion
- **Microservice Ready**: Docker containers deployable independently

## Project Structure

```
Continuum/
├── README.md                           # Main documentation (this file)
├── DOCKER_README.md                    # Docker deployment guide
├── DOCKER_GUIDE.md                     # Comprehensive Docker reference
├── DOCKER_QUICK_START.md               # Docker command reference
├── DOCKER_IMPLEMENTATION_SUMMARY.md    # Docker setup summary
├── IMPLEMENTATION_SUMMARY.md           # Data persistence overview
├── DATA_PERSISTENCE_GUIDE.md           # Persistence architecture
├── PERSISTENCE_QUICK_START.md          # Persistence quick reference
│
├── requirements.txt                    # Python dependencies
├── Dockerfile                          # Docker image definition
├── docker-compose.yml                  # Service orchestration
├── .dockerignore                       # Build optimization
├── .env.example                        # Environment template
│
├── main.py                             # Background monitor entry point
├── dashboard/
│   ├── app.py                          # Streamlit dashboard main app
│   ├── utils.py                        # Analysis execution utilities
│   ├── visualizations.py               # Plotly chart functions
│   ├── history_utils.py                # History browsing utilities
│   └── pages/                          # Streamlit multi-page support
│       ├── 1_Overview.py
│       ├── 2_Supply_Chain_Graph.py
│       └── 3_Risks_&_Decisions.py
│
├── core/
│   ├── llm_analyzer.py                 # LLM interaction layer
│   ├── memory.py                       # Shared memory singleton
│   ├── news_fetcher.py                 # News data ingestion
│   ├── orchestrator.py                 # Agent orchestration
│   └── persistence.py                  # Data persistence layer
│
├── agents/
│   ├── ingestion_agent.py              # Data collection agent
│   ├── graph_agent.py                  # Graph modeling agent
│   ├── risk_agent.py                   # Risk detection agent
│   ├── simulation_agent.py             # Impact simulation agent
│   └── decision_agent.py               # Recommendation agent
│
├── data/
│   ├── suppliers.csv                   # Supplier master data
│   └── history/                        # Persisted analysis cycles
│
├── lib/
│   ├── bindings/
│   │   └── utils.js                    # Frontend utilities
│   ├── tom-select/                     # UI component library
│   └── vis-9.1.2/                      # Network visualization library
│
├── logs/                               # Application logs
├── tests/                              # Test suite directory
│
└── .streamlit/
    └── config.toml                     # Streamlit configuration
```

## Core Components

### 1. Ingestion Agent (`agents/ingestion_agent.py`)

**Purpose**: Collect and prepare supply chain data

**Functionality**:
- Loads supplier master data from CSV
- Fetches news articles from RSS feeds
- Enriches data with timestamps
- Calculates data quality metrics
- Returns structured data for graph building

**Output**:
```python
{
    "suppliers": [
        {
            "name": "Supplier Name",
            "country": "Country",
            "product": "Category",
            "lead_time_days": 14,
            "reliability": 0.95
        }
    ],
    "news_items": [
        {
            "title": "Article Title",
            "summary": "Content summary",
            "source": "RSS Feed",
            "published_date": "2026-01-12"
        }
    ]
}
```

### 2. Graph Agent (`agents/graph_agent.py`)

**Purpose**: Model supply chain as network graph

**Functionality**:
- Creates directed graph from supplier relationships
- Calculates node importance (degree, betweenness)
- Establishes weighted edges based on dependency
- Identifies critical suppliers and paths
- Performs reachability analysis

**Output**:
```python
{
    "graph": NetworkX.DiGraph object,
    "node_count": 15,
    "edge_count": 24,
    "critical_nodes": ["Supplier A", "Supplier B"]
}
```

### 3. Risk Agent (`agents/risk_agent.py`)

**Purpose**: Detect and analyze supply chain risks from news

**Functionality**:
- Uses LLM to analyze news relevance to supply chain
- Extracts risk indicators and severity scores
- Maps risks to affected suppliers
- Calculates geographic impact
- Determines risk categories

**Output**:
```python
{
    "risks_detected": [
        {
            "title": "Risk Title",
            "severity": 0.75,
            "affected_suppliers": ["Supplier A"],
            "category": "Geopolitical",
            "source_news_index": 3
        }
    ],
    "max_severity": 0.92
}
```

### 4. Simulation Agent (`agents/simulation_agent.py`)

**Purpose**: Model disruption scenarios and calculate impacts

**Functionality**:
- Generates Monte Carlo disruption scenarios
- Simulates impact propagation through graph
- Calculates delay impact in days
- Estimates service impact percentage
- Identifies worst-case scenarios

**Output**:
```python
{
    "scenarios": [
        {
            "scenario_id": "Scenario_1",
            "delay_days": 14,
            "affected_nodes": 5,
            "service_impact_pct": 35.0
        }
    ],
    "worst_case_delay_days": 21,
    "worst_case_affected_nodes": 7
}
```

### 5. Decision Agent (`agents/decision_agent.py`)

**Purpose**: Generate actionable recommendations with confidence scores

**Functionality**:
- Evaluates material criticality (semiconductors > steel > others)
- Considers geopolitical risk (Taiwan > China > others)
- Calculates multi-factor confidence (max 100%)
- Applies tiered decision logic (CRITICAL/HIGH/MEDIUM/LOW)
- Recommends from 7-action library with lead times
- Prevents duplicate recommendations

**Actions Available**:
1. `expedite_shipment` - Urgency 5, 2-day lead time
2. `activate_alternative_source` - Urgency 4, 5-day lead time
3. `increase_safety_stock` - Urgency 3, 3-day lead time
4. `diversify_suppliers` - Urgency 2, 30-day lead time
5. `negotiate_contract_terms` - Urgency 2, 7-day lead time
6. `notify_stakeholders` - Urgency 2, 1-day lead time
7. `monitor_closely` - Urgency 1, 0-day lead time

**Output**:
```python
{
    "recommended_actions": [
        {
            "action": "expedite_shipment",
            "confidence": 0.95,
            "affected_supplier": "Supplier A",
            "material_type": "Semiconductors",
            "supplier_country": "Taiwan",
            "urgency": 5,
            "lead_time_days": 2
        }
    ],
    "overall_confidence": 0.95,
    "decision_count": 3
}
```

### 6. Memory System (`core/memory.py`)

**Purpose**: Share state across agents

**Functionality**:
- Singleton pattern for global access
- Thread-safe data storage
- Supports nested dictionaries
- Get/set/clear operations
- Memory dumping for persistence

**Usage**:
```python
from core.memory import memory

# Store data
memory.set("ingestion_result", data)

# Retrieve data
result = memory.get("ingestion_result")

# Dump all for persistence
full_state = memory.dump()
```

### 7. Orchestrator (`core/orchestrator.py`)

**Purpose**: Coordinate all agents in sequence

**Functionality**:
- Manages agent execution order
- Passes data between agents via memory
- Handles errors and retries
- Logs progress and timing
- Triggers automatic data persistence
- Returns comprehensive results

**Usage**:
```python
from core.orchestrator import Orchestrator

orchestrator = Orchestrator()
result = orchestrator.run_single_cycle()
# Returns: {
#     "status": "success",
#     "timestamp": "2026-01-12T08:00:00",
#     "persisted": True,
#     "persistence_filename": "20260112_080000"
# }
```

### 8. Persistence Layer (`core/persistence.py`)

**Purpose**: Automatically save and retrieve analysis cycles

**Functionality**:
- Auto-saves complete memory state as JSON
- Timestamps files as `YYYYMMDD_HHMMSS.json`
- Serializes NetworkX graphs to JSON
- Lists all saved cycles
- Exports data to CSV format
- Calculates storage statistics

**Usage**:
```python
from core.persistence import persistence

# Save cycle (automatic)
persistence.save_cycle(memory.dump())

# List history
cycles = persistence.list_history(limit=50)

# Load past cycle
data = persistence.load_cycle("20260112_075600")

# Export to CSV
persistence.export_cycle_csv("20260112_075600")
```

## Usage

### Running an Analysis

#### Method 1: Dashboard UI (Recommended)

```
1. Open http://localhost:8501
2. Click "Run New Analysis" button
3. Monitor progress in sidebar
4. View results across tabs:
   - Overview: Summary metrics
   - Supply Chain Graph: Network visualization
   - Risks & Decisions: Details and actions
   - Advanced Visuals: Charts and trends
   - History: Past analyses
```

#### Method 2: Background Monitoring

```bash
# Terminal 1: Dashboard
docker-compose up -d
# or
streamlit run dashboard/app.py

# Terminal 2: Background monitoring (runs continuous cycles)
docker-compose --profile background up -d
# or
python main.py
```

Background monitor runs continuous analysis cycles (timing configurable in `main.py`).

### Dashboard Tabs

#### Overview Tab

Shows latest analysis summary with:
- Maximum risk severity (0-1 scale)
- Worst-case delay (days)
- Number of decisions made
- Top 3 recommended actions with confidence
- Progress bar showing confidence level

#### Supply Chain Graph Tab

Network visualization showing:
- Supplier nodes (colored by criticality)
- Relationship edges (weighted by dependency)
- Graph layout using physics simulation
- Interactive panning and zooming
- Node details on hover

#### Risks & Decisions Tab

Detailed analysis results:
- Detected risks with severity and affected suppliers
- Recommended actions with urgency and lead times
- Simulation scenarios with delay and impact metrics
- Risk details expandable for full context

#### Advanced Visuals Tab

Interactive charts for deeper analysis:
- Supplier bubble chart: X=delay, Y=impact, size=risk
- News timeline: Chronological with relevance coloring
- Scenario comparison: Delay vs impact across simulations

#### History Tab

Manage past analyses:
- Statistics: Total cycles, storage usage, date range
- Browse: Select cycle from dropdown
- View: Details in 4 tabs (Risks, Simulations, Decisions, News)
- Compare: Two-cycle comparison with change detection
- Export: Download data as CSV
- Delete: Remove cycles to save space

### Data Exports

Export functionality available in History tab:

```bash
# Downloaded CSV files include:
risks_<filename>.csv          # Risk details
simulations_<filename>.csv    # Scenario impacts
decisions_<filename>.csv      # Recommended actions
```

### API Usage (Python)

For programmatic access:

```python
from core.orchestrator import Orchestrator
from core.memory import memory
from core.persistence import persistence

# 1. Run single analysis cycle
orchestrator = Orchestrator()
result = orchestrator.run_single_cycle()

# 2. Access results from memory
risks = memory.get("risk_result")
decisions = memory.get("decision_result")
graph = memory.get("graph_result")

# 3. Query history
all_cycles = persistence.list_history()
stats = persistence.get_summary_stats()

# 4. Load past analysis
past_data = persistence.load_cycle("20260112_075600")
```

### Configuration

#### Environment Variables

Create `.env` file (copy from `.env.example`):

```env
# Streamlit Server
STREAMLIT_SERVER_PORT=8501
STREAMLIT_SERVER_ADDRESS=0.0.0.0
STREAMLIT_SERVER_HEADLESS=true

# Python Logging
PYTHONUNBUFFERED=1
LOG_LEVEL=INFO

# Optional: LLM API
OPENAI_API_KEY=sk_your_key_here
```

#### Streamlit Configuration

Edit `.streamlit/config.toml`:

```ini
[server]
port = 8501
address = 0.0.0.0
headless = true

[theme]
primaryColor = "#FF6B6B"
backgroundColor = "#F8F9FA"
```

#### Application Configuration

Modify in source code:

```python
# core/news_fetcher.py
MAX_ARTICLES = 10
NEWS_REFRESH_INTERVAL = 3600  # seconds

# main.py
CYCLE_INTERVAL = 60  # seconds between cycles

# agents/decision_agent.py
CRITICAL_RISK_THRESHOLD = 0.85
MATERIAL_CRITICALITY = {...}  # Custom weights
```

## Docker Deployment

### Quick Start

```bash
# Start all services
docker-compose up -d

# Access at http://localhost:8501
```

### Docker Compose Services

```yaml
continuum-dashboard:
  - Main Streamlit UI
  - Port: 8501
  - Always running
  - Health checks enabled

continuum-monitor:
  - Background analysis
  - Profile: background (optional)
  - Runs main.py continuously
```

### Build and Deploy

```bash
# Build image
docker build -t continuum:latest .

# Run container
docker run -d -p 8501:8501 -v ./data/history:/app/data/history continuum:latest

# Using compose
docker-compose up -d

# View logs
docker-compose logs -f

# Stop services
docker-compose down
```

### Volume Mounts

```yaml
volumes:
  - ./data/history:/app/data/history     # Persisted analyses
  - ./logs:/app/logs                      # Application logs
  - ./data/suppliers.csv:/app/data/suppliers.csv
```

### Production Deployment

For production, see `DOCKER_GUIDE.md` for:
- Resource limits
- Restart policies
- Monitoring setup
- Security hardening
- Cloud deployment options
- Kubernetes manifests

## Data Persistence

### Storage Format

All analyses saved as JSON with complete state:

```json
{
  "timestamp": "2026-01-12T08:00:00",
  "ingestion_result": {...},
  "graph_result": {...},
  "risk_result": {...},
  "simulation_result": {...},
  "decision_result": {...}
}
```

### File Organization

```
data/history/
├── 20260112_075600.json       # YYYYMMDD_HHMMSS format
├── 20260112_075530.json
└── 20260112_075430.json
```

### Retrieval and Export

```bash
# List all cycles
docker exec continuum-dashboard python -c "
from core.persistence import persistence
for cycle in persistence.list_history():
    print(cycle)
"

# Load specific cycle
docker exec continuum-dashboard python -c "
from core.persistence import persistence
data = persistence.load_cycle('20260112_075600')
print(data)
"

# Export to CSV
docker exec continuum-dashboard python -c "
from core.persistence import persistence
persistence.export_cycle_csv('20260112_075600')
"
```

### Storage Statistics

```
Typical cycle size: 50-200 KB
100 cycles: 10-20 MB
1000 cycles: 100-200 MB
```

See `DATA_PERSISTENCE_GUIDE.md` for comprehensive persistence documentation.

## Configuration

### Python Version

Requires Python 3.13 or higher:

```bash
python --version  # Should be 3.13+
```

### Dependency Management

Update dependencies:

```bash
# Upgrade specific package
pip install --upgrade streamlit

# Install all requirements
pip install -r requirements.txt

# Generate requirements file (for development)
pip freeze > requirements.txt
```

### Logging Configuration

Set logging level:

```bash
# Environment variable
export PYTHONLOGLEVEL=DEBUG

# Or in code
import logging
logging.basicConfig(level=logging.DEBUG)
```

### Custom Supplier Data

Replace `data/suppliers.csv` with your data:

```csv
name,country,product,lead_time_days,reliability
Supplier Name,Country,Category,14,0.95
```

Required columns: name, country, product, lead_time_days, reliability

### News Sources

Add or modify RSS feeds in `core/news_fetcher.py`:

```python
NEWS_FEEDS = [
    "https://feeds.example.com/supply-chain",
    "https://feeds.example.com/trade-news",
    # Add your sources here
]
```

## Development

### Setting Up Development Environment

```bash
# Clone repository
git clone <repo> && cd "- Continuum"

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Linux/Mac
# or
venv\Scripts\activate     # Windows

# Install development dependencies
pip install -r requirements.txt
pip install pytest black flake8  # Optional dev tools

# Create local environment
cp .env.example .env
```

### Running Tests

```bash
# Run all tests
pytest tests/

# Run with coverage
pytest --cov=. tests/

# Run specific test
pytest tests/test_agents.py -v
```

### Code Style

For development, maintain consistency:

```bash
# Format code
black agents/ core/ dashboard/

# Check linting
flake8 agents/ core/ dashboard/

# Type checking (optional)
mypy agents/ core/ dashboard/
```

### Adding New Agents

1. Create file `agents/new_agent.py`
2. Implement class inheriting from base
3. Add `run()` method returning dictionary
4. Update `core/orchestrator.py` to call agent
5. Store results in memory

Example template:

```python
# agents/new_agent.py
class NewAgent:
    def __init__(self):
        from core.memory import memory
        self.memory = memory
    
    def run(self):
        # Get input from memory
        previous_result = self.memory.get("previous_agent_result")
        
        # Perform analysis
        result = self.analyze(previous_result)
        
        # Store result
        self.memory.set("new_agent_result", result)
        return result
    
    def analyze(self, data):
        # Implementation
        return {"status": "complete", "data": data}
```

### Extending Dashboard

Add new pages in `dashboard/pages/`:

```python
# dashboard/pages/4_Custom_Analysis.py
import streamlit as st
from core.memory import memory

st.title("Custom Analysis")
# Your code here
```

## Troubleshooting

### Common Issues

#### Port Already in Use

```bash
# Find process using port 8501
lsof -i :8501          # Linux/Mac
netstat -ano | findstr :8501  # Windows

# Kill process or change port in docker-compose.yml
```

#### Docker Daemon Not Running

```bash
# Check Docker status
docker ps

# Start Docker
# macOS: Open Docker Desktop
# Linux: sudo systemctl start docker
# Windows: Start Docker Desktop
```

#### Out of Memory

```bash
# Check resource usage
docker stats

# Limit memory in docker-compose.yml
deploy:
  resources:
    limits:
      memory: 2G
```

#### Analysis Takes Too Long

```bash
# Check orchestrator logs
docker-compose logs orchestrator

# Reduce data size
# Edit news sources in core/news_fetcher.py
# Edit supplier count in data/suppliers.csv
```

#### Dashboard Won't Load

```bash
# Check Streamlit logs
docker-compose logs continuum-dashboard

# Verify file permissions
docker exec continuum-dashboard ls -la /app

# Rebuild image
docker-compose build --no-cache
docker-compose up -d
```

### Debug Mode

Run with verbose logging:

```bash
# Container
docker exec -it continuum-dashboard bash
PYTHONLOGLEVEL=DEBUG streamlit run dashboard/app.py

# Native
PYTHONLOGLEVEL=DEBUG streamlit run dashboard/app.py
```

### Checking Data

Verify analysis results:

```bash
# List saved cycles
docker exec continuum-dashboard ls -la /app/data/history/

# View cycle contents
docker exec continuum-dashboard head -c 500 /app/data/history/20260112_075600.json

# Check memory state
docker exec continuum-dashboard python -c "
from core.memory import memory
import json
print(json.dumps(memory.dump(), indent=2, default=str))
"
```

## Contributing

### Development Workflow

1. Create feature branch: `git checkout -b feature/your-feature`
2. Make changes and test
3. Format code: `black .`
4. Lint code: `flake8 .`
5. Run tests: `pytest`
6. Commit: `git commit -m "Add your feature"`
7. Push: `git push origin feature/your-feature`
8. Create pull request

### Code Standards

- Follow PEP 8 style guide
- Add docstrings to functions and classes
- Include type hints where possible
- Write unit tests for new features
- Update documentation

### Issue Reporting

Report issues with:
- Clear title
- Reproduction steps
- Expected vs actual behavior
- Environment details (Python version, OS, Docker version)
- Relevant logs

## Support

### Documentation

- **README.md** - This file, comprehensive overview
- **DOCKER_README.md** - Docker setup and usage
- **DOCKER_GUIDE.md** - Detailed Docker reference
- **DATA_PERSISTENCE_GUIDE.md** - Data storage architecture
- **IMPLEMENTATION_SUMMARY.md** - System components overview

### Getting Help

1. Check documentation files above
2. Review troubleshooting section
3. Check application logs: `docker-compose logs -f`
4. Search existing issues
5. Create detailed issue report

### Performance Tips

- Run on SSD for faster I/O
- Allocate sufficient RAM (8GB recommended)
- Use latest Python version (3.13+)
- Keep Docker image updated
- Monitor resource usage regularly

## License

This project is provided as-is for supply chain risk management purposes. Refer to LICENSE file for full terms.

## Acknowledgments

Continuum integrates:
- Streamlit for interactive dashboards
- Plotly for advanced visualizations
- NetworkX for graph analysis
- LangGraph for LLM orchestration
- Transformers for NLP capabilities
- PyVis for network visualization
- Pandas for data manipulation

---

**Version**: 1.0.0  
**Last Updated**: January 12, 2026  
**Status**: Production Ready  

For the latest updates and comprehensive guides, see the documentation files in the project root.
