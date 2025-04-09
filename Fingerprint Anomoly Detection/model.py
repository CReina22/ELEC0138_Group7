import pandas as pd
from sklearn.ensemble import IsolationForest
import sqlite3
import joblib



# Add a method to check fingerprint similarity
def check_fingerprint_similarity(new_fingerprint_hash, existing_hashes):
    from sklearn.metrics.pairwise import cosine_similarity
    import numpy as np

    new_hash_array = np.array([new_fingerprint_hash]).reshape(1, -1)
    existing_hash_array = np.array(existing_hashes).reshape(-1, 1)

    similarity_scores = cosine_similarity(new_hash_array, existing_hash_array)
    return similarity_scores.max()