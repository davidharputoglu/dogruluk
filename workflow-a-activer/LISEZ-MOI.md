# Activation du pipeline de build

Le fichier `build.yml` est prêt. GitHub interdit son ajout automatique sans un token ayant la case "workflow" cochée.

**Activez-le en 3 clics :**
1. Sur https://github.com/davidharputoglu/dogruluk/new/main/.github/workflows → nom du fichier : `build.yml`
2. Ouvrez https://github.com/davidharputoglu/dogruluk/blob/main/workflow-a-activer/build.yml , copiez TOUT le contenu (bouton <> → Raw)
3. Collez dans la fenêtre du point 1 → "Commit changes".

Dès ce commit, une Release v0.1 avec tous les installateurs se construit automatiquement (onglet Actions).
