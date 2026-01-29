import pandas as pd
import numpy as np
from sklearn.neural_network import MLPClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report, accuracy_score
from sklearn.utils import resample # Pour équilibrer les classes
import joblib
import os

# 1. Chargement des données
columns = ['dist_x', 'obs_y', 'game_speed', 'action']
df = pd.read_csv('data/dino_data.csv', names=columns)

# 2. Équilibrage automatique des données (Oversampling)
# On sépare les classes pour les rééquilibrer
df_run = df[df.action == 0]
df_jump = df[df.action == 1]
df_duck = df[df.action == 2]

# On augmente la taille des classes minoritaires (Jump et Duck) 
# pour qu'elles aient autant de poids que la classe majoritaire (Run)
n_samples = len(df_run)

df_jump_upsampled = resample(df_jump, replace=True, n_samples=n_samples, random_state=42)
df_duck_upsampled = resample(df_duck, replace=True, n_samples=n_samples, random_state=42)

# Fusion du nouveau dataset équilibré
df_balanced = pd.concat([df_run, df_jump_upsampled, df_duck_upsampled])

# 3. Préparation des Features/Target
X = df_balanced[['dist_x', 'obs_y', 'game_speed']]
y = df_balanced['action']

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# 4. Modèle plus puissant (réseau plus large)
# On augmente la taille des couches pour mieux capturer les patterns
clf = MLPClassifier(hidden_layer_sizes=(128, 64, 32), 
                    max_iter=2000, 
                    activation='relu', 
                    solver='adam', 
                    alpha=0.0001, # Régularisation pour éviter le sur-apprentissage
                    random_state=42,
                    verbose=True)

print(f"Entraînement sur {len(df_balanced)} lignes (données équilibrées)...")
clf.fit(X_train, y_train)

# 5. Évaluation
y_pred = clf.predict(X_test)
print(f"\nNouvelle précision globale : {accuracy_score(y_test, y_pred):.2%}")
print("\nTableau de performance détaillé :")
print(classification_report(y_test, y_pred))

# 6. Sauvegarde
if not os.path.exists('models'):
    os.makedirs('models')
joblib.dump(clf, 'models/dino_brain.pkl')
print("\nModèle optimisé sauvegardé dans 'models/dino_brain.pkl'")