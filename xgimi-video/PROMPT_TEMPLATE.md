# Prompt template: horizontal + vertical promo videos

Copy the block below into a new session, fill in the `[brackets]`, and attach the image files.

```
Crée 2 vidéos promotionnelles pour un produit, avec ffmpeg : une horizontale (16:9) et une verticale (9:16).

PRODUIT
- Nom exact : [ex. XGIMI Horizon 20 Max]
- Caractéristiques à utiliser (copiées de la fiche produit, je ne te donne pas le lien car tu ne peux pas l'ouvrir) :
  [colle ici les puces « About this item » telles quelles]
- N'utilise QUE ces faits. N'invente aucun chiffre ni avantage.

VISUELS
- Photo du produit jointe : [fichier PNG/JPG, idéalement fond blanc ou transparent, haute résolution]
- Logo de la chaîne (facultatif) : [fichier]

LIEN D'AFFILIATION
- Lien court à afficher : [ex. geni.us/KOSecnr]
- Mention obligatoire à afficher : [ex. « Affiliate link - no extra cost to you »]

FORMATS
- Horizontale 1920x1080, durée visée : [ex. 29 s]
- Verticale 1080x1920, durée visée : [ex. 19 s]
- Langue du texte à l'écran : [anglais / français]

CONTENU
- Accroche du premier plan : [ex. « TV KILLER? »]
- Messages à mettre en avant, dans l'ordre : [ex. luminosité, contraste, jeu, Google TV, optique]
- Appel à l'action final : [ex. « WORTH IT? Link in description, like & subscribe »]

STYLE
- Ambiance : [nerveuse / sobre / luxe]
- Couleurs d'accent ou charte : [ou « au choix »]

MUSIQUE
- [Musique synthétique générée / mon fichier audio joint : fichier + licence]
- Pas de voix off, sauf fichier audio fourni.

LIVRAISON
- Envoie-moi les vidéos dans la conversation.
- Pousse-les dans le dépôt [Raclegit/nom-du-depot], dossier [xgimi-video/], sur la branche désignée, puis ouvre une pull request.
- Mon dépôt est [public / privé].

CONFIDENTIALITÉ
- Traite mes fichiers localement et ne les envoie nulle part ailleurs.
- Ne commite pas mes fichiers bruts (captures d'écran) : seulement ce que la vidéo utilise.

CONTRÔLES
- Vérifie le rendu sur des images extraites de chaque scène avant de livrer.
- Dis-moi clairement ce que tu n'as pas pu faire.
```

## Required inputs (valid for any video request)

| Input | Why |
|---|---|
| Product features pasted as text | Marketplace and short links (Amazon, geni.us) can return 403, so there is no reliable source otherwise. |
| Product photo | Without it the video is animated text only. A white background allows a clean cut-out. |
| Short link and affiliate notice | A link burned into the image is not clickable; it must also go in the description and pinned comment. |
| Formats and durations | Horizontal and vertical need different layouts. |
| On-screen language | Avoids translating afterwards. |
| Key messages and call to action | Otherwise they are chosen for you. |
| Music: file + license, or synthetic | Commercial music can get a YouTube claim or block. |
| Destination and GitHub access | Repository, branch, public or private. The Claude GitHub App must be installed on the repository before the session, or the push fails. |

## What the prompt cannot replace
- **Voice-over:** there is no text-to-speech available. Provide an audio file.
- **Real footage of the product in use** (unboxing, setup, picture tests): it has to be filmed. Editing can follow.
- **Personal opinions** (days of testing, price, verdict): left as blanks to fill in, never invented.

If the repository is public, anyone with the links can see the videos. Use a private repository if the product or project must stay confidential.

## Existing scripts
- `build.py`: horizontal teaser (1920x1080)
- `build_short.py`: vertical Short (1080x1920)
- `product.png`: cut-out product shot used by both
