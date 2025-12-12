"""
consensus_tracer.py

Tracks recursive alignment between agents based on symbolic + semantic echoing.
"""

import json
from scipy.spatial.distance import cosine
import numpy as np

def load_embeddings(path):
    with open(path, 'r') as f:
        data = json.load(f)
    return {k: np.array(v) for k, v in data.items()}

def trace_consensus(agent1_emb, agent2_emb, threshold=0.85):
    sim = 1 - cosine(agent1_emb, agent2_emb)
    return sim >= threshold, sim

if __name__ == "__main__":
    agent1 = load_embeddings("agent_1_embedding.json")
    agent2 = load_embeddings("agent_2_embedding.json")

    for key in agent1:
        ok, score = trace_consensus(agent1[key], agent2.get(key, agent1[key]*0))
        print(f"[{key}] → {'✔' if ok else '✘'} (score: {score:.3f})")