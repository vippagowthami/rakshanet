# Literature Review - RakshaNet (Table Format)

## 1. Research Studies Summary

| S.No | Author | Year | Title | Method | Dataset | Accuracy/Merit | Limitations |
|------|--------|------|-------|--------|---------|--------|--|
| 1 | Nitcholas P Tatcnett, Patrick B Rousti, Daneith Gu | 2022 | Data-Driven Field Detection of Drug Effects and Interactions | Adaptive Bayesian Corrected Mining-SCRIBD | FDA AERS, SIDER LRMs | Detects drug interaction patterns | Limited to databases |
| 2 | Veer Patel, Mann Shah | 2022 | Artificial Science and Machine Learning in Drug Discovery | Survey of ML/NLP approaches | 36 studies, public DBs | Cost-effective, high potential | Skill gaps in application |
| 3 | Ha Vuong, Jang, Howard Lee-Birchell Moen | 2022 | ML-based Quantitative Prediction of Exposure in DCIs | PK-QSAR, Guard-active ML approach | FDA Table's DrugBank (HMSE 0.59, Robust external validation) | Quantitative accuracy | Fall-out after strong steps |
| 4 | Mengyu Kang, Li Hsu, Xiao Lu | 2023 | Drug-Disease Association Prediction with Literature Fusion | LBMFF (GCN+BERT), Feature fusion | CTD DrugBank, SIDER | Best ALC/ALPH discovery | Needs large literature |
| 5 | Piyush Chandra, Nirmata Gaikwad, Deepti Codevarshi | 2023 | Multi-algo Prediction & Drug Recommendation | Multi-algo (ML/NLP, Rev-ew-NLP) | MLNet DB, Rev-ew-NLP approach | 97-95% for drug disease links | Interpretability small data |
| 6 | Tanisha Palli, Rupali B Hegadi, Gaurav Bhatnagar, S D Kant S'e | 2024 | Disease Prediction & Drug Recommendation with ML | LR, RF, KNN, NB Classifiers | Columbia, Kaggle DB | Early prediction, 65% accuracy robust ensembling | Accuracy <85% |
| 7 | Esmerai Fon, Aheida Fulshi, Salim Jimoh | 2024 | ML Techniques for Predicting Drug-Side Effects | Survey: RF, KNN, SVM MLP, hybrid | SIDER, DrugBank, PubChem | RF best AUC/F1, b/c chemical fusion enhances prediction | Lacks clinical validation across all drugs |
| 8 | Changi'n Chen | 2024 | Research on Drug Class Classification Using ML Model | Research on Drug Classification in Drug Class | Random Forest, Logistic Regression | Simulated patients' histories human error | RF/LR to 85% accuracy |
| 9 | Peter Petscher, Hiroshi Ursa, Lilian Luza | 2025 | Machine Learning for Predicting Drug-Drug Interactions: GNN & Beyond | ML for GNNs & Beyond Neural Networks | GNN/hypergraph, KEGG, TWOSIDES | GNN/hypergraph best DDI prediction | Cannot replace doctor's expert |
| 10 | Okerini Henry, Anayo, Edward, USChe Nwachi | 2025 | Disease Prediction and Drug Recommendation System | Decision Tree, Neural Networks, ML pipeline | Kaggle, survey (4920 pts) personalized recommendation | High accuracy (>95%), personalized recommendation, real-time | Cannot replace doctor's expert |

---

## 2. Machine Learning Models Comparison

| Model | Algorithm Type | Accuracy | Speed | Interpretability | Best Use Case | Dataset Size |
|-------|---|---|---|---|---|---|
| KNN (K-Nearest Neighbors) | Instance-based | 75-82% | Medium | High | Small-medium datasets | < 100K |
| Decision Trees | Tree-based | 80-88% | Fast | Very High | Interpretable decisions | All sizes |
| Logistic Regression | Linear | 78-85% | Fast | High | Binary classification | All sizes |
| Random Forest | Ensemble | 85-92% | Medium | Medium | Robust predictions | < 1M |
| Neural Networks | Deep Learning | 90-95% | Slow | Low (Black box) | Complex patterns | 100K+ |
| Graph Neural Networks | Graph-based | 92-97% | Slow | Medium | Drug interactions | Network data |
| SVM (Support Vector Machine) | Kernel-based | 82-89% | Medium | Low | High-dimensional data | Medium |

---

## 3. Medical Databases Integration

| Database | Full Name | Coverage | Records | Use in RakshaNet | Validation |
|----------|-----------|----------|---------|---|---|
| **AERS** | FDA Adverse Event Reporting System | Drug adverse events | 13M+ | Drug safety alerts | FDA approved |
| **SIDER** | Side Effect Resource | Drug side effects | 1.4M reactions | Side effect prediction | Curated literature |
| **DrugBank** | Drug Information Database | Drug profiles | 13,000+ drugs | Drug-disease mapping | WHO recommended |
| **CTD** | Comparative Toxicogenomics DB | Disease-drug associations | 500K+ | Disease prediction | NIH-supported |
| **KEGG** | Kyoto Encyclopedia of Genes/Genomes | Drug pathways | 18K+ | Drug interaction detection | Peer-reviewed |
| **TWOSIDES** | Drug-Drug Interactions | DDI adverse events | 63.5K interactions | DDI prediction | Machine learning validated |

---

## 4. RakshaNet System Features

| Feature | Component | Input | Output | ML Method | Database |
|---------|-----------|-------|--------|---|---|
| **Drug Recommendation** | Drug Engine | Symptoms, History | Ranked Medications | KNN/RF/NN | DrugBank, SIDER |
| **Disease Prediction** | Diagnosis Module | Symptoms, Demographics | Disease Probability | Decision Tree/NN | CTD, SIDER |
| **Drug Interaction Detection** | Safety Module | Drug List | Interaction Warnings | Graph Neural Network | KEGG, TWOSIDES |
| **Emergency Beacon** | Crisis Module | GPS Location | Alert Distribution | Real-time Alert | Local DB |
| **Resource Allocation** | Crisis Management | Crisis Type, Location | Resource Routes | Optimization Algorithm | Disaster DB |
| **Real-time Chat** | Communication | User Messages | Instant Delivery | Socket/WebSocket | Message Queue |
| **Emergency Contacts** | Network Module | User List | Contact Alert | Broadcasting | User DB |

---

## 5. Data Processing Pipeline

| Stage | Process | Input | Output | Technique | Quality Check |
|-------|---------|-------|--------|-----------|---|
| **1. Collection** | Gather raw data | Patient info, Symptoms, Labs | Raw dataset | APIs, Forms | Data validation rules |
| **2. Cleaning** | Remove errors | Duplicate, Null, Invalid | Clean dataset | Deduplication, Filtering | Null check, Range validation |
| **3. Missing Values** | Handle gaps | Incomplete records | Filled records | Mean/Median/Mode | Imputation accuracy |
| **4. Normalization** | Scale features | Raw numerical values | 0-1 or standardized | Min-Max, Z-score | Distribution check |
| **5. Feature Selection** | Choose relevant features | All features | Important features | Expert review, ML ranking | Domain validation |
| **6. Data Splitting** | Train-test split | Clean dataset | 70% train, 30% test | Random split | Stratification check |
| **7. Model Training** | Train ML models | Training data | Trained model | Supervised learning | Cross-validation score |
| **8. Evaluation** | Test accuracy | Test data | Performance metrics | Confusion matrix | Accuracy >85% |

---

## 6. Performance Metrics by Year

| Year | Best Model | Accuracy | Approach | Key Innovation |
|------|-----------|----------|----------|---|
| 2022 | Bayesian Corrected Mining | 78% | Supervised learning | Adverse event detection |
| 2023 | GCN+BERT Fusion | 89% | Graph + NLP | Literature integration |
| 2024 | Random Forest Ensemble | 88% | Multiple algorithms | Side effect prediction |
| 2025 | Neural Networks + GNN | **>95%** | Deep learning + Graph | DDI prediction, Personalization |

---

## 7. Limitations & Considerations

| Aspect | Limitation | Impact | Mitigation |
|--------|-----------|--------|---|
| **Accuracy** | 85%+ is industry standard, not 100% | Some false positives/negatives | Always flag confidence scores |
| **Clinical Validation** | Cannot replace doctor judgment | Diagnosis errors possible | Mandatory expert review |
| **Demographic Bias** | Model trained on majority datasets | Lower accuracy for minorities | Diverse training data |
| **Rare Diseases** | Insufficient training examples | Poor prediction for rare conditions | Manual specialist input |
| **Data Privacy** | Patient sensitive information | HIPAA/GDPR compliance needed | Encryption, Access control |
| **Real-time Requirements** | ML inference latency | Slow recommendations in emergencies | Edge deployment, caching |
| **Drug Database Updates** | New drugs added frequently | Outdated model knowledge | Continuous learning pipeline |

---

## 8. RakshaNet Target Metrics

| Metric | Target | Current | Status |
|--------|--------|---------|--------|
| Disease Prediction Accuracy | >90% | To be tested | 📊 In development |
| Drug Recommendation Accuracy | >85% | To be tested | 📊 In development |
| DDI Detection Rate | >95% | To be tested | 📊 In development |
| Response Time (Avg) | <2 seconds | TBD | ⏱️ Optimization pending |
| System Uptime | 99.5% | TBD | 🔧 Infrastructure setup |
| Data Security (Encryption) | 256-bit AES | TBD | 🔒 Implementation phase |

---

## 9. Implementation Roadmap

| Phase | Component | Timeline | Dependencies | Status |
|-------|-----------|----------|---|---|
| **Phase 1** | Data pipeline setup | Q1 2026 | Database access | 🟢 Starting |
| **Phase 2** | ML model training | Q2 2026 | Training dataset | 🟡 Planned |
| **Phase 3** | API integration | Q3 2026 | Model deployment | 🟡 Planned |
| **Phase 4** | Crisis features | Q4 2026 | Real-time architecture | 🟡 Planned |
| **Phase 5** | Clinical validation | Q1 2027 | Medical review board | 🟡 Planned |

---

## 10. Dataset Specifications

| Dataset | Type | Size | Features | Source | License |
|---------|------|------|----------|--------|---------|
| AERS | Adverse Events | 13M+ records | Drug, Event, Date, Demographics | FDA | Public domain |
| SIDER | Side Effects | 1.4M reactions | Drug, Effect, Frequency, Severity | Public | CC BY-NC-SA |
| DrugBank | Drug Info | 13,000+ drugs | SMILES, Targets, Interactions, Properties | Open access | Free |
| CTD | Disease-Drug | 500K+ associations | Gene, Chemical, Disease, Reference | Public | Free |
| KEGG | Pathways | 18K+ | Gene, Drug, Pathway, Interaction | Public | Academic use |

---

**Document Version**: 1.0  
**Format**: Table-based Reference Guide  
**Last Updated**: March 2026  
**For**: RakshaNet Healthcare System Documentation
