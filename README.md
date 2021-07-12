# co-duplicates

## Présentation
Le module **co-duplicates** est un module qui supprimer des doublons.

## Fonctionnement
TODO

## Utilisation

### Installation
Installer les modules nécessaires :
```
npm install
```

### Vérification du fonctionnement
Commande d'exécution des tests unitaires :
```
npm test
```

### Exécution
Comme pour tous les modules, la présente partie métier n'est pas destinée à être exécutée directement, puisqu'elle consiste uniquement à mettre à disposition une fonction `doTheJob`.

L'exécution se fera donc en appelant cette fonction depuis une instanciation de `li-canvas` ou indirectement depuis les tests unitaires.

## Annexes

### Arborescence
```
.
├── node_modules/                        // Modules NPM
│   └── ...
├── test/                                // Fichiers nécessaires aux tests unitaires
│   ├── dataset/
│   │   └── in/
│   │       └── data.js                  // Fichier contenant les données
│   └── run.js                           // Point d'entrée des tests unitaires
├── .editorconfig                        // Configuration de l'éditeur pour l'indentation (entre autre)
├── .eslintrc.json                       // Configuration pour eslint
├── .gitignore
├── error.js                             // Module JS pour traiter les erreurs
├── index.js                             // Point d'entrée, contenant la fonction doTheJob()
├── Licence.fr.txt                       // Licence CeCILL en Français
├── License.en.txt                       // Licence CeCILL en Anglais
├── package-lock.json
├── package.json                         // Description du module pour NPM
└── README.md
```
