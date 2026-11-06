# **Arborescence du site:**

projet-deskbud/
├── index.html                  # Squelette sémantique unique
├── assets/
    ├── model 3D desk_bud.glb
    ├── model 3D desk_bud.gltf                 # Icônes, schémas, captures
├── css/
│   ├── style.css               # Fichier d'assemblage (@import)
│   ├── 01-variables.css        # Tokens, palettes de couleurs (Flavours), polices
│   ├── 02-base.css             # Reset CSS, grille globale, fil conducteur
│   ├── 03-components.css       # Boutons, simulateur OLED, ticker, blocs de code
│   ├── 04-sections.css         # Hero, bento grid, coupe CAO sticky, timeline
│   └── 05-responsive.css       # Adaptations tablettes et mobiles (@media)
└── js/
    ├── main.js                 # Chef d'orchestre (point d'entrée)
    └── modules/
        ├── nav.js              # Menu déroulant & sommaire mobile
        ├── flavour-observer.js # Changement de palette au scroll & télémétrie
        ├── scroll-engine.js    # Rendu live CAO (wipe), fil central & parallaxe
        ├── simulator.js        # Gestion des expressions faciales du Desk Bud
        └── ticker.js           # Défilement fluide en pixels/seconde