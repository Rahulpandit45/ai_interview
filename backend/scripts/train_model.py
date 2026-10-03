"""
train_model.py
Fine-tunes the open-source lightweight google/flan-t5-small model on the IT QA dataset
and builds a neural semantic vector knowledge base using sentence-transformers (all-MiniLM-L6-v2).

Features:
- Fine-tunes Flan-T5 seq2seq model on 1,575 IT Q&A instruction pairs
- Serializes fine-tuned weights and tokenizer to backend/trained_models/it_qa_model/
- Precomputes and serializes dense semantic embeddings to backend/trained_models/it_qa_kb.pkl
- Enables robust handling of question paraphrases and variations
"""

import os
import sys
import json
import pickle
import torch
from torch.utils.data import Dataset, DataLoader
import numpy as np

# Ensure project root is in sys.path
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ROOT_DIR = os.path.dirname(BASE_DIR)
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

DATASETS_DIR = os.path.join(BASE_DIR, "datasets")
MODELS_DIR = os.path.join(BASE_DIR, "trained_models")
os.makedirs(MODELS_DIR, exist_ok=True)

MODEL_OUTPUT_DIR = os.path.join(MODELS_DIR, "it_qa_model")
KB_OUTPUT_PATH = os.path.join(MODELS_DIR, "it_qa_kb.pkl")

class ITQADataset(Dataset):
    def __init__(self, examples, tokenizer, max_input_len=128, max_target_len=128):
        self.examples = examples
        self.tokenizer = tokenizer
        self.max_input_len = max_input_len
        self.max_target_len = max_target_len

    def __len__(self):
        return len(self.examples)

    def __getitem__(self, idx):
        item = self.examples[idx]
        prompt = item["prompt"]
        target = item["target"]

        input_enc = self.tokenizer(
            prompt,
            max_length=self.max_input_len,
            padding="max_length",
            truncation=True,
            return_tensors="pt"
        )
        target_enc = self.tokenizer(
            target,
            max_length=self.max_target_len,
            padding="max_length",
            truncation=True,
            return_tensors="pt"
        )

        labels = target_enc["input_ids"].squeeze(0)
        # Replace padding token id's of the label by -100 so they are ignored by CrossEntropyLoss
        labels[labels == self.tokenizer.pad_token_id] = -100

        return {
            "input_ids": input_enc["input_ids"].squeeze(0),
            "attention_mask": input_enc["attention_mask"].squeeze(0),
            "labels": labels
        }


def build_semantic_knowledge_base():
    print("=" * 70)
    print("  [1/2] BUILDING SEMANTIC KNOWLEDGE BASE WITH SENTENCE-TRANSFORMERS")
    print("=" * 70)
    
    json_path = os.path.join(DATASETS_DIR, "it_questions.json")
    with open(json_path, "r", encoding="utf-8") as f:
        questions = json.load(f)

    print(f"Loading Sentence-Transformer (all-MiniLM-L6-v2) for {len(questions)} questions...")
    from sentence_transformers import SentenceTransformer
    embedder = SentenceTransformer("all-MiniLM-L6-v2")

    # Generate synthetic question variations to make retrieval robust to phrasing
    texts_to_embed = []
    metadata = []

    for q in questions:
        q_id = q["id"]
        q_text = q["question"]
        cat = q["category"]
        a1 = q["answer_1"]
        a2 = q["answer_2"]
        a3 = q["answer_3"]

        # Base question
        texts_to_embed.append(q_text)
        metadata.append({
            "id": q_id,
            "category": cat,
            "canonical_question": q_text,
            "answer_1": a1,
            "answer_2": a2,
            "answer_3": a3
        })

        # Variation 1: Explain ...
        clean_q = q_text.rstrip("?").replace("What is ", "").replace("What are ", "")
        texts_to_embed.append(f"Explain {clean_q}")
        metadata.append({
            "id": q_id,
            "category": cat,
            "canonical_question": q_text,
            "answer_1": a1,
            "answer_2": a2,
            "answer_3": a3
        })

        # Variation 2: Tell me about ...
        texts_to_embed.append(f"Tell me about {clean_q}")
        metadata.append({
            "id": q_id,
            "category": cat,
            "canonical_question": q_text,
            "answer_1": a1,
            "answer_2": a2,
            "answer_3": a3
        })

    print(f"Encoding {len(texts_to_embed)} question variations into dense vector embeddings...")
    embeddings = embedder.encode(texts_to_embed, show_progress_bar=True, normalize_embeddings=True)

    kb_payload = {
        "texts": texts_to_embed,
        "embeddings": np.array(embeddings, dtype=np.float32),
        "metadata": metadata
    }

    with open(KB_OUTPUT_PATH, "wb") as f:
        pickle.dump(kb_payload, f)

    print(f"[OK] Saved Semantic Knowledge Base to: {KB_OUTPUT_PATH}")
    print(f"     Embeddings shape: {kb_payload['embeddings'].shape}")
    return kb_payload


def train_flan_t5_model(epochs=3, batch_size=16, lr=5e-4):
    print("\n" + "=" * 70)
    print("  [2/2] FINE-TUNING PRETRAINED MODEL (google/flan-t5-small)")
    print("=" * 70)

    train_jsonl = os.path.join(DATASETS_DIR, "it_qa_train.jsonl")
    examples = []
    with open(train_jsonl, "r", encoding="utf-8") as f:
        for line in f:
            if line.strip():
                examples.append(json.loads(line))

    print(f"Loaded {len(examples)} instruction-tuning training examples.")

    from transformers import AutoTokenizer, AutoModelForSeq2SeqLM
    base_model_name = "google/flan-t5-small"

    print(f"Loading pretrained base model and tokenizer: {base_model_name}...")
    tokenizer = AutoTokenizer.from_pretrained(base_model_name)
    model = AutoModelForSeq2SeqLM.from_pretrained(base_model_name)

    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    print(f"Training on device: {device}")
    model.to(device)

    dataset = ITQADataset(examples, tokenizer)
    dataloader = DataLoader(dataset, batch_size=batch_size, shuffle=True)

    optimizer = torch.optim.AdamW(model.parameters(), lr=lr, weight_decay=0.01)

    model.train()
    print(f"Starting fine-tuning: {epochs} epochs, batch size {batch_size}, {len(dataloader)} steps per epoch...")

    for epoch in range(1, epochs + 1):
        total_loss = 0.0
        step = 0
        for batch in dataloader:
            step += 1
            input_ids = batch["input_ids"].to(device)
            attention_mask = batch["attention_mask"].to(device)
            labels = batch["labels"].to(device)

            optimizer.zero_grad()
            outputs = model(
                input_ids=input_ids,
                attention_mask=attention_mask,
                labels=labels
            )
            loss = outputs.loss
            loss.backward()
            optimizer.step()

            total_loss += loss.item()
            if step % 25 == 0 or step == len(dataloader):
                avg_loss = total_loss / step
                print(f"  Epoch [{epoch}/{epochs}] Step [{step}/{len(dataloader)}] - Loss: {loss.item():.4f} (Avg: {avg_loss:.4f})")

        print(f"--> Epoch {epoch} complete. Average Loss: {total_loss / len(dataloader):.4f}")

    # Save fine-tuned checkpoint and tokenizer
    print(f"\nSaving fine-tuned model and tokenizer to: {MODEL_OUTPUT_DIR}...")
    model.save_pretrained(MODEL_OUTPUT_DIR)
    tokenizer.save_pretrained(MODEL_OUTPUT_DIR)
    print(f"[OK] Fine-tuned model checkpoint saved successfully!")


def main():
    print("=" * 70)
    print("  AI INTERVIEW SYSTEM - IT QA MODEL TRAINING PIPELINE")
    print("=" * 70)

    # 1. Build Semantic Vector Knowledge Base (handles semantic paraphrasing)
    build_semantic_knowledge_base()

    # 2. Fine-tune Flan-T5 model
    train_flan_t5_model(epochs=3, batch_size=16, lr=5e-4)

    print("\n" + "=" * 70)
    print("  [SUCCESS] IT QA MODEL TRAINING & KNOWLEDGE BASE COMPLETE!")
    print("=" * 70)


if __name__ == "__main__":
    main()
