# 🏰 Les Donjons

Les Donjons sont des défis en solo avec des **ennemis et boss plus puissants que dans le Monde**, mais qui offrent de bien meilleures récompenses. Il existe **3 niveaux de difficulté**.

---

## Les 3 types de donjons

| Type | Coût | Difficulté | Récompenses |
|------|:----:|------------|-------------|
| **Classique** | 3 ⚡ | ⭐ Accessible | Bonnes récompenses |
| **Élite** | 5 ⚡ | ⭐⭐⭐ Difficile | Très bonnes récompenses |
| **Abyssal** | 10 ⚡ | ⭐⭐⭐⭐⭐ Extrême | Récompenses d'exception |

---

## 🔍 Simulateur d'ennemi

Sélectionne un boss, une difficulté et un niveau pour voir ses statistiques exactes.

> Les stats sont calculées avec la même formule que le jeu.

<div id="enemy-calculator">

  <div id="ec-ctrl-donjon" class="ec-controls">
    <div class="ec-row">
      <label class="ec-label">Boss</label>
      <select id="ec-donjon-boss" class="ec-select">
        <option value="d_casque">🪖 Gardien des Crânes (★ Déf. Physique)</option>
        <option value="d_plastron">🛡️ Titan Cuirassé (★ HP)</option>
        <option value="d_pantalon">🌪️ Danseur de Guerre (★ Vitesse)</option>
        <option value="d_chaussures">⚡ Spectre Fulgurant (★ Vitesse)</option>
        <option value="d_arme">⚔️ Lame Dévastatrice (★ Att. Physique)</option>
        <option value="d_amulette">📿 Mystique Absolu (★ Att. Magique)</option>
        <option value="d_anneau">💍 Catalyseur Éternel (★ Critique)</option>
      </select>
    </div>
    <div class="ec-row">
      <label class="ec-label">Difficulté</label>
      <div class="ec-radio-group">
        <label><input type="radio" name="ec-diff" value="classique" checked /> Classique</label>
        <label><input type="radio" name="ec-diff" value="elite" /> Élite</label>
        <label><input type="radio" name="ec-diff" value="abyssal" /> Abyssal</label>
      </div>
    </div>
    <div class="ec-row">
      <label class="ec-label">Niveau <strong id="ec-donjon-level-val">1</strong> <span class="ec-hint">/ 100</span></label>
      <input type="range" id="ec-donjon-level" class="ec-range" min="1" max="100" value="1" />
    </div>

  </div>

  <div id="ec-result" style="display:none"></div>

</div>
