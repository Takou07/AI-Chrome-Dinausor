import pandas as pd
from sklearn.neural_network import MLPClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score
import joblib
import os

# 1. Chargement des données
# On nomme les colonnes comme dans notre collecteur
columns = ['distance_x', 'obstacle_y', 'game_speed', 'action']
df = pd.read_csv('data/dino_data.csv', names=columns)

# 2. Nettoyage des données (Filtrage)
# L'IA peut être confuse si elle voit 'action=0' pendant que tu sautes déjà.
# On ne garde que les moments où l'obstacle est proche ou quand une action est prise.
df = df[df['distance_x'] < 500] 

# 3. Séparation Features (X) et Cible (y)
X = df[['distance_x', 'obstacle_y', 'game_speed']]
y = df['action']

# split pour vérifier la performance
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2)

# 4. Création du "Cerveau" (Réseau de neurones MLP)
# On utilise 2 couches cachées de 10 neurones chacune
model = MLPClassifier(hidden_layer_sizes=(10, 10), max_iter=1000, activation='relu')

print("Entraînement en cours...")
model.fit(X_train, y_train)

# 5. Validation
predictions = model.predict(X_test)
print(f"Précision du modèle : {accuracy_score(y_test, predictions):.2%}")

# 6. Sauvegarde pour le jeu
if not os.path.exists('models'):
    os.makedirs('models')
joblib.dump(model, 'models/dino_brain.pkl')
print("Modèle sauvegardé dans models/dino_brain.pkl")