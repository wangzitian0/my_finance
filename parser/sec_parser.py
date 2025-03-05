
import re
from bs4 import BeautifulSoup

def preprocess_sec_content(content):
    """
    Preprocess the SEC file content to add closing tags for unclosed fields.
    This regex looks for an opening tag (e.g., <TYPE>) followed by some non-tag characters
    and a newline, and inserts a corresponding closing tag.
    """
    # List of tag names to fix
    tags_to_fix = ['TYPE', 'SEQUENCE', 'FILENAME', 'DESCRIPTION']
    for tag in tags_to_fix:
        # This regex finds <TAG> followed by one or more non-"<" characters up to a newline
        # and inserts the closing tag before the newline.
        pattern = re.compile(rf'(<{tag}>[^<\n]+)(\n)')
        content = pattern.sub(rf'\1</{tag}>\2', content)
    return content

def parse_sec_file(file_path):
    # Read the file content, ignoring errors for problematic characters.
    with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
        raw_content = f.read()

    # Preprocess content to insert closing tags for unclosed fields.
    cleaned_content = preprocess_sec_content(raw_content)

    # Use BeautifulSoup with a tolerant parser (html.parser) to handle SGML-like structure.
    soup = BeautifulSoup(cleaned_content, 'html.parser')

    # Try to locate the main SEC-DOCUMENT element.
    sec_document = soup.find('sec-document')
    if not sec_document:
        sec_document = soup  # If not found, use the whole document.

    # Find all DOCUMENT sections.
    documents = sec_document.find_all('document')
    parsed_docs = []

    for doc in documents:
        # Extract each field; BeautifulSoup should now have proper closing tags.
        doc_type = doc.find('type')
        sequence = doc.find('sequence')
        filename = doc.find('filename')
        description = doc.find('description')
        text = doc.find('text')

        doc_info = {
            'type': doc_type.get_text(strip=True) if doc_type else None,
            'sequence': sequence.get_text(strip=True) if sequence else None,
            'filename': filename.get_text(strip=True) if filename else None,
            'description': description.get_text(strip=True) if description else None,
            'text': text.get_text(strip=True) if text else None,
        }
        parsed_docs.append(doc_info)

    return parsed_docs

# Example usage
if __name__ == '__main__':
    from parser.rcts import sec_text_doc_splitter
    
    file_path = 'data/sec-edgar/0000320193/10k/0000320193/10-K/0000320193-24-000123.txt'
    documents = parse_sec_file(file_path)

    # Suppose you have a long SEC filing text in the variable sec_text
    chunks = sec_text_doc_splitter.split_text(documents[0]['text'])

    print(f"Number of chunks: {len(chunks)}")
    for chunk in chunks:
        print(chunk)
        print("-" * 40)
