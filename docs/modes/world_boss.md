# 🌍 World Boss

Le World Boss est un **boss coopératif hebdomadaire** que tous les joueurs du serveur peuvent affronter ensemble. C'est le défi le plus puissant du jeu.

---

## Règles et limites

| Paramètre | Valeur |
|-----------|--------|
| Prérequis | Avoir atteint la **zone 1 000** |
| Coût par attaque | 100 ⚡ |
| Attaques max par joueur | **10 par semaine** |
| Tours max par combat | 25 tours |
| Réinitialisation | Chaque **lundi à minuit UTC** |

!!! info "Boss partagé"
    Le World Boss a une **barre de vie commune** pour tous les joueurs. Chaque attaque contribue à l'abattre — et chaque joueur est classé selon ses dégâts totaux de la semaine.

---

## Récompenses hebdomadaires

Les récompenses sont distribuées à la fin de chaque semaine selon le classement par dégâts totaux infligés.

| Rang | Relique | Or |
|------|---------|:--:|
| 🥇 1 | 🌈 Prismatique | 300 000 |
| 🥈 2 | 🩵 Transcendante | 250 000 |
| 🥉 3 | 🟡 Divine | 200 000 |
| 4 | 🔶 Artefact | 175 000 |
| 5 | 🟥 Mythique | 150 000 |
| 6 | 🟧 Légendaire | 125 000 |
| 7 | 🟪 Épique | 100 000 |
| 8 | 🟦 Rare | 85 000 |
| 9 | 🟩 Peu Commune | 70 000 |
| 10 | 🟩 Peu Commune | 60 000 |
| 11+ | ⬜ Commune | 50 000 |

!!! tip "Tout le monde est récompensé"
    Même au-delà du rang 10, tout joueur ayant participé reçoit au minimum une **Relique Commune** et **50 000 or**. Aucune participation n'est perdue.

---

---

## 🔍 Simulateur d'ennemi

<div id="enemy-calculator">

  <div id="ec-ctrl-wb" class="ec-controls">
    <div class="ec-row">
      <label class="ec-label">Tour personnel <strong id="ec-wb-tour-val">1</strong></label>
      <input type="range" id="ec-wb-tour" class="ec-range" min="1" max="25" value="1" />
      <input type="number" id="ec-wb-tour-input" class="ec-input" min="1" max="25" value="1" style="max-width:120px; margin-top:0.4rem" />
      <div id="ec-wb-zone-equiv" class="ec-note" style="margin-top:0.3rem">Zone équivalente : ~1 000</div>
    </div>
  </div>

  <div id="ec-result" style="display:none"></div>

</div>
