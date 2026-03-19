# ⚔️ Mécanique de combat

Tous les combats dans le RPG se déroulent **au tour par tour**. Ce guide explique comment fonctionnent les statistiques, les dégâts, les coups critiques et l'ordre des actions.

---

## Les statistiques

| Stat | Nom complet | Rôle |
|------|-------------|------|
| **PV** | Points de Vie | Ta barre de vie. À 0, tu perds le combat |
| **Att. Phy** | Attaque Physique | Dégâts des attaques corporelles |
| **Att. Mag** | Attaque Magique | Dégâts des attaques et sorts magiques |
| **Déf. Phy** | Défense Physique | Réduit les dégâts physiques reçus |
| **Déf. Mag** | Défense Magique | Réduit les dégâts magiques reçus |
| **Pén. Phy** | Pénétration Physique | Ignore une partie de la Défense Physique ennemie |
| **Pén. Mag** | Pénétration Magique | Ignore une partie de la Défense Magique ennemie |
| **Vitesse** | Vitesse | Détermine qui attaque en premier |
| **Critique** | Chance de Critique | Probabilité de faire un coup critique (en %) |
| **Dég. Critique** | Dégâts de Critique | Multiplicateur de dégâts lors d'un critique (en %) |

---

## Comment sont calculés les dégâts ?

**Dégâts physiques :**

> Attaque Physique − max(0 ; Défense Physique − Pénétration Physique)

**Dégâts magiques :**

> Attaque Magique − max(0 ; Défense Magique − Pénétration Magique)

En clair : ta pénétration "annule" une partie de la défense de l'ennemi. Si ta Pénétration Physique est supérieure à la Défense Physique de l'ennemi, il ne dispose d'aucune protection contre tes attaques.

Le minimum de dégâts est toujours **1** (impossible de faire 0 dégâts).

---

## Les coups critiques

Lorsqu'un coup critique survient, les dégâts sont multipliés par le **pourcentage de Dégâts de Critique** divisé par 100.

> Exemple : 1 000 dégâts + Critique à 175% = **1 750 dégâts**

Si ta Chance de Critique dépasse 100%, l'excédent se transforme en bonus sur les Dégâts de Critique.

> Exemple : 120% de Chance de Critique = 100% de crit garanti + 20% de Dégâts de Critique en plus

---

## L'ordre des actions (Vitesse)

La Vitesse détermine qui agit en premier à chaque tour. Si ta Vitesse est **supérieure** à celle de l'ennemi, tu attaques avant lui. En cas d'égalité, l'ordre est aléatoire.

Certains sorts modifient temporairement la vitesse ennemie ou la tienne.

---

## Le bouclier

Certains sorts ou effets passifs créent un **bouclier** qui absorbe les dégâts avant tes PV. Le bouclier disparaît quand il est épuisé ou à la fin de son effet.

---

## Les effets de statut

### Sur l'ennemi

| Effet | Description |
|-------|-------------|
| **Poison** | Inflige des dégâts à chaque fin de tour |
| **Brûlure** | Stacks de brûlure qui infligent des dégâts passifs et amplifient l'Inferno |
| **Ralentissement** | Réduit la Vitesse ennemie temporairement |
| **Débuff de stat** | Réduit une statistique de l'ennemi (Gardien du Temps) |
| **Étourdissement** | L'ennemi ne peut pas agir pendant X tours |
| **Marquage** | L'ennemi reçoit +X% de dégâts de toutes sources |

### Sur toi

| Effet | Description |
|-------|-------------|
| **Bouclier** | Absorbe les dégâts avant tes PV |
| **Buff de stat** | Augmente temporairement une statistique |
| **Vol de vie** | Récupère des PV proportionnellement aux dégâts infligés |
| **Indestructible** | Survie à un coup fatal avec 1 PV restant |

---

## Les sorts

À ton tour, tu peux choisir d'**attaquer normalement** ou d'utiliser un **sort** de ta classe.

- Chaque sort a un **coût en ressource** (Rage, Mana ou Combo selon ta classe)
- Certains sorts ont un **temps de recharge** : tu dois attendre X tours avant de pouvoir le réutiliser
- Certains sorts ont un **tour minimum** avant d'être disponibles

Si tu n'as pas assez de ressource ou si le sort est en recharge, seule l'attaque normale est disponible.
