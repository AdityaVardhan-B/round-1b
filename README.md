
#  Intelligent PDF Extractor & Summarizer

This project automatically extracts and summarizes the most relevant sections from a set of PDF documents, based on a given **persona** and **task**.

It combines:
-  Semantic similarity via Sentence Transformers
-  PDF parsing using PyMuPDF
-  Relevance-driven content filtering via pretrained Hugging Face models

Built for **Adobe India Hackathon 2025 – Round 1B**.

---

##  Project Structure

```
root/
├── input/
│   └── input.json               # Input persona, task, and PDF metadata
│
├── output/
│   └── output.json              # Final JSON output (auto-generated)
│
├── PDFs/                        # Folder with input PDF documents
│   ├── input1.pdf
│   └── input2.pdf
│
├── SummarizerModel/            # Fine-tuned Transformer summarization model
├── SentenceTransformerModel/   # Sentence embedding model directory
│
├── script.py                   # Main pipeline script
├── requirements.txt            # Python dependencies
├── Dockerfile                  # Container config
```

---

##  Input Format

The `input/input.json` file should follow this structure:

```json
{
  "challenge_info": {
    "challenge_id": "<round_id_or_project_name>",
    "test_case_name": "<test_case_identifier>",
    "description": "<short_description_of_the_context>"
  },
  "documents": [
    {
      "filename": "<document1.pdf>",
      "title": "<Document 1 Title>"
    },
    {
      "filename": "<document2.pdf>",
      "title": "<Document 2 Title>"
    }
    // Add more documents as needed
  ],
  "persona": {
    "role": "<Who is the user? e.g., Travel Planner, Policy Analyst>"
  },
  "job_to_be_done": {
    "task": "<What is the user trying to achieve?>"
  }
}

```

---

##  Output Format

The script generates `output/output.json` with:

- Extracted top sections from the most relevant PDFs
- Retrieves refined versions of each section

Example:
```json
{
  "metadata": {
    "input_documents": [
      "<document1.pdf>",
      "<document2.pdf>",
      "<document3.pdf>"
      // Add more as needed
    ],
    "persona": "<Persona Role, e.g., Travel Planner>",
    "job_to_be_done": "<Task Description>",
    "processing_timestamp": "<ISO Timestamp of Processing>"
  },
  "extracted_sections": [
    {
      "document": "<source_document.pdf>",
      "page_number": <page_number>,
      "section_title": "<Section Title>",
      "importance_rank": 1
    },
    {
      "document": "<source_document.pdf>",
      "page_number": <page_number>,
      "section_title": "<Section Title>",
      "importance_rank": 2
    }
    // Up to top 5 ranked sections
  ],
  "subsection_analysis": [
    {
      "document": "<source_document.pdf>",
      "page_number": <page_number>,
      "refined_text": "<Summarized content relevant to the persona and task>"
    },
    {
      "document": "<source_document.pdf>",
      "page_number": <page_number>,
      "refined_text": "<Another summarized section>"
    }
    // Summaries corresponding to the extracted sections
  ]
}

```

---

##  Installation & Running


### Steps to Clone the Repository:

Follow these steps to ensure that the repository and all Git LFS files are cloned correctly:

#### **1. Install Git and Git LFS**
Run the following in terminal

**For Ubuntu/Debian:**
```bash
sudo apt update
sudo apt install git git-lfs
```
**For macOS (Homebrew):**
```bash
brew install git git-lfs
```
**For Windows (Chocolatey):**
```bash
choco install git-lfs
```
#### 2. **Initialize Git LFS**
```bash
git lfs install
```
#### 3. Clone the Repository
```bash
git clone https://github.com/AdityaVardhan-B/round-1b.git
```
###  Steps to run the Dockerfile

1. **Build the Docker image**:
   ```bash
   docker build -t pdf-summarizer .
   ```

2. **Run the container** (mount PDFs/input/output):
   ```bash
   docker run --rm `
     -v "$(pwd)/PDFs:/app/PDFs" `
     -v "$(pwd)/input/input.json:/app/input.json" `
     -v "$(pwd)/output:/app/output" `
     pdf-summarizer
   ```

>  Ensure `SummarizerModel/` and `SentenceTransformerModel/` are present in the root before building the Docker image — they get copied into the container.

---

##  Python Dependencies

Listed in `requirements.txt`:

```
PyMuPDF==1.23.25
sentence-transformers==2.7.0
scikit-learn==1.5.0
numpy>=1.24.0
torch>=2.2.0
transformers>=4.39.0
ftfy>=6.1.1
regex>=2023.12.25
tokenizers>=0.15.0
```

---

##  Notes

- The script will skip PDFs that are missing from the input.json file
- Only the **top 5 most relevant sections** are extracted and summarized
- Works fully offline since models are preloaded into their folders

---
##  Author

**Adobe India Hackathon 2025 — Round 1A**  
**Team:** `BAN`

