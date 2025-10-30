# Deep Research System

A comprehensive multi-agent research system designed for thorough, high-quality research with detailed citation tracking, quality assessment, and iterative refinement.

## Overview

This system implements a hierarchical multi-agent architecture inspired by:
- **Cursor/Composer's** structured agent design and clear role definitions
- **Anthropic's** multi-agent research system patterns
- **LangGraph's** hierarchical supervisor coordination
- **Academic citation management** best practices

## Architecture

### Head Researcher (Main Agent)
Coordinates the entire research process, delegating tasks to specialized subagents and ensuring quality through iterative refinement.

### Specialized Subagents

1. **Search Specialist**
   - Executes targeted web searches
   - Optimizes search queries for maximum relevance
   - Documents findings with clear summaries
   - Tools: `internet_search`, `deep_search`

2. **Citation Manager**
   - Maintains comprehensive citation database
   - Tracks DOI, authors, publication dates, URLs
   - Documents WHY each source was used and WHAT was extracted
   - Assesses source reliability
   - Output: `citations.json`

3. **Deep Analyzer**
   - Analyzes findings for insights and patterns
   - Performs critical evaluation of evidence
   - Identifies trends across sources
   - Notes gaps and limitations
   - Output: `analysis.md`

4. **Quality Assessor**
   - Evaluates research completeness and accuracy
   - Performs systematic quality checks
   - Identifies biases and gaps
   - Provides actionable improvement recommendations
   - Output: `quality_report.md`

5. **Synthesis Agent**
   - Integrates findings into coherent narratives
   - Builds logical connections between ideas
   - Creates clear information flow
   - Output: `synthesis.md`

6. **Report Writer**
   - Creates polished, professional reports
   - Ensures proper formatting and structure
   - Integrates citations correctly
   - Output: `final_report.md`

## Research Workflow

### Phase 1: Planning and Initial Research
1. Save research question to `research_question.txt`
2. Create research plan in `research_plan.md`
3. Execute parallel searches with focused sub-questions

### Phase 2: Documentation and Analysis
4. Consolidate findings in `findings.md`
5. Track citations in `citations.json` (with full metadata)
6. Generate deep analysis in `analysis.md`

### Phase 3: Quality Assurance
7. Perform quality assessment
8. Address identified gaps
9. Iterate until quality is satisfactory

### Phase 4: Synthesis and Reporting
10. Synthesize information into coherent narrative
11. Write polished final report
12. Final quality check and refinement

## Key Features

### Detailed Citation Tracking

Citations include:
- **Bibliographic Info**: Title, URL, DOI, authors, dates, publisher
- **Usage Context**: Why the source was used, what information was extracted
- **Quality Assessment**: Reliability score and notes
- **Metadata**: Content type, access date, publication details

Example citation structure:
```json
{
  "id": 1,
  "title": "AI in Healthcare: A Comprehensive Review",
  "url": "https://example.com/article",
  "doi": "10.1000/example.2024",
  "authors": ["Smith, J.", "Johnson, A."],
  "publication_date": "2024-03-15",
  "publisher": "Journal of Medical AI",
  "content_type": "journal article",
  "why_used": "Provides evidence for AI diagnostic accuracy improvements",
  "what_extracted": "Meta-analysis showing 15% improvement in diagnostic accuracy",
  "reliability_score": "high"
}
```

### Quality Assurance Framework

Multi-dimensional assessment:
- **Completeness**: Coverage of all aspects
- **Accuracy**: Fact verification and citation quality
- **Evidence Quality**: Source reliability and authority
- **Analysis Depth**: Insight quality and pattern recognition
- **Structure**: Organization and clarity
- **Bias Check**: Balance and objectivity

### Parallel Execution

The system leverages parallel agent calls for efficiency:
```python
# Instead of sequential searches:
# search("AI diagnostics") -> search("AI costs") -> search("patient outcomes")

# Call search-specialist multiple times in parallel:
# search("AI diagnostics") + search("AI costs") + search("patient outcomes")
```

### Iterative Refinement

Quality-driven iteration loop:
1. Initial research and analysis
2. Quality assessment identifies gaps
3. Targeted additional research
4. Re-analysis and synthesis
5. Quality verification
6. Final report generation

## Usage

### Basic Usage

```python
from examples.deep_research_system import create_deep_research_agent

# Create the agent
agent = create_deep_research_agent()

# Run research
config = {"configurable": {"thread_id": "research-session-1"}}

# Ask a research question
result = agent.invoke(
    {
        "messages": [
            {
                "role": "user",
                "content": "Research the impact of AI on healthcare in 2024-2025"
            }
        ]
    },
    config=config,
)

# The agent will:
# 1. Create a research plan
# 2. Execute parallel searches
# 3. Track all citations with detailed metadata
# 4. Perform deep analysis
# 5. Assess quality and iterate if needed
# 6. Synthesize findings
# 7. Generate a polished final report
```

### Advanced Usage

```python
from langchain_core.messages import HumanMessage
from examples.deep_research_system import create_deep_research_agent

agent = create_deep_research_agent()

config = {
    "configurable": {
        "thread_id": "research-session-advanced"
    }
}

# Complex research question
messages = [
    HumanMessage(
        content="""
        Conduct deep research on the following question:

        "What are the most promising applications of quantum computing
        in drug discovery, and what are the current limitations?"

        Please ensure:
        - Comprehensive coverage of applications
        - Analysis of technical limitations
        - Assessment of timeline to practical use
        - Comparison with classical computing approaches
        - Expert perspectives from academia and industry
        """
    )
]

result = agent.invoke({"messages": messages}, config=config)

# Access the final report
print(result["messages"][-1].content)
```

### Accessing Research Artifacts

The system creates structured files during research:

```python
# After research is complete, you can access:

# 1. Research plan
# Shows the strategy and sub-questions

# 2. Citations database
import json
with open("citations.json") as f:
    citations = json.load(f)
    for citation in citations["citations"]:
        print(f"{citation['id']}: {citation['title']}")
        print(f"  Why used: {citation['why_used']}")
        print(f"  What extracted: {citation['what_extracted']}")

# 3. Deep analysis
# Contains insights, patterns, critical assessment

# 4. Quality reports
# Shows assessment results and recommendations

# 5. Final report
# The polished research output with proper citations
```

## File Structure

The system creates and maintains these files:

```
research_question.txt      # Original research question
research_plan.md          # Research strategy and sub-questions
findings.md              # Consolidated search results
citations.json           # Detailed citation database
analysis.md             # Deep analysis with insights
quality_report.md       # Quality assessment results
synthesis.md           # Synthesized narrative
final_report.md        # Final polished report
```

## Best Practices

### 1. Question Formulation
- Be specific about what you want to know
- Indicate desired scope (overview, comparison, deep dive)
- Specify any particular angles or perspectives needed

### 2. Research Depth
- For quick overviews: The system will be efficient
- For comprehensive research: Be patient, quality takes time
- For specialized topics: Provide context in your question

### 3. Citation Quality
- The system automatically tracks all sources
- DOI information is captured when available
- Usage context ensures citations are meaningful
- Reliability scoring helps assess source quality

### 4. Iterative Improvement
- The system may iterate multiple times for quality
- This is normal for complex research questions
- Quality assessment drives improvements
- Final output is thoroughly vetted

### 5. Language Support
- Ask your question in any language
- The final report will be in the same language
- Citations and URLs remain in original language
- Analysis is language-aware

## Design Principles

### 1. Clear Role Separation
Each agent has a specific, focused role inspired by Cursor's clear task delegation:
- Search agents search
- Citation agents track sources
- Analysis agents analyze
- Quality agents assess
- Synthesis agents integrate
- Writing agents write

### 2. Context Engineering
Following multi-agent best practices:
- Each agent receives appropriate context
- Task descriptions are specific and actionable
- Output formats are clearly defined
- Handoffs between agents are structured

### 3. Token Efficiency
Based on research showing token usage drives performance:
- Parallel searches maximize information gathering
- Specialized agents focus token usage
- Iterative refinement spends tokens on quality
- Synthesis reduces redundancy

### 4. Quality First
Inspired by deep research agent frameworks:
- Systematic quality assessment
- Introspection loops
- Fact verification
- Source credibility evaluation
- Iterative refinement

### 5. Citation Excellence
Following academic standards:
- Complete bibliographic information
- DOI tracking for academic sources
- Usage documentation (why/what)
- Reliability assessment
- Proper formatting

## Comparison with Basic Research Agent

| Feature | Basic Research Agent | Deep Research System |
|---------|---------------------|---------------------|
| Agents | 2 (researcher, critic) | 6 specialized agents |
| Citation Tracking | Basic URLs | Full metadata + DOI + usage context |
| Quality Process | Single critique | Multi-phase quality assessment |
| Analysis Depth | Summary level | Deep analysis with patterns/insights |
| Workflow | Linear | Iterative with quality loops |
| Source Documentation | Title + URL | Complete bibliographic + usage + reliability |
| Parallel Execution | Limited | Optimized for parallelization |
| Introspection | Basic | Systematic multi-dimensional |

## Requirements

```bash
pip install deepagents tavily-python langchain langchain-anthropic langgraph
```

Environment variables:
```bash
export ANTHROPIC_API_KEY="your-key"
export TAVILY_API_KEY="your-key"
```

## Advanced Configuration

### Custom Model

```python
from langchain_anthropic import ChatAnthropic

agent = create_deep_agent(
    model=ChatAnthropic(model_name="claude-sonnet-4-5-20250929", max_tokens=30000),
    # ... other parameters
)
```

### Custom Backend for Persistence

```python
from deepagents.backends.filesystem import FilesystemBackend

agent = create_deep_agent(
    backend=FilesystemBackend(root_dir="./my_research"),
    # ... other parameters
)
```

## Troubleshooting

### Issue: Citations missing DOI
**Solution**: DOI may not be available for all sources (e.g., blog posts, news articles). The system will still track comprehensive metadata.

### Issue: Quality assessment requests more research
**Solution**: This is normal. The system is thorough. It will iterate until quality is satisfactory.

### Issue: Research takes longer than expected
**Solution**: Deep research requires time. The system is optimizing for quality over speed. For faster results, ask more specific questions.

### Issue: Too many sources
**Solution**: The citation manager tracks all sources. This is intentional for transparency and reproducibility.

## Examples

See `deep_research_examples.py` for complete examples including:
- Technology research (AI in healthcare)
- Comparative analysis (quantum vs classical computing)
- Trend analysis (climate tech developments)
- Market research (emerging technologies)

## Contributing

When extending this system:
1. Maintain clear agent role separation
2. Follow the established file structure
3. Update citation tracking for new sources
4. Add quality assessment criteria for new domains
5. Document new agents thoroughly

## License

Same as deepagents package.

## Acknowledgments

This system synthesizes best practices from:
- Anthropic's multi-agent research systems
- Cursor/Composer's agent architecture
- LangGraph's hierarchical patterns
- Academic research workflows
- Professional citation management systems

The design emphasizes quality, thoroughness, and transparency in AI-assisted research.
