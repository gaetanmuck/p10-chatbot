**Objet du document:**

Description de l'architecture du model utilisé dans le *chat bot* de FlyMe: surveillance des performances,explicitation des critères d'évaluation, des seuils d'alertes et des modalités de mise à jour.


# 1. Le modèle initial

Initialement, le modèle est entrainé *offline* avec des données que nous avons à disposition des base de données publique. C'est ce modèle que nous avons utilisé lors de notre *MVP* et qui est en ligne aujourd'hui. 

# 2. La base de donnée

Pour la suite du projet, nous pouvons penser à une base de donnée Postgres pour le stockage des données, remplie par la base de donnée mentionnée ci-avant (après avoir été mise en forme grâce aux scripts déjà développé pour le *MVP*) et alimentée tous les jours par l'utilisation du chat bot. 

En effet, de la même manière que nous avons réalisé l'enregistrement de l'historique des conversations dans le *MVP*, nous pouvons penser utiliser le server web pour insérer au bon format les nouveaux messages correctement interprété par le *bot* afin d'agrandir la base de donnée d'entrainement. 

En ce qui concerne les messages mal interprétés, ceux-ci pourront être analysés manuellement afin de comprendre ce qui s'est mal passé (le bot a t-il mal compris, ou le message n'était pas clair ?) dans ces messages et éventuellement insérer, manuellement pour le moment (par une API mise à disposition par exemple), les bons messages avec les bonnes choses à y interpréter.

**Pourquoi Postgres ?**

Il s'agit d'une technologie aboutie, avec une communauté présente et développée et qui nous laisse la possibilité si besoin dans le future d'utiliser la technologie *PL/Python*, qui permet d'utiliser du code python à l'intérieure de function *pgsql*. De plus, il s'agit de la technologie dont l'équipe de FlyMe bot a le plus d'expérence


# 3. Surveillances des performances

Pour ceci, nous avons mis en place dans le *MVP* une application Azure *Insights* alimentée par le serveur Web (lors des messages des utilisateurs) qui permet de surveiller le nombre de discussion, le nombre de discussion étant aller jusqu'au bout (la demande à entièrement été comprise par le *bot*), le nombre de messages, le nombre de message correctement interprétés. Ces paramètres que nous surveillons nous permettent d'avoir à la void une idée de l'activité du *Chat Bot*, du ratio de personnes qui l'utilisent jusqu'au bout (ce qui peut être un indicateur de pénébilité par exemple) et du ratio de message correctement intreprété.


# 4. Les alertes

Par le levier de la surveillance des performances, nous pouvons utiliser les alertes d'*Azure Insights* (dû au modification des tarifs d'Azure, nous n'avons pas pu l'intégrer au *MVP*), oubien développer une autre route d'API (estimation de charge de travail: 1 jour homme) qui s'occuperait par exemple de lever une alerte en envoyant un email où un message (par exemple sur le serveur Discord dédiés aux administrateurs du *ChatBot*). 

Dans cette optique, nous pensons que le dépassement de 10% des messages mal interprétés devrait lever une alerte et en informer les développeurs. 
Ceci en gardant à l'esprit qu'il faudra certainement attendre un certain temps (avoir une certaine taille d'historique) avant de pouvoir réellement traiter ces alertes.

# 5. Mise à jour du model

Afin d'améliorer les performances du model, et ainsi les performances du *Chatbot*, nous avons pensé à plusieurs à un moyen de mise à jour manuel, et un moyen de mise à jour automatique.

### Mise à jour manuelle.

Nous laissons la possibilité aux développeurs d'effectuer une mise à jour manuelle : en effet, l'équipe peut, de par son travail, trouver une nouvelle base de donnée, ou récupérer des discussions sur les *ChatBot* concurrent par exemple et enrichir de ce fait la base de donnée d'entrainement. 

Ainsi après enrichissement de 5-10% de la base de donnée les développeurs, par l'execution (après adaptation) des scripts déjà développés pour le *MVP* meuvent manuellement lancer toute la chaîne d'entrainement, deploiement et *release* du model.


### Mise à jour automatique.

Afin d'automatiser le workflow autant que possible et ainsi de diminuer la charge de travail des développeurs, nous avons également penser à une mise à jour automatique du modèle. En effet après avoir passé un temps certain à accueillir des nouveaux messages (depuis le dernier déploiement, manuel ou automatique) ; nous pouvons ajouter dans la chaîne d'alerte un lancement des scripts de la chaîne d'intégration afin de mettre à jour le modèle avec les nouvelles informations, et de déployer cette nouvelle version.

Cependant, nous n'estimons pas nécessaire d'attendre une simple augmentation de la taille de la base de donnée (5-10% pour la mise à jour manuelle), mais plutôt un compte du nombre de message mal interprété, ajouté manuellement. En effet, les message ajoutés dans la base de données ayant, par définition correctement été interprété, leur nombre augmentant ne devrait pas lancé une mise à jour du model.

Ainsi, nous proposons d'effectuer une mise à jour automatique du modèle après une augmentation d


# 6. En résumé

- Une utilisation du *ChatBot* va enrichir la base de donnée
- Une revue manuelle des messages mal interprétés est nécessaire
- Le taux d'interprétation correcte est un critère d'évaluation du modèle
- Le taux de complétion de discussion est un critère d'évaluation du modèle
- Lorsque les critères d'évaluations du modèles sont trop bas une alerte est levée
- Le modèle du *ChatBot* peut être ré-entraîné de manière manuelle ou automatique
- Lorsque le modèle est ré-entraîné, la base d'entrainement a été enrichie depuis le dernier entrainement