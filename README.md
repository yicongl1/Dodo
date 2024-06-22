# Projet *Gopher and Dodo* : sujet v1.3

## Commande
Afin de faire marcher le jeu, on ajoute "from jeux import Environment, strategy, initialize, final" à test_client.py.
Pour lancer, la commande à utiliser dans le terminal est: python .\test_client.py 33 yicongli_michaelfernandez g33
Il faut avoir test_client.py, jeux.py, gndclient.py dans un même répertoire
La plupart des fonctions codées sont situés dans le fichier jeux.py

## Structure du code
Pour les fonction, on utilise la même structure qu'on a appris pour le tictactoe dans les TP, il y a un légal pour donner les movements possibles (en fonction du jeu passé en argument), une évaluation pour le choix des actions(encore une fois en fonction du jeu).Nous avons aussi fait 2 versions, une mix-max au début puis une alpha beta par la suite, mais nous nous somme rendu compte que notre minmax (avec memoization), obtenait de meilleurs résultats de manière générale donc c'est ce programme que nous avons choisi pour le tournois.

Pour l'axe hexagonal, son initialisation est faite aussi grâce à plusieurs fonctions dépendants du jeu.(nous avons assez bien commenté le code pour que celui-ci soit assez compréhensible)En ce qui concerne la fonction final, elle est assez simple et renvoie le joueur gagant.

## Les + et - du projet
Nous avons réussi à faire fonctionner notre code sur les deux jeux avec cette IA minmax avec winrate contre random d'environ 90-95% et un depth de 3(bon compromis temps/résultat).
Ce qui a été le plus dur dans notre projet a été l'implémentation de la fonction legals puisque nous avons été bloqué pendant plusieurs jours sur ce type de problème mais nous avons réussi à le régler quelques jours avant le tournois.

De manière générale notre code est bien structuré et fonctionne mais n'est pas parfait et pourrait encore être améliorer comme notamment en améliorant l'évaluation en rajoutant des conditions qui facilite la bonne prise de décision.


