# Tools & Technologies

> Maps to **Objective 4** - Design & Develop

---

## Technology Stack

### Backend
| Technology | Purpose |
|-----------|---------|
| Python 3.11 | Core language |
| Flask 3 | REST API framework |
| PostgreSQL (Supabase) | Production database |
| SQLite | Development database |
| scikit-learn | ML (Random Forest, K-Means) |
| imbalanced-learn | SMOTE oversampling |
| SHAP | Model explainability |
| APScheduler | Background OSINT ingestion |

### Frontend
| Technology | Purpose |
|-----------|---------|
| React 18 | UI framework |
| Vite | Build tool |
| TypeScript | Type safety |
| Tailwind CSS v4 | Styling |
| Recharts | Data visualisation |
| Framer Motion | Animations |

### OSINT Sources
| Source | Data Provided |
|-------|--------------|
| Phishing.Database | Live phishing URLs |
| AlienVault OTX | Threat indicators (IoCs) |
| Phishing.Database | URL scanning results |
| Phishing.Database | Community-maintained phishing URLs |

### Infrastructure
| Service | Purpose |
|---------|---------|
| Supabase | Managed PostgreSQL |
| Render | Backend hosting |
| Vercel | Frontend hosting |

## Justification for Choices
- **Why Flask?** Lightweight, Python ecosystem for ML, sufficient for API needs
- **Why React?** Component-based, large ecosystem, team familiarity
- **Why scikit-learn?** Industry standard, great documentation, sufficient for tabular data
- **Why SHAP over LIME?** Theoretical guarantees (Shapley values), better for feature interactions

## Notes
- 
