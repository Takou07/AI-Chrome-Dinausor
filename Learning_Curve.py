import matplotlib.pyplot as plt
import numpy as np

# Données basées sur tes résultats
labels = ['Précision Globale', 'F1-Score (Saut)', 'F1-Score (Baisse)']
model_66 = [66, 63, 54] # Ancien modèle
model_87 = [87, 86, 92] # Nouveau modèle (après équilibrage)

x = np.arange(len(labels))
width = 0.35

fig, ax = plt.subplots(figsize=(10, 6))
rects1 = ax.bar(x - width/2, model_66, width, label='Modèle Initial (Déséquilibré)', color='#ff9999')
rects2 = ax.bar(x + width/2, model_87, width, label='Modèle Optimisé (Équilibré)', color='#66b3ff')

# Mise en forme
ax.set_ylabel('Score (%)')
ax.set_title('Impact de l\'équilibrage des données sur les performances de l\'IA')
ax.set_xticks(x)
ax.set_xticklabels(labels)
ax.legend()
ax.set_ylim(0, 100)

# Ajout des valeurs au-dessus des barres
def autolabel(rects):
    for rect in rects:
        height = rect.get_height()
        ax.annotate(f'{height}%',
                    xy=(rect.get_x() + rect.get_width() / 2, height),
                    xytext=(0, 3),
                    textcoords="offset points",
                    ha='center', va='bottom')

autolabel(rects1)
autolabel(rects2)

plt.tight_layout()
plt.savefig('performance_comparison.png')
plt.show()