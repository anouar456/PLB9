"""
train_model.py
--------------
Entraîne 3  modèles  ML pour la prédiction des pics de puissance solaire :
- Random Forest
- XGBoost
- LightGBM
"""

import os
import joblib
import pandas as pd
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import (accuracy_score, precision_score,
                             recall_score, f1_score, confusion_matrix)
import warnings
warnings.filterwarnings('ignore')

# ── Chemins ───────────────────────────────────────────────────────────────────
current_dir  = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.abspath(os.path.join(current_dir, '..'))
DATA_DIR     = os.path.join(project_root, 'data', 'processed')
MODELS_DIR   = os.path.join(project_root, 'models')
os.makedirs(MODELS_DIR, exist_ok=True)


# ── 1. Chargement ─────────────────────────────────────────────────────────────
def load_processed_data(plant_id='1'):
    train_df = pd.read_csv(os.path.join(DATA_DIR, f'train_plant_{plant_id}.csv'))
    test_df  = pd.read_csv(os.path.join(DATA_DIR, f'test_plant_{plant_id}.csv'))

    X_train = train_df.drop('power_peak', axis=1)
    y_train = train_df['power_peak']
    X_test  = test_df.drop('power_peak', axis=1)
    y_test  = test_df['power_peak']

    print(f"📊 Centrale {plant_id} : {X_train.shape[0]} train | {X_test.shape[0]} test")
    return X_train, X_test, y_train, y_test


# ── 2. Entraînement et évaluation ─────────────────────────────────────────────
def train_and_evaluate(model, model_name, X_train, X_test, y_train, y_test):
    print(f"\n{'='*50}")
    print(f"🚀 Entraînement : {model_name}")
    print(f"{'='*50}")

    model.fit(X_train, y_train)
    y_pred = model.predict(X_test)

    metrics = {
        'model_name'   : model_name,
        'model'        : model,
        'accuracy_test': accuracy_score(y_test, y_pred),
        'precision'    : precision_score(y_test, y_pred, zero_division=0),
        'recall'       : recall_score(y_test, y_pred, zero_division=0),
        'f1_score'     : f1_score(y_test, y_pred, zero_division=0),
        'y_pred'       : y_pred
    }

    print(f"✅ Accuracy  : {metrics['accuracy_test']*100:.2f}%")
    print(f"✅ Precision : {metrics['precision']:.4f}")
    print(f"✅ Recall    : {metrics['recall']:.4f}")
    print(f"✅ F1-Score  : {metrics['f1_score']:.4f}")
    return metrics


# ── 3. Modèles ────────────────────────────────────────────────────────────────
def create_models():
    try:
        from xgboost import XGBClassifier
        xgb = XGBClassifier(n_estimators=100, max_depth=6,
                            learning_rate=0.1, random_state=42,
                            eval_metric='logloss', verbosity=0)
    except ImportError:
        print("[WARNING] XGBoost non installé — pip install xgboost")
        xgb = None

    try:
        from lightgbm import LGBMClassifier
        lgbm = LGBMClassifier(n_estimators=100, max_depth=8,
                              learning_rate=0.1, random_state=42, verbose=-1)
    except ImportError:
        print("[WARNING] LightGBM non installé — pip install lightgbm")
        lgbm = None

    models = {
        'Random Forest': RandomForestClassifier(
            n_estimators=100, max_depth=10, random_state=42, n_jobs=-1)
    }
    if xgb:  models['XGBoost']  = xgb
    if lgbm: models['LightGBM'] = lgbm
    return models


# ── 4. Matrice de confusion ───────────────────────────────────────────────────
def plot_confusion_matrix(y_true, y_pred, model_name, plant_id):
    plt.figure(figsize=(5, 4))
    cm = confusion_matrix(y_true, y_pred)
    sns.heatmap(cm, annot=True, fmt='d', cmap='Blues')
    plt.title(f'Confusion Matrix - {model_name}')
    plt.xlabel('Prédit'); plt.ylabel('Réel')
    plt.tight_layout()
    fname = f'cm_{model_name.lower().replace(" ","_")}_plant_{plant_id}.png'
    plt.savefig(os.path.join(MODELS_DIR, fname))
    plt.close()
    print(f"   📊 {fname} sauvegardé")


# ── 5. Comparaison ────────────────────────────────────────────────────────────
def compare_models(results):
    df = pd.DataFrame([{
        'Modèle'   : r['model_name'],
        'Accuracy' : round(r['accuracy_test'], 4),
        'Précision': round(r['precision'], 4),
        'Rappel'   : round(r['recall'], 4),
        'F1-Score' : round(r['f1_score'], 4)
    } for r in results]).sort_values('F1-Score', ascending=False)

    print("\n" + "="*60)
    print("📊 COMPARAISON DES MODÈLES")
    print("="*60)
    print(df.to_string(index=False))
    return df


# ── 6. Sauvegarde meilleur modèle ─────────────────────────────────────────────
def save_best_model(results, plant_id):
    best = max(results, key=lambda x: x['f1_score'])
    print(f"\n🏆 MEILLEUR : {best['model_name']} — F1={best['f1_score']:.4f}")

    joblib.dump(best['model'],
                os.path.join(MODELS_DIR, f'best_model_plant_{plant_id}.pkl'))
    joblib.dump({'model_name': best['model_name'],
                 'accuracy'  : best['accuracy_test'],
                 'f1_score'  : best['f1_score']},
                os.path.join(MODELS_DIR, f'best_metrics_plant_{plant_id}.pkl'))
    print(f"✅ Modèle sauvegardé dans {MODELS_DIR}")
    return best


# ── 7. Pipeline ───────────────────────────────────────────────────────────────
def train_pipeline(plant_id='1'):
    print(f"\n{'='*60}\n🏭 ENTRAÎNEMENT - CENTRALE {plant_id}\n{'='*60}")

    X_train, X_test, y_train, y_test = load_processed_data(plant_id)
    models  = create_models()
    results = []

    for name, model in models.items():
        result = train_and_evaluate(model, name, X_train, X_test, y_train, y_test)
        results.append(result)
        plot_confusion_matrix(y_test, result['y_pred'], name, plant_id)

    compare_models(results)
    best = save_best_model(results, plant_id)
    return results, best


# ── Exécution ─────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    for plant in ['1', '2']:
        train_pipeline(plant)

    print("\n" + "="*60)
    print("✅ ENTRAÎNEMENT TERMINÉ POUR LES 2 CENTRALES !")
    print("="*60)