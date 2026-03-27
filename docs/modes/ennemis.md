# 🔍 Simulateur d'Ennemis

Sélectionne un mode de jeu, configure les paramètres, et découvre les statistiques exactes de n'importe quel ennemi du jeu.

> Les stats sont calculées avec la même formule que le jeu.

---

<div id="enemy-calculator">

  <div class="ec-tabs">
    <button class="ec-tab ec-tab-active" data-mode="monde">🗺️ Monde</button>
    <button class="ec-tab" data-mode="donjon">⚔️ Donjon</button>
    <button class="ec-tab" data-mode="raid">👥 Raid</button>
    <button class="ec-tab" data-mode="wb">🐉 World Boss</button>
  </div>

  <!-- ── Monde ─────────────────────────────────────────── -->
  <div id="ec-ctrl-monde" class="ec-controls">
    <div class="ec-row">
      <label class="ec-label">Zone <span class="ec-hint">(1 – 10 000)</span></label>
      <input type="number" id="ec-zone" class="ec-input" min="1" max="10000" value="100" />
    </div>
    <div class="ec-row">
      <label class="ec-label">Ennemi</label>
      <select id="ec-stage" class="ec-select">
        <option value="boss_classique">⚔️ Boss de Zone (toutes zones)</option>
        <option value="boss_runique">🔮 Boss Runique (zone multiple de 10)</option>
        <option value="boss_emblematique">🌟 Boss Emblématique (zone multiple de 100)</option>
        <option value="boss_antique">⚠️ Boss Antique (zone multiple de 1 000)</option>
        <option value="sep" disabled>─── Ennemis normaux ───</option>
        <option value="1">Stage 1 — Guerrier</option>
        <option value="2">Stage 2 — Assassin</option>
        <option value="3">Stage 3 — Mage</option>
        <option value="4">Stage 4 — Tireur</option>
        <option value="5">Stage 5 — Support</option>
        <option value="6">Stage 6 — Vampire</option>
        <option value="7">Stage 7 — Gardien du Temps</option>
        <option value="8">Stage 8 — Ombre Venin</option>
        <option value="9">Stage 9 — Pyromancien</option>
        <option value="10">Stage 10 — Paladin</option>
      </select>
    </div>
    <div class="ec-row" id="ec-class-row" style="display:none">
      <label class="ec-label">Classe du boss <span class="ec-hint">(rotation par zone, modifiable)</span></label>
      <select id="ec-boss-class" class="ec-select">
        <option value="">Auto-détecté (rotation par zone)</option>
        <option value="Guerrier">⚔️ Guerrier</option>
        <option value="Assassin">🗡️ Assassin</option>
        <option value="Mage">🔮 Mage</option>
        <option value="Tireur">🏹 Tireur</option>
        <option value="Support">💚 Support</option>
        <option value="Vampire">🧛 Vampire</option>
        <option value="Gardien du Temps">⏳ Gardien du Temps</option>
        <option value="Ombre Venin">☠️ Ombre Venin</option>
        <option value="Pyromancien">🔥 Pyromancien</option>
        <option value="Paladin">🛡️ Paladin</option>
      </select>
    </div>
    <div class="ec-hint-box">
      💡 Les options grisées sont activées automatiquement quand la zone le permet. Zone ×10 → Runique (HP ×1,5) · Zone ×100 → Emblématique (HP ×2) · Zone ×1 000 → Antique (HP ×3)
    </div>
  </div>

  <!-- ── Donjon ─────────────────────────────────────────── -->
  <div id="ec-ctrl-donjon" class="ec-controls" style="display:none">
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

  <!-- ── Raid ───────────────────────────────────────────── -->
  <div id="ec-ctrl-raid" class="ec-controls" style="display:none">
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

  <!-- ── World Boss ─────────────────────────────────────── -->
  <div id="ec-ctrl-wb" class="ec-controls" style="display:none">
    <div class="ec-row">
      <label class="ec-label">Tour personnel <strong id="ec-wb-tour-val">1</strong></label>
      <input type="range" id="ec-wb-tour" class="ec-range" min="1" max="20" value="1" />
      <input type="number" id="ec-wb-tour-input" class="ec-input" min="1" max="20" value="1" style="max-width:120px; margin-top:0.4rem" />
    </div>
    <div class="ec-hint-box">
      🐉 Le World Boss est <strong>Bot Suprême</strong>. Ses stats suivent une zone équivalente = 1 000 × 1,3<sup>tour−1</sup> (Tour 1 = Zone 1 000 · Tour 10 ≈ Zone 13 786 · Tour 20 ≈ Zone 190 050). <strong>Tour 20 maximum</strong> — en cas de défaite, le tour repart à 1.
    </div>
  </div>

  <!-- ── Résultat ───────────────────────────────────────── -->
  <div id="ec-result" style="display:none"></div>

</div>

---

## Comment lire les stats

| Stat marquée ★ | Signification |
|----------------|---------------|
| **★ sur une stat** | Statistique spécialement boostée ×diff (×1,2 / ×1,4 / ×1,6) selon la difficulté |

!!! info "Précision"
    Les noms d'ennemis normaux, runiques et de boss classiques varient aléatoirement en jeu. Pour les boss emblématiques et antiques, la **classe suit une rotation déterministe** par zone (Zone 100 = Guerrier, Zone 200 = Assassin…). Tu peux sélectionner une classe différente pour simuler un cas particulier.
