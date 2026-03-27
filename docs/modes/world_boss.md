# 🌍 World Boss

Le World Boss est un **boss coopératif hebdomadaire** que tous les joueurs du serveur peuvent affronter ensemble. C'est le défi le plus puissant du jeu.

---

## Comment ça fonctionne ?

Rends-toi dans le **Hub World Boss** pour attaquer le boss de la semaine.

- Coût : **50 énergie** par attaque
- Chaque joueur attaque **individuellement** à son rythme — pas besoin d'être synchronisé avec les autres
- Le boss a une **barre de vie commune** : tous les dégâts de tous les joueurs s'accumulent
- Quand la barre tombe à zéro, **tout le serveur gagne** et les récompenses sont distribuées

---

## Les combats

Contrairement aux Raids, chaque attaque contre le World Boss est un **combat solo** contre le boss. Tu joues ton combat normalement avec tes sorts, et tes dégâts s'ajoutent au total collectif.

!!! info "Mode éphémère"
    Le World Boss commence chaque combat à tes **PV maximum**, peu importe ton état. Il n'impacte pas tes PV hors combat.

---

## Le classement individuel

Un classement des joueurs ayant infligé le plus de dégâts au boss est affiché en temps réel. Les meilleurs contributeurs reçoivent des **récompenses supplémentaires**.

---

## Les récompenses

### Matériaux immédiats (à chaque attaque)

Tu reçois des matériaux aléatoires **immédiatement après chaque combat**, selon le tour personal que tu tiens :

| Tour personnel | Survie | Défaite |
|:--------------:|:------:|:-------:|
| Tour 1 | 12 | 10 |
| Tour 5 | 20 | 18 |
| Tour 10 | 30 | 28 |
| Tour 15 | 40 | 38 |
| Tour 20 | **50** | 48 |

**Formule :** `10 + 2 × attaques_du_WB_survivées`
- **Survie** : `10 + 2 × tour` (tu as survécu à l'attaque de ce tour)
- **Défaite** : `10 + 2 × (tour − 1)` (tu n'as pas survécu au dernier coup)
- Minimum garanti : **10 matériaux** (défaite au Tour 1)

Avec 10 attaques par semaine, tu obtiens entre **100** (tout Tour 1 mort) et **500** matériaux (tout Tour 20 survie).

### Récompenses de fin de semaine (classement)

À la défaite du World Boss :
- Tous les participants reçoivent des récompenses de base
- Les meilleurs dégâts reçoivent des récompenses **supplémentaires et exclusives**
- Possibilité d'obtenir des **Reliques** — des objets très rares qui donnent des effets passifs permanents en combat

---

## Les Reliques

Les Reliques sont des objets uniques obtenables via le World Boss. Elles ajoutent **6 effets passifs permanents** simultanément en combat. Les récompenses sont attribuées selon le classement final par dégâts infligés.

| Rang | Relique obtenue | Or |
|------|-----------------|:--:|
| 🥇 Rang 1 | 🌈 Prismatique | 300 000 |
| 🥈 Rang 2 | 🩵 Transcendante | 250 000 |
| 🥉 Rang 3 | 🟡 Divine | 200 000 |
| Rang 4 | 🔶 Artefact | 175 000 |
| Rang 5 | 🟥 Mythique | 150 000 |
| Rang 6 | 🟧 Légendaire | 125 000 |
| Rang 7 | 🟪 Épique | 100 000 |
| Rang 8 | 🟦 Rare | 85 000 |
| Rang 9 | 🟩 Peu Commune | 70 000 |
| Rang 10 | 🟩 Peu Commune | 60 000 |
| Rang 11+ | ⬜ Commune | 50 000 |

!!! info "Tous les participants sont récompensés"
    Tout joueur ayant contribué au World Boss reçoit au minimum une Relique Commune et 50 000 or, quelle que soit sa position dans le classement.

Chaque Relique confère simultanément **6 effets passifs** — Vol de vie, Réduction de dégâts, Bonus de dégâts, Reflet, Double frappe, et Régénération HP par tour — dont les valeurs augmentent avec la rareté.

> Pour les effets détaillés, les plafonds, et les règles de stacking : **[Objets → Reliques](../objets/reliques.md)**

---

## Conseils

- Participe chaque semaine — les Reliques sont des items très puissants disponibles nulle part ailleurs
- Plus tu infliges de dégâts, meilleures sont tes récompenses — utilise tes meilleurs sorts
- Utilise tes **nourritures** (Boulanger) avant d'attaquer pour maximiser tes dégâts
- Le World Boss est très résistant — ne t'attends pas à le finir seul, la coopération de tout le serveur est nécessaire

---

## 🔍 Simulateur d'ennemi

Indique ton tour personnel pour voir les statistiques du World Boss que tu affronteras.

> Les stats sont calculées avec la même formule que le jeu. La zone équivalente augmente de ×1,25 à chaque tour (Tour 1 = Zone 1 000, Tour 10 = Zone ~7 451, Tour 20 = Zone ~55 511). **Tour 20 maximum** — en cas de défaite, le tour repart à 1.

<div id="enemy-calculator">

  <div id="ec-ctrl-wb" class="ec-controls">
    <div class="ec-row">
      <label class="ec-label">Tour personnel <strong id="ec-wb-tour-val">1</strong></label>
      <input type="range" id="ec-wb-tour" class="ec-range" min="1" max="20" value="1" />
      <input type="number" id="ec-wb-tour-input" class="ec-input" min="1" max="20" value="1" style="max-width:120px; margin-top:0.4rem" />
      <div id="ec-wb-zone-equiv" class="ec-note" style="margin-top:0.3rem">Zone équivalente : ~1 000</div>
    </div>
    <div class="ec-hint-box">
      🐉 Le World Boss est <strong>Bot Suprême</strong>. Ses stats augmentent de ×1,25 à chaque tour survivé (Tour 1 = Zone 1 000 · Tour 10 = Zone ~7 451 · Tour 20 = Zone ~55 511). <strong>Tour 20 maximum</strong> — en cas de défaite, le tour repart à 1.
    </div>
  </div>

  <div id="ec-result" style="display:none"></div>

</div>
