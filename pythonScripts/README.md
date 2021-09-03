# Fonctionnement de l'algorithme de dédoublonnage

Dans ce qui suit, nous décrirons le fonctionnement de l'algorithme de dédoublonnage.

### 1 - Choix des champs utiles
L'algorithme reçoit en entrée un couple de notices à valider automatiquement. Une extraction des champs est faite par la suite de chacune des notices. Ces champs sont par la suite regroupé en catégories. Ce sont entre autre :

| groupe | champs utilisé |
| :---: | :---: |
| identifiant | doi, pmId, nnt |
| pagination | pageRange |
| volumaison | issue, volume |
| publication | issn, issn, eissn, title.meeting, title.journal, isbn, eisbn, teiBlob |
| titre |title.default, title.en, title.fr |

Avant la comparaison, chaque champ est traité en fonction de son type.
Remarque : On ajoutera aussi le champ idConditor.

### 2 - Comparaison des champs dans chaque groupe

#### 2.1 La comparaison des champs
La comparaison entre les champs se fait selon 2 cas :

- Les champs sont tous deux renseignés :
    Si les champs sont tous les deux renseignées et son identiques, alors on renvoie 1 sinon -1
- Au moins un des champs n'est pas renseignés:
    on renvoie 0

Ainsi, on se retrouve pour chaque comparaison avec un entier entre 0, 1 et -1.

#### 2.2 La comparaison dans un groupe
Dans chaque groupe, les comparaisons se font selon une certaine hiérarchie. L'idée est de
commencer la comparaison avec les champs les plus pertinents vers les ceux qui le sont moins.
On passe au champ suivant lorsque on a une donnée manquante dans l'un des champ en cours.
Le pseudocode est donné ci dessous :

> **si** valeurChampNotice1 **identique** valeurChampNotice2 **alors**:

>&nbsp;&nbsp;&nbsp;&nbsp;**retourne** 1

> **sinon si** valeurChampNotice1 **différent** valeurChampNotice2 **alors**:

>&nbsp;&nbsp;&nbsp;&nbsp;**retourne** -1

>**sinon**

>&nbsp;&nbsp;&nbsp;&nbsp;passe au champ suivant

Si au dernier champ, on a toujours, la valeur d'un des champ est manquant, alors on retourne 0.

Ainsi, pour chaque groupe, on a un resultat qui peut être soit 0, soit 1 ou soit -1

Au final, on se retrouve avec un quintuple de valeur compris entre -1, 0 et 1

### 3 - La règle de décision
Une règle de décision disponible via cette adresse http://vxgit.intra.inist.fr:60000/dago/co-duplicates/blob/master/deduplicate/config.py
a été éléboré. Elle valide ou pas le couple de notices suivant le quintuple cité plus haut. La règle de décision
est un objet dans lequel les clés sont toutes les combinaisons possibles  de quintuple de -1, 0 et 1 et en valeur la décision prise par les
experts metiers pour chaque quintuple.

### 5 - La décision finale
Selon la règle de décision, il en ressort soit 1 correspondant à doublon, -1 non doublon et 0 à incertain.
