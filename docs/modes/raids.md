# 👥 Les Raids

Les Raids sont des combats **coopératifs** contre des boss extrêmement puissants. Jusqu'à **5 joueurs** peuvent y participer ensemble, chacun attaquant à son tour.

---

## Comment rejoindre un raid ?

Rends-toi dans le **Hub Raids**. Tu peux :
- **Créer** un nouveau raid (tu deviens l'hôte)
- **Rejoindre** un raid existant lancé par un autre joueur

Le coût d'entrée est de **50 énergie** par joueur.

---

## Déroulement du combat

Une fois le raid lancé, chaque joueur attaque **à tour de rôle** (dans l'ordre d'arrivée). Chacun voit le log des actions des autres et peut utiliser ses sorts librement.

Le boss possède une **barre de vie partagée** — tous les joueurs contribuent à la réduire. Si la barre tombe à zéro, tout le groupe gagne.

Si un joueur meurt (ses PV tombent à 0), il est **éliminé** du raid mais les autres continuent. Le raid échoue seulement si **tous les joueurs sont éliminés**.

---

## Les sorts en Raid

Certains sorts ont un effet spécial en Raid :

| Classe | Sort | Effet en Raid |
|--------|------|--------------|
| Guerrier | Élan Offensif | Booste l'Attaque Physique de toute l'équipe (puissance réduite) |
| Support | Bouclier | Protège toute l'équipe (puissance réduite) |
| Paladin | Aura Sacrée | Protège toute l'équipe (puissance réduite) |
| Tireur | Marquage | Ennemi marqué pour toute l'équipe (+15% dégâts) |

---

## Les récompenses

À la victoire, chaque participant reçoit :
- De l'**or**
- De l'**expérience**
- Des équipements de **panoplie Raid** — les plus puissants du jeu (×4,5 par rapport au Monde)

Les pièces de panoplie Raid ne s'obtiennent **qu'en Raid**.

---

## Conseils

- La composition de l'équipe est importante — un Support ou un Paladin qui protège le groupe peut faire la différence
- Communique avec ton groupe pour coordonner l'utilisation des sorts (ex : Marquage du Tireur avant l'Ultime d'un autre joueur)
- Le Raid est le contenu le plus difficile du jeu — assure-toi d'avoir un bon équipement avant de te lancer
- En tant qu'hôte, tu peux **choisir le niveau du boss** — commence par des niveaux modérés avant de viser le haut niveau

---

## 🔍 Simulateur d'ennemi

Sélectionne un boss de raid pour voir ses statistiques exactes.

> Les stats sont calculées avec la même formule que le jeu. Les HP et stats tiennent compte du multiplicateur raid (jusqu'à 5 joueurs).

<div id="enemy-calculator">

  <div id="ec-ctrl-raid" class="ec-controls">
    <div class="ec-row">
      <label class="ec-label">Boss de Raid</label>
      <select id="ec-raid-boss" class="ec-select">
        <option value="raid_1">🐉 Raid 1 — Vorgath l'Implacable (Niv. 100)</option>
        <option value="raid_2">🗡️ Raid 2 — Shivra l'Ombre Mortelle (Niv. 200)</option>
        <option value="raid_3">⚡ Raid 3 — Zyrex l'Archmage (Niv. 300)</option>
        <option value="raid_4">🏹 Raid 4 — Karek le Chasseur (Niv. 400)</option>
        <option value="raid_5">🕸️ Raid 5 — Serath le Corrupteur (Niv. 500)</option>
        <option value="raid_6">🧛 Raid 6 — Mordas le Sans-Âme (Niv. 600)</option>
        <option value="raid_7">⏳ Raid 7 — Chronovex l'Invariant (Niv. 700)</option>
        <option value="raid_8">🐍 Raid 8 — Nyxara la Corrompue (Niv. 800)</option>
        <option value="raid_9">🔥 Raid 9 — Ignareth le Phénix (Niv. 900)</option>
        <option value="raid_10">🌑 Raid 10 — Omnifax le Divin (Niv. 1000)</option>
      </select>
    </div>
    <div class="ec-hint-box">
      👥 Chaque raid boss a une classe fixe. Stats ×2.5 pour un combat à 5 joueurs, puis HP ×4 supplémentaire (HP total ×10 vs un ennemi de zone équivalente).
    </div>
  </div>

  <div id="ec-result" style="display:none"></div>

</div>
