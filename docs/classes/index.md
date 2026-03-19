# ⚔️ Les Classes

Il y a **10 classes** jouables, chacune avec un passif unique, 3 sorts actifs et un sort ultime.

Chaque classe utilise une **ressource** pour lancer ses sorts :

| Ressource | Classes | Fonctionnement |
|-----------|---------|---------------|
| **Rage** | Guerrier, Paladin | Se régénère de +10 par tour et +5 à chaque attaque. Maximum : 100 |
| **Mana** | Mage, Gardien du Temps, Pyromancien | Se régénère de +15 par tour. Maximum : 100 |
| **Combo** | Assassin, Tireur, Support, Vampire, Ombre Venin | Se régénère de +1 par tour. Maximum : 5 |

---

## Comparatif des stats de départ (niveau 1)

| Classe | PV | Att. Phy | Att. Mag | Déf. Phy | Déf. Mag | Vitesse | Critique |
|--------|----|----------|----------|----------|----------|---------|---------|
| Guerrier | 1 200 | 80 | 20 | 60 | 30 | 80 | 5% |
| Assassin | 700 | 110 | 15 | 30 | 20 | 130 | 20% |
| Mage | 650 | 15 | 120 | 20 | 40 | 90 | 10% |
| Tireur | 750 | 100 | 10 | 25 | 25 | 110 | 15% |
| Support | 1 000 | 50 | 50 | 50 | 50 | 70 | 5% |
| Vampire | 850 | 95 | 40 | 40 | 35 | 100 | 12% |
| Gardien du Temps | 900 | 70 | 70 | 45 | 45 | 85 | 8% |
| Ombre Venin | 800 | 85 | 60 | 35 | 35 | 105 | 14% |
| Pyromancien | 700 | 20 | 130 | 25 | 45 | 88 | 10% |
| Paladin | 1 100 | 65 | 40 | 55 | 55 | 75 | 5% |

> Ces stats augmentent à chaque niveau. Les dégâts de critique sont séparés (valeur entre 130% et 200% selon la classe).

---

## Résumé des passifs

| Classe | Passif |
|--------|--------|
| Guerrier | +% dégâts proportionnel aux PV manquants (jusqu'à +50%) |
| Assassin | 20% de chance d'esquiver chaque attaque ennemie |
| Mage | +% dégâts magiques proportionnel aux PV actuels (jusqu'à +50%) |
| Tireur | 25% de chance de doubler tous ses dégâts |
| Support | 30% de chance de générer un bouclier de 8% des PV max |
| Vampire | Vol de vie de 15% des dégâts infligés (plafonné à 10% PV max par tour) |
| Gardien du Temps | Réduit une stat aléatoire de l'ennemi de -5% par tour (cumulatif, max -50%) |
| Ombre Venin | Applique du poison dès le premier tour de combat |
| Pyromancien | Ajoute 1 stack de brûlure par tour (maximum 5 stacks) |
| Paladin | Rampe : +3% dégâts ET -3% dégâts reçus par tour (maximum +30%/-30%) |
