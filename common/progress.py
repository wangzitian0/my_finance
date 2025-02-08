# common/progress.py
from tqdm import tqdm

def create_progress_bar(total, description="Processing"):
    """
    Return a tqdm progress bar instance.
    """
    return tqdm(total=total, desc=description, unit="ticker")
