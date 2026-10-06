# Pack Kling – Teaser TikTok 20 s (9:16)

Kling génère des clips courts (en général 5 s ou 10 s) et dispose d'un champ « negative prompt » séparé. On travaille donc en **5 clips** assemblés dans CapCut. Les noms de boutons et les limites (durée, crédits, filigrane, résolution) changent souvent : vérifiez-les dans l'interface avant de lancer.

## Réglages dans Kling
- Mode : **Text to Video** (ou Image to Video, voir astuce plus bas)
- Format : **9:16**
- Durée : **5 s** pour chaque plan (10 s possible mais coûte plus de crédits ; inutile ici)
- Mode qualité : « Standard » pour tester, « Professional » pour la version finale si vos crédits le permettent
- Le palier gratuit ajoute en général un filigrane et limite la résolution. Si 1080x1920 n'est pas proposé, générez au maximum disponible et laissez CapCut mettre à l'échelle.

## Negative prompt (à coller dans le champ dédié pour CHAQUE plan)
```
face, faces, people, text, letters, logo, brand name, watermark, price, numbers, subtitles, distorted hands, extra fingers, deformed fingers, flicker, fast motion, shaky camera, blur, low quality
```

## Préfixe de style (à coller devant chaque prompt)
```
Vertical 9:16 faceless tabletop commercial, bright clean look, warm soft window light, wooden table, deep navy background with warm amber accents. Only hands visible. Smooth slow camera movement, stable lighting. Subject centered with empty space above and below. Plain unbranded objects.
```

## Prompts par plan

| # | Durée de génération | Durée à garder au montage |
|---|---|---|
| 1 | 5 s | ~2 s |
| 2 | 5 s | 5 s |
| 3 | 5 s | 5 s |
| 4 | 5 s | 4 s |
| 5 | 5 s | 4 s |

**Plan 1 – Hook**
```
A hand slides a small closed gift box across the wooden table into frame, slight slow push-in.
```

**Plan 2 – Casque**
```
Dark blue over-ear wireless headphones resting on the wooden table. A hand lifts them slowly and rotates them, soft light glints on the ear cups.
```

**Plan 3 – Voiture en briques**
```
Close-up, shallow depth of field. Two hands snap together a half-built orange building-brick sports-car model, loose bricks scattered around it.
```

**Plan 4 – Jeu de société**
```
A family guessing board game on the table. An adult hand and a smaller hand flip small cartoon-animal character cards upright, cheerful playful pace.
```

**Plan 5 – Final**
```
Calm static shot of dark blue headphones, an orange brick sports-car model and a board game arranged on the wooden table. The camera slowly pulls back, clean empty area in the lower middle of the frame.
```

Pour chaque plan : préfixe + prompt dans le champ principal, negative prompt dans le champ dédié.

## Astuces spécifiques à Kling
- **Cohérence visuelle entre les plans** : générez d'abord une image fixe de la table (Kling ou autre outil d'image gratuit), puis utilisez-la comme première image en **Image to Video** pour les plans 2, 3 et 5. Cela garde les mêmes couleurs, la même table et la même lumière.
- **Plan 5** : si Kling propose « image de début / image de fin », utilisez une image large de l'arrangement en image de fin pour obtenir un recul de caméra net.
- **Mouvement de caméra** : si l'interface offre des réglages de caméra, choisissez « zoom in » doux pour le plan 1 et « zoom out » doux pour le plan 5. Sinon, le prompt suffit.
- **Mains déformées** : générez 2 à 3 variantes de chaque plan et gardez la meilleure. Réduisez le geste (« hand lifts slowly » plutôt qu'une action complexe).
- **Plan 4** : si l'enfant ou la famille est mal rendu, mettez « a smaller hand » ou ne montrez qu'une seule main sur les cartes.
- **Crédits** : testez en qualité Standard, puis refaites uniquement les plans retenus en qualité supérieure. Les crédits gratuits se renouvellent chaque jour : vous pouvez répartir les 5 plans sur 2 jours.

## Montage (CapCut gratuit)
1. Importer les 5 clips dans l'ordre, couper aux durées de la colonne « à garder ».
2. Projet en 9:16, 1080x1920, 30 fps.
3. Ajouter une musique instrumentale légère libre de droits (bibliothèque CapCut ou TikTok).
4. Ajouter dans les zones laissées vides (haut 15 %, bas 20 %) : texte, mention Prime Big Deal, prix, logo, selon les règles du programme d'affiliation Amazon et de TikTok.
5. Si un filigrane Kling apparaît : n'essayez pas de le masquer. Utilisez une offre sans filigrane si vous publiez à but commercial.
6. Exporter en 1080x1920, 30 fps, H.264.
