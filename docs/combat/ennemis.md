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
        <option value="boss">⚔️ Boss (type auto-détecté selon la zone)</option>
        <option value="1">Stage 1</option>
        <option value="2">Stage 2</option>
        <option value="3">Stage 3</option>
        <option value="4">Stage 4</option>
        <option value="5">Stage 5</option>
        <option value="6">Stage 6</option>
        <option value="7">Stage 7</option>
        <option value="8">Stage 8</option>
        <option value="9">Stage 9</option>
        <option value="10">Stage 10</option>
      </select>
    </div>
    <div class="ec-row" id="ec-class-row" style="display:none">
      <label class="ec-label">Classe du boss <span class="ec-hint">(aléatoire en jeu)</span></label>
      <select id="ec-boss-class" class="ec-select">
        <option value="">Moyenne toutes classes</option>
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
      💡 <strong>Zones spéciales :</strong> Zone multiple de 100 → Boss Emblématique · Zone multiple de 1 000 → Boss Antique · Zone 10 000 → Boss Final
    </div>
  </div>

  <!-- ── Donjon ─────────────────────────────────────────── -->
  <div id="ec-ctrl-donjon" class="ec-controls" style="display:none">
    <div class="ec-row">
      <label class="ec-label">Boss</label>
      <select id="ec-donjon-boss" class="ec-select">
        <option value="d_hp">❤️ Colosse Indestructible</option>
        <option value="d_patk">⚔️ Berserker Frénétique</option>
        <option value="d_matk">🔮 Archimage Déchaîné</option>
        <option value="d_pdef">🛡️ Gardien Impénétrable</option>
        <option value="d_mdef">✨ Sanctuaire Vivant</option>
        <option value="d_speed">⚡ Spectre Fulgurant</option>
        <option value="d_ppen">🗡️ Déchireur de Plaques</option>
        <option value="d_mpen">💫 Brise-Barrière Arcanique</option>
        <option value="d_crit">🎯 Prédateur Précis</option>
        <option value="d_critdmg">💀 Exécuteur Absolu</option>
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
        <option value="raid_1">🐉 Raid 1 — Ancêtre Vorgath (Niv. 100)</option>
        <option value="raid_2">🐍 Raid 2 — Tiamorph l'Hydre (Niv. 200)</option>
        <option value="raid_3">⚡ Raid 3 — Zyrex l'Électriseur (Niv. 300)</option>
        <option value="raid_4">🪨 Raid 4 — Gorthax le Fossilisé (Niv. 400)</option>
        <option value="raid_5">🕷️ Raid 5 — Nexara la Tisseuse (Niv. 500)</option>
        <option value="raid_6">🔥 Raid 6 — Embrasys le Phénix (Niv. 600)</option>
        <option value="raid_7">⏳ Raid 7 — Chronovex l'Invariant (Niv. 700)</option>
        <option value="raid_8">☀️ Raid 8 — Luxara la Sainte (Niv. 800)</option>
        <option value="raid_9">🧛 Raid 9 — Mortemis le Vampirique (Niv. 900)</option>
        <option value="raid_10">🌑 Raid 10 — Omnifax l'Absolu (Niv. 1000)</option>
      </select>
    </div>
    <div class="ec-hint-box">
      👥 Les stats de raid sont calculées en moyenne sur toutes les classes, avec HP ×15 pour un combat d'équipe.
    </div>
  </div>

  <!-- ── World Boss ─────────────────────────────────────── -->
  <div id="ec-ctrl-wb" class="ec-controls" style="display:none">
    <div class="ec-row">
      <label class="ec-label">Tour personnel <strong id="ec-wb-tour-val">1</strong></label>
      <input type="range" id="ec-wb-tour" class="ec-range" min="1" max="50" value="1" />
      <input type="number" id="ec-wb-tour-input" class="ec-input" min="1" max="9999" value="1" style="max-width:120px; margin-top:0.4rem" />
    </div>
    <div class="ec-hint-box">
      🐉 Le World Boss est <strong>Bot Suprême</strong>. Ses stats augmentent à chaque tour survivé (Tour 1 = Zone 1 000, Tour 10 = Zone 10 000…). En cas de défaite, ton tour repart à 1. Il n'y a pas de maximum.
    </div>
  </div>

  <!-- ── Résultat ───────────────────────────────────────── -->
  <div id="ec-result" style="display:none"></div>

</div>

---

## Comment lire les stats

| Stat marquée ★ | Signification |
|----------------|---------------|
| **★ sur une stat** | Statistique spécialement boostée ×10 par ce boss de donjon |

!!! info "Précision"
    Les noms d'ennemis normaux et de boss classiques varient aléatoirement en jeu. Pour les boss emblématiques et antiques, la **classe est tirée aléatoirement** — la moyenne de toutes les classes est affichée par défaut, mais tu peux sélectionner une classe spécifique pour voir le pire/meilleur cas.
