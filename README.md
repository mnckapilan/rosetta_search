# 🔍 Rosetta Search

**Rosetta Search** is a semantic code search tool that helps developers find relevant source files in unfamiliar codebases using **natural language queries**. 

Instead of relying on exact keyword matches, Rosetta tries to understand your intent through commit messages, leveraging NLP techniques to connect concepts to code.

Rosetta Search was developed as part of a final-year MEng project at Imperial College London, supervised by Dr. Robert Chatley.  


---

## 🚀 Why Rosetta Search?

Navigating a new or large codebase is hard—especially if you don’t know the right variable or function names. Traditional search tools like `Ctrl+F` or regex don’t help if you're unfamiliar with internal naming conventions.

Rosetta Search bridges that gap. It empowers you to search for concepts like:

```
"authentication timeout"
"order management"
"password reset"
```

...and get a ranked list of relevant source files, **even if those exact words don’t appear in the code**.

---

## ✨ Features

- 🔤 **Semantic Search** via NLP techniques and word embeddings
- 📦 **Local Indexing** using Git commit history
- 💬 **Natural Language Queries**
- ⚡️ Fast fuzzy matching using vector similarity and TF-IDF ranking
- 🔌 CLI tool, Python package, and cross-platform GUI prototype available
- 🔒 Private by design — all indexing happens locally

---

## 🧠 How It Works

1. **Extract commit messages** from the Git history
2. **Tokenize and lemmatize** each message to extract key semantic concepts
3. Build a **Bag-of-Words model** mapping tokens → modified files
4. Calculate **TF-IDF** scores to assess token importance per file
5. For each query:
   - Use **FastText embeddings** (trained on real commit messages) to compare similarity between query and indexed tokens
   - Rank relevant files using cosine similarity and tf-idf scores

---

## 🛠 Installation

### Option 1: Install from PyPI
```bash
pip install rosetta-search
```
---

## 🧭 Usage

### 1. Create an Index
```bash
rosetta --repo-path /path/to/your/git/repo create
```

To perform a full build with precomputed tf-idf (better search performance):
```bash
rosetta --repo-path /path/to/your/git/repo create --full-build
```

### 2. Search with Natural Language
```bash
rosetta --repo-path /path/to/your/git/repo search --query "password reset"
```

Add `--show-all` to return more than the top 20 results.

---


## ✨ Acknowledgements

Thanks to:
- [Dr. Robert Chatley](https://www.doc.ic.ac.uk/~rbc/) for supervision
- Open-source contributors and commit authors whose messages power the model
- [FastText](https://fasttext.cc/) and [NLTK](https://www.nltk.org/) for enabling accessible NLP

---

## 📬 Contributing

PRs and feedback welcome! If you want to contribute or suggest improvements, open an issue or reach out.
