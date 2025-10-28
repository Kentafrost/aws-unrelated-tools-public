import re

def clean_japanese_text(text):
    """Clean and validate text with focus on Japanese content"""
    if not text or not text.strip():
        return ""
    
    # Remove extra whitespace and normalize
    text = re.sub(r'\s+', ' ', text.strip())
    
    # Remove obvious OCR artifacts (isolated single characters, excessive punctuation)
    text = re.sub(r'\b[a-zA-Z]\b', '', text)  # Remove isolated single letters
    text = re.sub(r'[^\w\s\u3040-\u309F\u30A0-\u30FF\u4E00-\u9FFF]', ' ', text)  # Keep only alphanumeric, Japanese chars, and spaces
    text = re.sub(r'\s+', ' ', text.strip())  # Clean up spaces again
    
    # Must have at least 2 characters to be considered valid
    if len(text) < 2:
        return ""
        
    return text

# Test with the garbled OCR output we got
test_texts = [
    'Lo\n\nmy),\n/\n\n=\n\' SA\n\nie\n\n(AN\n\n1 ,\n\nES\n\nby\n\nsp\n\nZ /',
    '6',
    'UN)\n\n(d\n\n(AY\n\n5H\n\nES\n\n4\n\nA',
    '\\@\nJ we',
    'iS',
    'i\n\nvA',
    'a wo\nGs ([e\nDS yp\n/ Rm\n) §3\nR\nYE\nre (2\n(AY L @\nAS',
    'vs',
    'jl (?\n( bys',
    'iF'
]

print("Testing text cleaning function:")
for i, text in enumerate(test_texts):
    cleaned = clean_japanese_text(text)
    print(f"Text {i+1}: '{text[:30]}{'...' if len(text) > 30 else ''}' -> '{cleaned}'")
