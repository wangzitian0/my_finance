# Data Model Design

## Neo4j Graph Database Extended Schema

Extended data model based on existing `ETL/models.py` to support SEC filings and DCF calculations.

### Core Entity Nodes

#### 1. Stock (Existing)
```python
class Stock(StructuredNode):
    ticker = StringProperty(unique_index=True)
    period = StringProperty()
    interval = StringProperty()
    fetched_at = DateTimeProperty()
```

#### 2. New: SECFiling
```python
class SECFiling(StructuredNode):
    cik = StringProperty()
    filing_type = StringProperty()  # 10-K, 10-Q, 8-K
    filing_date = DateProperty()
    period_end_date = DateProperty()
    document_url = StringProperty()
    parsed_content = JSONProperty()  # Parsed structured content
    sections = JSONProperty()  # Section content index
```

#### 3. New: FinancialMetrics
```python
class FinancialMetrics(StructuredNode):
    metric_name = StringProperty()
    value = FloatProperty()
    currency = StringProperty()
    period = StringProperty()
    calculated_at = DateTimeProperty()
    source = StringProperty()  # SEC, YFinance, Calculated
```

### Relationships

```python
# Stock relationships
class HAS_FILING(StructuredRel):
    filing_date = DateProperty()
    filing_type = StringProperty()

class HAS_METRICS(StructuredRel):
    period = StringProperty()
    source = StringProperty()

# Cross-entity relationships  
class REFERENCES(StructuredRel):
    context = StringProperty()
    confidence = FloatProperty()
```

## Usage

```python
# Create nodes
stock = Stock(ticker="AAPL").save()
filing = SECFiling(cik="320193", filing_type="10-K").save()

# Create relationships
stock.filings.connect(filing, {'filing_date': date.today()})
```
