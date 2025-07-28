import os
import json
from pydoc import text
import re
import fitz  # PyMuPDF
from datetime import datetime
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
from transformers import pipeline, AutoModelForSeq2SeqLM, AutoTokenizer
import unicodedata
from ftfy import fix_text
import warnings
warnings.filterwarnings("ignore")




model_path = "./SummarizerModel"
smodel = AutoModelForSeq2SeqLM.from_pretrained(model_path)
stokenizer = AutoTokenizer.from_pretrained(model_path)

summarizer = pipeline("summarization", model=smodel, tokenizer=stokenizer)
# Load embedding model
model = SentenceTransformer("./SentenceTransformerModel")

# Load input JSON
with open("input.json", "r", encoding="utf-8") as f:
    input_data = json.load(f)

PDF_DIR = "./PDFs"
persona = input_data["persona"]["role"]
job = input_data["job_to_be_done"]["task"]
query = f"{persona}. {job}"
query_vec = model.encode([query])

# Output base structure
output = {
    "metadata": {
        "input_documents": [doc["filename"] for doc in input_data["documents"]],
        "persona": persona,
        "job_to_be_done": job,
        "processing_timestamp": datetime.now().isoformat()
    },
    "extracted_sections": [],
    "subsection_analysis": []
}


def extract_sections_from_pdf(pdf_path, filename):
    doc = fitz.open(pdf_path)
    sections = []
    for page_num, page in enumerate(doc, start=1):
        blocks = page.get_text("blocks")
        i=0
        while i < len(blocks):
            text = blocks[i][4].strip()
            text = re.sub(r"[\u2022\u2023\u25E6\u2043\u2219]", "", text)  # remove bullets
            text = re.sub(r"\s+", " ", text).strip()
            text = unicodedata.normalize("NFKC", text)
            text = fix_text(text)
            
            if not re.search(r'[a-zA-Z0-9]', text):
                i += 1
                continue
            if 0 < len(text) < 100000:
                # If it's a potential heading
                if len(text) < 100:  # heading threshold
                    heading = text
                    raw_text = ""

                    # Look ahead for next block with substantial content
                    j = i + 1
                    while j < len(blocks):
                        next_text = blocks[j][4].strip()
                        next_text = re.sub(r"[\u2022\u2023\u25E6\u2043\u2219]", "", next_text)
                        next_text = re.sub(r"\s+", " ", next_text).strip()
                        next_text = unicodedata.normalize("NFKC", next_text)
                        next_text = fix_text(next_text)

                        
                        if not re.search(r'[a-zA-Z0-9]', next_text):
                            j += 1
                            continue
                        if len(next_text) > 200:  # paragraph threshold
                            raw_text = next_text
                            break
                        j += 1

                    if raw_text.strip():  # Only add if raw_text is not empty
                        sections.append({
                            "document": filename,
                            "page_number": page_num,
                            "section_title": heading,
                            "raw_text": raw_text
                        })
                        i = j  # move to the block after used paragraph
            i += 1

    return sections

# Aggregate all extracted text blocks
all_sections = []

for doc in input_data["documents"]:
    filename = doc["filename"]
    filepath = os.path.join(PDF_DIR, filename)
    if not os.path.exists(filepath):
        print(f"Skipping missing file: {filename}")
        continue
    all_sections += extract_sections_from_pdf(filepath, filename)

# Compute similarity scores
for section in all_sections:
    text_vec = model.encode([section["raw_text"]])
    score = cosine_similarity(text_vec, query_vec)[0][0]
    section["score"] = score

# Sort and pick top 5
top_sections = sorted(all_sections, key=lambda x: -x["score"])[:5]

for rank, sec in enumerate(top_sections, 1):
    output["extracted_sections"].append({
        "document": sec["document"],
        "page_number": sec["page_number"],
        "section_title": sec["section_title"],
        "importance_rank": rank
    })
    summary = summarizer(f"As {persona} summarize this: {sec['raw_text']}", min_length=25, do_sample=False)[0]["summary_text"]
    summary = re.sub(r"[\u2022\u2023\u25E6\u2043\u2219]", "", summary)
    summary = re.sub(r"\s+", " ", summary).strip()
    summary = unicodedata.normalize("NFKC", summary)
    summary = fix_text(summary)

    output["subsection_analysis"].append({
        "document": sec["document"],
        "page_number": sec["page_number"],
        "refined_text": summary
    })


with open("output/output.json", "w", encoding="utf-8") as f:
    json.dump(output, f, indent=2)

print("Output written to output.json")
