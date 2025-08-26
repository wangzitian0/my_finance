# Automated Issue Labeling

This repository uses an automated GitHub workflow to intelligently apply labels to issues based on their title and content.

## How It Works

The workflow (`.github/workflows/auto-label-issues.yml`) triggers when issues are:
- Opened
- Edited

It analyzes the issue title and body content to automatically apply relevant labels from the following categories:

## Label Categories

### Priority Labels
- **`priority: P0-critical`** - Critical issues requiring immediate attention
  - Keywords: `critical`, `urgent`, `emergency`, `broken`, `production down`, `security`, `data loss`, `corruption`, `crash`, `failure`, `immediate`
- **`priority: P1-high`** - High priority issues
  - Keywords: `important`, `high priority`, `blocking`, `regression`, `major bug`, `performance`, `memory leak`, `timeout`, `error`, `exception`
- **`priority: P2-medium`** - Medium priority (default)
- **`priority: P3-low`** - Low priority issues
  - Keywords: `nice to have`, `low priority`, `minor`, `cosmetic`

### Type Labels
- **`type: bug`** - Something isn't working
  - Keywords: `bug`, `error`, `issue`, `problem`, `fix`, `broken`, `incorrect`, `fail`, `exception`, `crash`, `not working`
  - Prefix: `[BUG]`
- **`type: feature`** - New functionality
  - Keywords: `feature`, `enhancement`, `implement`, `add`, `create`, `new`, `improve`, `extend`, `support`
  - Prefix: `[Feature]`
- **`type: docs`** - Documentation updates
  - Keywords: `documentation`, `doc`, `readme`, `guide`, `tutorial`, `example`, `comment`, `explain`, `clarify`
  - Prefix: `[Documentation]` or `[Doc`
- **`type: refactor`** - Code refactoring
  - Keywords: `refactor`, `cleanup`, `reorganize`, `restructure`, `optimize`, `simplify`, `architecture`
  - Prefix: `[Refactor]`
- **`type: adr`** - Architecture Decision Record
  - Keywords: `adr`, `architecture decision`, `decision record`, `design decision`
  - Prefix: `[ADR]`
- **`type: ci/cd`** - CI/CD and automation
  - Keywords: `github action`, `github workflow`, `ci pipeline`, `automation`, `deploy`, `build pipeline`, `test automation`

### Component Labels
- **`component: infrastructure`** - Infrastructure and DevOps
  - Keywords: `infrastructure`, `infra`, `docker`, `container`, `podman`, `deployment`, `environment`, `setup`, `ansible`, `pixi`, `database`, `neo4j`
- **`component: data-storage`** - Data storage and management
  - Keywords: `data storage`, `storage`, `directory`, `file system`, `data layer`, `stage_`, `layer_`, `build_data`, `sec-edgar`, `yfinance`
- **`component: etl`** - ETL pipeline
  - Keywords: `etl`, `etl pipeline`, `spider`, `parser`, `extraction`, `transform`, `semantic embedding`, `data processing`
- **`component: dcf-engine`** - DCF calculation engine
  - Keywords: `dcf`, `valuation`, `dcf_engine`, `financial`, `calculation`
- **`component: graph-rag`** - Graph RAG system
  - Keywords: `graph rag`, `graph_rag`, `semantic retrieval`, `vector search`, `retrieval-augmented generation`, `rag system`

### Status Labels
- **`status: blocked`** - Blocked by dependencies
  - Keywords: `blocked`, `waiting for`, `dependency`, `depends on`, `prerequisite`
- **`status: needs-triage`** - Needs initial assessment
  - Keywords: `need`, `question`, `unclear`, `investigate`, `research`, `help wanted`

### Phase Labels
- **`phase: MVP`** - Minimum viable product phase
  - Keywords: `mvp`, `minimum viable product`, `prototype`, `basic`, `initial`
- **`phase: production`** - Production phase
  - Keywords: `production`, `prod`, `live`, `release`, `deployment`

### Effort Labels
- **`effort: large`** - Large effort (> 3 days)
  - Keywords: `major refactor`, `migration`, `restructure`, `major`, `complete overhaul`, `system overhaul`, `large effort`
  - Also applied to very long issues (>1500 characters)
- **`effort: medium`** - Medium effort (1-3 days)
  - Keywords: `enhance`, `extend`, `integration`
  - Also applied to medium-length issues (>800 characters)
- **`effort: small`** - Small effort (< 1 day) - *not automatically assigned*

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

## Examples

### Example 1: Bug Report
**Title**: `[BUG] Critical production failure in DCF engine`  
**Body**: `The DCF calculation is crashing when processing SEC filings`  
**Labels Applied**: `priority: P0-critical`, `type: bug`, `component: dcf-engine`

### Example 2: Feature Request
**Title**: `[Feature] Implement automated issue labeling GitHub workflow`  
**Body**: `Add automated GitHub workflow that applies appropriate labels to issues`  
**Labels Applied**: `priority: P2-medium`, `type: feature`, `type: ci/cd`, `effort: medium`

### Example 3: Documentation Issue
**Title**: `[Documentation] Add comprehensive ETL pipeline guide`  
**Body**: `Need to create documentation for the ETL pipeline including spider usage`  
**Labels Applied**: `priority: P2-medium`, `type: docs`, `component: etl`, `status: needs-triage`

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