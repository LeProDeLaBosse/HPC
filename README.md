# Projet BRFSS 2024

Comparaison de Pandas et Dask sur des données de santé, puis exploration dans un dashboard Streamlit.

Le benchmark compare trois opérations sur six tailles : filtrage selon l’IMC, agrégation par classe d’âge et distribution des réponses de santé générale. Le dashboard reprend le filtrage et l’agrégation, permet de choisir la taille et les technologies, puis affiche les résultats et les temps.

## 1. Dépendances

Le projet a été exécuté sous Windows 11 avec **Python 3.13.14**. Il est possible d’utiliser son environnement Python habituel ; aucun environnement virtuel particulier n’est imposé.

| Bibliothèque | Utilisation | Version du benchmark |
|---|---|---|
| Pandas | Lecture et traitement des données | 3.0.2 |
| Dask | Traitement des données à comparer avec Pandas | 2026.8.0 |
| PyArrow | Lecture et écriture des fichiers Parquet | 24.0.0 |
| NumPy | Manipulation des données numériques | 2.4.3 |
| Matplotlib | Courbes du benchmark | 3.10.8 |
| Streamlit | Dashboard | Non enregistrée |
| IPykernel | Exécution des notebooks | Non enregistrée |

Si nécessaire, installer les dépendances avec les versions principales utilisées :

```powershell
python -m pip install "pandas==3.0.2" "dask[dataframe]==2026.8.0" "pyarrow==24.0.0" "numpy==2.4.3" "matplotlib==3.10.8" streamlit ipykernel
```

## 2. Organisation du projet

| Chemin depuis la racine | Rôle |
|---|---|
| `01_preparation.ipynb` | Lecture XPT, exploration et conversion en Parquet brut. |
| `02_benchmark_brfss.ipynb` | Nettoyage des variables, construction des tailles, benchmark et courbes. |
| `app_brfss.py` | Dashboard Streamlit. |
| `data/raw/LLCP2024.XPT` | Données originales décompressées. |
| `data/processed/brfss_2024_brut.parquet` | Fichier complet produit par le premier notebook. |
| `data/processed/benchmark_<date>/` | Six jeux Parquet préparés par le second notebook. |
| `results/benchmark_<date>/` | Mesures et exports d’une exécution. |
| `Synthese_BRFSS.md` | Interprétation des résultats transmis. |
| `README.md` | Instructions d’exécution et de reproductibilité. |

Les fichiers XPT et Parquet sont nécessaires pour exécuter les traitements. Les CSV de résultats et les sorties enregistrées des notebooks ne les remplacent pas.

## 3. Exécuter la préparation

Ouvrir `01_preparation.ipynb` et exécuter toutes les cellules dans l’ordre.

La première cellule affiche le dossier de travail. Il doit correspondre à la racine `projet`, car les notebooks construisent leurs chemins avec `Path.cwd()`.

Résultat attendu :

```text
data/processed/brfss_2024_brut.parquet
```

Le notebook lit le XPT, affiche les dimensions et types, explore les valeurs manquantes et écrit le fichier complet avec la compression Snappy. Le nettoyage spécifique aux trois variables du benchmark est réalisé dans le second notebook.

Ouvrir `02_benchmark_brfss.ipynb` et exécuter toutes les cellules. Cette étape génère les jeux Parquet utilisés par le dashboard et les fichiers de résultats.

### Fichiers produits et contrôles attendus

| Fichier | Contenu |
|---|---|
| `mesures_brutes.csv` | 180 lignes de mesures : 6 tailles × 3 opérations × 2 moteurs × 5 répétitions. Temps en secondes. |
| `resume.csv` | 36 lignes : médiane, minimum, maximum et quartiles par taille, opération et moteur. |
| `comparaison.csv` | 18 lignes : médianes et ratio Pandas/Dask. Ratio inférieur à 1 = Pandas plus rapide. |
| `validation.csv` | 18 lignes avec `coherence=True` si tous les contrôles initiaux ont réussi. Chaque répétition est aussi vérifiée par le code. |
| `jeux.csv` | Taille, nombre de lignes, nombre de groupes et chemin des jeux préparés. |
| `environnement.json` | Système, Python, versions principales, paramètres et informations sur la source. |
| `courbes_temps.png` | Temps médians selon la taille, avec bandes entre les quartiles 25 % et 75 %. |

La synthèse jointe décrit l’exécution **`20261004_171009_221598`**. Une nouvelle exécution produit un autre dossier. L’interprétation de l’exécution transmise figure dans `Synthese_BRFSS.md`.

## 4. Lancer le dashboard

Conserver les jeux Parquet générés dans `data/processed/benchmark_<date>/`, puis exécuter depuis la racine du projet :

```powershell
python -m streamlit run app_brfss.py
```

Ouvrir l’adresse `Local URL` indiquée dans le terminal, généralement [http://localhost:8501](http://localhost:8501). Laisser le terminal ouvert ; `Ctrl+C` arrête le serveur.

Dans la page principale :

1. Choisir le dossier de données si plusieurs exécutions existent.
2. Choisir la taille et l’opération.
3. Régler l’IMC minimum pour le filtrage.
4. Sélectionner Pandas, Dask ou les deux.
5. Cliquer sur **Exécuter**.

La comparaison porte sur le même jeu de données. Le filtrage affiche un aperçu limité à 100 lignes, mais le calcul porte sur tout le jeu choisi. Les temps du dashboard correspondent à **une exécution par clic**, sans le protocole de chauffe et de répétitions du notebook : ils ne remplacent pas les médianes du benchmark.
