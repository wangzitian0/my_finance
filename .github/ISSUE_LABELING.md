# Automated Issue Labeling (Updated for Issue #279 Module Architecture)

This repository uses an automated GitHub workflow to intelligently apply labels to issues based on their title and content, following the new L1/L2 business module structure from Issue #279.

## How It Works

The workflow (`.github/workflows/auto-label-issues.yml`) triggers when issues are:
- Opened
- Edited

It analyzes the issue title and body content to automatically apply relevant labels from the following **mutually exclusive** categories designed to eliminate label redundancy and conflicts.

## Label Categories (Module-Aware)

### Priority Labels (Mutually Exclusive)
- **`priority:P0`** - Critical priority - immediate action
  - Keywords: `critical`, `urgent`, `emergency`, `broken`, `production down`, `security`, `data loss`, `corruption`, `crash`, `failure`, `immediate`
- **`priority:P1`** - High priority
  - Keywords: `important`, `high priority`, `blocking`, `regression`, `major bug`, `performance`, `memory leak`, `timeout`, `error`, `exception`
- **`priority:P2`** - Medium priority (default)
- **`priority:P3`** - Low priority
  - Keywords: `nice to have`, `low priority`, `minor`, `cosmetic`

### Type Labels (Mutually Exclusive)
- **`type:bug`** - Error fixes
  - Keywords: `bug`, `error`, `issue`, `problem`, `fix`, `broken`, `incorrect`, `fail`, `exception`, `crash`, `not working`
  - Prefix: `[BUG]`
- **`type:feature`** - New functionality
  - Keywords: `feature`, `enhancement`, `implement`, `add`, `create`, `new`, `improve`, `extend`, `support`
  - Prefix: `[Feature]`
- **`type:enhancement`** - Improvements to existing features
  - Keywords: `enhance`, `update`, `upgrade`, `optimize`, `better`
  - Prefix: `[Enhancement]`
- **`type:docs`** - Documentation updates
  - Keywords: `documentation`, `doc`, `readme`, `guide`, `tutorial`, `example`, `comment`, `explain`, `clarify`
  - Prefix: `[Documentation]` or `[Doc`
- **`type:refactor`** - Code refactoring
  - Keywords: `refactor`, `cleanup`, `reorganize`, `restructure`, `simplify`, `architecture`
  - Prefix: `[Refactor]`
- **`type:adr`** - Architecture Decision Record
  - Keywords: `adr`, `architecture decision`, `decision record`, `design decision`
  - Prefix: `[ADR]`

### L1 Business Module Labels (Mutually Exclusive - Based on Issue #279)
- **`module:ETL`** - Data processing pipeline issues
  - Keywords: `etl`, `etl pipeline`, `spider`, `parser`, `extraction`, `transform`, `semantic embedding`, `data processing`, `sec_filing_processor`, `embedding_generator`, `crawlers`, `schedulers`, `loaders`
- **`module:engine`** - Graph-RAG investment analysis engine
  - Keywords: `engine`, `graph rag`, `graph_rag`, `semantic retrieval`, `vector search`, `retrieval-augmented generation`, `rag system`, `dcf`, `valuation`, `dcf_engine`, `financial`, `calculation`, `retrieval`, `reasoning`, `reporting`
- **`module:evaluation`** - Strategy validation system
  - Keywords: `evaluation`, `backtesting`, `metrics`, `benchmarks`, `strategy validation`, `performance testing`
- **`module:common`** - Unified system architecture
  - Keywords: `common`, `core`, `config`, `templates`, `tools`, `database`, `schemas`, `types`, `utils`, `data storage`, `storage`, `directory`, `file system`, `data layer`
- **`module:infra`** - Infrastructure and system management
  - Keywords: `infrastructure`, `infra`, `docker`, `container`, `podman`, `deployment`, `environment`, `setup`, `ansible`, `pixi`, `p3`, `hrbp`, `development`, `ci`, `cd`, `github action`, `github workflow`, `automation`, `build pipeline`

### Status Labels (Mutually Exclusive)
- **`status:needs-triage`** - Needs initial assessment
  - Keywords: `need`, `question`, `unclear`, `investigate`, `research`, `help wanted`
- **`status:ready`** - Ready to start work
  - Keywords: `ready`, `approved`, `go ahead`
- **`status:in-progress`** - Work in progress
  - Keywords: `working on`, `in progress`, `started`
- **`status:blocked`** - Blocked by dependencies
  - Keywords: `blocked`, `waiting for`, `dependency`, `depends on`, `prerequisite`
- **`status:review`** - Waiting for review
  - Keywords: `review`, `feedback`, `check`

### Effort Labels (Mutually Exclusive)
- **`effort:small`** - Small effort (< 1 day)
  - Keywords: `quick`, `simple`, `minor`, `small`
- **`effort:medium`** - Medium effort (1-3 days)
  - Keywords: `enhance`, `extend`, `integration`, `medium`
  - Also applied to medium-length issues (>800 characters)
- **`effort:large`** - Large effort (> 3 days)
  - Keywords: `major refactor`, `migration`, `restructure`, `major`, `complete overhaul`, `system overhaul`, `large effort`
  - Also applied to very long issues (>1500 characters)

### Scope Labels (Mutually Exclusive - Optional)
- **`scope:f2`** - Development testing (2 companies)
  - Keywords: `f2`, `development`, `dev test`, `2 companies`
- **`scope:m7`** - Integration testing (7 companies)
  - Keywords: `m7`, `integration`, `7 companies`
- **`scope:n100`** - Production validation (100 companies)
  - Keywords: `n100`, `validation`, `100 companies`
- **`scope:v3k`** - Full production (3000+ companies)
  - Keywords: `v3k`, `production`, `3000`

### Agent Labels (Can be combined)
- **`agent:coordinator`** - Agent coordinator
  - Keywords: `coordinator`, `orchestration`, `multi-agent`
- **`agent:data-engineer`** - Data engineer agent
  - Keywords: `data engineer`, `etl agent`
- **`agent:quant-research`** - Quantitative research agent
  - Keywords: `quant research`, `quantitative`, `research`
- **`agent:infra-ops`** - Infrastructure operations agent
  - Keywords: `infra ops`, `infrastructure ops`, `p3`
- **`agent:dev-quality`** - Development quality agent
  - Keywords: `dev quality`, `quality`, `testing`

## Workflow Features

### Smart Detection
- **Prefix Recognition**: Issues with prefixes like `[BUG]`, `[Feature]`, `[Documentation]` get accurate type labels
- **Keyword Matching**: Intelligent keyword matching with word boundary detection to avoid false positives
- **Multiple Labels**: Can apply multiple relevant labels (e.g., both `type: feature` and `component: etl`)
- **Default Handling**: Assigns `priority: P2-medium` when no specific priority indicators are found

### Non-Destructive
- Only adds labels, never removes existing ones
- Labels can be manually adjusted after automatic assignment
- Safe to run multiple times on the same issue

### Logging and Feedback
- Logs all labeling decisions for transparency
- Adds a comment explaining which labels were applied automatically
- Provides clear reasoning for debugging

## Label Migration from Old System

To eliminate redundancy and conflicts, the following old labels are replaced:

| Old Label | New Label |
|-----------|-----------|
| `component: etl` | `module:ETL` |
| `component: graph-rag` | `module:engine` |
| `component: dcf-engine` | `module:engine` |
| `component: data-storage` | `module:common` |
| `component: infrastructure` | `module:infra` |
| `component: management` | `module:infra` |
| `priority: P0-critical` | `priority:P0` |
| `priority: P1-high` | `priority:P1` |
| `priority: P2-medium` | `priority:P2` |
| `priority: P3-low` | `priority:P3` |
| `type: ci/cd` | `module:infra` + `type:enhancement` |
| `phase: MVP` | `priority:P1` + `status:needs-triage` |
| `phase: production` | `priority:P0` |

## Label Usage Rules

### Required Labels (every issue must have exactly one of each)
1. **One Module**: `module:ETL|engine|evaluation|common|infra`
2. **One Type**: `type:bug|feature|enhancement|docs|refactor|adr`
3. **One Priority**: `priority:P0|P1|P2|P3`
4. **One Effort**: `effort:small|medium|large`
5. **One Status**: `status:needs-triage|ready|in-progress|blocked|review`

### Optional Labels
- **Scope**: `scope:f2|m7|n100|v3k` (for data-related issues)
- **Agent**: Multiple `agent:*` labels allowed

### Correct vs Incorrect Examples

✅ **Correct**: `module:ETL`, `type:bug`, `priority:P1`, `effort:medium`, `status:ready`

❌ **Incorrect**: `module:ETL`, `module:engine`, `type:bug`, `type:feature`, `priority:P1`, `priority:P0`

## Examples

### Example 1: Bug Report
**Title**: `[BUG] Critical production failure in DCF engine`
**Body**: `The DCF calculation is crashing when processing SEC filings`
**Labels Applied**: `priority:P0`, `type:bug`, `module:engine`, `effort:large`, `status:needs-triage`

### Example 2: Feature Request
**Title**: `[Feature] Implement automated issue labeling GitHub workflow`
**Body**: `Add automated GitHub workflow that applies appropriate labels to issues`
**Labels Applied**: `priority:P2`, `type:feature`, `module:infra`, `effort:medium`, `status:needs-triage`

### Example 3: Documentation Issue
**Title**: `[Documentation] Add comprehensive ETL pipeline guide`
**Body**: `Need to create documentation for the ETL pipeline including spider usage`
**Labels Applied**: `priority:P2`, `type:docs`, `module:ETL`, `effort:medium`, `status:needs-triage`

## Configuration

The workflow is configured in `.github/workflows/auto-label-issues.yml` and requires:
- **Permissions**: `issues: write`, `contents: read`
- **Triggers**: `issues: [opened, edited]`
- **Token**: Uses `${{ secrets.GITHUB_TOKEN }}` (automatically available)

## Troubleshooting

### Common Issues
1. **Labels not applied**: Check that the workflow has proper permissions
2. **Wrong labels**: Keywords might need adjustment in the workflow file
3. **Missing labels**: Ensure all repository labels exist and match the workflow configuration

### Workflow Logs
Check the Actions tab for detailed logs of the labeling decisions, including:
- Which keywords matched
- Why specific labels were chosen
- Any errors during label application

## Maintenance

### Adding New Labels
1. Create the label in GitHub repository settings
2. Update the workflow file with appropriate keywords
3. Test with sample issues to ensure correct matching

### Updating Keywords
Modify the keyword arrays in the workflow file to improve accuracy:
- Add new keywords that should trigger specific labels
- Remove or adjust keywords that cause false positives
- Use word boundaries (spaces) to avoid partial word matches

## Label Reference

For a complete list of available labels and their descriptions, see the repository's label configuration or use:
```bash
gh label list --repo wangzitian0/my_finance
```