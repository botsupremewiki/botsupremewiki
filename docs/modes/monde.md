# 🗺️ Le Monde

Le Monde est le **mode de jeu principal** pour progresser en solo. Il se compose de **1 000 zones** avec des ennemis de plus en plus puissants.

- Toutes les **10 zones** (sauf multiples de 100) : un **Boss Runique** barre la route
- Toutes les **100 zones** (sauf la zone 1 000) : un **Boss Emblématique** de plus en plus redoutable
- **Zone 1 000** : les **10 Boss Antiques** en séquence, un par classe — les combats les plus difficiles du Monde

---

## Coûts en énergie

| Type d'ennemi | Coût |
|---|:---:|
| Ennemi normal | 1 ⚡ |
| Boss de zone | 10 ⚡ |
| Boss Runique | 25 ⚡ |
| Boss Emblématique | 50 ⚡ |
| Boss Antique | 100 ⚡ |

---

## 🔍 Simulateur d'ennemi

<div id="enemy-calculator">
  <div id="ec-ctrl-monde" class="ec-controls">
    <div class="ec-row">
      <label class="ec-label">Zone <span class="ec-hint">(1 – 1 000)</span></label>
      <input type="number" id="ec-zone" class="ec-input" min="1" max="1000" value="50" />
    </div>
    <div class="ec-row">
      <label class="ec-label">Type d'ennemi</label>
      <select id="ec-stage" class="ec-select">
        <option value="ennemi">👿 Ennemi de stage</option>
        <option value="boss_classique">⚔️ Boss de zone</option>
        <option value="boss_runique">🔮 Boss Runique</option>
        <option value="boss_emblematique">🌟 Boss Emblématique</option>
        <option value="boss_antique">⚠️ Boss Antique (zone 1 000)</option>
      </select>
    </div>
    <div class="ec-row" id="ec-stage-row" style="display:none">
      <label class="ec-label">Ennemi</label>
      <select id="ec-enemy-stage" class="ec-select">
        <option value="1">⚔️ Stage 1 — Guerrier</option>
        <option value="2">🗡️ Stage 2 — Assassin</option>
        <option value="3">🔮 Stage 3 — Mage</option>
        <option value="4">🏹 Stage 4 — Tireur</option>
        <option value="5">💚 Stage 5 — Support</option>
        <option value="6">🧛 Stage 6 — Vampire</option>
        <option value="7">⏳ Stage 7 — Gardien du Temps</option>
        <option value="8">☠️ Stage 8 — Ombre Venin</option>
        <option value="9">🔥 Stage 9 — Pyromancien</option>
        <option value="10">🛡️ Stage 10 — Paladin</option>
      </select>
    </div>
    <div class="ec-row" id="ec-class-row" style="display:none">
      <label class="ec-label">Boss Antique</label>
      <select id="ec-boss-class" class="ec-select">
        <option value="Guerrier">⚔️ Guerrier — Vrethax le Primordial</option>
        <option value="Assassin">🗡️ Assassin — Azkoth la Conscience Noire</option>
        <option value="Mage">🔮 Mage — Solarius le Dévoreur d'Étoiles</option>
        <option value="Tireur">🏹 Tireur — Mortifax l'Impérissable</option>
        <option value="Support">💚 Support — Chronaxis le Maître Absolu</option>
        <option value="Vampire">🧛 Vampire — Nexuvor l'Indicible</option>
        <option value="Gardien du Temps">⏳ Gardien du Temps — Erebos la Nuit Éternelle</option>
        <option value="Ombre Venin">☠️ Ombre Venin — Pantheos le Dieu-Bête</option>
        <option value="Pyromancien">🔥 Pyromancien — Ultharak l'Abomination</option>
        <option value="Paladin">🛡️ Paladin — Omegaris la Fin du Monde</option>
      </select>
    </div>
  </div>
  <div id="ec-result" style="display:none"></div>
</div>
