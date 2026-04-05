# ⚒️ Métiers d'Artisanat

Les métiers d'artisanat fabriquent les pièces de la **panoplie Craft** — l'une des 6 sources d'équipement du jeu. Le multiplicateur de puissance dépend du **tier de maîtrise** atteint (max ×2.00 au niveau 100).

---

<div id="craft-calculator">

  <div class="cc-section-label">Métier d'artisanat</div>
  <div class="cc-tab-bar" id="cc-profession-bar"></div>
  <div id="cc-profession-info" class="cc-profession-info"></div>

  <div class="cc-section-label">Classe du joueur</div>
  <div class="cc-tab-bar" id="cc-class-bar"></div>

  <div id="cc-recipe-result">
    <table class="cc-table">
      <thead>
        <tr>
          <th>Tier</th>
          <th>Niv. requis</th>
          <th id="cc-mat-header">Matériaux</th>
          <th>Mult. source</th>
        </tr>
      </thead>
      <tbody id="cc-recipe-tbody"></tbody>
    </table>
  </div>

</div>

---

## Rareté des items craftés

La rareté dépend du **niveau de métier** (zone équivalente = niveau × 10).

<div id="rarity-calculator">

  <div class="cc-field">
    <label class="cc-label" for="cc-prof-level">Niveau de métier <span class="cc-hint">(1–100)</span></label>
    <input type="number" id="cc-prof-level" class="ec-input" min="1" max="100" value="1">
  </div>

  <table class="cc-table">
    <thead>
      <tr>
        <th>Rareté</th>
        <th>Probabilité</th>
        <th>Répartition</th>
      </tr>
    </thead>
    <tbody id="cc-rarity-tbody"></tbody>
  </table>

</div>

---

## Voir aussi

- [Récolte](recolte.md) — obtenir les matériaux nécessaires
- [Équipements & Panoplies](../objets/equipements.md) — statistiques, raretés et sources
- [Runes](../objets/runes.md) — enchanter ton équipement après le craft
