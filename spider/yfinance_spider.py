def sanitize_data(obj):
    """
    Recursively convert dictionary keys to strings.
    """
    if isinstance(obj, dict):
        return {str(k): sanitize_data(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [sanitize_data(item) for item in obj]
    else:
        return obj

def save_data(ticker, source, oid, data):
    """
    Save the data as a JSON file with the filename format:
    <ticker>_<source>_<oid>_<date_str>.json
    The file is stored under data/original/<source>/<ticker>/.
    Before saving, the data is sanitized to ensure all dictionary keys are strings.
    """
    date_str = datetime.now().strftime("%y%m%d-%H%M%S")
    filename = f"{ticker}_{source}_{oid}_{date_str}.json"
    ticker_dir = os.path.join(ORIGINAL_DATA_DIR, source, ticker)
    os.makedirs(ticker_dir, exist_ok=True)
    filepath = os.path.join(ticker_dir, filename)
    sanitized_data = sanitize_data(data)
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(sanitized_data, f, ensure_ascii=False, indent=2, default=str)
    return filepath
