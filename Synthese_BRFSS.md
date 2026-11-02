# Synthèse du projet BRFSS 2024

## 1. Méthodologie et environnement de test

L’objectif est de comparer les performances de **Pandas et Dask** sur les données de santé BRFSS 2024.

Le fichier contient **457 670 lignes et 301 colonnes**. Trois variables sont utilisées : l’IMC, la tranche d’âge et la santé générale. Les données sont nettoyées puis enregistrées au format **Parquet**.

Trois opérations sont comparées :

- Filtrer les personnes ayant un IMC supérieur ou égal à 30.
- Calculer l’IMC moyen et le nombre d’IMC valides par tranche d’âge.
- Compter les réponses pour chaque catégorie de santé générale.

Les tests portent sur **10 %, 25 %, 50 % et 100 %** des données, puis sur des jeux **×2 et ×3** obtenus par duplication. Le mélange des données utilise une graine fixe de 42 pour retrouver les mêmes échantillons.

Après une première exécution de préparation, chaque test est répété **cinq fois**. Le temps retenu est la médiane, c’est-à-dire la valeur centrale des cinq mesures. Il comprend la lecture du fichier et le calcul, y compris `.compute()` pour Dask. La préparation des données et l’affichage sont exclus.

Environnement utilisé :

- Windows 11 et Python 3.13.14.
- Processeur Intel avec 16 processeurs logiques ; Dask configuré avec 4 workers.
- Pandas 3.0.2, Dask 2026.8.0 et PyArrow 24.0.0.
- NumPy 2.4.3 et Matplotlib 3.10.8.

## 2. Principaux résultats du benchmark

Les tests produisent **180 mesures**. Les **18 vérifications** entre Pandas et Dask ont réussi : les deux technologies donnent des résultats cohérents.

**Pandas est plus rapide pour les trois opérations, à toutes les tailles testées.** Voici les temps médians pour le jeu complet et le jeu triplé :

| Taille | Opération | Pandas | Dask |
|---|---|---:|---:|
| 100 % | Filtrage | 13,41 ms | 38,84 ms |
| 100 % | IMC par tranche d’âge | 19,93 ms | 56,07 ms |
| 100 % | Comptage des réponses | 11,41 ms | 50,75 ms |
| ×3 | Filtrage | 30,46 ms | 82,59 ms |
| ×3 | IMC par tranche d’âge | 52,84 ms | 116,71 ms |
| ×3 | Comptage des réponses | 22,75 ms | 123,15 ms |

Sur l’ensemble des tests, Pandas est environ **2,2 à 8,3 fois plus rapide** que Dask.

## 3. Analyse et interprétation des résultats

Les temps augmentent globalement avec le nombre de lignes. Cependant, même avec **1 373 010 lignes**, Pandas reste plus rapide.

Cela peut s’expliquer par la simplicité des calculs et le faible nombre de colonnes utilisées. Dask doit organiser le travail en plusieurs tâches, ce qui ajoute un coût. Sur ces données, le travail à répartir semble trop léger pour compenser ce coût.

Les variations entre répétitions ne changent pas le classement : dans chaque cas testé, même le temps le plus élevé de Pandas reste inférieur au temps le plus faible de Dask.

Ces conclusions concernent uniquement cette configuration. Le cache du système peut influencer les temps, et les données dupliquées n’ajoutent pas de nouvelles personnes. La quantité de RAM et le type de disque n’ont pas été enregistrés.

## 4. Recommandations sur les technologies à retenir

**Pandas avec Parquet est le choix recommandé pour ce projet**, car il est le plus rapide dans tous les tests réalisés.

Dask reste présent dans le dashboard pour permettre la comparaison demandée. Il faudrait refaire des tests avant de le retenir pour des données plus volumineuses ou des calculs plus complexes.

Pour comparer les performances, il faut privilégier les résultats répétés du benchmark : les temps du dashboard correspondent à une seule exécution par clic.

*Les résultats utilisés pour cette synthèse sont ceux actuellement présents dans le projet avec pour nom : `20261004_171009_221598`. Les notebooks peuvent bien entendu être relancés pour avoir de nouveaux résultats*
