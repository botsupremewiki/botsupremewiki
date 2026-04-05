# 🛡️ Équipements & Panoplies

Les équipements améliorent tes statistiques en combat. Il existe **7 emplacements** à équiper, et des **panoplies** (sets) qui donnent des bonus supplémentaires quand plusieurs pièces du même set sont portées ensemble.

Il y a au total **60 panoplies** : 6 par classe × 10 classes.

---

## Simulateur d'équipement

<div id="eq-builder" class="eq-card">

  <div class="eq-builder-grid">

    <div class="ec-field">
      <label class="ec-label">Slot</label>
      <select id="eq-slot" class="ec-select">
        <option value="casque">⛑️ Casque</option>
        <option value="plastron">🦺 Plastron</option>
        <option value="pantalon">👖 Pantalon</option>
        <option value="chaussures">👟 Chaussures</option>
        <option value="arme">⚔️ Arme</option>
        <option value="amulette">📿 Amulette</option>
        <option value="anneau">💍 Anneau</option>
      </select>
    </div>

    <div class="ec-field">
      <label class="ec-label">Classe</label>
      <select id="eq-class" class="ec-select">
        <option>Guerrier</option>
        <option>Assassin</option>
        <option>Mage</option>
        <option>Tireur</option>
        <option>Support</option>
        <option>Vampire</option>
        <option>Gardien du Temps</option>
        <option>Ombre Venin</option>
        <option>Pyromancien</option>
        <option>Paladin</option>
      </select>
    </div>

    <div class="ec-field">
      <label class="ec-label">Niveau</label>
      <input type="number" id="eq-level" class="ec-input" min="1" max="1000" value="100">
    </div>

    <div class="ec-field">
      <label class="ec-label">Source</label>
      <select id="eq-source" class="ec-select">
        <option value="monde">🌍 Monde</option>
        <option value="donjon_classique">🏰 Donjon Classique</option>
        <option value="donjon_elite">⚔️ Donjon Élite</option>
        <option value="donjon_abyssal">🌑 Donjon Abyssal</option>
        <option value="raid">👑 Raid</option>
        <option value="craft">⚒️ Craft</option>
      </select>
    </div>

    <div class="ec-field" id="eq-craft-row" style="display:none">
      <label class="ec-label">Tier craft</label>
      <input type="number" id="eq-craft-tier" class="ec-input" min="1" max="10" value="1">
    </div>

    <div class="ec-field">
      <label class="ec-label">Rareté</label>
      <select id="eq-rarity" class="ec-select">
        <option value="commun">⬜ Commun</option>
        <option value="peu commun">🟩 Peu Commun</option>
        <option value="rare">🟦 Rare</option>
        <option value="épique">🟪 Épique</option>
        <option value="légendaire">🟧 Légendaire</option>
        <option value="mythique">🟥 Mythique</option>
        <option value="artefact">🔶 Artefact</option>
        <option value="divin">🌟 Divin</option>
        <option value="transcendant">💠 Transcendant</option>
        <option value="prismatique">🌈 Prismatique</option>
      </select>
    </div>

    <div class="ec-field">
      <label class="ec-label">Forge</label>
      <input type="number" id="eq-forge" class="ec-input" min="0" max="10" value="0">
    </div>

  </div>

  <div id="eq-preview" class="eq-preview"></div>

  <button id="eq-add-btn" class="eq-add-btn">＋ Ajouter au test</button>

</div>

---

## Équipement test

<div class="eq-card">
  <table class="cc-table">
    <thead>
      <tr>
        <th>Slot</th>
        <th>Item</th>
        <th>Stats</th>
        <th></th>
      </tr>
    </thead>
    <tbody id="eq-test-tbody"></tbody>
  </table>
  <div id="eq-totals"></div>
</div>

---

## Taux de drop par source

## Taux de drop par source

<div id="drop-calc" class="eq-card">

  <div class="eq-builder-grid">
    <div class="ec-field">
      <label class="ec-label">Source</label>
      <select id="dr-source" class="ec-select">
        <option value="monde">🌍 Monde</option>
        <option value="donjon_classique">🏰 Donjon Classique</option>
        <option value="donjon_elite">⚔️ Donjon Élite</option>
        <option value="donjon_abyssal">🌑 Donjon Abyssal</option>
        <option value="raid">👑 Raid</option>
      </select>
    </div>
    <div class="ec-field">
      <label class="ec-label" id="dr-level-label">Zone (1–1000)</label>
      <input type="number" id="dr-level" class="ec-input" min="1" max="1000" value="500">
    </div>
  </div>

  <table class="cc-table" style="margin-top:.75rem">
    <thead>
      <tr><th>Rareté</th><th>Probabilité</th><th>Répartition</th></tr>
    </thead>
    <tbody id="dr-tbody"></tbody>
  </table>

</div>

---

## 📊 Bonus de panoplie par classe

<div id="set-browser" class="eq-card">
  <div id="set-class-tabs"  class="set-tab-group"></div>
  <div id="set-source-tabs" class="set-tab-group" style="margin-top:.5rem;display:none"></div>
  <div id="set-table-wrap"  style="margin-top:.5rem"></div>
</div>
