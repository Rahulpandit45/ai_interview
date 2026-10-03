"""
train_candidate_question_model.py
Fine-tunes the Candidate Profile & Follow-Up Question Generator Model
using PyTorch, Transformers (google/flan-t5-small), and Sentence-Transformers.

Outputs:
- Fine-tuned Seq2Seq Model: backend/trained_models/candidate_question_model/
- Neural Profile Question Knowledge Base: backend/trained_models/candidate_question_kb.pkl
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

MODEL_OUTPUT_DIR = os.path.join(MODELS_DIR, "candidate_question_model")
KB_OUTPUT_PATH = os.path.join(MODELS_DIR, "candidate_question_kb.pkl")


class QuestionGenDataset(Dataset):
    def __init__(self, examples, tokenizer, max_input_len=192, max_target_len=128):
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
        labels[labels == self.tokenizer.pad_token_id] = -100

        return {
            "input_ids": input_enc["input_ids"].squeeze(0),
            "attention_mask": input_enc["attention_mask"].squeeze(0),
            "labels": labels
        }


def build_candidate_question_knowledge_base():
    print("=" * 70)
    print("  [1/2] BUILDING CANDIDATE PROFILE QUESTION KNOWLEDGE BASE")
    print("=" * 70)

    # Combine questions from it_questions.json and candidate dataset
    json_path = os.path.join(DATASETS_DIR, "it_questions.json")
    with open(json_path, "r", encoding="utf-8") as f:
        it_questions = json.load(f)

    from sentence_transformers import SentenceTransformer
    print("Loading Sentence-Transformer (all-MiniLM-L6-v2)...")
    embedder = SentenceTransformer("all-MiniLM-L6-v2")

    texts_to_embed = []
    metadata = []

    for q in it_questions:
        q_id = q["id"]
        q_text = q["question"]
        cat = q.get("category", "IT")
        diff = q.get("difficulty", "easy").lower()
        a1 = q.get("answer_1", "")
        a2 = q.get("answer_2", "")
        a3 = q.get("answer_3", "")

        texts_to_embed.append(f"{cat} {diff}: {q_text}")
        metadata.append({
            "id": q_id,
            "category": cat,
            "difficulty": diff,
            "question_text": q_text,
            "answer_1": a1,
            "answer_2": a2,
            "answer_3": a3,
            "benchmark_answer": a2 or a1
        })

    print(f"Encoding {len(texts_to_embed)} questions into dense vector embeddings...")
    embeddings = embedder.encode(texts_to_embed, show_progress_bar=False, normalize_embeddings=True)

    kb_payload = {
        "texts": texts_to_embed,
        "embeddings": np.array(embeddings, dtype=np.float32),
        "metadata": metadata
    }

    with open(KB_OUTPUT_PATH, "wb") as f:
        pickle.dump(kb_payload, f)

    print(f"[OK] Saved Candidate Question KB to: {KB_OUTPUT_PATH}")
    print(f"     Embeddings shape: {kb_payload['embeddings'].shape}")
    return kb_payload


def train_candidate_question_model(epochs=3, batch_size=8, lr=5e-4):
    print("\n" + "=" * 70)
    print("  [2/2] TRAINING CANDIDATE PROFILE & FOLLOW-UP GENERATOR MODEL")
    print("=" * 70)

    # Load dataset examples
    q_train_path = os.path.join(DATASETS_DIR, "candidate_questions_train.jsonl")
    f_train_path = os.path.join(DATASETS_DIR, "candidate_followups_train.jsonl")

    examples = []
    if os.path.exists(q_train_path):
        with open(q_train_path, "r", encoding="utf-8") as f:
            for line in f:
                if line.strip():
                    examples.append(json.loads(line))

    if os.path.exists(f_train_path):
        with open(f_train_path, "r", encoding="utf-8") as f:
            for line in f:
                if line.strip():
                    examples.append(json.loads(line))

    print(f"Loaded {len(examples)} training examples for profile-conditioned question generation.")

    from transformers import AutoTokenizer, AutoModelForSeq2SeqLM
    base_model_name = "google/flan-t5-small"

    print(f"Loading pretrained base model: {base_model_name}...")
    tokenizer = AutoTokenizer.from_pretrained(base_model_name)
    model = AutoModelForSeq2SeqLM.from_pretrained(base_model_name)

    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    print(f"Training device: {device}")
    model.to(device)

    dataset = QuestionGenDataset(examples, tokenizer)
    dataloader = DataLoader(dataset, batch_size=batch_size, shuffle=True)

    optimizer = torch.optim.AdamW(model.parameters(), lr=lr, weight_decay=0.01)

    model.train()
    print(f"Starting training: {epochs} epochs, batch size {batch_size}...")

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

        avg_loss = total_loss / max(1, len(dataloader))
        print(f"  Epoch [{epoch}/{epochs}] Complete - Average Loss: {avg_loss:.4f}")

    print(f"\nSaving fine-tuned model checkpoint to: {MODEL_OUTPUT_DIR}...")
    model.save_pretrained(MODEL_OUTPUT_DIR)
    tokenizer.save_pretrained(MODEL_OUTPUT_DIR)
    print(f"[OK] Candidate Question Model saved successfully to {MODEL_OUTPUT_DIR}!")


def main():
    print("=" * 70)
    print("  AI INTERVIEW SYSTEM - CANDIDATE QUESTION MODEL TRAINING")
    print("=" * 70)

    # 1. Build Semantic Vector Knowledge Base
    build_candidate_question_knowledge_base()

    # 2. Train and serialize question generator
    train_candidate_question_model(epochs=3, batch_size=8, lr=5e-4)

    print("\n" + "=" * 70)
    print("  [SUCCESS] CANDIDATE PROFILE QUESTION MODEL READY!")
    print("=" * 70)


if __name__ == "__main__":
    main()
