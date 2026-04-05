# 📊 Calculateur de Stats

Sélectionne une classe et un niveau pour voir les statistiques exactes, avec ou sans bonus de prestige.

<div id="stat-calculator">

  <div class="sc-inputs">

    <div class="sc-field">
      <label class="sc-label" for="sc-class">Classe</label>
      <select id="sc-class" class="ec-select"></select>
    </div>

    <div class="sc-field">
      <label class="sc-label" for="sc-level-num">
        Niveau
        <span class="sc-label-hint">(1 – 1000)</span>
      </label>
      <input type="number" id="sc-level-num" class="ec-input" min="1" max="1000" value="1">
    </div>

    <div class="sc-field">
      <label class="sc-label" for="sc-prestige">
        Prestige
        <span class="sc-label-hint">(optionnel)</span>
      </label>
      <input type="number" id="sc-prestige" class="ec-input" min="0" max="9999" value="0" placeholder="0">
    </div>

  </div>

  <div id="sc-prestige-badge" class="sc-prestige-badge" style="display:none"></div>

  <div id="sc-result" class="sc-result">
    <div id="sc-class-header" class="sc-class-header"></div>
    <table class="sc-table">
      <thead>
        <tr>
          <th>Stat</th>
          <th>Valeur</th>
          <th id="sc-th-base" style="display:none">Sans prestige</th>
        </tr>
      </thead>
      <tbody id="sc-tbody"></tbody>
    </table>
  </div>

</div>
