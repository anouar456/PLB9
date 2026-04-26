"""
data_processing.py
------------------
Prétraitement des données solaires pour la prédiction des pics de puissance.
"""

import pandas as pd
import numpy as np
import os
import joblib
from sklearn.preprocessing import LabelEncoder, StandardScaler
from sklearn.model_selection import train_test_split

# ── Chemins ───────────────────────────────────────────────────────────────────
current_dir  = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.abspath(os.path.join(current_dir, '..'))
DATA_DIR     = os.path.join(project_root, 'data')
MODELS_DIR   = os.path.join(project_root, 'models')


# ── 1. Chargement ─────────────────────────────────────────────────────────────
def load_data():
    print(f"[INFO] Recherche des fichiers dans : {DATA_DIR}")
    csv_files = [f for f in os.listdir(DATA_DIR) if f.endswith('.csv')]
    print(f"[INFO] Fichiers trouvés : {csv_files}")

    all_data = {}
    for file in csv_files:
        df = pd.read_csv(os.path.join(DATA_DIR, file))
        df['DATE_TIME'] = pd.to_datetime(df['DATE_TIME'], dayfirst=False)
        all_data[file] = df
        print(f"[INFO] {file} : {df.shape[0]} lignes, {df.shape[1]} colonnes")

    df_dict = {}
    for name, df in all_data.items():
        if 'Generation' in name:
            plant_id     = name.split('_')[1]
            weather_name = f"Plant_{plant_id}_Weather_Sensor_Data.csv"
            if weather_name in all_data:
                df_weather = all_data[weather_name].copy()
                df['DATE_TIME']         = df['DATE_TIME'].dt.round('15min')
                df_weather['DATE_TIME'] = df_weather['DATE_TIME'].dt.round('15min')

                df_agg = df.groupby('DATE_TIME').agg(
                    DC_POWER    =('DC_POWER',    'sum'),
                    AC_POWER    =('AC_POWER',    'sum'),
                    DAILY_YIELD =('DAILY_YIELD', 'mean'),
                    TOTAL_YIELD =('TOTAL_YIELD', 'mean'),
                ).reset_index()

                df_merged = pd.merge(df_agg, df_weather, on='DATE_TIME', how='inner')
                df_dict[plant_id] = df_merged
                print(f"[INFO] Centrale {plant_id} : {df_merged.shape[0]} lignes fusionnées")

    return df_dict


# ── 2. Valeurs manquantes ─────────────────────────────────────────────────────
def handle_missing_values(df):
    missing = df.isnull().sum().sum()
    if missing == 0:
        print("[INFO] Aucune valeur manquante ✅")
        return df
    for col in df.select_dtypes(include=[np.number]).columns:
        df[col].fillna(df[col].median(), inplace=True)
    for col in df.select_dtypes(exclude=[np.number]).columns:
        df[col].fillna(df[col].mode()[0], inplace=True)
    print(f"[INFO] Valeurs manquantes traitées ✅")
    return df


# ── 3. Optimisation mémoire ───────────────────────────────────────────────────
def optimize_memory(df):
    if len(df) == 0:
        return df
    before = df.memory_usage(deep=True).sum() / 1024
    print(f"[INFO] Mémoire avant : {before:.2f} KB")

    for col in df.select_dtypes(include=['float64']).columns:
        df[col] = df[col].astype('float32')
        print(f"   ✓ {col} : float64 → float32")
    for col in df.select_dtypes(include=['int64']).columns:
        df[col] = df[col].astype('int32')
        print(f"   ✓ {col} : int64 → int32")
    for col in df.select_dtypes(include=['object']).columns:
        if len(df) > 0 and df[col].nunique() / len(df) < 0.5:
            df[col] = df[col].astype('category')
            print(f"   ✓ {col} : object → category")

    after = df.memory_usage(deep=True).sum() / 1024
    print(f"[INFO] Mémoire après : {after:.2f} KB ({(before-after)/before*100:.1f}% économisé) ✅")
    return df


# ── 4. Colonne cible ──────────────────────────────────────────────────────────
def add_target_column(df, power_col='DC_POWER', threshold_pct=50):
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


# ── 5. Encodage ───────────────────────────────────────────────────────────────
def encode_features(df):
    df = df.copy()
    label_encoders = {}
    categorical_cols = df.select_dtypes(include=['object', 'category']).columns.tolist()
    if 'power_peak' in categorical_cols:
        categorical_cols.remove('power_peak')
    for col in categorical_cols:
        le = LabelEncoder()
        df[col] = le.fit_transform(df[col].astype(str))
        label_encoders[col] = le
        print(f"   ✓ {col} encodée")
    print("[INFO] Encodage terminé ✅")
    return df, label_encoders


# ── 6. Séparation features / target ──────────────────────────────────────────
def split_features_target(df, target_col='power_peak'):
    if target_col not in df.columns:
        print(f"[ERROR] Colonne '{target_col}' non trouvée")
        return None, None
    cols_to_drop = [target_col, 'DATE_TIME', 'SOURCE_KEY', 'PLANT_ID',
                'PLANT_ID_x', 'PLANT_ID_y', 'DC_POWER', 'AC_POWER',
                'DAILY_YIELD', 'TOTAL_YIELD']
    cols_to_drop = [c for c in cols_to_drop if c in df.columns]
    X = df.drop(columns=cols_to_drop)
    y = df[target_col]
    print(f"[INFO] Features : {list(X.columns)}")
    return X, y


# ── 7. Split train / test + SMOTE ────────────────────────────────────────────
def split_train_test(X, y, test_size=0.2, random_state=42):
    from imblearn.over_sampling import SMOTE

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=test_size, random_state=random_state, stratify=y
    )
    # Équilibrer avec SMOTE
    smote = SMOTE(random_state=42)
    X_train, y_train = smote.fit_resample(X_train, y_train)

    print(f"[INFO] Après SMOTE — Train : {X_train.shape[0]} | Test : {X_test.shape[0]}")
    print(f"[INFO] Distribution : {pd.Series(y_train).value_counts().to_dict()}")
    return X_train, X_test, y_train, y_test


# ── 8. Normalisation ──────────────────────────────────────────────────────────
def normalize_features(X_train, X_test):
    numerical_cols = X_train.select_dtypes(include=[np.number]).columns.tolist()
    if not numerical_cols:
        return X_train, X_test, None
    scaler = StandardScaler()
    X_train[numerical_cols] = scaler.fit_transform(X_train[numerical_cols])
    X_test[numerical_cols]  = scaler.transform(X_test[numerical_cols])
    print(f"[INFO] Normalisation sur {len(numerical_cols)} colonnes ✅")
    return X_train, X_test, scaler


# ── 9. Sauvegarde ─────────────────────────────────────────────────────────────
def save_processed_data(X_train, X_test, y_train, y_test, label_encoders, scaler, plant_id):
    processed_dir = os.path.join(DATA_DIR, 'processed')
    os.makedirs(processed_dir, exist_ok=True)
    os.makedirs(MODELS_DIR, exist_ok=True)

    train_df = pd.DataFrame(X_train); train_df['power_peak'] = y_train.values
    test_df  = pd.DataFrame(X_test);  test_df['power_peak']  = y_test.values

    train_df.to_csv(os.path.join(processed_dir, f'train_plant_{plant_id}.csv'), index=False)
    test_df.to_csv(os.path.join(processed_dir,  f'test_plant_{plant_id}.csv'),  index=False)
    print(f"[INFO] Données sauvegardées ✅")

    if label_encoders:
        joblib.dump(label_encoders, os.path.join(MODELS_DIR, f'encoders_plant_{plant_id}.pkl'))
    if scaler:
        joblib.dump(scaler, os.path.join(MODELS_DIR, f'scaler_plant_{plant_id}.pkl'))
    print(f"[INFO] Encoders/Scaler sauvegardés ✅")


# ── 10. Pipeline complet ──────────────────────────────────────────────────────
def preprocess_pipeline(plant_id='1', power_col='DC_POWER', threshold_pct=50):
    print("="*60)
    print("🚀 DÉMARRAGE DU PRÉTRAITEMENT")
    print("="*60)

    data_dict = load_data()
    if plant_id not in data_dict:
        plant_id = list(data_dict.keys())[0]

    df = data_dict[plant_id]
    print(f"\n[INFO] Traitement centrale {plant_id} — {len(df)} lignes")

    if len(df) == 0:
        print("[ERROR] DataFrame vide")
        return None, None, None, None, None, None

    df = handle_missing_values(df)
    df = optimize_memory(df)
    df = add_target_column(df, power_col, threshold_pct)
    df, label_encoders = encode_features(df)

    X, y = split_features_target(df)
    if X is None:
        return None, None, None, None, None, None

    X_train, X_test, y_train, y_test = split_train_test(X, y)
    X_train, X_test, scaler = normalize_features(X_train, X_test)
    save_processed_data(X_train, X_test, y_train, y_test, label_encoders, scaler, plant_id)

    return X_train, X_test, y_train, y_test, label_encoders, scaler


# ── Exécution ─────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    for plant in ['1', '2']:
        print(f"\n{'='*60}\n🏭 TRAITEMENT CENTRALE {plant}\n{'='*60}")
        result = preprocess_pipeline(plant_id=plant, threshold_pct=50)
        if result[0] is not None:
            X_train, X_test = result[0], result[1]
            print(f"✅ Train : {X_train.shape} | Test : {X_test.shape}")

    print("\n" + "="*60)
    print("✅ PRÉTRAITEMENT TERMINÉ !")
    print("="*60)