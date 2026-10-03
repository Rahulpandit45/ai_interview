"""
generate_question_training_dataset.py
Generates instruction-tuning datasets for training the Candidate Profile Question Generator
and Real-time Contextual Follow-up Generation Model.

Generates:
1. Profile-to-Question pairs (Junior/Mid/Senior, multi-domain, varied technical skills & projects)
2. Answer-to-Followup pairs (Conditioned on question, candidate answer text, and performance quality)
"""

import os
import json
import random

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATASETS_DIR = os.path.join(BASE_DIR, "datasets")
os.makedirs(DATASETS_DIR, exist_ok=True)

TRAIN_DATASET_PATH = os.path.join(DATASETS_DIR, "candidate_questions_train.jsonl")
FOLLOWUP_DATASET_PATH = os.path.join(DATASETS_DIR, "candidate_followups_train.jsonl")

# Base domain templates and knowledge
DOMAINS = {
    "Python": {
        "easy": [
            ("What are the key differences between Python lists and tuples in terms of mutability and performance?",
             "Lists are mutable and dynamically resized, while tuples are immutable with lower memory overhead."),
            ("How does Python manage memory and what is the role of the garbage collector and reference counting?",
             "Python uses reference counting as its primary memory management mechanism along with a cyclic garbage collector."),
            ("What is the difference between shallow copy and deep copy in Python?",
             "A shallow copy creates a new object but inserts references to original nested objects, while deep copy recursively duplicates nested objects.")
        ],
        "medium": [
            ("How do Python decorators work and how can you pass arguments to a custom decorator?",
             "Decorators wrap functions using higher-order closures and can accept arguments using an outer factory function."),
            ("Explain the Global Interpreter Lock (GIL) and its implications for multi-threaded CPU-bound programs.",
             "The GIL is a mutex that prevents multiple native threads from executing Python bytecodes simultaneously in CPython."),
            ("How do generators and the `yield` keyword differ from standard iterator classes in memory efficiency?",
             "Generators produce items lazily on demand without loading the entire collection into memory.")
        ],
        "hard": [
            ("How would you profile, optimize, and eliminate CPU bottlenecks in a high-throughput asyncio event loop?",
             "By offloading CPU-bound tasks to ProcessPoolExecutor, using uvloop, profiling with cProfile/yappi, and avoiding blocking I/O calls."),
            ("Explain Python's method resolution order (MRO) and C3 linearization in multiple inheritance.",
             "C3 linearization computes a consistent deterministic linear class precedence order that preserves local precedence and monotonicity.")
        ]
    },
    "Web Development / React / JS": {
        "easy": [
            ("What is the difference between `var`, `let`, and `const` in modern JavaScript (ES6+)?",
             "`var` is function-scoped and hoisted, whereas `let` and `const` are block-scoped; `const` cannot be reassigned."),
            ("How does the Virtual DOM work in React and how does it optimize UI re-rendering?",
             "React maintains an in-memory Virtual DOM tree, computes diffs against the previous tree, and batches minimal DOM updates.")
        ],
        "medium": [
            ("How do React Hooks like `useEffect` and `useCallback` manage closures and stale state dependencies?",
             "`useEffect` and `useCallback` require accurate dependency arrays to prevent capturing stale closures across renders."),
            ("Explain Server-Side Rendering (SSR) vs Static Site Generation (SSG) and their respective trade-offs in Next.js.",
             "SSR renders HTML dynamically per request on the server, while SSG pre-renders static HTML at build time for lower latency.")
        ],
        "hard": [
            ("How does the JavaScript event loop handle microtasks (Promises) versus macrotasks (setTimeout/I/O) under high concurrency?",
             "Microtasks in the microtask queue are executed immediately after the current call stack before any macrotasks are processed."),
            ("How would you architect a zero-runtime CSS or WebAssembly module to optimize Web Vitals (LCP, FID, CLS)?",
             "By minimizing JS bundle execution, code-splitting routes, using critical CSS inlining, and offloading compute to WebAssembly.")
        ]
    },
    "Database & SQL": {
        "easy": [
            ("What is the difference between `INNER JOIN`, `LEFT JOIN`, and `FULL OUTER JOIN` in SQL?",
             "`INNER JOIN` returns matching rows; `LEFT JOIN` returns all left rows plus matched right rows; `FULL OUTER JOIN` returns all rows."),
            ("What is the purpose of database normalization and what are the rules of 1NF, 2NF, and 3NF?",
             "Normalization reduces data redundancy; 1NF requires atomic values, 2NF eliminates partial dependencies, 3NF eliminates transitive dependencies.")
        ],
        "medium": [
            ("How do B-tree indexes speed up SQL queries and what are composite indexing best practices?",
             "B-tree indexes maintain balanced sorted trees for logarithmic lookups; composite indexes should order columns by selectivity and query filter order."),
            ("Explain the ACID properties of relational databases and how transaction isolation levels affect concurrency.",
             "ACID guarantees Atomicity, Consistency, Isolation, and Durability; isolation levels range from Read Uncommitted to Serializable.")
        ],
        "hard": [
            ("How would you diagnose and resolve deadlocks and table locks in a PostgreSQL database experiencing 50,000 writes/sec?",
             "By analyzing pg_locks/pg_stat_activity, ensuring consistent lock acquisition ordering, partitioning tables, and tuning wal_buffers."),
            ("Explain database sharding strategies (hash-based vs range-based) and how you manage distributed cross-shard transactions.",
             "Hash sharding evenly distributes data using consistent hashing; distributed transactions require 2-Phase Commit (2PC) or Saga patterns.")
        ]
    },
    "Cloud & DevOps": {
        "easy": [
            ("What is containerization with Docker and how does a container differ from a virtual machine?",
             "Containers share the host OS kernel and are lightweight, whereas VMs run a complete guest OS on top of a hypervisor."),
            ("What is CI/CD and how does an automated deployment pipeline improve software reliability?",
             "CI/CD continuously integrates code with automated tests and builds, automating release deployments to reduce manual human errors.")
        ],
        "medium": [
            ("How does Kubernetes orchestrate containers and what is the function of Pods, Deployments, and Services?",
             "Kubernetes automates container scheduling; Pods are the smallest deployable units, Deployments manage replicas, and Services handle networking."),
            ("Explain Infrastructure as Code (IaC) using Terraform and how state locking prevents deployment race conditions.",
             "Terraform defines cloud resources declaratively in HCL; remote backend state locking ensures only one deployment modifies resources at a time.")
        ],
        "hard": [
            ("How would you design a zero-downtime Blue-Green or Canary deployment architecture on AWS EKS with Istio service mesh?",
             "By configuring Istio virtual services to route 5% traffic to canary pods, monitoring Prometheus error rates, and shifting traffic on health checks."),
            ("How do you handle multi-region active-active database replication and failover latency across AWS regions?",
             "Using Aurora Global Database or CockroachDB with multi-region quorum consensus and Route 53 latency-based routing.")
        ]
    },
    "Data Structures & Algorithms": {
        "easy": [
            ("What is the time and space complexity of binary search compared to linear search?",
             "Binary search has O(log n) time complexity on sorted arrays, whereas linear search has O(n) time complexity."),
            ("Explain how a hash map works and how hash collisions are resolved using chaining or open addressing.",
             "Hash maps use a hash function to map keys to bucket indices; collisions are handled by linked lists (chaining) or probing (open addressing).")
        ],
        "medium": [
            ("What are the core differences between Breadth-First Search (BFS) and Depth-First Search (DFS) in graph traversal?",
             "BFS uses a queue to traverse layer-by-layer (finding shortest unweighted paths), while DFS uses a stack/recursion to explore branches deeply."),
            ("Explain Dynamic Programming and the difference between top-down memoization and bottom-up tabulation.",
             "Dynamic programming breaks problems into overlapping subproblems; top-down memoizes recursion, bottom-up builds tabular solutions iteratively.")
        ],
        "hard": [
            ("How would you implement a distributed Least Recently Used (LRU) cache with O(1) get/put operations and thread safety?",
             "Using a Doubly Linked List paired with a Hash Map and read-write locks or concurrent skip-lists."),
            ("Explain Trie data structure operations and how you would design an autocomplete search system for 100 million queries.",
             "A Trie stores strings by character nodes; autocomplete queries can be precomputed with top-k heaps at each prefix node.")
        ]
    },
    "AI & Machine Learning": {
        "easy": [
            ("What is the difference between supervised, unsupervised, and reinforcement learning?",
             "Supervised learning uses labeled training data, unsupervised finds latent patterns in unlabeled data, and RL learns policies via rewards."),
            ("What is overfitting and how do techniques like cross-validation and L1/L2 regularization prevent it?",
             "Overfitting occurs when a model memorizes training noise; regularization penalizes large weights to encourage simpler models.")
        ],
        "medium": [
            ("Explain the Transformer self-attention mechanism and how multi-head attention captures linguistic dependencies.",
             "Self-attention computes Query-Key dot products to dynamically weigh token relevance across the entire sequence."),
            ("How do embeddings work in NLP and how does vector similarity (cosine distance) enable semantic search?",
             "Embeddings represent words/sentences as dense vectors in semantic space; cosine distance measures angle alignment between vectors.")
        ],
        "hard": [
            ("How would you design a Low-Rank Adaptation (LoRA) fine-tuning pipeline for large language models on limited GPU memory?",
             "By freezing base model weights and inserting trainable rank decomposition matrices into attention layers (e.g. Q and V projections)."),
            ("How do you mitigate hallucination in retrieval-augmented generation (RAG) systems serving 10,000 concurrent queries?",
             "By using hybrid dense-sparse vector search, re-ranking with cross-encoders, and strict prompt grounding with citation verification.")
        ]
    }
}

# Candidate profile archetypes
CANDIDATE_ARCHETYPES = [
    {
        "role": "Python Backend Developer",
        "skills": ["Python", "FastAPI", "PostgreSQL", "Docker", "Redis"],
        "experience": "2 years",
        "education": "B.Sc. in Computer Science",
        "projects": "Built high-throughput REST APIs and Redis caching microservice"
    },
    {
        "role": "Full Stack Engineer",
        "skills": ["JavaScript", "React", "Node.js", "MongoDB", "TailwindCSS"],
        "experience": "3 years",
        "education": "B.E. in Information Technology",
        "projects": "Developed real-time collaborative dashboard with WebSockets"
    },
    {
        "role": "DevOps & Cloud Engineer",
        "skills": ["Docker", "Kubernetes", "AWS", "Terraform", "CI/CD", "Linux"],
        "experience": "4 years",
        "education": "B.Tech in Computer Engineering",
        "projects": "Automated multi-region Kubernetes deployment pipelines with Terraform"
    },
    {
        "role": "AI & ML Engineer",
        "skills": ["Python", "PyTorch", "NLP", "Transformers", "FastAPI", "Vector DB"],
        "experience": "2 years",
        "education": "M.Sc. in Artificial Intelligence",
        "projects": "Built RAG search pipeline using sentence embeddings and LLMs"
    },
    {
        "role": "Junior Software Engineer",
        "skills": ["Python", "Data Structures", "SQL", "Git", "OOP"],
        "experience": "Entry Level / 0-1 year",
        "education": "B.Sc. in Computer Science",
        "projects": "Completed university capstone project on database optimization"
    },
    {
        "role": "Senior Backend Architect",
        "skills": ["Python", "PostgreSQL", "System Design", "Microservices", "Kafka", "Docker"],
        "experience": "6 years",
        "education": "B.Tech in Computer Science",
        "projects": "Architected distributed event-driven payment processing engine handling 20k TPS"
    }
]

def generate_profile_questions_dataset():
    """Builds paired instruction prompts for generating 10 distinct profile-tailored questions."""
    examples = []

    for arch in CANDIDATE_ARCHETYPES:
        role = arch["role"]
        skills = arch["skills"]
        exp = arch["experience"]
        proj = arch["projects"]

        for stage in range(1, 11):
            if stage in [1, 2]:
                diff = "easy"
                focus = f"Core foundational concept in {skills[0]}"
            elif stage in [3, 4]:
                diff = "medium"
                focus = f"Applied practical concept in {skills[1] if len(skills) > 1 else skills[0]}"
            elif stage in [5, 6]:
                diff = "medium"
                focus = f"System architecture, database, or tool in {skills[2] if len(skills) > 2 else 'Database & SQL'}"
            elif stage in [7, 8]:
                diff = "medium-hard"
                focus = f"Project scenario based on: {proj}"
            else:
                diff = "hard"
                focus = f"Advanced scalability, trade-offs, and deep mechanisms in {skills[0]}"

            prompt = (
                f"Generate a {diff.upper()} interview question for Candidate Profile:\n"
                f"- Target Role: {role}\n"
                f"- Experience: {exp}\n"
                f"- Technical Skills: {', '.join(skills)}\n"
                f"- Project Experience: {proj}\n"
                f"- Interview Stage: Question {stage} of 10 ({focus})\n"
                f"Question:"
            )

            # Sample domain questions
            primary_domain = None
            for d in DOMAINS:
                if any(s.lower() in d.lower() or d.lower() in s.lower() for s in skills):
                    primary_domain = d
                    break
            if not primary_domain:
                primary_domain = "Python"

            tier = "easy" if diff == "easy" else ("hard" if diff == "hard" else "medium")
            domain_pool = DOMAINS.get(primary_domain, DOMAINS["Python"]).get(tier, DOMAINS["Python"]["easy"])
            q_text, b_ans = random.choice(domain_pool)

            examples.append({
                "prompt": prompt,
                "target": q_text,
                "stage": stage,
                "difficulty": diff,
                "benchmark_answer": b_ans,
                "category": primary_domain,
                "role": role
            })

    with open(TRAIN_DATASET_PATH, "w", encoding="utf-8") as f:
        for ex in examples:
            f.write(json.dumps(ex) + "\n")

    print(f"[OK] Generated {len(examples)} candidate profile question training examples to {TRAIN_DATASET_PATH}")
    return examples


def generate_followup_dataset():
    """Builds paired instruction prompts for generating dynamic follow-up questions conditioned on candidate answers."""
    followup_patterns = [
        ("What is Python?",
         "Python is an interpreted, object-oriented, high-level programming language with dynamic typing.",
         "Can you explain how Python's dynamic typing is implemented internally compared to statically typed languages?",
         "Strong"),
        ("What is Python?",
         "It's a programming language for writing scripts.",
         "Could you give a concrete example of a real-world application or web framework built with Python?",
         "Average"),
        ("How does the Virtual DOM work in React?",
         "React keeps a lightweight copy of the real DOM in memory and diffs it during state changes.",
         "How does React's reconciliation algorithm ensure minimal re-renders when rendering large lists of items with keys?",
         "Strong"),
        ("What is database normalization?",
         "Normalization organizes tables to reduce redundancy.",
         "Can you describe a scenario where you would intentionally denormalize a database table for read-heavy performance?",
         "Strong"),
        ("What is a container in Docker?",
         "A container is a packaged application that runs anywhere.",
         "How do Docker containers leverage Linux namespaces and cgroups for process isolation and resource limiting?",
         "Strong"),
        ("How do you handle deadlocks in SQL?",
         "I would check locks and retry transactions.",
         "What specific database isolation level or query locking strategy (e.g., SELECT FOR UPDATE) would you apply to prevent deadlocks upfront?",
         "Average")
    ]

    examples = []
    for q_text, ans_text, followup_q, rating in followup_patterns:
        prompt = (
            f"Generate an intelligent interview follow-up question based on the candidate's response:\n"
            f"- Previous Question: {q_text}\n"
            f"- Candidate Answer: {ans_text}\n"
            f"- Demonstrated Performance: {rating}\n"
            f"Follow-up Question:"
        )

        examples.append({
            "prompt": prompt,
            "target": followup_q,
            "parent_question": q_text,
            "candidate_answer": ans_text,
            "performance": rating
        })

    with open(FOLLOWUP_DATASET_PATH, "w", encoding="utf-8") as f:
        for ex in examples:
            f.write(json.dumps(ex) + "\n")

    print(f"[OK] Generated {len(examples)} contextual follow-up training examples to {FOLLOWUP_DATASET_PATH}")
    return examples


if __name__ == "__main__":
    generate_profile_questions_dataset()
    generate_followup_dataset()
