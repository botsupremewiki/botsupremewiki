# 🗺️ Modes de jeu

Le RPG propose plusieurs modes de jeu avec des objectifs et des récompenses différents.

| Mode | Joueurs | Coût en énergie | Récompenses |
|------|---------|-----------------|-------------|
| [Monde](monde.md) | Solo | 1 par combat (boss : 10–100) | XP, or, équipements |
| [Donjons Classiques](donjons.md) | Solo | 5 | Meilleures récompenses |
| [Donjons Élite](donjons.md) | Solo | 10 | Récompenses supérieures |
| [Donjons Abyssaux](donjons.md) | Solo | 15 | Récompenses d'élite |
| [Raids](raids.md) | Jusqu'à 3 | 500 | Récompenses exclusives |
| [World Boss](world_boss.md) | Tous | 100 | Récompenses hebdomadaires |
| [Taverne — PvP Classique](pvp.md) | 2 joueurs | 5 | Aucune (pour le fun) |
| [Taverne — PvP Classé](pvp.md) | 2 joueurs | 5 | Élo et classement |

---

## Les statistiques de combat

| Stat | Rôle |
|------|------|
| **PV** | Ta barre de vie — à 0, tu perds le combat |
| **Att. Physique** | Dégâts des attaques et sorts physiques |
| **Att. Magique** | Dégâts des attaques et sorts magiques |
| **Déf. Physique** | Réduit les dégâts physiques reçus |
| **Déf. Magique** | Réduit les dégâts magiques reçus |
| **Pén. Physique** | Ignore une partie de la Déf. Physique ennemie |
| **Pén. Magique** | Ignore une partie de la Déf. Magique ennemie |
| **Vitesse** | Détermine qui agit en premier |
| **Critique** | Probabilité de faire un coup critique |
| **Dég. Critique** | Multiplicateur de dégâts lors d'un critique |

---

## Dégâts, défense et pénétration

La **pénétration** réduit la défense ennemie avant le calcul des dégâts. La défense effective ne peut pas descendre sous 0.

| Défense effective | Réduction des dégâts reçus |
|:-----------------:|:--------------------------:|
| 0 | 0% |
| 100 | 17% |
| 250 | 33% |
| 500 | 50% |
| 750 | 60% |
| 1 000 | 67% |
| 2 000 | 80% |
| 4 000 | 89% |

Le minimum de dégâts infligés est toujours **1**.

---

## Critique et Vitesse

Les coups critiques multiplient les dégâts selon le pourcentage de **Dégâts de Critique**. Si la **Chance de Critique** dépasse 100%, l'excédent augmente automatiquement les Dégâts de Critique.

La **Vitesse** détermine qui agit en premier dans un combat. Si les deux combattants ont la même vitesse, l'ordre est aléatoire.

---

## Sorts et ressources

Chaque classe possède des sorts uniques. Utiliser un sort coûte de la ressource selon la classe :

| Ressource | Classes | Régénération |
|-----------|---------|--------------|
| 🔴 Rage (max 100) | Guerrier, Vampire, Paladin | +5 début de ton tour, +15 après l'attaque ennemie |
| 🔵 Mana (max 100) | Mage, Support, Pyromancien | +15 au début de ton tour |
| 🟡 Combo (max 10) | Assassin, Tireur, Gardien du Temps, Ombre Venin | +1 en fin de ton tour, +1 en fin du tour ennemi |

Certains sorts ont aussi un **temps de recharge** entre deux utilisations. Sans assez de ressource, tu attaques normalement.

---

## Effets de statut

Des effets peuvent s'appliquer pendant le combat, sur toi ou sur l'ennemi :

| Effet | Description |
|-------|-------------|
| **Poison** | Dégâts par tour proportionnels aux stacks actifs (max 10 stacks) |
| **Brûlure** | Dégâts par tour proportionnels aux stacks actifs (max 5 stacks) |
| **Étourdissement** | L'ennemi ne peut pas agir pendant X tours |
| **Bouclier** | Absorbe les dégâts avant les PV |
| **Buff de stat** | Augmente temporairement une ou plusieurs stats |
| **Débuff de stat** | Réduit temporairement une ou plusieurs stats ennemies |
| **Vol de vie** | Récupère des PV proportionnellement aux dégâts infligés |
| **Reflet** | Renvoie une partie des dégâts reçus à l'ennemi |

---

## Les boss

- **Boss Runiques** — toutes les 10 zones. Plus résistants qu'un ennemi classique, avec un passif selon leur classe.
- **Boss Emblématiques** — toutes les 100 zones. Encore plus dangereux, ils utilisent des sorts actifs.
- **Boss Antiques** — toutes les 1 000 zones. Les ennemis les plus redoutables du mode Monde. Prépare tes consommables avant de les affronter.
