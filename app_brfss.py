from pathlib import Path
from time import perf_counter
import os

import dask.dataframe as dd
import pandas as pd
import pyarrow.parquet as pq
import streamlit as st


ROOT = Path(__file__).resolve().parent
N_WORKERS = min(4, os.cpu_count() or 1)
TAILLES = {10: "10 %", 25: "25 %", 50: "50 %", 100: "100 %", 200: "×2", 300: "×3"}
OPERATIONS = {
    "Filtrer selon l'IMC": "filtrage",
    "IMC moyen par tranche d'âge": "groupby",
}
COLONNES = {
    "filtrage": ["id_ligne", "imc"],
    "groupby": ["age_classe", "imc"],
}
AGES = dict(enumerate([
    "18-24 ans", "25-29 ans", "30-34 ans", "35-39 ans", "40-44 ans",
    "45-49 ans", "50-54 ans", "55-59 ans", "60-64 ans", "65-69 ans",
    "70-74 ans", "75-79 ans", "80 ans et plus",
], start=1))


def operation(table, nom, seuil):
    """Mêmes calculs et exclusions que dans le notebook de la partie I."""
    if nom == "filtrage":
        return table.loc[table["imc"] >= seuil, ["id_ligne", "imc"]]
    return (
        table.dropna(subset=["age_classe"])
        .groupby("age_classe")["imc"]
        .agg(["count", "mean"])
    )


def executer(chemin, moteur, nom, seuil):
    debut = perf_counter()
    if moteur == "Pandas":
        table = pd.read_parquet(chemin, columns=COLONNES[nom], engine="pyarrow")
        resultat = operation(table, nom, seuil)
    else:
        table = dd.read_parquet(
            chemin, columns=COLONNES[nom], engine="pyarrow", split_row_groups=True
        )
        resultat = operation(table, nom, seuil).compute(
            scheduler="threads", num_workers=N_WORKERS
        )
    return resultat, perf_counter() - debut


def verifier(pandas_resultat, dask_resultat, nom):
    if nom == "filtrage":
        gauche = pandas_resultat.sort_values("id_ligne").reset_index(drop=True)
        droite = dask_resultat.sort_values("id_ligne").reset_index(drop=True)
        pd.testing.assert_frame_equal(gauche, droite, check_dtype=False, check_exact=True)
    else:
        gauche, droite = pandas_resultat.sort_index(), dask_resultat.sort_index()
        pd.testing.assert_series_equal(
            gauche["count"], droite["count"], check_dtype=False, check_exact=True
        )
        pd.testing.assert_series_equal(
            gauche["mean"], droite["mean"], check_dtype=False,
            check_exact=False, rtol=1e-10, atol=1e-10
        )


def main():
    st.set_page_config(page_title="BRFSS — Exploration", layout="wide")
    st.title("BRFSS 2024 — Exploration des données")
    st.caption("Calculs non pondérés sur les réponses du fichier.")

    dossiers = sorted([
        dossier for dossier in (ROOT / "data" / "processed").glob("benchmark_*")
        if dossier.is_dir() and any(
            (dossier / f"brfss_{taille}pct.parquet").is_file() for taille in TAILLES
        )
    ], reverse=True)
    if not dossiers:
        st.info(
            "Aucun jeu disponible. Place cette application à la racine de projet_brfss "
            "et exécute le notebook 02_benchmark_brfss.ipynb avec "
            "FACTEURS = [0.10, 0.25, 0.50, 1.0, 2.0, 3.0]."
        )
        st.stop()

    dossier = dossiers[0]
    if len(dossiers) > 1:
        dossier = st.selectbox(
            "Données préparées lors du benchmark", dossiers, format_func=lambda p: p.name
        )

    disponibles = [t for t in TAILLES if (dossier / f"brfss_{t}pct.parquet").is_file()]
    taille = st.selectbox("Taille des données", disponibles, format_func=TAILLES.get)
    if len(disponibles) < len(TAILLES):
        st.caption("Seules les tailles générées dans ce dossier sont disponibles.")
    chemin = dossier / f"brfss_{taille}pct.parquet"
    libelle = st.selectbox("Opération", list(OPERATIONS))
    nom = OPERATIONS[libelle]
    seuil = 30.0
    if nom == "filtrage":
        seuil = st.number_input("IMC minimum inclus", min_value=12.0, max_value=100.0,
                                value=30.0, step=0.5)
    moteurs = st.multiselect("Technologies", ["Pandas", "Dask"], default=["Pandas", "Dask"])
    st.caption(
        "Temps affiché : une exécution, lecture Parquet + calcul. "
        "L'affichage est exclu ; le cache du système peut influencer les temps."
    )
    if not st.button("Exécuter", disabled=not moteurs):
        return

    try:
        fichier = pq.ParquetFile(chemin)
        if not set(COLONNES[nom]).issubset(fichier.schema_arrow.names):
            st.error("Colonnes manquantes : régénère les fichiers avec le notebook de la partie 1.")
            return
        st.write(f"Nombre de lignes du jeu : {fichier.metadata.num_rows:,}")
        if taille > 100:
            st.caption("Volume augmenté par duplication : aucune nouvelle personne ajoutée.")
        with st.spinner("Calcul en cours…"):
            resultats = {moteur: executer(chemin, moteur, nom, seuil) for moteur in moteurs}
        if len(resultats) == 2:
            verifier(resultats["Pandas"][0], resultats["Dask"][0], nom)
            st.success("Résultats Pandas et Dask cohérents.")
    except AssertionError:
        st.error("Les résultats Pandas et Dask divergent. Vérifie les données et les versions installées.")
        return
    except Exception as erreur:
        st.error(f"Impossible d'exécuter le calcul : {erreur}")
        return

    for colonne, moteur in zip(st.columns(len(moteurs)), moteurs):
        resultat, secondes = resultats[moteur]
        with colonne:
            st.subheader(moteur)
            st.metric("Temps d'exécution", f"{secondes:.4f} s")
            if nom == "filtrage":
                st.write(f"Lignes retenues : {len(resultat):,}")
                st.dataframe(resultat.head(100).rename(columns={"id_ligne": "Ligne", "imc": "IMC"}),
                             hide_index=True)
                st.caption("Aperçu limité à 100 lignes ; le calcul porte sur tout le jeu.")
            else:
                tableau = resultat.sort_index().reset_index()
                tableau["age_classe"] = tableau["age_classe"].map(AGES)
                st.dataframe(tableau.rename(columns={
                    "age_classe": "Tranche d'âge", "count": "IMC valides", "mean": "IMC moyen"
                }), hide_index=True)


if __name__ == "__main__":
    main()
