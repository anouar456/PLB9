# 🐙 Publier DURASIA sur GitHub (+ hébergement gratuit)

Guide pas-à-pas pour mettre le projet en ligne et héberger l'application
gratuitement avec **GitHub Pages**.

---

## A. Préparer Git (une seule fois)

1. Installer Git : <https://git-scm.com/downloads>
2. Configurer votre identité :

```bash
git config --global user.name "Votre Nom"
git config --global user.email "votre@email.com"
```

---

## B. Créer le dépôt sur GitHub

1. Connectez-vous sur <https://github.com> → bouton **New** (nouveau dépôt).
2. **Repository name** : `durasia`
3. Description : *Supervision photovoltaïque intelligente — projet DURASIA*.
4. Laissez en **Public** (nécessaire pour GitHub Pages gratuit).
5. **Ne cochez rien** (pas de README/licence : on les a déjà).
6. Cliquez **Create repository**.

---

## C. Envoyer le projet (depuis le dossier `durasia/`)

```bash
cd durasia                 # le dossier qui contient index.html

git init
git add .
git commit -m "Initial commit — DURASIA app + acquisition + IA"
git branch -M main
git remote add origin https://github.com/<VOTRE-PSEUDO>/durasia.git
git push -u origin main
```

> Remplacez `<VOTRE-PSEUDO>` par votre identifiant GitHub.
> GitHub peut demander un **token** au lieu du mot de passe :
> Settings → Developer settings → *Personal access tokens* → générez-en un et
> utilisez-le comme mot de passe.

---

## D. Héberger l'application avec GitHub Pages

1. Sur la page du dépôt : **Settings → Pages**.
2. **Source** : `Deploy from a branch`.
3. **Branch** : `main` · dossier `/ (root)` → **Save**.
4. Patientez ~1 minute. L'URL apparaît :
   `https://<VOTRE-PSEUDO>.github.io/durasia/`

✅ Votre application est en ligne, accessible à tout jury depuis un simple lien.

> Le **mode Démo** fonctionne parfaitement en ligne (données embarquées).
> Le **mode Live** nécessite que le Raspberry Pi soit accessible depuis le
> réseau du navigateur (même réseau local, ou tunnel type `ngrok` pour une
> démo à distance). En HTTPS (Pages), pointez l'API vers une URL HTTPS pour
> éviter le blocage *mixed content*.

---

## E. Mettre à jour le projet plus tard

```bash
git add .
git commit -m "Description des changements"
git push
```

GitHub Pages se met à jour automatiquement après chaque `push`.

---

## F. Bonnes pratiques pour un rendu de concours

- ✅ Soignez le **README** (captures d'écran, schéma, résultats du modèle).
- ✅ Ajoutez des **Releases** (versions taguées) pour marquer les jalons.
- ✅ Utilisez les **Issues** / un tableau **Projects** pour montrer la gestion.
- ✅ Vérifiez que `raspberry/data/` (mesures runtime) est bien ignoré
  (`.gitignore`) pour garder le dépôt propre.
- ✅ Ajoutez une courte **vidéo de démo** (lien) en haut du README.

> Astuce captures d'écran : placez vos images dans `docs/img/` et référencez-les
> dans le README avec `![légende](docs/img/fichier.png)`.
