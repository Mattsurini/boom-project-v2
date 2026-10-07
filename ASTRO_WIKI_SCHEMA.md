# Astrology Wiki Schema

This document defines the structure and conventions for the Boom Project Astrology Wiki, following the LLM Wiki pattern from Karpathy's gist.

## Wiki Structure

```
E:\Boom Project\
├── wiki/                     # LLM-generated markdown knowledge base
│   ├── index.md              # Content-oriented catalog
│   ├── log.md                # Chronological record of operations
│   ├── entities/             # Planet, sign, house, aspect definitions
│   │   ├── sun.md
│   │   ├── moon.md
│   │   ├── mercury.md
│   │   ├── venus.md
│   │   ├── mars.md
│   │   ├── jupiter.md
│   │   ├── saturn.md
│   │   ├── rahu.md
│   │   ├── ketu.md
│   │   ├── aries.md
│   │   ├── taurus.md
│   │   ├── gemini.md
│   │   ├── cancer.md
│   │   ├── leo.md
│   │   ├── virgo.md
│   │   ├── libra.md
│   │   ├── scorpio.md
│   │   ├── sagittarius.md
│   │   ├── capricorn.md
│   │   ├── aquarius.md
│   │   ├── pisces.md
│   │   ├── first-house.md
│   │   ├── second-house.md
│   │   ├── ...               # all 12 houses
│   │   ├── conjunction.md
│   │   ├── opposition.md
│   │   ├── trine.md
│   │   ├── square.md
│   │   └── sextile.md
│   ├── concepts/             # Higher-level astrological concepts
│   │   ├── dasha-system.md
│   │   ├── nakshatras.md
│   │   ├── yogas.md
│   │   ├── transits.md
│   │   ├── aspects.md
│   │   ├── strengths.md
│   │   └── weaknesses.md
│   ├── sources/              # Source document summaries
│   │   ├── vedic-classics/
│   │   ├── western-astrology/
│   │   ├── financial-astrology/
│   │   └── jaimini/
│   ├── syntheses/            # Integrated understanding pages
│   │   ├── career-guidelines.md
│   │   ├── relationship-patterns.md
│   │   ├── health-indicators.md
│   │   └── spiritual-path.md
│   └── explorations/         # User queries filed back as knowledge
│       ├── venus-in-libra-career.md
│       └── saturn-transit-7th-house.md
└── Knowledge/                # Immutable raw sources (unchanged)
    ├── Astrology-Database/
    ├── Chinese-Astrology/
    └── ...                   # existing structure
```

## Naming Conventions

- All filenames use lowercase with hyphens as separators
- Entity pages: `[planet|sign|house|aspect].md`
- Concept pages: `descriptive-name.md`
- Source summaries: `[tradition|topic]/[source-name].md`
- Synthesis pages: `topic-area.md`
- Exploration pages: `specific-question-topic.md`

## Page Format

Each wiki page should include:

```markdown
# Page Title

## Summary
2-3 sentence overview of the topic.

## Key Points
- Bullet point summary of essential information
- Extracted from sources and synthesized

## Details
### From Sources
- Specific information attributed to particular sources
- Format: `[Source Tradition/Name]: Specific detail`

### Traditions Covered
- Vedic: [bullet points]
- Western: [bullet points]
- etc.

## Cross-References
- Links to related wiki pages using `[[Page Name]]` syntax
- Example: See also [[Venus]], [[7th House]], [[Conjunction]]

## Contradictions & Open Questions
- Note any conflicting information between sources
- Areas requiring further research

## Last Updated
- Date: YYYY-MM-DD
- Sources consulted: [list]
```

## Operations

### Ingest
When adding a new source:
1. Read and understand the source material
2. Create/update source summary in `wiki/sources/[tradition]/[name].md`
3. Extract key facts and update relevant entity/concept pages
4. Update cross-references and contradictions sections
5. Add entry to `log.md`
6. Update `index.md`

### Query
When answering questions:
1. Consult `index.md` to find relevant pages
2. Read those pages and synthesize answer
3. Provide citations to wiki pages
4. Optionally file the Q&A as an exploration page

### Lint
Periodically:
1. Check for contradictions between pages
2. Identify orphan pages (no inbound links)
3. Find important concepts lacking their own page
4. Update stale claims with newer information
5. Suggest new sources to consult

## Source Attribution

When extracting information:
- Use format: `[Tradition/Source]: Detail`
- For specific texts: `[Brihat Parashara Hora Shastra]: Detail`
- For authors: `[Author Name, Tradition]: Detail`
- For general consensus: `[Multiple Sources]: Detail`

## Wiki Maintenance Principles

1. **LLM Owns the Wiki**: The LLM creates and updates all wiki content
2. **Human Guides**: User selects sources, asks questions, validates important changes
3. **Compound Knowledge**: Each source makes the wiki more valuable, not just adds to it
4. **Traceability**: All information should be traceable to sources
5. **Consistency**: Cross-references maintained, contradictions noted