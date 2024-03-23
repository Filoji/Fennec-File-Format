# Fennec file format - `.fen`

Le format de ficher `.fen` fait partie d'un projet d'étudiant réalisé durant des études à l'INSA de Rouen. Ce format a été conçu par Vespier Michel.

## Header

L'en-tête du fichier va être composé de l'arbre utilisé pour encoder les valeurs.

### Encodage

Chaque nœud d'un arbre peut être de deux types différents : soit une branche, soit une feuille.\
Afin de différencier les branches et les feuilles, on utilise le bit le plus fort.

#### Les feuilles (`0XXXXXXX`)

Afin d'encoder les feuilles, on va utiliser `1 + len(label)` octets.

Le premier octet est composé du bit indicatif d'une feuille - le bit le plus fort - et de sept autres bits représentant la longueur du label.\
Ainsi, un label peut contenir en tout 127 caractères.

Les caractères sont enregistrés en UTF-8.

#### Les branches (`1XXXXXXX`)

Afin d'encoder les branches, on va utiliser `1` octet.

L'octet est composé du bit indicatif d'une branche - le bit le plus fort - et de sept bits qui ne représentent aucunes données.

> Dans une future version du format de fichier, on pourra représenter les branches avec uniquement un seul bit.

### Ordre de sauvegarde

Afin de pouvoir retrouver exactement le même arbre entre l'écriture et la lecture du fichier, il faut garder un ordre de description des données.

#### Les feuilles

Voir [Encodage > Feuille](#les-feuilles-0xxxxxxx).

> Exemple :\
> La représentation d'une feuille ayant pour label `a` est `0x01 0x61`.

#### Les branches

Les branches sont représentés d'abord par leur octet indicatif, puis par la représentation de leur enfant gauche -  représenté par un `0` - puis de leur enfant droit - représenté par un `1` -.

> Exemple:\
> La représentation d'une branche ayant pour enfant deux feuilles `a` et `b` est donc `0x80 0x01 0x61 0x01 0x62`.

#### Le nombre de caractères

Le nombre de caractères écrit en tout dans un fichier est enregistré dans un entier de huit octets.\
En tout, cela veut dire qu'on peut écrire `18446744073709551615` lettres, ce qui est bien plus grand que n'importe quel capacité de données actuelle.

## Body

Le corps du fichier est la représentation du texte origninal écrit grâce à l'algorithme de Huffmann.

> Dans une future version du format de fichier, on pourra utiliser LZ77 afin de pouvoir encore plus compresser les données.
