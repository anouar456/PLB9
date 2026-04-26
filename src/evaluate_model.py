 
"""
evaluate_model.py
-----------------
Évaluation approfondie du meilleur modèle sauvegardé.
Génère :
- Métriques complètes (Accuracy, F1-Macro, F1-Weighted, ROC-AUC)
- Matrice de confusion finale
- Courbes ROC (une par classe pour classification binaire)
- Interprétation automatique des résultats
"""

import os
import sys
import joblib
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import warnings
warnings.filterwarnings('ignore')

from sklearn.metrics import (
    accuracy_score, f1_score,
    classification_report, confusion_matrix,
    roc_auc_score, roc_curve, auc
)

# Chemins
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.abspath(os.path.join(current_dir, '..'))
DATA_DIR = os.path.join(project_root, 'data', 'processed')
MODELS_DIR = os.path.join(project_root, 'models')
OUTPUTS_DIR = os.path.join(project_root, 'outputs')
os.makedirs(OUTPUTS_DIR, exist_ok=True)

print("="*60)
print("🔍 DÉMARRAGE DE L'ÉVALUATION")
print("="*60)


# ============================================
# 1. CHARGEMENT DU MEILLEUR MODÈLE ET DONNÉES
# ============================================
def load_best_model_and_data(plant_id='1'):
    """Charge le meilleur modèle et les données de test"""
    
    # Charger le modèle
    model_path = os.path.join(MODELS_DIR, f'best_model_plant_{plant_id}.pkl')
    if not os.path.exists(model_path):
        raise FileNotFoundError(f"Modèle introuvable : {model_path}")
    
    model = joblib.load(model_path)
    print(f"✅ Modèle chargé : {model_path}")
    
    # Charger les données de test
    test_path = os.path.join(DATA_DIR, f'test_plant_{plant_id}.csv')
    test_df = pd.read_csv(test_path)
    
    X_test = test_df.drop('power_peak', axis=1)
    y_test = test_df['power_peak']
    
    # Charger les métriques sauvegardées
    metrics_path = os.path.join(MODELS_DIR, f'best_metrics_plant_{plant_id}.pkl')
    if os.path.exists(metrics_path):
        metrics_info = joblib.load(metrics_path)
        print(f"📊 Métriques sauvegardées : Accuracy={metrics_info['accuracy']:.2%}")
    
    return model, X_test, y_test


# ============================================
# 2. CALCUL DES MÉTRIQUES
# ============================================
def compute_metrics(y_test, y_pred, y_proba):
    """Calcule toutes les métriques d'évaluation"""
    
    print("\n" + "="*60)
    print("📊 MÉTRIQUES GLOBALES")
    print("="*60)
    
    accuracy = accuracy_score(y_test, y_pred)
    f1 = f1_score(y_test, y_pred)
    
    # ROC-AUC
    try:
        roc_auc = roc_auc_score(y_test, y_proba)
    except:
        roc_auc = None
    
    print(f"   Accuracy   : {accuracy:.4f} ({accuracy*100:.2f}%)")
    print(f"   F1-Score   : {f1:.4f}")
    if roc_auc:
        print(f"   ROC-AUC    : {roc_auc:.4f}")
    
    # Interprétation clinique
    print("\n🩺 Interprétation :")
    if accuracy >= 0.95:
        print("   🟢 Excellent — modèle fiable pour la détection des pics")
    elif accuracy >= 0.85:
        print("   🟡 Correct — supervision recommandée")
    else:
        print("   🔴 Insuffisant — à améliorer")
    
    # Rapport détaillé
    print("\n" + "="*60)
    print("📋 RAPPORT PAR CLASSE")
    print("="*60)
    print(classification_report(y_test, y_pred, target_names=['Normal', 'Pic']))
    
    return {
        'accuracy': accuracy,
        'f1_score': f1,
        'roc_auc': roc_auc
    }


# ============================================
# 3. MATRICE DE CONFUSION
# ============================================
def plot_confusion_matrix_final(y_test, y_pred, plant_id):
    """Matrice de confusion finale"""
    
    plt.figure(figsize=(8, 6))
    cm = confusion_matrix(y_test, y_pred)
    sns.heatmap(cm, annot=True, fmt='d', cmap='Blues',
                xticklabels=['Normal', 'Pic'],
                yticklabels=['Normal', 'Pic'])
    plt.title(f'Matrice de Confusion - Centrale {plant_id}')
    plt.xlabel('Prédit')
    plt.ylabel('Réel')
    plt.tight_layout()
    
    path = os.path.join(OUTPUTS_DIR, f'confusion_matrix_final_plant_{plant_id}.png')
    plt.savefig(path)
    plt.close()
    print(f"   ✅ Matrice sauvegardée : {path}")


# ============================================
# 4. COURBE ROC
# ============================================
def plot_roc_curve(y_test, y_proba, plant_id):
    """Trace la courbe ROC"""
    
    try:
        fpr, tpr, _ = roc_curve(y_test, y_proba)
        roc_auc = auc(fpr, tpr)
        
        plt.figure(figsize=(8, 6))
        plt.plot(fpr, tpr, color='darkorange', lw=2,
                 label=f'ROC curve (AUC = {roc_auc:.2f})')
        plt.plot([0, 1], [0, 1], color='navy', lw=2, linestyle='--')
        plt.xlim([0.0, 1.0])
        plt.ylim([0.0, 1.05])
        plt.xlabel('Taux de Faux Positifs')
        plt.ylabel('Taux de Vrais Positifs')
        plt.title(f'Courbe ROC - Centrale {plant_id}')
        plt.legend(loc="lower right")
        plt.tight_layout()
        
        path = os.path.join(OUTPUTS_DIR, f'roc_curve_plant_{plant_id}.png')
        plt.savefig(path)
        plt.close()
        print(f"   ✅ Courbe ROC sauvegardée : {path}")
        
    except Exception as e:
        print(f"   ⚠️ Erreur ROC : {e}")


# ============================================
# 5. HISTOGRAMME DES PROBABILITÉS
# ============================================
def plot_probability_distribution(y_test, y_proba, plant_id):
    """Distribution des probabilités prédites"""
    
    plt.figure(figsize=(10, 5))
    
    # Proba pour les vrais négatifs (Normal)
    plt.subplot(1, 2, 1)
    plt.hist(y_proba[y_test == 0], bins=20, alpha=0.7, color='green', edgecolor='black')
    plt.xlabel('Probabilité prédite pour "Pic"')
    plt.ylabel('Fréquence')
    plt.title(f'Vrais Négatifs (Normal)\nCentrale {plant_id}')
    plt.xlim(0, 1)
    
    # Proba pour les vrais positifs (Pic)
    plt.subplot(1, 2, 2)
    plt.hist(y_proba[y_test == 1], bins=20, alpha=0.7, color='red', edgecolor='black')
    plt.xlabel('Probabilité prédite pour "Pic"')
    plt.ylabel('Fréquence')
    plt.title(f'Vrais Positifs (Pic)\nCentrale {plant_id}')
    plt.xlim(0, 1)
    
    plt.tight_layout()
    path = os.path.join(OUTPUTS_DIR, f'prob_distribution_plant_{plant_id}.png')
    plt.savefig(path)
    plt.close()
    print(f"   ✅ Distribution sauvegardée : {path}")


# ============================================
# 6. RAPPORT FINAL
# ============================================
def generate_report(metrics, plant_id):
    """Génère un rapport textuel"""
    
    report = f"""
============================================================
RAPPORT D'ÉVALUATION - CENTRALE {plant_id}
============================================================

📊 PERFORMANCES GLOBALES :
   - Accuracy : {metrics['accuracy']*100:.2f}%
   - F1-Score : {metrics['f1_score']:.4f}
   - ROC-AUC  : {metrics['roc_auc']:.4f}

🩺 INTERPRÉTATION :
   Le modèle est {'EXCELLENT' if metrics['accuracy'] >= 0.95 else 'BON' if metrics['accuracy'] >= 0.85 else 'À AMÉLIORER'}
   pour la détection des pics de puissance.

📁 FICHIERS GÉNÉRÉS :
   - Matrice de confusion : confusion_matrix_final_plant_{plant_id}.png
   - Courbe ROC : roc_curve_plant_{plant_id}.png
   - Distribution : prob_distribution_plant_{plant_id}.png

============================================================
"""
    # Sauvegarde du rapport
    path = os.path.join(OUTPUTS_DIR, f'report_plant_{plant_id}.txt')
    with open(path, 'w', encoding='utf-8') as f:
        f.write(report)
    print(report)


# ============================================
# 7. EXÉCUTION PRINCIPALE
# ============================================
if __name__ == "__main__":
    
    for plant_id in ['1', '2']:
        print(f"\n{'='*60}")
        print(f"🔍 ÉVALUATION - CENTRALE {plant_id}")
        print(f"{'='*60}")
        
        try:
            # Charger modèle et données
            model, X_test, y_test = load_best_model_and_data(plant_id)
            
            # Prédictions
            y_pred = model.predict(X_test)
            y_proba = model.predict_proba(X_test)[:, 1]
            
            # Métriques
            metrics = compute_metrics(y_test, y_pred, y_proba)
            
            # Graphiques
            plot_confusion_matrix_final(y_test, y_pred, plant_id)
            plot_roc_curve(y_test, y_proba, plant_id)
            plot_probability_distribution(y_test, y_proba, plant_id)
            
            # Rapport
            generate_report(metrics, plant_id)
            
        except Exception as e:
            print(f"❌ Erreur centrale {plant_id}: {e}")
    
    print("\n" + "="*60)
    print("✅ ÉVALUATION TERMINÉE")
    print("="*60)