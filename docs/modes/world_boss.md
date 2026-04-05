# 🌍 World Boss

Le World Boss est un **boss coopératif hebdomadaire** que tous les joueurs du serveur peuvent affronter ensemble. C'est le défi le plus puissant du jeu.

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
