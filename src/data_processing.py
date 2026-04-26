"""
data_processing.py
------------------
Chargement, nettoyage, encodage, normalisation,
optimisation mémoire et sauvegarde
des données de tension/puissance pour la prédiction des pics de batterie.
"""

import pandas as pd
import numpy as np
import os
import joblib
from sklearn.preprocessing import LabelEncoder, StandardScaler
from sklearn.model_selection import train_test_split


# ============================================
# 1. CHARGEMENT DES DONNÉES
# ============================================

def load_data():
    """Charge les fichiers CSV depuis le dossier data/"""
    
    current_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.abspath(os.path.join(current_dir, '..'))
    data_dir = os.path.join(project_root, 'data')
    
    print(f"[INFO] Recherche des fichiers dans : {data_dir}")
    
    # Lister tous les fichiers CSV
    csv_files = [f for f in os.listdir(data_dir) if f.endswith('.csv')]
    print(f"[INFO] Fichiers trouvés : {csv_files}")
    
    # Dictionnaire pour stocker tous les DataFrames
    all_data = {}
    
    for file in csv_files:
        df = pd.read_csv(os.path.join(data_dir, file))
        all_data[file] = df
        print(f"[INFO] {file} : {df.shape[0]} lignes, {df.shape[1]} colonnes")
    
    # Fusionner les données de generation et météo pour chaque centrale
    # Convention : Plant_X_Generation_Data.csv + Plant_X_Weather_Sensor_Data.csv
    
    df_dict = {}
    
    for name, df in all_data.items():
        if 'Generation' in name:
            plant_id = name.split('_')[1]  # Extrait le numéro de centrale
            weather_name = f"Plant_{plant_id}_Weather_Sensor_Data.csv"
            
            if weather_name in all_data:
                # Fusionner sur la colonne DATE_TIME
                df_merged = pd.merge(
                    df, 
                    all_data[weather_name], 
                    on='DATE_TIME', 
                    how='inner'
                )
                df_dict[plant_id] = df_merged
                print(f"[INFO] Centrale {plant_id} : {df_merged.shape[0]} lignes fusionnées")
    
    # Si pas de fusion possible, prendre le premier fichier
    if not df_dict and csv_files:
        df_dict['default'] = all_data[csv_files[0]]
        print(f"[INFO] Utilisation du fichier par défaut : {csv_files[0]}")
    
    return df_dict


# ============================================
# 2. VÉRIFICATION DES VALEURS MANQUANTES
# ============================================

def handle_missing_values(df):
    """Vérifie et traite les valeurs manquantes."""
    
    missing_before = df.isnull().sum().sum()
    
    if missing_before == 0:
        print("[INFO] Aucune valeur manquante détectée ✅")
        return df
    
    print(f"[INFO] {missing_before} valeurs manquantes détectées")
    
    # Pour les colonnes numériques : remplacer par la médiane
    numeric_cols = df.select_dtypes(include=[np.number]).columns
    for col in numeric_cols:
        if df[col].isnull().sum() > 0:
            median_val = df[col].median()
            df[col].fillna(median_val, inplace=True)
            print(f"[INFO] Colonne {col} : remplie avec médiane = {median_val:.2f}")
    
    # Pour les colonnes non numériques : remplacer par le mode
    non_numeric_cols = df.select_dtypes(exclude=[np.number]).columns
    for col in non_numeric_cols:
        if df[col].isnull().sum() > 0:
            mode_val = df[col].mode()[0]
            df[col].fillna(mode_val, inplace=True)
            print(f"[INFO] Colonne {col} : remplie avec mode = {mode_val}")
    
    missing_after = df.isnull().sum().sum()
    print(f"[INFO] Valeurs manquantes après traitement : {missing_after} ✅")
    
    return df


# ============================================
# 3. OPTIMISATION MÉMOIRE
# ============================================

def optimize_memory(df):
    """
    Optimise l'utilisation mémoire du DataFrame
    en réduisant les types de données :
    - float64 → float32 (2x moins de mémoire)
    - int64   → int32 (2x moins de mémoire)
    - object  → category (si peu de valeurs uniques)
    """
    
    before = df.memory_usage(deep=True).sum() / 1024
    print(f"[INFO] Mémoire avant optimisation : {before:.2f} KB")

    # Optimisation des floats
    for col in df.select_dtypes(include=['float64']).columns:
        df[col] = df[col].astype('float32')
        print(f"   ✓ {col} : float64 → float32")
    
    # Optimisation des entiers
    for col in df.select_dtypes(include=['int64']).columns:
        df[col] = df[col].astype('int32')
        print(f"   ✓ {col} : int64 → int32")
    
    # Optimisation des colonnes textuelles
    for col in df.select_dtypes(include=['object']).columns:
        # Si peu de valeurs uniques, convertir en catégorie
        if df[col].nunique() / len(df) < 0.5:
            df[col] = df[col].astype('category')
            print(f"   ✓ {col} : object → category")

    after = df.memory_usage(deep=True).sum() / 1024
    reduction = ((before - after) / before * 100)
    print(f"[INFO] Mémoire après optimisation  : {after:.2f} KB")
    print(f"[INFO] Réduction : {reduction:.1f}% ✅")
    
    return df


# ============================================
# 4. AJOUT DE LA COLONNE CIBLE (DÉTECTION DES PICS)
# ============================================

def add_target_column(df, power_col='DC_POWER', threshold_pct=80):
    """
    Ajoute une colonne 'power_peak' pour détecter les pics de puissance.
    
    Paramètres :
    - power_col : nom de la colonne contenant la puissance (ex: 'DC_POWER')
    - threshold_pct : pourcentage du max pour définir un pic (ex: 80% = 0.8 * max)
    
    La colonne power_peak vaut :
    - 1 si la puissance dépasse le seuil (pic dangereux)
    - 0 sinon (normal)
    """
    
    if power_col not in df.columns:
        print(f"[WARNING] Colonne {power_col} non trouvée")
        return df
    
    max_power = df[power_col].max()
    threshold = max_power * threshold_pct / 100
    
    df['power_peak'] = (df[power_col] > threshold).astype(int)
    
    print(f"[INFO] Puissance max : {max_power:.2f}")
    print(f"[INFO] Seuil ({threshold_pct}%) : {threshold:.2f}")
    print(f"[INFO] Pics détectés : {df['power_peak'].sum()} / {len(df)} ({df['power_peak'].mean()*100:.1f}%)")
    
    return df


# ============================================
# 5. ENCODAGE DES VARIABLES CATÉGORIELLES
# ============================================

def encode_features(df):
    """Encode les variables catégorielles en valeurs numériques."""
    
    df = df.copy()
    label_encoders = {}
    
    # Identifier les colonnes catégorielles
    categorical_cols = df.select_dtypes(include=['object', 'category']).columns.tolist()
    
    # Exclure la colonne cible si elle est catégorielle
    if 'power_peak' in categorical_cols:
        categorical_cols.remove('power_peak')
    
    print(f"[INFO] Colonnes à encoder : {categorical_cols}")
    
    for col in categorical_cols:
        le = LabelEncoder()
        df[col] = le.fit_transform(df[col].astype(str))
        label_encoders[col] = le
        print(f"   ✓ {col} encodée")
    
    print("[INFO] Encodage terminé ✅")
    return df, label_encoders


# ============================================
# 6. NORMALISATION DES COLONNES NUMÉRIQUES
# ============================================

def normalize_features(X_train, X_test):
    """
    Normalise les colonnes numériques avec StandardScaler.
    - Fit sur X_train uniquement (pour éviter le data leakage)
    - Transform sur X_train et X_test
    """
    
    # Colonnes numériques à normaliser (exclure les colonnes encodées et la cible)
    exclude_cols = [col for col in X_train.columns if 'peak' in col or 'id' in col.lower()]
    numerical_cols = X_train.select_dtypes(include=[np.number]).columns.tolist()
    cols_to_scale = [col for col in numerical_cols if col not in exclude_cols]
    
    if not cols_to_scale:
        print("[WARNING] Aucune colonne à normaliser")
        return X_train, X_test, None
    
    scaler = StandardScaler()
    X_train[cols_to_scale] = scaler.fit_transform(X_train[cols_to_scale])
    X_test[cols_to_scale] = scaler.transform(X_test[cols_to_scale])
    
    print(f"[INFO] Normalisation appliquée sur {len(cols_to_scale)} colonnes : {cols_to_scale} ✅")
    return X_train, X_test, scaler


# ============================================
# 7. SÉPARATION FEATURES / TARGET
# ============================================

def split_features_target(df, target_col='power_peak'):
    """Sépare les features (X) de la variable cible (y)."""
    
    if target_col not in df.columns:
        print(f"[ERROR] Colonne cible '{target_col}' non trouvée")
        return None, None
    
    X = df.drop(columns=[target_col])
    y = df[target_col]
    
    print(f"[INFO] Features : {X.shape[1]} colonnes")
    print(f"[INFO] Target : {target_col} ({y.nunique()} classes : {sorted(y.unique())})")
    
    return X, y


# ============================================
# 8. SPLIT TRAIN / TEST
# ============================================

def split_train_test(X, y, test_size=0.2, random_state=42):
    """
    Divise les données en ensembles d'entraînement et de test.
    - stratify y uniquement si c'est une classification équilibrée
    """
    
    # Vérifier si stratification possible
    stratify = y if y.nunique() <= 10 else None
    
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, 
        test_size=test_size, 
        random_state=random_state, 
        stratify=stratify
    )
    
    print(f"[INFO] Train : {X_train.shape[0]} échantillons")
    print(f"[INFO] Test  : {X_test.shape[0]} échantillons")
    print(f"[INFO] Train target distribution :\n{y_train.value_counts(normalize=True).to_string()}")
    
    return X_train, X_test, y_train, y_test


# ============================================
# 9. SAUVEGARDE DES DONNÉES ET ENCODERS
# ============================================

def save_processed_data(X_train, X_test, y_train, y_test, label_encoders, scaler, plant_id):
    """
    Sauvegarde :
    - Le dataset traité en CSV dans data/processed/
    - Les encoders et scaler avec joblib pour l'app Streamlit
    """
    
    current_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.abspath(os.path.join(current_dir, '..'))
    data_dir = os.path.join(project_root, 'data', 'processed')
    models_dir = os.path.join(project_root, 'models')
    
    os.makedirs(data_dir, exist_ok=True)
    os.makedirs(models_dir, exist_ok=True)
    
    # Sauvegarde CSV
    train_df = X_train.copy()
    train_df['power_peak'] = y_train.values
    train_df.to_csv(os.path.join(data_dir, f'train_processed_plant_{plant_id}.csv'), index=False)
    
    test_df = X_test.copy()
    test_df['power_peak'] = y_test.values
    test_df.to_csv(os.path.join(data_dir, f'test_processed_plant_{plant_id}.csv'), index=False)
    
    print(f"[INFO] Données sauvegardées dans {data_dir} ✅")
    
    # Sauvegarde encoders et scaler
    if label_encoders:
        joblib.dump(label_encoders, os.path.join(models_dir, f'label_encoders_plant_{plant_id}.pkl'))
        print(f"[INFO] Encoders sauvegardés dans {models_dir} ✅")
    
    if scaler:
        joblib.dump(scaler, os.path.join(models_dir, f'scaler_plant_{plant_id}.pkl'))
        print(f"[INFO] Scaler sauvegardé dans {models_dir} ✅")


# ============================================
# 10. PIPELINE COMPLET
# ============================================

def preprocess_pipeline(plant_id='1', power_col='DC_POWER', threshold_pct=80):
    """
    Pipeline complet de prétraitement des données.
    
    Paramètres :
    - plant_id : identifiant de la centrale ('1' ou '2')
    - power_col : colonne de puissance (défaut: 'DC_POWER')
    - threshold_pct : seuil de détection des pics (défaut: 80%)
    """
    
    print("="*60)
    print("🚀 DÉMARRAGE DU PRÉTRAITEMENT")
    print("="*60)
    
    # 1. Charger les données
    data_dict = load_data()
    
    if plant_id not in data_dict and plant_id != 'default':
        print(f"[WARNING] Centrale {plant_id} non trouvée, utilisation de la première disponible")
        plant_id = list(data_dict.keys())[0]
    
    df = data_dict[plant_id]
    print(f"\n[INFO] Traitement de la centrale {plant_id}")
    
    # 2. Nettoyer les valeurs manquantes
    df = handle_missing_values(df)
    
    # 3. Optimiser la mémoire
    df = optimize_memory(df)
    
    # 4. Ajouter la colonne cible (détection des pics)
    df = add_target_column(df, power_col, threshold_pct)
    
    # 5. Encoder les variables catégorielles
    df, label_encoders = encode_features(df)
    
    # 6. Séparer features et target
    X, y = split_features_target(df, target_col='power_peak')
    
    if X is None:
        print("[ERROR] Prétraitement impossible")
        return None, None, None, None, None, None
    
    # 7. Split train/test
    X_train, X_test, y_train, y_test = split_train_test(X, y)
    
    # 8. Normaliser
    X_train, X_test, scaler = normalize_features(X_train, X_test)
    
    # 9. Sauvegarder
    save_processed_data(X_train, X_test, y_train, y_test, label_encoders, scaler, plant_id)
    
    return X_train, X_test, y_train, y_test, label_encoders, scaler


# ============================================
# 11. EXÉCUTION
# ============================================

if __name__ == "__main__":
    
    # Pour la centrale 1
    print("\n" + "="*60)
    print("🏭 TRAITEMENT DE LA CENTRALE 1")
    print("="*60)
    
    X_train_1, X_test_1, y_train_1, y_test_1, encoders_1, scaler_1 = preprocess_pipeline(
        plant_id='1',
        power_col='DC_POWER',
        threshold_pct=80
    )
    
    # Pour la centrale 2 (si elle existe)
    print("\n" + "="*60)
    print("🏭 TRAITEMENT DE LA CENTRALE 2")
    print("="*60)
    
    X_train_2, X_test_2, y_train_2, y_test_2, encoders_2, scaler_2 = preprocess_pipeline(
        plant_id='2',
        power_col='DC_POWER',
        threshold_pct=80
    )
    
    print("\n" + "="*60)
    print("✅ PRÉTRAITEMENT TERMINÉ AVEC SUCCÈS !")
    print("="*60)
    
    if X_train_1 is not None:
        print(f"\n📊 Centrale 1 - Train shape : {X_train_1.shape}, Test shape : {X_test_1.shape}")
    if X_train_2 is not None:
        print(f"📊 Centrale 2 - Train shape : {X_train_2.shape}, Test shape : {X_test_2.shape} ")