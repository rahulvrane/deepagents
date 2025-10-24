# Co-Scientist Agent System: Design Document

## Executive Summary

This document outlines a comprehensive design for transforming the DeepAgents framework into a specialized **Co-Scientist Agent System** - an AI assistant that works alongside scientists to accelerate research, from literature review to experimental design, data analysis, and scientific writing.

---

## Table of Contents

1. [Current DeepAgents Architecture Analysis](#current-deepagents-architecture-analysis)
2. [Co-Scientist Requirements](#co-scientist-requirements)
3. [Proposed Architecture](#proposed-architecture)
4. [Implementation Roadmap](#implementation-roadmap)
5. [Example Use Cases](#example-use-cases)

---

## Current DeepAgents Architecture Analysis

### Core Components

Based on the comprehensive codebase review:

#### 1. **Planning & Task Management** (`TodoListMiddleware`)
- Built-in `write_todos` tool for task decomposition
- Adaptive planning as new information emerges
- Track progress through multi-step objectives

#### 2. **Context Management** (`FilesystemMiddleware`)
- Four filesystem tools: `ls`, `read_file`, `write_file`, `edit_file`
- Short-term memory (ephemeral, in-state)
- Long-term memory (persistent, via LangGraph Store)
- Automatic eviction of large tool results (>80KB) to filesystem
- Lines truncated at 2000 characters

#### 3. **Subagent Spawning** (`SubAgentMiddleware`)
- `task` tool for delegating to specialized subagents
- Context isolation for complex subtasks
- Supports custom models, tools, and middleware per subagent
- General-purpose fallback agent

#### 4. **Middleware Architecture**
Default stack:
1. `TodoListMiddleware`
2. `FilesystemMiddleware`
3. `SubAgentMiddleware`
4. `SummarizationMiddleware` (170k tokens max)
5. `AnthropicPromptCachingMiddleware`
6. `PatchToolCallsMiddleware`
7. `HumanInTheLoopMiddleware` (conditional)

### Current Strengths for Scientific Research

✅ **Planning** - Excellent for breaking down research tasks
✅ **Memory** - Can store papers, protocols, experimental data
✅ **Modularity** - Easy to add domain-specific tools
✅ **Subagents** - Delegate to specialized scientific experts
✅ **Long-term Memory** - Track research projects over time
✅ **Human-in-the-loop** - Review sensitive operations

### Current Gaps for Scientific Research

❌ **Literature Access** - No scientific paper search/retrieval
❌ **Data Analysis** - No statistical or computational tools
❌ **Visualization** - No plotting or figure generation
❌ **Code Execution** - No sandboxed Python environment for analysis
❌ **Scientific Formatting** - No LaTeX/citation management
❌ **Domain Tools** - No bioinformatics, chemistry, physics tools
❌ **Collaboration** - No version control integration
❌ **Reproducibility** - No experiment tracking or versioning

---

## Co-Scientist Requirements

### 1. Literature Review & Research Management

**Capabilities Needed:**
- Search scientific databases (PubMed, arXiv, Google Scholar, Semantic Scholar)
- Retrieve and parse PDFs of scientific papers
- Extract key information: abstract, methods, results, conclusions
- Manage citations and references (BibTeX format)
- Identify research gaps and trends
- Generate literature reviews

**Tools:**
- `search_papers(query, database, max_results, filters)`
- `download_paper(paper_id, source)`
- `parse_pdf(file_path)`
- `extract_citations(file_path)`
- `generate_bibtex(paper_metadata)`
- `analyze_citation_network(seed_papers)`

### 2. Experimental Design

**Capabilities Needed:**
- Help design experiments and protocols
- Suggest appropriate methodologies
- Statistical power analysis
- Sample size calculations
- Generate experimental protocols
- Design control experiments

**Tools:**
- `power_analysis(effect_size, alpha, power)`
- `sample_size_calculator(parameters)`
- `suggest_controls(experiment_description)`
- `generate_protocol(experiment_type, parameters)`
- `design_factorial_experiment(factors)`
- `randomization_scheme(groups, blocking_factors)`

### 3. Data Analysis & Statistics

**Capabilities Needed:**
- Execute Python code for data analysis
- Statistical hypothesis testing
- Data visualization (plots, graphs, figures)
- Machine learning and modeling
- Data cleaning and preprocessing
- Results interpretation

**Tools:**
- `execute_python(code, timeout)` - Sandboxed execution
- `statistical_test(test_type, data)`
- `create_plot(plot_type, data, parameters)`
- `fit_model(model_type, data, parameters)`
- `clean_data(file_path, operations)`
- `summarize_statistics(data)`

### 4. Scientific Writing & Communication

**Capabilities Needed:**
- Draft scientific papers (sections: abstract, intro, methods, results, discussion)
- Generate LaTeX documents
- Format citations and references
- Create figures and tables
- Write grant proposals
- Peer review assistance

**Tools:**
- `format_latex(content, document_type)`
- `generate_figure_caption(figure_description)`
- `format_table(data, format_spec)`
- `check_scientific_writing(text, domain)`
- `suggest_revisions(text, reviewer_comments)`
- `extract_key_findings(results_text)`

### 5. Domain-Specific Scientific Tools

**Bioinformatics:**
- `blast_search(sequence, database)`
- `align_sequences(sequences, method)`
- `annotate_genome(sequence_file)`
- `protein_structure_prediction(sequence)`

**Chemistry:**
- `molecular_structure(smiles)`
- `reaction_prediction(reactants)`
- `property_calculation(molecule, properties)`
- `literature_synthesis_routes(compound)`

**Physics/Math:**
- `symbolic_computation(expression)`
- `numerical_simulation(model, parameters)`
- `solve_differential_equation(equation, conditions)`
- `unit_conversion(value, from_unit, to_unit)`

### 6. Collaboration & Project Management

**Capabilities Needed:**
- Version control integration (Git)
- Experiment tracking and versioning
- Lab notebook functionality
- Collaboration with other researchers
- Project timeline management

**Tools:**
- `git_operations(command, repo_path)`
- `log_experiment(metadata, data_files)`
- `version_protocol(protocol_file, changes)`
- `create_lab_notebook_entry(date, experiment_id, notes)`
- `track_milestone(project_id, milestone, status)`

---

## Proposed Architecture

### Overview Diagram

```
┌─────────────────────────────────────────────────────────────┐
│                   Co-Scientist Agent System                  │
│                                                               │
│  ┌─────────────┐  ┌──────────────┐  ┌───────────────┐     │
│  │   Planning  │  │  Filesystem  │  │   Subagents   │     │
│  │     Tool    │  │    Memory    │  │   (10+ types) │     │
│  └─────────────┘  └──────────────┘  └───────────────┘     │
│                                                               │
│  ┌───────────────────────────────────────────────────────┐  │
│  │            New Scientific Middleware Layer             │  │
│  │                                                         │  │
│  │  • LiteratureSearchMiddleware                          │  │
│  │  • DataAnalysisMiddleware (Python exec sandbox)        │  │
│  │  • VisualizationMiddleware                             │  │
│  │  • CitationManagementMiddleware                        │  │
│  │  • ExperimentalDesignMiddleware                        │  │
│  │  • DomainToolsMiddleware (bio, chem, physics)          │  │
│  │  • ScientificWritingMiddleware                         │  │
│  └───────────────────────────────────────────────────────┘  │
│                                                               │
│  ┌───────────────────────────────────────────────────────┐  │
│  │              Specialized Subagents                      │  │
│  │                                                         │  │
│  │  • literature-reviewer    • data-analyst                │  │
│  │  • experimental-designer  • statistician                │  │
│  │  • scientific-writer      • domain-expert-bio           │  │
│  │  • citation-manager       • domain-expert-chem          │  │
│  │  • hypothesis-generator   • domain-expert-physics       │  │
│  │  • protocol-designer      • grant-writer                │  │
│  └───────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
```

### 1. Scientific Middleware Components

#### A. LiteratureSearchMiddleware

**Purpose:** Provides tools for searching, retrieving, and analyzing scientific literature.

**Tools:**
```python
class LiteratureSearchMiddleware(AgentMiddleware):
    tools = [
        search_pubmed,          # Search PubMed database
        search_arxiv,           # Search arXiv preprints
        search_semantic_scholar, # Semantic Scholar API
        download_paper,         # Retrieve full-text PDFs
        parse_scientific_pdf,   # Extract structured data
        extract_references,     # Get bibliography
        generate_bibtex,        # Create BibTeX entries
        analyze_citation_graph, # Citation network analysis
    ]

    system_prompt = """
    ## Literature Search Tools

    You have access to scientific literature databases...
    """
```

**Integration Points:**
- Store papers in filesystem at `/papers/`
- Cache search results in long-term memory
- Integrate with citation management tools

#### B. DataAnalysisMiddleware

**Purpose:** Provides sandboxed Python execution for data analysis.

**Tools:**
```python
class DataAnalysisMiddleware(AgentMiddleware):
    tools = [
        execute_python_code,    # Sandboxed Python environment
        statistical_test,       # Common statistical tests
        data_visualization,     # Create plots (matplotlib, seaborn)
        fit_regression_model,   # Statistical modeling
        machine_learning,       # ML model training/prediction
        clean_dataset,          # Data preprocessing
        summarize_data,         # Descriptive statistics
    ]

    # Security: Sandbox environment with restricted imports
    # Libraries: numpy, pandas, scipy, sklearn, matplotlib, seaborn
    # Timeout: 60 seconds per execution
    # Memory limit: 2GB
```

**Key Features:**
- Restricted execution environment (no network, limited file access)
- Pre-installed scientific libraries
- Automatic figure saving to filesystem
- Result caching for reproducibility

#### C. VisualizationMiddleware

**Purpose:** Generate scientific figures and visualizations.

**Tools:**
```python
class VisualizationMiddleware(AgentMiddleware):
    tools = [
        create_plot,            # Generic plotting
        create_heatmap,         # Heatmap visualization
        create_volcano_plot,    # For -omics data
        create_network_graph,   # Network visualization
        create_3d_structure,    # 3D molecular/protein structures
        annotate_figure,        # Add annotations
        export_publication_figure, # High-res export
    ]
```

**Output:**
- Save figures to `/figures/` in filesystem
- Support multiple formats (PNG, PDF, SVG)
- Publication-quality settings

#### D. CitationManagementMiddleware

**Purpose:** Manage references and citations.

**Tools:**
```python
class CitationManagementMiddleware(AgentMiddleware):
    tools = [
        add_reference,          # Add paper to reference library
        cite_paper,             # Generate in-text citation
        format_bibliography,    # Create bibliography section
        export_bibtex,          # Export references
        import_bibtex,          # Import existing references
        check_citations,        # Verify all citations present
        suggest_citations,      # Recommend relevant papers
    ]

    # Storage: /references/library.bib in long-term memory
```

#### E. ExperimentalDesignMiddleware

**Purpose:** Assist with experimental design and protocols.

**Tools:**
```python
class ExperimentalDesignMiddleware(AgentMiddleware):
    tools = [
        power_analysis,
        sample_size_calculator,
        randomization_generator,
        design_factorial_experiment,
        suggest_controls,
        generate_protocol,
        protocol_version_control,
        safety_check,           # Check for safety concerns
    ]
```

#### F. DomainToolsMiddleware

**Purpose:** Domain-specific scientific tools (modular by field).

**Bioinformatics:**
```python
class BioinformaticsMiddleware(AgentMiddleware):
    tools = [
        blast_search,
        sequence_alignment,
        protein_structure_prediction,
        gene_annotation,
        phylogenetic_analysis,
        pathway_analysis,
    ]
```

**Chemistry:**
```python
class ChemistryMiddleware(AgentMiddleware):
    tools = [
        smiles_to_structure,
        predict_properties,
        reaction_prediction,
        retrosynthesis,
        docking_simulation,
    ]
```

**Physics/Math:**
```python
class PhysicsMiddleware(AgentMiddleware):
    tools = [
        symbolic_math,
        numerical_integration,
        differential_equation_solver,
        unit_converter,
        simulation_runner,
    ]
```

#### G. ScientificWritingMiddleware

**Purpose:** Assist with scientific writing and formatting.

**Tools:**
```python
class ScientificWritingMiddleware(AgentMiddleware):
    tools = [
        format_latex_document,
        generate_abstract,
        format_methods_section,
        create_results_section,
        write_discussion,
        format_table,
        generate_figure_legend,
        check_grammar_scientific,
        suggest_revisions,
    ]
```

### 2. Specialized Subagents

#### Literature Reviewer
```python
literature_reviewer = {
    "name": "literature-reviewer",
    "description": "Expert at conducting comprehensive literature reviews, identifying research gaps, and synthesizing findings across multiple papers.",
    "system_prompt": """You are a scientific literature review expert. Your role is to:
    1. Search and retrieve relevant scientific papers
    2. Read and analyze papers systematically
    3. Identify key findings, methodologies, and limitations
    4. Synthesize information across multiple papers
    5. Identify research gaps and opportunities
    6. Generate comprehensive literature review sections

    Store all papers in /papers/ and maintain a summary in /literature_review_summary.md
    Keep track of citations in /references/library.bib
    """,
    "tools": [
        search_pubmed, search_arxiv, search_semantic_scholar,
        download_paper, parse_scientific_pdf, extract_references,
        generate_bibtex, analyze_citation_graph
    ],
    "middleware": [
        LiteratureSearchMiddleware(),
        CitationManagementMiddleware(),
    ]
}
```

#### Data Analyst
```python
data_analyst = {
    "name": "data-analyst",
    "description": "Expert in statistical analysis, data visualization, and interpreting experimental results. Can execute Python code for complex analyses.",
    "system_prompt": """You are a data analysis expert. Your role is to:
    1. Clean and preprocess experimental data
    2. Perform appropriate statistical tests
    3. Create publication-quality visualizations
    4. Interpret results and identify patterns
    5. Assess statistical significance and effect sizes
    6. Generate comprehensive results sections

    Store datasets in /data/ and figures in /figures/
    Document all analysis steps for reproducibility
    """,
    "tools": [
        execute_python_code, statistical_test, data_visualization,
        fit_regression_model, machine_learning, summarize_data
    ],
    "middleware": [
        DataAnalysisMiddleware(),
        VisualizationMiddleware(),
    ]
}
```

#### Experimental Designer
```python
experimental_designer = {
    "name": "experimental-designer",
    "description": "Expert in designing rigorous experiments, protocols, and methodologies. Helps with study design, controls, and power analysis.",
    "system_prompt": """You are an experimental design expert. Your role is to:
    1. Design rigorous experimental protocols
    2. Suggest appropriate controls and replicates
    3. Perform power analysis and sample size calculations
    4. Identify potential confounds and biases
    5. Generate detailed step-by-step protocols
    6. Consider ethical and safety implications

    Store protocols in /protocols/ with version control
    Document design rationale and expected outcomes
    """,
    "tools": [
        power_analysis, sample_size_calculator, randomization_generator,
        design_factorial_experiment, suggest_controls, generate_protocol,
        safety_check
    ],
    "middleware": [
        ExperimentalDesignMiddleware(),
    ]
}
```

#### Scientific Writer
```python
scientific_writer = {
    "name": "scientific-writer",
    "description": "Expert in writing scientific papers, grants, and presentations. Handles formatting, citations, and scientific communication.",
    "system_prompt": """You are a scientific writing expert. Your role is to:
    1. Draft scientific papers in proper format
    2. Write clear, concise scientific prose
    3. Format documents in LaTeX or Markdown
    4. Manage citations and references properly
    5. Create publication-ready figures and tables
    6. Revise based on reviewer feedback

    Main document stored at /manuscript/main.tex or /manuscript/main.md
    Figures in /figures/ and tables in /tables/
    References in /references/library.bib
    """,
    "tools": [
        format_latex_document, generate_abstract, format_methods_section,
        create_results_section, write_discussion, format_table,
        generate_figure_legend, cite_paper, format_bibliography
    ],
    "middleware": [
        ScientificWritingMiddleware(),
        CitationManagementMiddleware(),
    ]
}
```

#### Hypothesis Generator
```python
hypothesis_generator = {
    "name": "hypothesis-generator",
    "description": "Expert in generating testable hypotheses based on literature review and preliminary data. Helps frame research questions.",
    "system_prompt": """You are a hypothesis generation expert. Your role is to:
    1. Analyze existing literature and data
    2. Identify research gaps and opportunities
    3. Generate testable, specific hypotheses
    4. Frame clear research questions
    5. Propose mechanisms and predictions
    6. Consider alternative explanations

    Document hypotheses in /hypotheses.md with rationale
    Link to supporting literature and preliminary data
    """,
    "tools": [
        search_pubmed, search_arxiv, analyze_citation_graph,
        execute_python_code, statistical_test
    ],
    "middleware": [
        LiteratureSearchMiddleware(),
        DataAnalysisMiddleware(),
    ]
}
```

#### Domain Experts (Bio, Chem, Physics)
```python
bioinformatics_expert = {
    "name": "bioinformatics-expert",
    "description": "Expert in bioinformatics analysis: sequence analysis, genomics, protein structure, and pathway analysis.",
    "system_prompt": """You are a bioinformatics expert...""",
    "tools": [
        blast_search, sequence_alignment, protein_structure_prediction,
        gene_annotation, phylogenetic_analysis, pathway_analysis
    ],
    "middleware": [BioinformaticsMiddleware()]
}

chemistry_expert = {
    "name": "chemistry-expert",
    "description": "Expert in computational chemistry: molecular modeling, reaction prediction, and property calculations.",
    "system_prompt": """You are a computational chemistry expert...""",
    "tools": [
        smiles_to_structure, predict_properties, reaction_prediction,
        retrosynthesis, docking_simulation
    ],
    "middleware": [ChemistryMiddleware()]
}

physics_expert = {
    "name": "physics-expert",
    "description": "Expert in computational physics: simulations, mathematical modeling, and numerical analysis.",
    "system_prompt": """You are a computational physics expert...""",
    "tools": [
        symbolic_math, numerical_integration, differential_equation_solver,
        simulation_runner
    ],
    "middleware": [PhysicsMiddleware()]
}
```

#### Grant Writer
```python
grant_writer = {
    "name": "grant-writer",
    "description": "Expert in writing grant proposals, research statements, and funding applications.",
    "system_prompt": """You are a grant writing expert. Your role is to:
    1. Draft compelling research proposals
    2. Articulate significance and innovation
    3. Write clear specific aims and methodologies
    4. Address feasibility and preliminary data
    5. Format according to funder requirements
    6. Incorporate budget justifications

    Store grant drafts in /grants/ with version history
    Track requirements and submission deadlines
    """,
    "tools": [
        format_latex_document, generate_abstract, cite_paper,
        format_bibliography, check_scientific_writing
    ],
    "middleware": [
        ScientificWritingMiddleware(),
        CitationManagementMiddleware(),
    ]
}
```

### 3. Main Co-Scientist Agent System Prompt

```python
CO_SCIENTIST_SYSTEM_PROMPT = """You are a Co-Scientist AI Assistant, designed to work alongside scientists throughout the entire research lifecycle. You have access to comprehensive tools and specialized subagents to help with:

## Your Capabilities

### 1. Literature Review & Research
- Search scientific databases (PubMed, arXiv, Semantic Scholar)
- Retrieve and analyze scientific papers
- Identify research gaps and trends
- Manage citations and references

### 2. Experimental Design
- Design rigorous experiments and protocols
- Perform power analysis and sample size calculations
- Suggest appropriate controls and methodologies
- Generate detailed experimental protocols

### 3. Data Analysis
- Execute Python code for statistical analysis
- Create publication-quality visualizations
- Perform hypothesis testing
- Build predictive models

### 4. Scientific Writing
- Draft scientific papers, grants, and reports
- Format documents in LaTeX or Markdown
- Manage citations and references
- Generate figures and tables

### 5. Domain-Specific Expertise
- Bioinformatics: sequence analysis, protein structure, genomics
- Chemistry: molecular modeling, reaction prediction, property calculations
- Physics: simulations, mathematical modeling, numerical analysis

## Workflow Philosophy

You are designed to assist with long-term research projects. Use the filesystem to:
- Store papers in `/papers/`
- Save experimental protocols in `/protocols/`
- Store datasets in `/data/`
- Save figures in `/figures/`
- Maintain manuscript drafts in `/manuscript/`
- Track references in `/references/library.bib`
- Document hypotheses in `/hypotheses.md`
- Keep a research journal in `/research_journal.md`

## Using Subagents

You have access to specialized subagents for deep, focused work:

- **literature-reviewer**: Comprehensive literature reviews
- **data-analyst**: Statistical analysis and visualization
- **experimental-designer**: Experiment and protocol design
- **scientific-writer**: Paper writing and formatting
- **hypothesis-generator**: Generate testable hypotheses
- **bioinformatics-expert**: Bioinformatics analysis
- **chemistry-expert**: Computational chemistry
- **physics-expert**: Computational physics
- **grant-writer**: Grant proposal writing

Delegate complex, multi-step tasks to appropriate subagents to keep your context clean.

## Research Project Management

For long-term projects:
1. Create a project plan at `/project_plan.md`
2. Track progress with todos and milestones
3. Document all decisions and rationale
4. Maintain reproducibility by saving code and parameters
5. Version control protocols and manuscripts
6. Keep comprehensive notes in `/research_journal.md`

## Best Practices

1. **Systematic Approach**: Break down research questions into manageable tasks
2. **Document Everything**: Store all information in the filesystem for future reference
3. **Reproducibility**: Document analysis steps, code, and parameters
4. **Critical Thinking**: Question assumptions, consider alternatives, identify limitations
5. **Citation Management**: Always cite sources and maintain proper references
6. **Human Collaboration**: Ask for clarification when needed, seek human approval for critical decisions

You are not here to replace scientists, but to amplify their capabilities and handle time-consuming tasks efficiently.
"""
```

### 4. Creating the Co-Scientist Agent

```python
from deepagents import create_deep_agent
from langgraph.store.memory import InMemoryStore

# Define all specialized subagents
subagents = [
    literature_reviewer,
    data_analyst,
    experimental_designer,
    scientific_writer,
    hypothesis_generator,
    bioinformatics_expert,
    chemistry_expert,
    physics_expert,
    grant_writer,
]

# Create Co-Scientist agent with all middleware and subagents
co_scientist = create_deep_agent(
    model="claude-sonnet-4-5-20250929",  # Or other capable model
    tools=[
        # Additional tools can be added here
    ],
    system_prompt=CO_SCIENTIST_SYSTEM_PROMPT,
    middleware=[
        LiteratureSearchMiddleware(),
        DataAnalysisMiddleware(),
        VisualizationMiddleware(),
        CitationManagementMiddleware(),
        ExperimentalDesignMiddleware(),
        BioinformaticsMiddleware(),
        ChemistryMiddleware(),
        PhysicsMiddleware(),
        ScientificWritingMiddleware(),
    ],
    subagents=subagents,
    use_longterm_memory=True,
    store=InMemoryStore(),  # Or PostgreSQL/Redis store for production
    interrupt_on={
        "execute_python_code": True,  # Human approval for code execution
        "download_paper": False,       # Auto-approve paper downloads
        # Add other sensitive operations
    }
)
```

---

## Implementation Roadmap

### Phase 1: Foundation (Weeks 1-2)

**Goal:** Set up core scientific middleware infrastructure

**Tasks:**
1. Create `LiteratureSearchMiddleware`
   - Integrate PubMed API
   - Integrate arXiv API
   - Integrate Semantic Scholar API
   - PDF parsing (PyMuPDF, pdfplumber)
   - Citation extraction

2. Create `DataAnalysisMiddleware`
   - Set up sandboxed Python execution (RestrictedPython or Docker)
   - Install scientific libraries (numpy, pandas, scipy, sklearn)
   - Implement result caching
   - Set up security restrictions

3. Create `VisualizationMiddleware`
   - Matplotlib/Seaborn integration
   - Figure saving to filesystem
   - Publication-quality settings

4. Create `CitationManagementMiddleware`
   - BibTeX generation and parsing
   - Citation formatting
   - Reference storage in long-term memory

**Deliverables:**
- 4 new middleware classes
- Integration tests for each
- Example usage documentation

### Phase 2: Specialized Subagents (Weeks 3-4)

**Goal:** Implement core subagents

**Tasks:**
1. Literature Reviewer subagent
   - System prompt tuning
   - Tool integration
   - Example workflows

2. Data Analyst subagent
   - Statistical analysis workflows
   - Visualization examples
   - Result interpretation prompts

3. Experimental Designer subagent
   - Power analysis tools
   - Protocol generation templates
   - Safety checking rules

4. Scientific Writer subagent
   - LaTeX formatting
   - Section writing templates
   - Citation management integration

**Deliverables:**
- 4 fully functional subagents
- Example research workflows
- Unit and integration tests

### Phase 3: Domain-Specific Tools (Weeks 5-6)

**Goal:** Add domain-specific scientific capabilities

**Tasks:**
1. `BioinformaticsMiddleware`
   - NCBI BLAST integration
   - Sequence alignment (Biopython)
   - Protein structure prediction (AlphaFold API if available)

2. `ChemistryMiddleware`
   - RDKit integration
   - SMILES processing
   - Molecular property calculations

3. `PhysicsMiddleware`
   - SymPy for symbolic math
   - SciPy for numerical methods
   - Simulation frameworks

4. Domain expert subagents for each field

**Deliverables:**
- 3 domain-specific middleware classes
- 3 domain expert subagents
- Domain-specific example notebooks

### Phase 4: Advanced Features (Weeks 7-8)

**Goal:** Polish user experience and add advanced features

**Tasks:**
1. `ExperimentalDesignMiddleware` enhancements
   - DOE (Design of Experiments) tools
   - Randomization schemes
   - Sample size calculators

2. `ScientificWritingMiddleware` improvements
   - LaTeX template library
   - Grammar checking integration
   - Revision suggestion system

3. Grant Writer subagent
   - Grant-specific prompts
   - Template library
   - Budget tools

4. Research project management features
   - Milestone tracking
   - Timeline visualization
   - Collaboration features

**Deliverables:**
- Enhanced middleware with advanced features
- Grant writer subagent
- Project management tools
- User documentation

### Phase 5: Testing & Documentation (Week 9-10)

**Goal:** Comprehensive testing and documentation

**Tasks:**
1. End-to-end testing
   - Full research workflow tests
   - Integration tests across middleware
   - Performance benchmarking

2. Documentation
   - API reference
   - Tutorial notebooks
   - Example research projects
   - Best practices guide

3. Example projects
   - Complete literature review example
   - Data analysis workflow example
   - Full paper writing example
   - Domain-specific case studies

4. Deployment preparation
   - Docker containers
   - Configuration templates
   - Production deployment guide

**Deliverables:**
- Comprehensive test suite
- Complete documentation website
- 4+ example research projects
- Production-ready deployment

---

## Example Use Cases

### Use Case 1: Comprehensive Literature Review

```python
# User initiates a literature review
result = co_scientist.invoke({
    "messages": [{
        "role": "user",
        "content": "I need a comprehensive literature review on CRISPR gene editing applications in cancer therapy from the last 5 years. Focus on clinical trials and their outcomes."
    }]
})

# Behind the scenes:
# 1. Main agent creates a plan using write_todos
# 2. Delegates to literature-reviewer subagent
# 3. Subagent searches PubMed, arXiv, Semantic Scholar
# 4. Downloads and parses ~50 relevant papers
# 5. Extracts key findings, methodologies, results
# 6. Stores papers in /papers/
# 7. Builds citation library in /references/library.bib
# 8. Generates comprehensive review in /literature_review.md
# 9. Returns summary to user with key findings and research gaps
```

### Use Case 2: Data Analysis and Visualization

```python
# User provides experimental data
result = co_scientist.invoke({
    "messages": [{
        "role": "user",
        "content": """I have RNA-seq data in /data/rnaseq_counts.csv.
        Please perform differential expression analysis between control and treatment groups,
        create a volcano plot, and identify the top 20 differentially expressed genes."""
    }]
})

# Behind the scenes:
# 1. Main agent delegates to data-analyst subagent
# 2. Subagent reads the CSV file
# 3. Executes Python code for DESeq2-like analysis
# 4. Performs statistical testing (multiple testing correction)
# 5. Creates volcano plot and saves to /figures/volcano_plot.png
# 6. Generates results table and saves to /results/deg_table.csv
# 7. Interprets biological significance of findings
# 8. Returns summary with key differentially expressed genes
```

### Use Case 3: Experimental Design

```python
# User needs help designing an experiment
result = co_scientist.invoke({
    "messages": [{
        "role": "user",
        "content": """I want to test if drug X inhibits cancer cell proliferation.
        I have 3 cell lines available and can test 5 different drug concentrations.
        Help me design a rigorous experiment with appropriate controls."""
    }]
})

# Behind the scenes:
# 1. Main agent delegates to experimental-designer subagent
# 2. Subagent asks clarifying questions (available resources, timeline)
# 3. Performs power analysis to determine sample size
# 4. Designs factorial experiment (3 cell lines × 6 conditions including control)
# 5. Suggests positive/negative controls
# 6. Creates randomization scheme
# 7. Generates detailed protocol in /protocols/drug_screening_protocol.md
# 8. Identifies potential confounds and mitigation strategies
# 9. Returns protocol with rationale and expected outcomes
```

### Use Case 4: Scientific Paper Writing

```python
# User wants to write a paper
result = co_scientist.invoke({
    "messages": [{
        "role": "user",
        "content": """Help me write a scientific paper based on my research.
        The literature review is in /literature_review.md,
        experimental protocol in /protocols/experiment.md,
        and results in /results/. Format it as a LaTeX document."""
    }]
})

# Behind the scenes:
# 1. Main agent reviews all available materials
# 2. Delegates to scientific-writer subagent
# 3. Subagent generates paper structure:
#    - Abstract (150-200 words)
#    - Introduction (citing relevant literature)
#    - Methods (based on protocol)
#    - Results (incorporating figures/tables)
#    - Discussion (interpreting findings)
#    - References (from /references/library.bib)
# 4. Formats as LaTeX document in /manuscript/main.tex
# 5. Creates separate files for figures and tables
# 6. Returns draft for user review
# 7. Can iterate with user feedback
```

### Use Case 5: Bioinformatics Analysis

```python
# User has a protein sequence to analyze
result = co_scientist.invoke({
    "messages": [{
        "role": "user",
        "content": """I discovered a novel protein sequence. Please:
        1. Run BLAST to find homologs
        2. Predict its 3D structure
        3. Identify functional domains
        4. Suggest possible functions based on homology"""
    }]
})

# Behind the scenes:
# 1. Main agent delegates to bioinformatics-expert subagent
# 2. Subagent performs BLAST search against nr database
# 3. Identifies top homologs and extracts alignment
# 4. Calls protein structure prediction tool
# 5. Performs domain analysis
# 6. Searches literature for homolog functions
# 7. Generates comprehensive analysis report in /analysis/protein_analysis.md
# 8. Saves structure file to /structures/predicted_structure.pdb
# 9. Returns summary with predicted function and confidence
```

### Use Case 6: Long-term Research Project

```python
# Multi-month research project with memory
# Week 1: Literature review
co_scientist.invoke({
    "messages": [{"role": "user", "content": "Start a project on neurodegenerative disease mechanisms. Begin with a literature review."}]
}, config={"configurable": {"thread_id": "project_001"}})

# Week 2: Hypothesis generation (remembers previous work)
co_scientist.invoke({
    "messages": [{"role": "user", "content": "Based on the literature review, generate 3 testable hypotheses about protein aggregation."}]
}, config={"configurable": {"thread_id": "project_001"}})

# Week 4: Experimental design (remembers hypotheses)
co_scientist.invoke({
    "messages": [{"role": "user", "content": "Design experiments to test hypothesis 2."}]
}, config={"configurable": {"thread_id": "project_001"}})

# Week 12: Data analysis (remembers entire project context)
co_scientist.invoke({
    "messages": [{"role": "user", "content": "Analyze the experimental results in /data/experiment_results.csv"}]
}, config={"configurable": {"thread_id": "project_001"}})

# Week 16: Paper writing (full project memory)
co_scientist.invoke({
    "messages": [{"role": "user", "content": "Write a paper summarizing our findings."}]
}, config={"configurable": {"thread_id": "project_001"}})

# Behind the scenes:
# - Long-term memory stores all previous conversations
# - Filesystem stores all documents, data, protocols
# - Agent can reference any previous work
# - Maintains project timeline and milestones
```

---

## Technical Considerations

### Security

1. **Sandboxed Execution**
   - Use Docker containers or RestrictedPython for code execution
   - Limit network access from sandbox
   - Restrict file system access
   - Set memory and CPU limits
   - Timeout for long-running operations

2. **Data Privacy**
   - Ensure sensitive research data is not logged
   - Use local deployment for confidential projects
   - Implement access controls
   - Encrypt long-term memory storage

3. **API Key Management**
   - Secure storage of API keys (PubMed, arXiv, etc.)
   - Rate limiting for external APIs
   - Cost monitoring for LLM calls

### Performance

1. **Caching**
   - Cache paper searches and downloads
   - Cache expensive computations
   - Use Anthropic prompt caching for repeated prompts

2. **Parallel Execution**
   - Run independent subagents in parallel
   - Parallel literature searches
   - Batch API calls when possible

3. **Context Management**
   - Aggressive use of filesystem to offload context
   - Summarization for long research projects
   - Strategic subagent delegation

### Reproducibility

1. **Version Control**
   - Track protocol versions
   - Version data analysis code
   - Maintain change logs

2. **Documentation**
   - Automatic logging of all operations
   - Research journal with timestamps
   - Parameter tracking for analyses

3. **Data Management**
   - Structured file organization
   - Metadata for all datasets
   - Link data to analyses and figures

---

## Success Metrics

### Functionality
- ✅ Can perform comprehensive literature reviews (>50 papers)
- ✅ Can execute and interpret statistical analyses
- ✅ Can generate publication-quality figures
- ✅ Can design rigorous experiments with power analysis
- ✅ Can write scientific paper sections with proper citations
- ✅ Can perform domain-specific analyses (bio/chem/physics)

### Performance
- ✅ Literature review completion: <30 minutes for 50 papers
- ✅ Data analysis execution: <5 minutes for typical datasets
- ✅ Paper draft generation: <20 minutes for complete draft
- ✅ Experiment design: <15 minutes for detailed protocol

### User Experience
- ✅ Intuitive interaction for scientists without AI expertise
- ✅ Clear progress tracking with todos
- ✅ Well-organized filesystem structure
- ✅ Reproducible results
- ✅ Helpful error messages and suggestions

### Reliability
- ✅ Accurate citation formatting (>95% correct)
- ✅ Valid statistical analyses (verified by experts)
- ✅ Secure code execution (no security breaches)
- ✅ Consistent outputs across runs

---

## Conclusion

This design transforms DeepAgents into a comprehensive Co-Scientist Agent System by:

1. **Leveraging existing strengths**: Planning, filesystem, subagents, long-term memory
2. **Adding scientific middleware**: Literature search, data analysis, visualization, citations, experimental design, domain tools
3. **Creating specialized subagents**: 9+ expert subagents for different research tasks
4. **Maintaining modularity**: Each component can be used independently or together
5. **Ensuring extensibility**: Easy to add new domains, tools, or subagents

The resulting system can assist scientists throughout the entire research lifecycle, from initial literature review to final paper submission, while maintaining rigor, reproducibility, and scientific best practices.

**Next Steps:**
1. Review and approve this design
2. Begin Phase 1 implementation
3. Gather feedback from scientists in target domains
4. Iterate and refine based on real-world usage
