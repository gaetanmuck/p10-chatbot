---
marp: true
title: OpenClassrooms - Parcours Ingénieur IA - Projet 10
description: Développer un chatbot pour réserver des vacances
author: Gaétan Muck
theme: gaia
header: OpenClassrooms - Parcours Ingénieur IA - Projet 10
paginate: true
_paginate: false

---

<style>
section.global p {
    text-align: justify;
}
section.centeredList ul {
    text-align: center;
    list-style-type: none;
}
img[alt~="center"] {
  display: block;
  margin: 0 auto;
}
</style>

<!-- _class: lead invert -->

# Développer un chatbot pour réserver des vacances


---
<!-- _class: invert global -->

## Problématiques metier

- Réalisation d'un premier MVP
- Utilisation de données extérieures
- Récupérer les informations des conversations
- Surveiller les performances
- Lancer des alertes
- Réentrainer (avec une chaine d'intégration)

---
<!-- _class: invert global -->

## Les données

- Conversation créée pour avoir des dialogues enregistrés
- Slack bot avec 12 humains sur 20 jours: 1369 dialogues

![width:400 center](analyse-exploratoire.png)

---
<!-- _class: invert global -->

## Le modèle: Conversational Language Understanding

![width:800 center](model-intents.png)
![width:1000 center](model-entities.png)


---
<!-- _class: invert global -->

## Entrainement du modèle

![width:800 center](training-set.png)

## Résultats

![width:1000 center](performances.png)

---
<!-- _class: invert global -->

## Web app de chat de réservation de vols

![width:1000 center](azure-web-app.png)

## Intégration continue et tests unitaires

![width:800 center](github-workflow.png)

---
<!-- _class: invert global -->

## Interface de chat

![width:500 center](chat-example.png)


---
<!-- _class: invert global -->

## Surveillance des performances et historique

![width:500 center](insights.png)

![width:500 center](history.png)

---
<!-- _class: invert global -->

## Mise à jour du modèle

- Scripts automatisés : entrainement, déploiement, tests unitaires

![width:500 center](scripts.png)


---
<!-- _class: invert global -->

## Problème rencontrés

- Application Azure LUIS non disponible (changement vers le CLU)
  => Solution : Utilisation du CLU

- Déploiement sur Azure non fonctionel
  => Solution : Déploiement sur un VPS

- Lancement d'alertes non disponible (payement requis)
  => Solution pour le MVP : surveillance visuelle des seuils et des historiques

---
<!-- _class: invert global -->

## Chaîne d'intégration future

![width:800 center](flyme-bot-model-architecture.png)

---
<!-- _class: invert global -->

## Conclusions

- MVP disponible en ligne
- Avoir nos propre données
- Construire notre propre système de surveillance et d'alerte
- Collecter des retours sur les fonctionnalités du Chatbot
