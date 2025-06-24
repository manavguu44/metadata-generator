import streamlit as st
import fitz
from docx import Document
import pytesseract
import spacy
from keybert import KeyBERT
import json

nlp = spacy.load("en_core_web_sm")
kw_model = KeyBERT()

def extract_text_pdf(path):
    text = ""
    doc = fitz.open(path)
    for page in doc:
        text += page.get_text()
    return text

def extract_text_docx(path):
    doc = Document(path)
    return "\n".join([p.text for p in doc.paragraphs])

def extract_text_txt(path):
    with open(path, 'r', encoding='utf-8') as f:
        return f.read()

def generate_metadata(text):
    doc = nlp(text)
    entities = list(set([f"{ent.label_}: {ent.text}" for ent in doc.ents]))
    keywords = [kw[0] for kw in kw_model.extract_keywords(text, top_n=5)]
    title_guess = next((line.strip() for line in text.split("\n") if line.strip()), "N/A")
    return {
        "entities": entities,
        "keywords": keywords,
        "word_count": len(text.split()),
        "title_guess": title_guess
    }

st.title("Automated Metadata Generator")

uploaded_file = st.file_uploader("Upload document (PDF, DOCX, TXT)", type=['pdf', 'docx', 'txt'])
if uploaded_file:
    with open(uploaded_file.name, "wb") as f:
        f.write(uploaded_file.getbuffer())
    
    if uploaded_file.name.endswith('.pdf'):
        text = extract_text_pdf(uploaded_file.name)
    elif uploaded_file.name.endswith('.docx'):
        text = extract_text_docx(uploaded_file.name)
    else:
        text = extract_text_txt(uploaded_file.name)

    metadata = generate_metadata(text)
    st.json(metadata)
    
    # Download link for metadata
    st.download_button("Download JSON metadata", json.dumps(metadata, indent=2), file_name="metadata.json", mime="application/json")
import spacy
try:
    nlp = spacy.load("en_core_web_sm")
except OSError:
    from spacy.cli import download
    download("en_core_web_sm")
    nlp = spacy.load("en_core_web_sm")
