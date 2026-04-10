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

## Mode Farm

Après avoir battu un boss, un bouton **Farm** apparaît pour refaire le même combat à coût réduit.

| Paramètre | Mode normal | Mode Farm |
|-----------|:-----------:|:---------:|
| Coût | 10–100 ⚡ (selon le tier) | 1 ⚡ |
| XP & or | 100% | 50% |
| Loot | 100% | 50% |

!!! info "Disponible sur tous les boss"
    Le mode Farm est disponible sur les Boss de zone, Runiques, Emblématiques et Antiques — pas sur les ennemis normaux.

---

## Passifs des boss

Chaque boss a un passif thématique qui dépend de sa **classe**. Plus le tier du boss est élevé, plus le passif est puissant.

=== "🔮 Boss Runiques"

    | Classe du boss | Passif | Effet |
    |----------------|--------|-------|
    | ⚔️ Guerrier | Furie Mineure | +3% dégâts par tranche de 25% HP perdus (max +12%) |
    | 🗡️ Assassin | Réflexes | 5% de chance d'esquiver une attaque physique |
    | 🔮 Mage | Résonance Arcanique | Ignore 8% de ta Déf. Mag. |
    | 🏹 Tireur | Visée Précise | +8% chance de critique |
    | 💚 Support | Régénération | Récupère 0.5% HP max au début de chaque tour |
    | 🧛 Vampire | Siphon Mineur | Récupère 5% des dégâts infligés en HP |
    | ⏳ Gardien du Temps | Distorsion Légère | Ta vitesse réduite de 5% |
    | ☠️ Ombre Venin | Glandes Actives | 10% de chance de poison additionnel à chaque attaque |
    | 🔥 Pyromancien | Braises | 20% de chance d'appliquer 1 stack de brûlure à chaque attaque |
    | ✝️ Paladin | Résistance | Dégâts reçus réduits de 5% |

=== "🌟 Boss Emblématiques"

    | Classe du boss | Passif | Effet |
    |----------------|--------|-------|
    | ⚔️ Guerrier | Furie Guerrière | +5% dégâts par tranche de 25% HP perdus (max +20%) |
    | 🗡️ Assassin | Instinct | 10% de chance d'esquiver une attaque physique |
    | 🔮 Mage | Voile Arcanique | Ignore 12% de ta Déf. Mag. |
    | 🏹 Tireur | Œil Affûté | +12% chance de critique |
    | 💚 Support | Régénération Active | Récupère 1% HP max au début de chaque tour |
    | 🧛 Vampire | Siphon de Vie | Récupère 8% des dégâts infligés |
    | ⏳ Gardien du Temps | Ralentissement | Ta vitesse réduite de 10% |
    | ☠️ Ombre Venin | Venin Persistant | 15% de chance de poison additionnel à chaque attaque |
    | 🔥 Pyromancien | Embrasement | 30% de chance d'appliquer 1 stack de brûlure à chaque attaque |
    | ✝️ Paladin | Aura Défensive | Dégâts reçus réduits de 8% |

=== "⚠️ Boss Antiques (zone 1 000)"

    | Classe du boss | Passif | Effet |
    |----------------|--------|-------|
    | ⚔️ Vrethax | Rage Ancienne | +8% dégâts par tranche de 25% HP perdus (max +32%) + immunité aux stuns |
    | 🗡️ Azkoth | Ombre Persistante | 15% de chance d'esquiver + ses critiques ignorent 15% de ta Déf. Phy. |
    | 🔮 Solarius | Annihilation Partielle | Ignore 20% de ta Déf. Mag. + dégâts purs 10% HP max tous les 5 tours |
    | 🏹 Mortifax | Salve Précise | +18% chance de critique + tes défenses physiques −10% |
    | 💚 Chronaxis | Bastion | Récupère 1.5% HP max/tour + dégâts reçus −10% |
    | 🧛 Nexuvor | Avidité Sanguine | Récupère 12% des dégâts infligés + te vole 1% HP max/tour |
    | ⏳ Erebos | Distorsion Temporelle | Ta vitesse −15%, sa vitesse +15% |
    | ☠️ Pantheos | Nuée Venimeuse | 20% de chance de poison additionnel + dégâts DoT ×1.2 |
    | 🔥 Ultharak | Combustion | 40% de chance d'appliquer 1 stack de brûlure + dégâts brûlure ×1.2 |
    | ✝️ Omegaris | Jugement | Dégâts reçus −12% + dégâts purs 8% HP max tous les 5 tours |

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
