/* ============================================================
   Simulateur d'Ennemis — Bot Suprême Wiki
   Reproduit fidèlement la logique de enemies.py + models.py
   ============================================================ */
(function () {
  'use strict';

  // ─── Données statiques ─────────────────────────────────────────────────────

  var ALL_CLASSES = [
    'Guerrier','Assassin','Mage','Tireur','Support',
    'Vampire','Gardien du Temps','Ombre Venin','Pyromancien','Paladin'
  ];

  var CLASS_EMOJI = {
    'Guerrier':'⚔️','Assassin':'🗡️','Mage':'🔮','Tireur':'🏹','Support':'💚',
    'Vampire':'🧛','Gardien du Temps':'⏳','Ombre Venin':'☠️','Pyromancien':'🔥',
    'Paladin':'🛡️','Titan':'🤖'
  };

  // Zone themes — rotation tous les 100 zones : ((zone-1)//100) % 10
  var ZONE_THEMES = [
    ['Plaine Verdoyante','🌿'],['Forêt Ombreuse','🌲'],['Marais Pestilentiel','🌫️'],
    ['Désert Ardent','🏜️'],['Toundra Glacée','❄️'],['Volcans Ardents','🌋'],
    ['Cités en Ruines','🏚️'],['Abysses Marines','🌊'],['Nécropole Maudite','💀'],
    ['Royaume Céleste','☁️']
  ];

  var ENEMY_FIRST = {
    'Guerrier':'Berserker','Assassin':'Rôdeur','Mage':'Sorcier','Tireur':'Archer Maudit',
    'Support':'Chaman Vénéneux','Vampire':'Vampire Ancien','Gardien du Temps':'Chronomancien',
    'Ombre Venin':'Araignée Toxique','Pyromancien':'Élémentaire de Feu','Paladin':'Croisé Déchu'
  };

  var EMBLEMATIC_NAMES = [
    "Malachar l'Éternel","Zephyros le Tempétueux","Mordreth la Dévoreuse",
    "Xanathos l'Omniscient","Valdris l'Implacable","Sylvara la Tisseuse",
    "Grudnak le Colossal","Elysia la Corrompue","Tharax le Venimeux",
    "Drakonus le Chromate","Abyssion le Profond","Ignaris le Volcanique",
    "Glacialis le Glaçant","Umbrath l'Ombral","Pyrion l'Incandescent",
    "Temporis le Figé","Necrosis la Putride","Aetherion l'Astral",
    "Tenebris le Ténébreux","Primordius l'Ancestral"
  ];

  var ANTIQUE_NAMES = [
    "Vrethax le Primordial","Azkoth la Conscience Noire","Solarius le Dévoreur d'Étoiles",
    "Mortifax l'Impérissable","Chronaxis le Maître Absolu","Nexuvor l'Indicible",
    "Erebos la Nuit Éternelle","Pantheos le Dieu-Bête","Ultharak l'Abomination",
    "Omegaris la Fin du Monde"
  ];

  // ─── BASE_STATS — models.py ────────────────────────────────────────────────
  var BASE_STATS = {
    'Guerrier':         {hp:550,  p_atk:52,  m_atk:0,   p_pen:8,  m_pen:0,  p_def:32, m_def:6,  speed:80,  crit_chance:5.0,  crit_damage:50.0},
    'Assassin':         {hp:500,  p_atk:50,  m_atk:0,   p_pen:10, m_pen:0,  p_def:4,  m_def:3,  speed:105, crit_chance:18.0, crit_damage:75.0},
    'Mage':             {hp:420,  p_atk:0,   m_atk:42,  p_pen:0,  m_pen:8,  p_def:3,  m_def:10, speed:92,  crit_chance:12.0, crit_damage:75.0},
    'Tireur':           {hp:440,  p_atk:44,  m_atk:0,   p_pen:8,  m_pen:0,  p_def:4,  m_def:4,  speed:105, crit_chance:16.0, crit_damage:75.0},
    'Support':          {hp:650,  p_atk:48,  m_atk:48,  p_pen:6,  m_pen:6,  p_def:25, m_def:25, speed:80,  crit_chance:5.0,  crit_damage:40.0},
    'Vampire':          {hp:580,  p_atk:60,  m_atk:0,   p_pen:9,  m_pen:0,  p_def:12, m_def:7,  speed:90,  crit_chance:15.0, crit_damage:75.0},
    'Gardien du Temps': {hp:480,  p_atk:35,  m_atk:35,  p_pen:6,  m_pen:6,  p_def:18, m_def:18, speed:95,  crit_chance:8.0,  crit_damage:55.0},
    'Ombre Venin':      {hp:460,  p_atk:32,  m_atk:32,  p_pen:5,  m_pen:5,  p_def:5,  m_def:5,  speed:115, crit_chance:17.0, crit_damage:70.0},
    'Pyromancien':      {hp:500,  p_atk:0,   m_atk:58,  p_pen:0,  m_pen:9,  p_def:2,  m_def:10, speed:85,  crit_chance:13.0, crit_damage:75.0},
    'Paladin':          {hp:560,  p_atk:42,  m_atk:0,   p_pen:8,  m_pen:0,  p_def:35, m_def:22, speed:72,  crit_chance:5.0,  crit_damage:50.0}
  };

  // ─── LEVEL_GROWTH — models.py ─────────────────────────────────────────────
  var LEVEL_GROWTH = {
    'Guerrier':         {hp:45.44, p_atk:2.400, m_atk:0.0,   p_pen:0.0,   m_pen:0.0,   p_def:0.822, m_def:0.194, speed:0.230, crit_chance:0.0, crit_damage:0.0},
    'Support':          {hp:72.42, p_atk:1.283, m_atk:1.283, p_pen:0.0,   m_pen:0.0,   p_def:0.630, m_def:0.630, speed:0.195, crit_chance:0.0, crit_damage:0.0},
    'Paladin':          {hp:71.51, p_atk:2.361, m_atk:0.0,   p_pen:0.0,   m_pen:0.0,   p_def:0.916, m_def:0.428, speed:0.193, crit_chance:0.0, crit_damage:0.0},
    'Assassin':         {hp:36.54, p_atk:2.643, m_atk:0.0,   p_pen:0.549, m_pen:0.0,   p_def:0.0,   m_def:0.0,   speed:0.365, crit_chance:0.0, crit_damage:0.0},
    'Tireur':           {hp:37.60, p_atk:2.668, m_atk:0.0,   p_pen:0.555, m_pen:0.0,   p_def:0.0,   m_def:0.0,   speed:0.360, crit_chance:0.0, crit_damage:0.0},
    'Mage':             {hp:39.64, p_atk:0.0,   m_atk:2.814, p_pen:0.0,   m_pen:0.553, p_def:0.0,   m_def:0.0,   speed:0.405, crit_chance:0.0, crit_damage:0.0},
    'Pyromancien':      {hp:43.64, p_atk:0.0,   m_atk:3.100, p_pen:0.0,   m_pen:0.610, p_def:0.0,   m_def:0.0,   speed:0.395, crit_chance:0.0, crit_damage:0.0},
    'Ombre Venin':      {hp:45.65, p_atk:1.540, m_atk:1.540, p_pen:0.300, m_pen:0.300, p_def:0.0,   m_def:0.0,   speed:0.345, crit_chance:0.0, crit_damage:0.0},
    'Vampire':          {hp:50.00, p_atk:2.638, m_atk:0.0,   p_pen:0.528, m_pen:0.0,   p_def:0.268, m_def:0.193, speed:0.245, crit_chance:0.0, crit_damage:0.0},
    'Gardien du Temps': {hp:41.56, p_atk:1.400, m_atk:1.400, p_pen:0.304, m_pen:0.304, p_def:0.362, m_def:0.362, speed:0.240, crit_chance:0.0, crit_damage:0.0}
  };

  var STAT_KEYS = ['hp','p_atk','m_atk','p_pen','m_pen','p_def','m_def','speed','crit_chance','crit_damage'];

  // ─── Passifs boss — enemies.py ────────────────────────────────────────────

  var RUNIC_PASSIFS = {
    'Guerrier':         "Furie Mineure : +3% dégâts par tranche de 25% HP perdus (max +12%)",
    'Assassin':         "Réflexes : 5% de chance d'esquiver une attaque physique",
    'Mage':             "Résonance Arcanique : ignore 8% de ta Déf. Mag.",
    'Tireur':           "Visée Précise : +8% chance de critique",
    'Support':          "Régénération : récupère 0,5% HP max au début de chaque tour",
    'Vampire':          "Siphon Mineur : récupère 5% des dégâts infligés en HP",
    'Gardien du Temps': "Distorsion Légère : ta vitesse réduite de 5%",
    'Ombre Venin':      "Glandes Actives : 10% de chance de poison additionnel à chaque attaque",
    'Pyromancien':      "Braises : 20% de chance d'appliquer 1 stack de brûlure à chaque attaque",
    'Paladin':          "Résistance : dégâts reçus réduits de 5%"
  };

  var EMBLEMATIC_PASSIFS = {
    'Guerrier':         "Furie Guerrière : +5% dégâts par tranche de 25% HP perdus (max +20%)",
    'Assassin':         "Instinct : 10% de chance d'esquiver une attaque physique",
    'Mage':             "Voile Arcanique : ignore 12% de ta Déf. Mag.",
    'Tireur':           "Œil Affûté : +12% chance de critique",
    'Support':          "Régénération Active : récupère 1% HP max/tour",
    'Vampire':          "Siphon de Vie : récupère 8% des dégâts infligés",
    'Gardien du Temps': "Ralentissement : ta vitesse réduite de 10%",
    'Ombre Venin':      "Venin Persistant : 15% de chance de poison additionnel à chaque attaque",
    'Pyromancien':      "Embrasement : 30% de chance d'appliquer 1 stack de brûlure à chaque attaque",
    'Paladin':          "Aura Défensive : dégâts reçus réduits de 8%"
  };

  var ANTIQUE_PASSIFS = {
    'Guerrier':         "Rage Ancienne : +8% dégâts par 25% HP perdus (max +32%) + immunité aux stuns",
    'Assassin':         "Ombre Persistante : 15% esquive + ses critiques ignorent 15% de ta Déf. Phy.",
    'Mage':             "Annihilation Partielle : ignore 20% de ta Déf. Mag. + tous les 5 tours : dégâts purs 10% HP max",
    'Tireur':           "Salve Précise : +18% chance de critique + tes défenses physiques -10%",
    'Support':          "Bastion : récupère 1,5% HP max/tour + dégâts reçus -10%",
    'Vampire':          "Avidité Sanguine : récupère 12% des dégâts infligés + te vole 1% HP max/tour",
    'Gardien du Temps': "Distorsion Temporelle : ta vitesse -15%, sa vitesse +15%",
    'Ombre Venin':      "Nuée Venimeuse : 20% de chance de poison additionnel + dégâts DoT ×1,2",
    'Pyromancien':      "Combustion : 40% de chance d'appliquer 1 stack de brûlure + dégâts brûlure ×1,2",
    'Paladin':          "Jugement : dégâts reçus -12% + tous les 5 tours : dégâts purs 8% HP max"
  };

  // ─── Donjons — enemies.py DUNGEON_BOSSES ──────────────────────────────────
  var DUNGEON_BOSSES = [
    {id:'d_casque',     slot:'casque',     name:'Gardien des Crânes',  emoji:'🪖', stat_boost:'p_def',       passif:'Armure Solide : réduit tous les dégâts reçus de 12%.'},
    {id:'d_plastron',   slot:'plastron',   name:'Titan Cuirassé',       emoji:'🛡️', stat_boost:'hp',          passif:'Endurance Absolue : récupère 3% de ses HP max au début de chaque tour.'},
    {id:'d_pantalon',   slot:'pantalon',   name:'Danseur de Guerre',    emoji:'🌪️', stat_boost:'speed',       passif:"Esquive Naturelle : 10% de chance d'éviter complètement une attaque."},
    {id:'d_chaussures', slot:'chaussures', name:'Spectre Fulgurant',    emoji:'⚡', stat_boost:'speed',       passif:"Foulée Redoublée : 20% de chance d'attaquer deux fois lors de son tour."},
    {id:'d_arme',       slot:'arme',       name:'Lame Dévastatrice',    emoji:'⚔️', stat_boost:'p_atk',       passif:'Tranchant Absolu : ignore 20% de ta Défense Physique et 20% de ta Défense Magique.'},
    {id:'d_amulette',   slot:'amulette',   name:'Mystique Absolu',      emoji:'📿', stat_boost:'m_atk',       passif:'Renvoi Mystique : renvoie 8% des dégâts reçus sous forme de dégâts purs (avant défense).'},
    {id:'d_anneau',     slot:'anneau',     name:'Catalyseur Éternel',   emoji:'💍', stat_boost:'crit_chance', passif:'Empowerment Runique : gagne +2,5% dégâts par tour (cumulé, max 10 stacks, +25% au maximum).'}
  ];

  // ─── Raids — enemies.py RAID_BOSSES ───────────────────────────────────────
  var RAID_BOSSES_DATA = [
    {id:'raid_1',  name:"Vorgath l'Implacable",    emoji:'🐉', raid_level:1,  level_req:100,  cls:'Guerrier'},
    {id:'raid_2',  name:"Shivra l'Ombre Mortelle", emoji:'🗡️', raid_level:2,  level_req:200,  cls:'Assassin'},
    {id:'raid_3',  name:"Zyrex l'Archmage",        emoji:'⚡', raid_level:3,  level_req:300,  cls:'Mage'},
    {id:'raid_4',  name:"Karek le Chasseur",        emoji:'🏹', raid_level:4,  level_req:400,  cls:'Tireur'},
    {id:'raid_5',  name:"Serath le Corrupteur",     emoji:'🕸️', raid_level:5,  level_req:500,  cls:'Support'},
    {id:'raid_6',  name:"Mordas le Sans-Âme",       emoji:'🧛', raid_level:6,  level_req:600,  cls:'Vampire'},
    {id:'raid_7',  name:"Chronovex l'Invariant",    emoji:'⏳', raid_level:7,  level_req:700,  cls:'Gardien du Temps'},
    {id:'raid_8',  name:"Nyxara la Corrompue",      emoji:'🐍', raid_level:8,  level_req:800,  cls:'Ombre Venin'},
    {id:'raid_9',  name:"Ignareth le Phénix",       emoji:'🔥', raid_level:9,  level_req:900,  cls:'Pyromancien'},
    {id:'raid_10', name:"Omnifax le Divin",          emoji:'🌑', raid_level:10, level_req:1000, cls:'Paladin'}
  ];

  // ─── Formule de calcul — enemies.py compute_enemy_stats ──────────────────
  // monde_scaling: pct = 0.50 + 9.50 × (level - 1) / 999
  // pct_override : valeur fixe (donjons, raids, world boss)

  function computeEnemyStats(level, cls, pctOverride) {
    level = Math.max(1, level);
    var pct = (pctOverride !== undefined && pctOverride !== null)
      ? pctOverride
      : 0.50 + 9.50 * (level - 1) / 999;
    var resolved = BASE_STATS[cls] ? cls : 'Guerrier';
    var base   = BASE_STATS[resolved];
    var growth = LEVEL_GROWTH[resolved] || LEVEL_GROWTH['Guerrier'];
    var stats  = {};
    STAT_KEYS.forEach(function(stat) {
      var playerVal = (base[stat] || 0) + (growth[stat] || 0) * (level - 1);
      if (stat === 'crit_chance' || stat === 'crit_damage') {
        stats[stat] = Math.round(playerVal * pct * 100) / 100;
      } else {
        stats[stat] = Math.floor(playerVal * pct);
      }
    });
    return stats;
  }

  function classForIndex(n) {
    return ALL_CLASSES[((n % 10) + 10) % 10];
  }

  // Zone theme : ((zone-1) // 100) % 10 — rotation tous les 100 zones
  function getTheme(zone) {
    return ZONE_THEMES[Math.floor((zone - 1) / 100) % 10];
  }

  // ── Monde : ennemi de stage ────────────────────────────────────────────────
  // Stage auto-déterminé : ((zone-1) % 10) + 1

  function calcMondeEnemy(zone, stage) {
    zone = Math.max(1, Math.min(1000, zone));
    if (!stage) stage = ((zone - 1) % 10) + 1;
    var cls   = classForIndex(stage - 1);
    var stats = computeEnemyStats(zone, cls);
    var th    = getTheme(zone);
    return {
      name: ENEMY_FIRST[cls] || cls,
      nameNote: 'Le nom exact varie à chaque combat',
      cls: cls, theme: th[0], themeEmoji: th[1],
      typeLabel: 'Stage ' + stage, typeBadge: 'Monde', typeEmoji: '👿',
      passif: null,
      xp:   Math.max(1, Math.floor(zone * 15) + stage),
      gold: Math.max(1, Math.floor(zone * 8)  + stage),
      drops: '10% chance : 1 item (ta classe) · 1% chance : 1 item (autre classe) — Panoplie Monde',
      stats: stats
    };
  }

  // ── Monde : boss de zone ───────────────────────────────────────────────────
  // Classe : _class_by_index(zone - 1) → rotation par zone
  // HP × 1.2

  function calcMondeBossClassique(zone) {
    zone = Math.max(1, Math.min(1000, zone));
    var cls   = classForIndex(zone - 1);
    var stats = computeEnemyStats(zone, cls);
    stats.hp  = Math.floor(stats.hp * 1.2);
    var th    = getTheme(zone);
    return {
      name: '[Préfixe aléatoire] ' + (ENEMY_FIRST[cls] || cls),
      nameNote: 'Le nom exact varie à chaque combat',
      cls: cls, theme: th[0], themeEmoji: th[1],
      typeLabel: 'Boss de Zone', typeBadge: 'Boss Zone', typeEmoji: '⚔️',
      passif: null,
      xp:   Math.max(3,  Math.floor(zone * 18)),
      gold: Math.max(2,  Math.floor(zone * 10)),
      drops: '50% chance : 1 item (ta classe) · 10% chance : 1 item (autre classe) — Panoplie Monde',
      stats: stats
    };
  }

  // ── Monde : boss runique (zones ×10, sauf ×100) ───────────────────────────
  // Classe : _class_by_index(zone // 10 - 1)
  // HP × 1.4

  function calcRunicBoss(zone) {
    zone = Math.max(1, Math.min(1000, zone));
    var cls   = classForIndex(Math.floor(zone / 10) - 1);
    var stats = computeEnemyStats(zone, cls);
    stats.hp  = Math.floor(stats.hp * 1.4);
    var th    = getTheme(zone);
    return {
      name: '[Préfixe aléatoire] ' + (ENEMY_FIRST[cls] || cls),
      nameNote: 'Le nom exact varie à chaque combat',
      cls: cls, theme: th[0], themeEmoji: '🔮',
      typeLabel: 'Boss Runique', typeBadge: 'Runique', typeEmoji: '🔮',
      passif: RUNIC_PASSIFS[cls] || null,
      xp:   Math.max(5,  Math.floor(zone * 23)),
      gold: Math.max(3,  Math.floor(zone * 12)),
      drops: '50% chance : 1 item (ta classe) · 10% chance : 1 item (autre classe) — Panoplie Monde',
      stats: stats
    };
  }

  // ── Monde : boss emblématique (zones ×100, sauf ×1000) ────────────────────
  // idx = zone // 100 - 1 → classe et nom
  // HP × 1.6

  function calcEmblematique(zone) {
    zone = Math.max(1, Math.min(1000, zone));
    var idx  = Math.floor(zone / 100) - 1;
    var cls  = classForIndex(idx);
    var stats = computeEnemyStats(zone, cls);
    stats.hp  = Math.floor(stats.hp * 1.6);
    return {
      name: EMBLEMATIC_NAMES[((idx % 20) + 20) % 20],
      nameNote: null,
      cls: cls, theme: 'Boss Emblématique', themeEmoji: '🌟',
      typeLabel: 'Boss Emblématique', typeBadge: 'Emblématique', typeEmoji: '🌟',
      passif: EMBLEMATIC_PASSIFS[cls] || null,
      xp:   Math.max(50,  Math.floor(zone * 30)),
      gold: Math.max(30,  Math.floor(zone * 16)),
      drops: '100% : 1 item (ta classe) + 50% : 1 item (autre classe) — Panoplie Monde',
      stats: stats
    };
  }

  // ── Monde : boss antique (zone 1000, idx 0-9 selon classe) ────────────────
  // idx déterminé par la classe choisie
  // HP × 1.8

  function calcAntique(cls) {
    var zone = 1000;
    var idx  = ALL_CLASSES.indexOf(cls);
    if (idx < 0) idx = 0;
    var stats = computeEnemyStats(zone, cls);
    stats.hp  = Math.floor(stats.hp * 1.8);
    return {
      name: ANTIQUE_NAMES[idx],
      nameNote: null,
      cls: cls, theme: 'Boss Antique', themeEmoji: '⚠️',
      typeLabel: 'Boss Antique — Zone 1 000', typeBadge: 'Antique', typeEmoji: '⚠️',
      passif: ANTIQUE_PASSIFS[cls] || null,
      xp:   Math.max(200, Math.floor(zone * 45)),
      gold: Math.max(100, Math.floor(zone * 24)),
      drops: '3 items garantis (ta classe) + 1 item (autre classe) — Panoplie Monde',
      stats: stats
    };
  }

  // ─── Donjon — enemies.py generate_dungeon_boss ────────────────────────────
  // player_level = zone_equiv = (tier_offset + level) × 3
  // pct linéaire : classique 1.0→4.0, elite 5.0→9.0, abyssal 10.0→14.0
  // stat_boost × 1.15
  // zone_equiv = (tier_offset + level) × 3 : classique=0, elite=100, abyssal=200

  function calcDonjon(bossId, difficulty, level) {
    var boss = DUNGEON_BOSSES.filter(function(b){ return b.id === bossId; })[0] || DUNGEON_BOSSES[0];
    var tierOffset = {classique:0, elite:100, abyssal:200}[difficulty] || 0;
    var zoneEquiv  = (tierOffset + level) * 3;
    var playerLevel = zoneEquiv;
    var pctMin = {classique:1.0, elite:5.0, abyssal:10.0}[difficulty] || 1.0;
    var pctMax = {classique:4.0, elite:9.0, abyssal:14.0}[difficulty] || 4.0;
    var pct    = pctMin + (pctMax - pctMin) * (level - 1) / 99;
    var cls    = classForIndex(level - 1);
    var rewardMult = {classique:2, elite:3, abyssal:5}[difficulty] || 2;
    var diffLabel  = {classique:'Classique', elite:'Élite', abyssal:'Abyssal'}[difficulty] || difficulty;

    var stats = computeEnemyStats(playerLevel, cls, pct);

    // Boost stat signature × 1.15
    var sb = boss.stat_boost;
    if (sb && stats[sb] !== undefined) {
      if (sb === 'crit_chance' || sb === 'crit_damage') {
        stats[sb] = Math.round(stats[sb] * 1.15 * 100) / 100;
      } else {
        stats[sb] = Math.floor(stats[sb] * 1.15);
      }
    }

    return {
      name: boss.name, nameNote: null,
      cls: cls,
      theme: 'Donjon ' + diffLabel + ' Niv.' + level, themeEmoji: boss.emoji,
      typeLabel: 'Donjon ' + diffLabel + ' — Niv.' + level,
      typeBadge: 'Donjon ' + diffLabel, typeEmoji: boss.emoji,
      passif: boss.passif, boostStat: boss.stat_boost,
      xp:   Math.max(1, Math.floor(zoneEquiv * 15 * rewardMult)),
      gold: Math.max(1, Math.floor(zoneEquiv * 8  * rewardMult)),
      drops: '1 équipement garanti (slot : ' + boss.emoji + ' ' + boss.name + ') — Panoplie Donjon ' + diffLabel,
      stats: stats
    };
  }

  // ─── Raid — enemies.py generate_raid_boss ─────────────────────────────────
  // player_level = raid_level × 100
  // pct = 1.0 + raid_level × 1.5 (raid1=2.5 → raid10=16.0)
  // HP × 3
  // zone_equiv = raid_level × 100

  function calcRaid(raidId) {
    var boss = RAID_BOSSES_DATA.filter(function(b){ return b.id === raidId; })[0] || RAID_BOSSES_DATA[0];
    var rl    = boss.raid_level;
    var playerLevel = rl * 100;
    var pct   = 1.0 + rl * 1.5;
    var zoneEquiv = rl * 100;

    var stats = computeEnemyStats(playerLevel, boss.cls, pct);
    stats.hp  = Math.floor(stats.hp * 3);

    return {
      name: boss.name, nameNote: null,
      cls: boss.cls, theme: 'Raid', themeEmoji: boss.emoji,
      typeLabel: 'Raid ' + rl + ' — Niveau requis : ' + boss.level_req,
      typeBadge: 'Raid ' + rl, typeEmoji: boss.emoji,
      passif: null, req: boss.level_req,
      xp:   Math.floor(zoneEquiv * 150),
      gold: Math.floor(zoneEquiv * 50),
      drops: '7 items garantis (1 par slot) — classe aléatoire — Panoplie Raid Niv. ' + rl,
      stats: stats
    };
  }

  // ─── World Boss ─────────────────────────────────────────────────────────────
  // Tour T : pct = T × 0.8 (tour 1 → ×0.8, tour 25 → ×20.0), level = T × 100
  // Vitesse verrouillée à 100

  function computeEnemyStatsAvg(level, pct) {
    var r = {};
    STAT_KEYS.forEach(function(k) {
      var sum = ALL_CLASSES.reduce(function(s, c) {
        return s + (computeEnemyStats(level, c, pct)[k] || 0);
      }, 0);
      if (k === 'crit_chance' || k === 'crit_damage') {
        r[k] = Math.round(sum / ALL_CLASSES.length * 100) / 100;
      } else {
        r[k] = Math.floor(sum / ALL_CLASSES.length);
      }
    });
    return r;
  }

  function calcWorldBoss(tour) {
    tour = Math.max(1, Math.min(25, tour));
    var level = tour * 100;
    var pct   = tour * 0.8;
    var stats = computeEnemyStatsAvg(level, pct);
    stats.speed = 100; // vitesse verrouillée
    delete stats.hp;   // HP collectifs hebdomadaires (non affichés ici)
    var zoneEquiv = level;
    return {
      name: 'Bot Suprême', nameNote: null,
      cls: 'Titan', theme: 'World Boss', themeEmoji: '🤖',
      typeLabel: 'Tour WB #' + tour + ' — Niveau équivalent : ' + fmt(level),
      typeBadge: 'World Boss T' + tour, typeEmoji: '🤖',
      passif: "Montée en puissance : Augmente ses stats à chaque tour.<br>Vitesse verrouillée à 100.<br>Max 25 tours.",
      xp:   Math.floor(zoneEquiv * 500),
      gold: Math.floor(zoneEquiv * 200),
      drops: 'Voir <a href="../objets/reliques/">Reliques</a>',
      stats: stats
    };
  }

  // ─── Matériaux ────────────────────────────────────────────────────────────

  var MATERIALS_DATA = [
    {prof:'mineur',     tier:1,  name:'Minerai de Fer',        emoji:'🪨'},
    {prof:'mineur',     tier:2,  name:"Minerai d'Acier",       emoji:'⛏️'},
    {prof:'mineur',     tier:3,  name:'Minerai de Mithril',    emoji:'💎'},
    {prof:'mineur',     tier:4,  name:'Adamantium Brut',       emoji:'🔷'},
    {prof:'mineur',     tier:5,  name:'Pierre de Feu',         emoji:'🔥'},
    {prof:'mineur',     tier:6,  name:'Pierre de Glace',       emoji:'❄️'},
    {prof:'mineur',     tier:7,  name:'Orichalque',            emoji:'🟠'},
    {prof:'mineur',     tier:8,  name:'Pierre de Foudre',      emoji:'⚡'},
    {prof:'mineur',     tier:9,  name:'Cristal Brut',          emoji:'🔮'},
    {prof:'mineur',     tier:10, name:'Diamant Brut',          emoji:'💠'},
    {prof:'bucheron',   tier:1,  name:'Bois de Chêne',         emoji:'🌳'},
    {prof:'bucheron',   tier:2,  name:'Bois de Sapin',         emoji:'🌲'},
    {prof:'bucheron',   tier:3,  name:"Bois d'Ébène",          emoji:'🪵'},
    {prof:'bucheron',   tier:4,  name:'Bois de Teck',          emoji:'🪵'},
    {prof:'bucheron',   tier:5,  name:'Bois de Cèdre',         emoji:'🪵'},
    {prof:'bucheron',   tier:6,  name:'Bois Enchanté',         emoji:'✨'},
    {prof:'bucheron',   tier:7,  name:'Bois de Sang',          emoji:'🔴'},
    {prof:'bucheron',   tier:8,  name:'Bois de Lune',          emoji:'🌙'},
    {prof:'bucheron',   tier:9,  name:'Bois de Feu',           emoji:'🔥'},
    {prof:'bucheron',   tier:10, name:'Bois de Dragon',        emoji:'🐉'},
    {prof:'herboriste', tier:1,  name:'Herbe de Soin',         emoji:'🌿'},
    {prof:'herboriste', tier:2,  name:'Herbe de Mana',         emoji:'💧'},
    {prof:'herboriste', tier:3,  name:'Racine de Force',       emoji:'🌱'},
    {prof:'herboriste', tier:4,  name:'Fleur de Lune',         emoji:'🌸'},
    {prof:'herboriste', tier:5,  name:'Pollen Doré',           emoji:'🌼'},
    {prof:'herboriste', tier:6,  name:'Champignon Vénéneux',   emoji:'🍄'},
    {prof:'herboriste', tier:7,  name:'Cristal Végétal',       emoji:'🔮'},
    {prof:'herboriste', tier:8,  name:'Mousse Ancienne',       emoji:'🌾'},
    {prof:'herboriste', tier:9,  name:'Épine de Dragon',       emoji:'🌵'},
    {prof:'herboriste', tier:10, name:"Lotus de l'Ombre",      emoji:'🖤'},
    {prof:'chasseur',   tier:1,  name:'Cuir de Loup',          emoji:'🐺'},
    {prof:'chasseur',   tier:2,  name:'Cuir de Cerf',          emoji:'🦌'},
    {prof:'chasseur',   tier:3,  name:'Écailles de Serpent',   emoji:'🐍'},
    {prof:'chasseur',   tier:4,  name:'Plumes de Phénix',      emoji:'🦅'},
    {prof:'chasseur',   tier:5,  name:'Croc de Goule',         emoji:'🦷'},
    {prof:'chasseur',   tier:6,  name:'Griffe de Griffon',     emoji:'🦁'},
    {prof:'chasseur',   tier:7,  name:'Peau de Dragon',        emoji:'🐉'},
    {prof:'chasseur',   tier:8,  name:'Os de Chimère',         emoji:'💀'},
    {prof:'chasseur',   tier:9,  name:'Venin de Basilic',      emoji:'☠️'},
    {prof:'chasseur',   tier:10, name:'Cœur de Bête',          emoji:'❤️'},
    {prof:'fermier',    tier:1,  name:'Blé',                   emoji:'🌾'},
    {prof:'fermier',    tier:2,  name:'Orge',                  emoji:'🌾'},
    {prof:'fermier',    tier:3,  name:'Farine de Maïs',        emoji:'🌽'},
    {prof:'fermier',    tier:4,  name:'Herbes Aromatiques',    emoji:'🌿'},
    {prof:'fermier',    tier:5,  name:'Baies Sauvages',        emoji:'🫐'},
    {prof:'fermier',    tier:6,  name:'Lait de Licorne',       emoji:'🦄'},
    {prof:'fermier',    tier:7,  name:'Miel Enchanté',         emoji:'🍯'},
    {prof:'fermier',    tier:8,  name:'Sel de Mer',            emoji:'🧂'},
    {prof:'fermier',    tier:9,  name:'Épices Rares',          emoji:'🌶️'},
    {prof:'fermier',    tier:10, name:'Fruit du Paradis',      emoji:'🍑'}
  ];

  var PROF_LABELS = {
    mineur:'⛏️ Mineur', bucheron:'🪓 Bûcheron', herboriste:'🌿 Herboriste',
    chasseur:'🏹 Chasseur', fermier:'🌾 Fermier'
  };
  var PROF_ORDER = ['mineur','bucheron','herboriste','chasseur','fermier'];

  // ─── Affichage ───────────────────────────────────────────────────────────

  function fmt(n) {
    return Math.floor(n).toLocaleString('fr-FR');
  }

  var STAT_ORDER  = ['hp','p_atk','m_atk','p_def','m_def','p_pen','m_pen','speed','crit_chance','crit_damage'];
  var STAT_LABELS = {
    hp:'Points de Vie', p_atk:'Att. Physique', m_atk:'Att. Magique',
    p_def:'Déf. Physique', m_def:'Déf. Magique', p_pen:'Pén. Physique',
    m_pen:'Pén. Magique', speed:'Vitesse', crit_chance:'Critique', crit_damage:'Dég. Critique'
  };
  var STAT_EMOJIS = {
    hp:'❤️', p_atk:'⚔️', m_atk:'🔮', p_def:'🛡️', m_def:'🔷',
    p_pen:'🗡️', m_pen:'💫', speed:'⚡', crit_chance:'🎯', crit_damage:'💥'
  };

  function fmtChance(eff) {
    if (eff >= 100) {
      var g = Math.floor(eff / 100);
      var r = Math.round((eff % 100) * 10) / 10;
      return g + '× garanti' + (r > 0 ? ' +' + r + '%' : '');
    }
    return Math.round(eff * 10) / 10 + '%';
  }

  function renderMaterialDrops(zone, matMult) {
    matMult = matMult || 1;
    var zoneMult  = Math.round((1 + zone / 1000) * 100) / 100;
    var totalMult = Math.round(zoneMult * matMult * 100) / 100;
    var byProf = {};
    PROF_ORDER.forEach(function(p) { byProf[p] = []; });
    MATERIALS_DATA.forEach(function(m) { byProf[m.prof].push(m); });

    var html = '<div class="ec-mat-scroll"><div class="ec-mat-grid">';
    PROF_ORDER.forEach(function(p) {
      html += '<div class="ec-mat-prof"><div class="ec-mat-prof-lbl">' + PROF_LABELS[p] + '</div>';
      byProf[p].forEach(function(m) {
        var base = Math.max(0.25, (26 - m.tier * 2.5) / 2);
        var eff  = base * totalMult;
        html += '<div class="ec-mat-item">' +
          '<span class="ec-mat-emoji">' + m.emoji + '</span>' +
          '<span class="ec-mat-name">T' + m.tier + ' ' + m.name + '</span>' +
          '<span class="ec-mat-chance">' + fmtChance(eff) + '</span>' +
          '</div>';
      });
      html += '</div>';
    });
    html += '</div></div>';
    html += '<div class="ec-mat-note">Taux = ton métier de récolte (×' + totalMult + '). Hors métier : ÷10. Tier verrouillé si niveau de récolte insuffisant.</div>';
    return html;
  }

  var BADGE_COLORS = {
    'Emblématique':'#d97706','Antique':'#dc2626','Runique':'#7c3aed',
    'Boss Zone':'#4b5563'
  };

  function badgeColor(badge) {
    if (BADGE_COLORS[badge]) return BADGE_COLORS[badge];
    if (badge.indexOf('World Boss') === 0) return '#16a34a';
    if (badge.indexOf('Raid')       === 0) return '#2563eb';
    if (badge.indexOf('Donjon')     === 0) return '#0891b2';
    return '#6b7280';
  }

  function renderEnemy(data, resultEl) {
    var s = data.stats;
    var statsHtml = '';
    var isWorldBoss = data.typeBadge && data.typeBadge.indexOf('World Boss') === 0;
    STAT_ORDER.forEach(function(k){
      var v = s[k]; if (v === undefined) return;
      if (k === 'hp' && isWorldBoss) return;
      var valStr    = (k === 'crit_chance' || k === 'crit_damage') ? v + '%' : fmt(v);
      var isBoosted = data.boostStat === k;
      var isHp      = k === 'hp';
      statsHtml +=
        '<div class="ec-stat' + (isHp ? ' ec-stat-hp' : '') + (isBoosted ? ' ec-stat-boosted' : '') + '">' +
        '<span class="ec-stat-icon">'  + STAT_EMOJIS[k]  + '</span>' +
        '<span class="ec-stat-name">'  + STAT_LABELS[k]  + '</span>' +
        '<span class="ec-stat-val">'   + valStr + (isBoosted ? ' ★' : '') + '</span></div>';
    });

    var passifHtml = data.passif
      ? '<div class="ec-passif"><div class="ec-passif-lbl">⚡ Passif</div>' +
        '<div class="ec-passif-txt">' + data.passif + '</div></div>'
      : '';

    var noteHtml = data.nameNote ? '<div class="ec-note">ℹ️ ' + data.nameNote + '</div>' : '';
    var reqHtml  = data.req      ? '<div class="ec-req">🔓 Niveau requis : <strong>' + data.req + '</strong></div>' : '';

    var bc = badgeColor(data.typeBadge);
    resultEl.innerHTML =
      '<div class="ec-header">' +
        '<div class="ec-emoji">'        + data.themeEmoji + '</div>' +
        '<div class="ec-title-block">' +
          '<div class="ec-name">'       + data.name + '</div>' +
          '<div class="ec-meta">'       + (CLASS_EMOJI[data.cls] || '👹') + ' ' + data.cls +
            ' &nbsp;·&nbsp; '           + data.theme + '</div>' + noteHtml +
        '</div>' +
        '<div class="ec-badge" style="background:' + bc + '">' + data.typeBadge + '</div>' +
      '</div>' +
      reqHtml +
      '<div class="ec-stats-grid">' + statsHtml + '</div>' +
      passifHtml +
      '<div class="ec-rewards">' +
        '<span>✨ XP : <strong>'  + fmt(data.xp)   + '</strong></span>' +
        '<span>🪙 Or : <strong>' + fmt(data.gold) + '</strong></span>' +
      '</div>' +
      (data.drops ? '<div class="ec-drops-equip">🎁 <strong>Récompenses</strong> : ' + data.drops + '</div>' : '') +
      (data.matZone ? '<details class="ec-drops-detail"><summary>📦 Matériaux possibles</summary>' +
        renderMaterialDrops(data.matZone, data.matMult) +
        '</details>' : '');

    resultEl.style.display = 'block';
  }

  // ─── Initialisation UI ────────────────────────────────────────────────────

  function setupCalculator(container) {
    var tabs   = container.querySelectorAll('.ec-tab');
    var panels = {
      monde:  container.querySelector('#ec-ctrl-monde'),
      donjon: container.querySelector('#ec-ctrl-donjon'),
      raid:   container.querySelector('#ec-ctrl-raid'),
      wb:     container.querySelector('#ec-ctrl-wb')
    };
    var resultEl = container.querySelector('#ec-result');
    var mode = 'monde';

    function showPanel(m) {
      mode = m;
      Object.keys(panels).forEach(function(k){
        if (panels[k]) panels[k].style.display = k === m ? '' : 'none';
      });
      tabs.forEach(function(t){
        t.className = 'ec-tab' + (t.dataset.mode === m ? ' ec-tab-active' : '');
      });
      refresh();
    }

    function refresh() {
      try {
        var data;
        if (mode === 'monde') {
          var zoneEl    = container.querySelector('#ec-zone');
          var stageVal  = container.querySelector('#ec-stage').value;
          var classRow  = container.querySelector('#ec-class-row');
          var stageRow  = container.querySelector('#ec-stage-row');
          var bossClass = container.querySelector('#ec-boss-class') ? container.querySelector('#ec-boss-class').value : 'Guerrier';

          // Boss antique : zone toujours 1000
          if (stageVal === 'boss_antique') {
            if (zoneEl) zoneEl.value = 1000;
          }
          var zone = Math.max(1, Math.min(1000, parseInt((zoneEl || {}).value || 50, 10) || 50));

          // Afficher les sélecteurs selon le type
          if (classRow) classRow.style.display = stageVal === 'boss_antique' ? '' : 'none';
          if (stageRow) stageRow.style.display  = stageVal === 'ennemi'       ? '' : 'none';

          if      (stageVal === 'boss_antique')      data = calcAntique(bossClass);
          else if (stageVal === 'boss_emblematique') data = calcEmblematique(zone);
          else if (stageVal === 'boss_runique')      data = calcRunicBoss(zone);
          else if (stageVal === 'boss_classique')    data = calcMondeBossClassique(zone);
          else {
            var enemyStageEl = container.querySelector('#ec-enemy-stage');
            var enemyStage   = enemyStageEl ? (parseInt(enemyStageEl.value, 10) || 1) : ((zone - 1) % 10 + 1);
            data = calcMondeEnemy(zone, enemyStage);
          }

        } else if (mode === 'donjon') {
          var bossId = container.querySelector('#ec-donjon-boss').value;
          var diff   = (container.querySelector('input[name="ec-diff"]:checked') || {}).value || 'classique';
          var lvl    = parseInt(container.querySelector('#ec-donjon-level').value, 10) || 1;
          data = calcDonjon(bossId, diff, lvl);

        } else if (mode === 'raid') {
          data = calcRaid(container.querySelector('#ec-raid-boss').value);

        } else {
          var wbInput = container.querySelector('#ec-wb-tour-input') || container.querySelector('#ec-wb-tour');
          data = calcWorldBoss(parseInt((wbInput || {}).value || 1, 10) || 1);
        }

        renderEnemy(data, resultEl);
      } catch(e) {
        console.error('[EnemyCalc]', e);
      }
    }

    tabs.forEach(function(t){
      t.addEventListener('click', function(){ showPanel(t.dataset.mode); });
    });

    // Sliders → label
    var djLvl = container.querySelector('#ec-donjon-level');
    var djVal = container.querySelector('#ec-donjon-level-val');
    if (djLvl && djVal) {
      djLvl.addEventListener('input', function(){ djVal.textContent = djLvl.value; refresh(); });
    }
    var wbTour      = container.querySelector('#ec-wb-tour');
    var wbVal       = container.querySelector('#ec-wb-tour-val');
    var wbTourInput = container.querySelector('#ec-wb-tour-input');

    function syncWbTour(val) {
      val = Math.max(1, Math.min(25, parseInt(val, 10) || 1));
      if (wbVal)       wbVal.textContent = val;
      if (wbTour)      wbTour.value      = val;
      if (wbTourInput) wbTourInput.value = val;
      var level = val * 100;
      var zeEl  = container.querySelector('#ec-wb-zone-equiv');
      if (zeEl) zeEl.textContent = 'Niveau équivalent : ' + level.toLocaleString('fr-FR');
    }

    if (wbTour) {
      wbTour.addEventListener('input', function(){ syncWbTour(wbTour.value); refresh(); });
    }
    if (wbTourInput) {
      wbTourInput.addEventListener('input',  function(){ syncWbTour(wbTourInput.value); refresh(); });
      wbTourInput.addEventListener('change', function(){ syncWbTour(wbTourInput.value); refresh(); });
    }

    container.querySelectorAll('input:not([type="range"]):not([type="radio"]), select').forEach(function(el){
      el.addEventListener('change', refresh);
      el.addEventListener('input',  refresh);
    });
    container.querySelectorAll('input[type="radio"]').forEach(function(el){
      el.addEventListener('change', refresh);
    });

    syncWbTour(1);

    var defaultMode = null;
    ['monde','donjon','raid','wb'].forEach(function(m) {
      if (!defaultMode && panels[m]) defaultMode = m;
    });
    if (defaultMode) showPanel(defaultMode);
  }

  // ─── Point d'entrée ───────────────────────────────────────────────────────

  function init() {
    var el = document.getElementById('enemy-calculator');
    if (!el || el.dataset.calcInit) return;
    el.dataset.calcInit = '1';
    setupCalculator(el);
  }

  if (typeof document$ !== 'undefined') {
    document$.subscribe(init);
  }
  document.addEventListener('DOMContentLoaded', init);

})();
