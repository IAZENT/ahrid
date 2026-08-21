# Chapter 07 - K-Means Clustering: Behavioural Archetypes

> While the Random Forest tells you **how risky** a user is, K-Means tells you **what kind** of user they are. This chapter covers unsupervised learning from scratch.

---

## Part 1: The Theory

### What Is Clustering?

Clustering groups similar data points together **without labels**. Unlike RF (which needs labels like "high risk"), KMeans discovers structure on its own.

**Analogy:** Imagine you have 1000 quiz-takers. You don't know who's careful vs. reckless. But if you measure their speed and accuracy, patterns emerge naturally - some cluster in the "fast and right" region, others in the "fast and wrong" region.

### The K-Means Algorithm

**Input:** Data points (feature vectors) and a desired number of clusters `k`

**Algorithm (Lloyd's algorithm):**

```
1. INITIALISE: Randomly place k centroids in feature space
2. ASSIGN: Assign each data point to its nearest centroid
3. UPDATE: Move each centroid to the mean of its assigned points
4. REPEAT steps 2-3 until centroids stop moving (convergence)
```

### Visual Walkthrough (2D)

```
Step 1: Random centroids (★)       Step 2: Assign points to nearest
                                    
  │     ·  ·                         │     ·  ·        
  │   ·  · ·    ★₁                   │   ·₁ ·₁·₁  ★₁   
  │  · ·· ·                          │  ·₁·₁·₁·₁       
  │              ·  ·                 │              ·₂ ·₂
  │           · ·★₂· ·               │           ·₂·₂★₂·₂·₂
  │            ·· ·                   │            ·₂·₂·₂  
  └─────────────────────             └─────────────────────

Step 3: Move centroids to mean     Step 4: Reassign (converged!)

  │     ·  ·                         │     ·  ·        
  │   ★₁  · ·                        │   ★₁ ·₁·₁      
  │  · ·· ·                          │  ·₁·₁·₁·₁       
  │              ·  ·                 │              ·₂ ·₂
  │           · ·  · ·               │           ·₂·₂  ·₂·₂
  │          ★₂ ·· ·                  │          ★₂·₂·₂·₂  
  └─────────────────────             └─────────────────────
```

### Distance Metric: Euclidean Distance

```
d(a, b) = √( Σ (aᵢ - bᵢ)² )
```

For 6-dimensional feature vectors:
```
d = √( (a₁-b₁)² + (a₂-b₂)² + (a₃-b₃)² + (a₄-b₄)² + (a₅-b₅)² + (a₆-b₆)² )
```

**This is why StandardScaler is essential** - without scaling, `avg_response_time_ms` (range 0-20000) would dominate the distance calculation, making all other features (range 0-1) irrelevant.

---

## Part 2: Your 5 Archetypes

After K-Means groups users into 5 clusters, each cluster is **interpreted** as a behavioural archetype:

### Cluster 0: 🔴 Overconfident Clicker

```python
{
    "label": "Overconfident Clicker",
    "description": "Answers quickly but gets it wrong. High risk of clicking "
                   "phishing links in the real world.",
    "colour": "#EF4444",  # Red
    "icon": "zap",
    "intervention": "Needs slowed-down scenario practice with explicit "
                    "red-flag identification training.",
}
```

**Typical feature profile:**
```
avg_response_time_ms: LOW  (< 3000ms - answering too fast)
overall_accuracy:     LOW  (< 0.40 - getting it wrong)
accuracy_variance:    LOW  (consistently wrong across all categories)
fast_attempt_rate:    HIGH (> 0.50 - rushing through)
total_sessions:       MODERATE
session_consistency:  HIGH (they rush consistently!)
```

### Cluster 1: 🟢 Cautious Learner

```python
{
    "label": "Cautious Learner",
    "description": "Takes time to think and mostly gets it right. Improving "
                   "steadily. On track to become a security asset.",
    "colour": "#22C55E",  # Green
    "icon": "shield-check",
    "intervention": "Needs challenge scenarios at higher difficulty.",
}
```

**Typical feature profile:**
```
avg_response_time_ms: HIGH (> 5000ms - reading carefully)
overall_accuracy:     HIGH (> 0.75)
accuracy_variance:    LOW  (good across all categories)
fast_attempt_rate:    LOW  (< 0.15 - rarely rushes)
total_sessions:       HIGH (engaged)
session_consistency:  HIGH (completes training fully)
```

### Cluster 2: 🟡 Inconsistent Performer

```python
{
    "label": "Inconsistent Performer",
    "description": "Excellent in some categories but has dangerous blind "
                   "spots in others. May have false confidence.",
    "colour": "#F59E0B",  # Amber
    "intervention": "Needs targeted training in weakest categories.",
}
```

**Typical feature profile:**
```
avg_response_time_ms: MODERATE
overall_accuracy:     MODERATE (0.50-0.70)
accuracy_variance:    HIGH (> 0.25 - key signal!)
fast_attempt_rate:    MODERATE
total_sessions:       MODERATE
session_consistency:  MODERATE
```

### Cluster 3: 🔵 Resilient Defender

```python
{
    "label": "Resilient Defender",
    "description": "Fast, accurate, and consistent across all categories. "
                   "A security role model.",
    "colour": "#3B82F6",  # Blue
    "intervention": "Can act as a peer mentor. Needs advanced scenarios.",
}
```

**Typical feature profile:**
```
avg_response_time_ms: MODERATE (fast but not reckless)
overall_accuracy:     VERY HIGH (> 0.85)
accuracy_variance:    VERY LOW (consistent excellence)
fast_attempt_rate:    MODERATE (fast but accurate)
total_sessions:       HIGH
session_consistency:  HIGH
```

### Cluster 4: 🟣 Disengaged Completer

```python
{
    "label": "Disengaged Completer",
    "description": "Completes sessions slowly with inconsistent results. "
                   "Likely not focused. High hidden risk.",
    "colour": "#8B5CF6",  # Purple
    "intervention": "Needs shorter, more frequent gamified sessions.",
}
```

**Typical feature profile:**
```
avg_response_time_ms: HIGH (slow - but from distraction, not care)
overall_accuracy:     LOW-MODERATE (0.40-0.55)
accuracy_variance:    HIGH (erratic)
fast_attempt_rate:    LOW (not rushing - just not paying attention)
total_sessions:       LOW (minimum compliance)
session_consistency:  LOW (inconsistent session lengths)
```

---

## Part 3: The Code

### Training Function

```python
def train_kmeans(*, min_attempts_per_user=5, model_path=None):
    from sklearn.cluster import KMeans
    from sklearn.metrics import silhouette_score
    from sklearn.preprocessing import StandardScaler

    # Step 1: Collect eligible users
    user_ids = [...]  # Users with ≥5 attempts
    
    # Step 2: Build 6-feature vectors
    rows = []
    for uid in user_ids:
        vec = build_feature_vector_for_user(uid)
        if vec is not None:
            rows.append(vec)
    
    # Step 3: Dynamic cluster count
    n_clusters = min(5, max(2, n_users // 2))
    
    # Step 4: Winsorize response times (clip outliers)
    rt_clip = float(np.percentile(X[:, 0], 95))
    X_clustering = X.copy()
    X_clustering[:, 0] = np.clip(X_clustering[:, 0], None, rt_clip)
    
    # Step 5: Scale features to zero mean, unit variance
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X_clustering)
    
    # Step 6: Fit K-Means
    kmeans = KMeans(n_clusters=n_clusters, random_state=42, n_init=10)
    kmeans.fit(X_scaled)
    
    # Step 7: Save everything as one bundle
    bundle = {
        "scaler": scaler,
        "model": kmeans,
        "feature_names": FEATURE_NAMES,
        "n_clusters": n_clusters,
        "rt_clip": rt_clip,
    }
    joblib.dump(bundle, out_path)
```

### Key Parameter: `n_init=10`

```python
KMeans(n_clusters=5, random_state=42, n_init=10)
```

K-Means is **sensitive to initial centroid placement**. `n_init=10` means:
- Run the full algorithm 10 times with different random initial centroids
- Keep the result with the **lowest inertia** (best fit)

This prevents the "bad initialisation" problem where random starting positions lead to suboptimal clusters.

### Dynamic Cluster Count

```python
n_clusters = min(N_CLUSTERS_DEFAULT, max(2, n_users // 2))
# N_CLUSTERS_DEFAULT = 5
```

| Users | Formula | Clusters |
|-------|---------|----------|
| 3 | min(5, max(2, 1)) | 2 |
| 5 | min(5, max(2, 2)) | 2 |
| 10 | min(5, max(2, 5)) | 5 |
| 100 | min(5, max(2, 50)) | 5 |

With < 10 users, using 5 clusters doesn't make sense (some clusters would be empty or have 1 user). The formula scales down gracefully.

---

## Part 4: Assigning Users to Clusters

### During Prediction

```python
class UserClusterer:
    def predict_cluster(self, user_id):
        vec = build_feature_vector_for_user(user_id)
        
        # Apply same winsorization as during training
        vec_clustering = vec.copy()
        if self.rt_clip is not None:
            vec_clustering[0] = min(vec_clustering[0], self.rt_clip)
        
        # Apply same scaling as during training (crucial!)
        scaled = self.scaler.transform(vec_clustering.reshape(1, -1))
        
        # Find nearest centroid
        return int(self.model.predict(scaled)[0])
```

**Critical:** The same `scaler` and `rt_clip` from training must be applied during prediction. That's why they're saved in the bundle.

### Persisting the Assignment

```python
def assign_user_to_cluster(user_id):
    cluster_id = clusterer.predict_cluster(user_id)
    archetype = CLUSTER_ARCHETYPES.get(cluster_id, {})
    
    # Update User record
    user.cluster_label = archetype["label"]
    user.cluster_assigned_at = datetime.utcnow()
    
    # Create UserCluster history record (append-only)
    db.session.add(UserCluster(
        user_id=user_id,
        cluster_id=cluster_id,
        archetype_label=label,
        feature_vector=json.dumps(features),
    ))
```

The `UserCluster` table is **append-only** - it keeps a history of all cluster assignments, so you can track how a user's archetype changes over time.

---

## Part 5: Evaluation Metric - Silhouette Score

```python
from sklearn.metrics import silhouette_score

silhouette = float(silhouette_score(X_scaled, labels))
```

### What Is Silhouette Score?

For each data point, it measures:
- **a** = average distance to other points in the **same cluster** (cohesion)
- **b** = average distance to points in the **nearest other cluster** (separation)

```
silhouette(i) = (b - a) / max(a, b)
```

| Value | Meaning |
|-------|---------|
| +1 | Point is far from other clusters, close to its own (perfect) |
| 0 | Point is on the border between clusters |
| -1 | Point is closer to another cluster than its own (misclassified) |

### Your Score: 0.230

```json
"silhouette_score": 0.23041573719902209
```

**Interpretation:** A silhouette of 0.23 is **moderate** - the clusters have some overlap, which is expected for human behavioural data (people don't neatly fall into distinct categories). For comparison:

| Range | Quality |
|-------|---------|
| > 0.70 | Strong structure (rare in behavioural data) |
| 0.50 - 0.70 | Reasonable structure |
| 0.25 - 0.50 | Weak but potentially useful |
| < 0.25 | No substantial structure |

Your score suggests the clusters are meaningful but not sharply separated - which makes sense for human behaviour.

---

## Part 6: Cluster Summary for Manager Dashboard

```python
def get_cluster_summary():
    users = User.query.all()
    counts = {cid: 0 for cid in CLUSTER_ARCHETYPES}
    
    for u in users:
        label = u.cluster_label
        cid = next(
            (cid for cid, meta in CLUSTER_ARCHETYPES.items() 
             if meta["label"] == label),
            None,
        )
        if cid is not None:
            counts[cid] += 1
    
    return {
        "archetypes": [...],          # Per-archetype counts + percentages
        "most_common_archetype": ...,  # Most frequent archetype
        "intervention_required": [...], # Users in clusters 0, 4 (risky)
    }
```

This powers the **Manager Dashboard**'s cluster pie chart and the "Needs Intervention" list.

---

## 🔬 Exercise

1. **Manually assign a user:** Given this feature vector:
   ```
   avg_rt=2500, accuracy=0.35, variance=0.05, fast_rate=0.55, sessions=4, consistency=0.80
   ```
   Which archetype would you expect this user to belong to? (Think before checking!)

2. **Why 5 clusters?** Your system uses exactly 5 archetypes. If you used `k=3` or `k=7`, what would change? Would some archetypes merge? Would new ones emerge?

3. **Silhouette deep-dive:** The silhouette score is 0.23. What would you do to improve it? (Options: more features, fewer clusters, different algorithm like DBSCAN)

4. **Viva question:** "Why K-Means instead of hierarchical clustering?" Good answer: K-Means is computationally efficient for your dataset size, produces the fixed number of archetypes needed for the UI, and the centroids serve as interpretable "prototypes" for each archetype.

---

> **Next:** [Chapter 08 - SHAP Explainability: Why the Model Decided →](./08_SHAP_EXPLAINABILITY.md)
