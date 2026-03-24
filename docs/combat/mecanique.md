# ⚔️ Mécanique de Combat

## 🔄 Déroulement d'un combat

Un combat se déroule en **tours**. À chaque tour :

1. Le joueur et l'ennemi jouent chacun leur tour (basé sur la **vitesse**)
2. Le joueur peut utiliser un **sort** s'il a assez de ressource
3. Les effets de statut (poison, brûlure) sont appliqués
4. La ressource du joueur se régénère automatiquement

---

## ⚡ Vitesse et ordre d'attaque

- Si ta **vitesse > vitesse ennemie** → tu attaques en premier
- Si ta vitesse est **3× supérieure** à celle de l'ennemi → tu attaques **2 fois** par tour
- La vitesse peut être boostée par des sorts ou des équipements

---

## 🗡️ Calcul des dégâts

Les dégâts physiques sont calculés comme suit :

> **Dégâts** = Attaque Physique − Défense Physique de l'ennemi + Pénétration Physique

La **Pénétration** ignore une partie de la défense ennemie.
Les **Critiques** multiplient les dégâts (multiplicateur de base : 150%).

---

## 🛡️ Types de défense

| Stat | Protège contre |
|------|----------------|
| 🛡️ Défense Physique | Attaques physiques (p_atk) |
| 🔷 Défense Magique | Attaques magiques (m_atk) |
| 🗡️ Pénétration Physique | Réduit la défense physique ennemie |
| 💫 Pénétration Magique | Réduit la défense magique ennemie |

---

## 💉 Effets de statut

| Effet | Description |
|-------|-------------|
| 🔥 Brûlure | Dégâts magiques par tour (15% ATK Mag/stack) |
| ☠️ Poison | Dégâts par tour (3% HP max/stack) |
| 😵 Étourdissement | L'ennemi ne peut pas agir pendant N tours |
| 🩸 Marque | L'ennemi subit des bonus de dégâts |

---

## ✨ Les Sorts

Chaque classe possède **3 sorts** :

- **Sort 1** (S1) : sort de base, coût faible, souvent sans temps de recharge
- **Sort 2** (S2) : sort intermédiaire, coût modéré, temps de recharge
- **⭐ Ultime** : sort puissant, coût élevé, long temps de recharge

Les sorts se déclenchent **automatiquement** quand :
- Tu as assez de ressource
- Le temps de recharge est écoulé
- C'est le bon moment selon l'IA du personnage

---

## ❤️ Régénération HP

Entre les combats, tu récupères automatiquement :
- **+3% de tes HP max** toutes les 10 minutes (passif)
- Des potions de soin peuvent être utilisées en combat

---

## 🎯 Critiques

- La **chance de critique** détermine la probabilité d'un coup critique
- Les **dégâts critiques** multiplient les dégâts du coup critique
- Base : 150% (×1.5 dégâts normaux)
- Certaines classes ont des modificateurs critiques élevés (Assassin 175%, Mage 175%)
