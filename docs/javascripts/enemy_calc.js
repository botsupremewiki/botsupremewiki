/* ============================================================
   Simulateur d'Ennemis — Bot Suprême Wiki
   Reproduit fidèlement la logique de enemies.py
   ============================================================ */
(function () {
  'use strict';

  // ─── Données statiques ────────────────────────────────────────────────────

  var ALL_CLASSES = [
    'Guerrier','Assassin','Mage','Tireur','Support',
    'Vampire','Gardien du Temps','Ombre Venin','Pyromancien','Paladin'
  ];

  var CLASS_EMOJI = {
    'Guerrier':'⚔️','Assassin':'🗡️','Mage':'🔮','Tireur':'🏹','Support':'💚',
    'Vampire':'🧛','Gardien du Temps':'⏳','Ombre Venin':'☠️','Pyromancien':'🔥',
    'Paladin':'🛡️','Chromaste':'🌈','Titan':'🐉'
  };

  var CLASS_MOD = {
    'Guerrier':         {hp:1.5, p_atk:1.2, p_def:1.3},
    'Assassin':         {p_atk:1.5, speed:1.5, crit_chance:2.0},
    'Mage':             {m_atk:1.8, m_pen:1.5, hp:0.7},
    'Tireur':           {p_atk:1.4, speed:1.3, crit_chance:1.5},
    'Support':          {hp:1.3, p_def:1.4, m_def:1.4},
    'Vampire':          {p_atk:1.3, hp:1.1},
    'Gardien du Temps': {speed:1.2, p_atk:1.1, m_atk:1.1},
    'Ombre Venin':      {p_atk:1.2, speed:1.3},
    'Pyromancien':      {m_atk:1.6, m_pen:1.3},
    'Paladin':          {hp:1.4, p_def:1.5, m_def:1.4},
    'Chromaste':        {hp:2.0, p_atk:1.5, m_atk:1.5, p_def:1.5, m_def:1.5},
    'Titan':            {hp:2.5, p_def:1.5, m_def:1.5}
  };

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

  var EMBLEMATIC_PASSIFS = [
    "Régénère 2% de ses HP max à chaque tour.",
    "Réduit toutes tes stats de 10% au premier tour.",
    "Inflige des dégâts purs = 5% de tes HP max par tour.",
    "Les 3 premiers tours, ses dégâts sont ×1,5.",
    "Immunité aux critiques pendant les 5 premiers tours.",
    "Enragé : +10% de dégâts par 20% HP perdus.",
    "Absorption : 20% des dégâts reçus convertis en bouclier.",
    "Maudit : tes soins sont réduits de 50%.",
    "Riposte : renvoie 30% des dégâts physiques.",
    "Aura glaciale : réduit ta vitesse de 20%."
  ];

  var ANTIQUE_PASSIFS = [
    "Bouclier Ancien : absorbe 30% des dégâts les 5 premiers tours.",
    "Fléau Primordial : réduit toutes tes stats de 15%.",
    "Éternité : ses HP ne peuvent pas tomber sous 50% avant le tour 10.",
    "Malédiction Antique : tes critiques ne font pas de dégâts supplémentaires.",
    "Terreur Abyssale : réduit ta Défense Physique et Magique de 30%.",
    "Résilience Ancienne : régénère 5% HP max chaque tour.",
    "Emprise Temporelle : bloque l'un de tes tours tous les 5 tours.",
    "Dévoration : vole 3% de tes stats offensives à chaque tour.",
    "Néant : tes passifs de classe sont désactivés les 3 premiers tours.",
    "Convergence : gagne +25% à toutes ses stats au début du combat."
  ];

  var DUNGEON_BOSSES = [
    {id:'d_hp',     name:'Colosse Indestructible',  emoji:'❤️',  cls:'Guerrier',         boost:'hp',          passif:'Régénère 3% HP max chaque tour.'},
    {id:'d_patk',   name:'Berserker Frénétique',     emoji:'⚔️',  cls:'Tireur',           boost:'p_atk',       passif:'Chaque attaque a 20% de chance de stun (perd 1 tour).'},
    {id:'d_matk',   name:'Archimage Déchaîné',       emoji:'🔮',  cls:'Mage',             boost:'m_atk',       passif:'Chaque 3e tour, inflige des dégâts purs = 10% de tes HP max.'},
    {id:'d_pdef',   name:'Gardien Impénétrable',     emoji:'🛡️',  cls:'Paladin',          boost:'p_def',       passif:'Les 5 premiers tours, dégâts physiques réduits de 70%.'},
    {id:'d_mdef',   name:'Sanctuaire Vivant',        emoji:'✨',  cls:'Support',          boost:'m_def',       passif:'Les 5 premiers tours, dégâts magiques réduits de 70%.'},
    {id:'d_speed',  name:'Spectre Fulgurant',        emoji:'⚡',  cls:'Assassin',         boost:'speed',       passif:'Attaque toujours 2 fois par tour.'},
    {id:'d_ppen',   name:'Déchireur de Plaques',     emoji:'🗡️',  cls:'Vampire',          boost:'p_pen',       passif:'Ignore 50% de ta Défense Physique.'},
    {id:'d_mpen',   name:'Brise-Barrière Arcanique', emoji:'💫',  cls:'Ombre Venin',      boost:'m_pen',       passif:'Ignore 50% de ta Défense Magique.'},
    {id:'d_crit',   name:'Prédateur Précis',         emoji:'🎯',  cls:'Pyromancien',      boost:'crit_chance', passif:'85% de chance de critique à chaque attaque.'},
    {id:'d_critdmg',name:'Exécuteur Absolu',         emoji:'💀',  cls:'Gardien du Temps', boost:'crit_damage', passif:'Ses critiques infligent 500% des dégâts normaux.'}
  ];

  var RAID_BOSSES_DATA = [
    {id:'raid_1',  name:"Ancêtre Vorgath",       emoji:'🐉', level:1,  req:100,  cls:'Guerrier',         passif:"Frappe le joueur le plus tanky. +5% dégâts par joueur mort."},
    {id:'raid_2',  name:"Tiamorph l'Hydre",      emoji:'🐍', level:2,  req:200,  cls:'Ombre Venin',      passif:"Applique un poison à tous les joueurs = 2% HP max/tour."},
    {id:'raid_3',  name:"Zyrex l'Électriseur",   emoji:'⚡', level:3,  req:300,  cls:'Mage',             passif:"Tous les 3 tours, décharge électrique sur tous = 15% HP max dégâts purs."},
    {id:'raid_4',  name:"Gorthax le Fossilisé",  emoji:'🪨', level:4,  req:400,  cls:'Support',          passif:"Absorbe 40% de tous les dégâts les 5 premiers tours."},
    {id:'raid_5',  name:"Nexara la Tisseuse",    emoji:'🕷️', level:5,  req:500,  cls:'Assassin',         passif:"Pièges : réduit la vitesse de 2 joueurs aléatoires de 30% par tour."},
    {id:'raid_6',  name:"Embrasys le Phénix",    emoji:'🔥', level:6,  req:600,  cls:'Pyromancien',      passif:"Brûlure de zone = 5% Att. Mag./joueur/tour. Ressuscite une fois à 30% HP."},
    {id:'raid_7',  name:"Chronovex l'Invariant", emoji:'⏳', level:7,  req:700,  cls:'Gardien du Temps', passif:"Inverse l'ordre d'attaque tous les 5 tours."},
    {id:'raid_8',  name:"Luxara la Sainte",      emoji:'☀️', level:8,  req:800,  cls:'Paladin',          passif:"Bouclier sacré : absorbe 20% HP max dégâts toutes les 5 tours."},
    {id:'raid_9',  name:"Mortemis le Vampirique",emoji:'🧛', level:9,  req:900,  cls:'Vampire',          passif:"Vol de vie massif : se soigne de 50% des dégâts infligés à l'équipe."},
    {id:'raid_10', name:"Omnifax l'Absolu",      emoji:'🌑', level:10, req:1000, cls:'Chromaste',        passif:"Possède tous les passifs des autres raid boss simultanément. Stats offensives doublées."}
  ];

  // ─── Fonctions de calcul ─────────────────────────────────────────────────

  function scaleStats(mult, cls) {
    var m = CLASS_MOD[cls] || {};
    return {
      hp:          Math.floor(200 * mult * (m.hp          || 1)),
      p_atk:       Math.floor(40  * mult * (m.p_atk       || 1)),
      m_atk:       Math.floor(28  * mult * (m.m_atk       || 1)),
      p_pen:       Math.floor(35  * mult * (m.p_pen       || 1)),
      m_pen:       Math.floor(20  * mult * (m.m_pen       || 1)),
      p_def:       Math.floor(12  * mult * (m.p_def       || 1)),
      m_def:       Math.floor(8   * mult * (m.m_def       || 1)),
      speed:       Math.floor((80 + Math.log1p(mult) * 10) * (m.speed || 1)),
      crit_chance: Math.min(Math.floor(5 * (m.crit_chance || 1)), 50),
      crit_damage: 150
    };
  }

  function scaleStatsAvg(mult) {
    var all = ALL_CLASSES.map(function(c){ return scaleStats(mult, c); });
    var r = {};
    Object.keys(all[0]).forEach(function(k){
      r[k] = Math.floor(all.reduce(function(s,o){ return s+o[k]; }, 0) / all.length);
    });
    return r;
  }

  function getTheme(zone) {
    return ZONE_THEMES[Math.floor((zone - 1) / 1000) % ZONE_THEMES.length];
  }

  function classForStage(stage) {
    return ALL_CLASSES[(stage - 1) % ALL_CLASSES.length];
  }

  // ── Monde ──────────────────────────────────────────────────────────────────

  function calcMondeEnemy(zone, stage) {
    var mult = zone <= 100
      ? 1 + (zone-1)*0.02 + stage*0.005
      : 1 + 2.0 + (zone-101)*0.15 + stage*0.01;
    var cls = classForStage(stage);
    var stats = scaleStats(mult, cls);
    var th = getTheme(zone);
    return {
      name: ENEMY_FIRST[cls] || cls,
      nameNote: 'Le nom exact varie à chaque combat',
      cls: cls, theme: th[0], themeEmoji: th[1],
      typeLabel: 'Stage ' + stage, typeBadge: 'Monde', typeEmoji: '👿',
      passif: null,
      xp: Math.max(1, zone*15 + stage),
      gold: Math.max(1, zone*8 + stage),
      stats: stats
    };
  }

  function calcMondeBossClassique(zone) {
    var mult = zone <= 100
      ? (1 + (zone-1)*0.02 + 10*0.005) * 1.5
      : (1 + 2.0 + (zone-101)*0.15 + 10*0.01) * 2.0;
    var cls = classForStage((zone % 10) + 1);
    var stats = scaleStats(mult, cls);
    var th = getTheme(zone);
    return {
      name: '[Préfixe] ' + (ENEMY_FIRST[cls] || cls),
      nameNote: 'Le nom exact varie à chaque combat',
      cls: cls, theme: th[0], themeEmoji: th[1],
      typeLabel: 'Boss de Zone', typeBadge: 'Boss Zone', typeEmoji: '⚔️',
      passif: null,
      xp: Math.max(3, zone*50),
      gold: Math.max(2, zone*20),
      stats: stats
    };
  }

  function calcEmblematique(zone, cls) {
    var mult = (1 + (zone-1)*0.15) * 5.0;
    var stats = cls ? scaleStats(mult, cls) : scaleStatsAvg(mult);
    stats.hp = Math.floor(stats.hp * 3);
    var idx  = (Math.floor(zone/100) - 1) % EMBLEMATIC_NAMES.length;
    var pidx = (Math.floor(zone/100) - 1) % EMBLEMATIC_PASSIFS.length;
    return {
      name: EMBLEMATIC_NAMES[idx],
      nameNote: null,
      cls: cls || '(Aléatoire — moyenne affichée)',
      theme: 'Boss Emblématique', themeEmoji: '🌟',
      typeLabel: 'Boss Emblématique', typeBadge: 'Emblématique', typeEmoji: '🌟',
      passif: EMBLEMATIC_PASSIFS[pidx],
      xp: Math.max(50, zone*200),
      gold: Math.max(30, zone*80),
      stats: stats
    };
  }

  function calcAntique(zone, cls) {
    var mult = (1 + (zone-1)*0.15) * 10.0;
    var stats = cls ? scaleStats(mult, cls) : scaleStatsAvg(mult);
    stats.hp = Math.floor(stats.hp * 5);
    var idx  = (Math.floor(zone/1000) - 1) % ANTIQUE_NAMES.length;
    var pidx = (Math.floor(zone/1000) - 1) % ANTIQUE_PASSIFS.length;
    return {
      name: ANTIQUE_NAMES[idx],
      nameNote: null,
      cls: cls || '(Aléatoire — moyenne affichée)',
      theme: 'Boss Antique', themeEmoji: '⚠️',
      typeLabel: 'Boss Antique', typeBadge: 'Antique', typeEmoji: '⚠️',
      passif: ANTIQUE_PASSIFS[pidx],
      xp: Math.max(200, zone*1000),
      gold: Math.max(100, zone*300),
      stats: stats
    };
  }

  function calcFinalBoss() {
    var zone = 10000;
    var mult = (1 + (zone-1)*0.15) * 15.0;
    var allS = ALL_CLASSES.map(function(c){ return scaleStats(mult, c); });
    var stats = {};
    Object.keys(allS[0]).forEach(function(k){
      stats[k] = Math.max.apply(null, allS.map(function(s){ return s[k]; }));
    });
    stats.hp = Math.floor(stats.hp * 10);
    return {
      name: 'Chromastrix, le Convergent des Âges',
      nameNote: null,
      cls: 'Chromaste', theme: 'Le Convergent des Âges', themeEmoji: '🌈',
      typeLabel: 'Boss Final', typeBadge: 'BOSS FINAL', typeEmoji: '🌈',
      passif: "Maîtrise Chromatique : possède les passifs de TOUTES les classes simultanément. Immunité aux DoT. Régénère 3% HP max/tour.",
      xp: 5000000, gold: 2000000,
      stats: stats
    };
  }

  // ── Donjon ─────────────────────────────────────────────────────────────────

  function calcDonjon(bossId, difficulty, level) {
    var boss = DUNGEON_BOSSES.filter(function(b){ return b.id === bossId; })[0] || DUNGEON_BOSSES[0];
    var diffMult = {classique:0.33, elite:0.66, abyssal:0.99}[difficulty] || 0.33;
    var zoneEquiv = Math.max(1, Math.floor(level * 100 * diffMult));
    var mult = 1 + (zoneEquiv - 1) * 0.15;
    var stats = scaleStats(mult, boss.cls);
    if (stats[boss.boost] !== undefined) stats[boss.boost] = Math.floor(stats[boss.boost] * 10);
    var diffLabel = {classique:'Classique', elite:'Élite', abyssal:'Abyssal'}[difficulty];
    return {
      name: boss.name, nameNote: null,
      cls: boss.cls, theme: 'Donjon ' + diffLabel + ' Niv.' + level, themeEmoji: boss.emoji,
      typeLabel: 'Donjon ' + diffLabel + ' — Niv.' + level,
      typeBadge: 'Donjon ' + diffLabel, typeEmoji: boss.emoji,
      passif: boss.passif, boostStat: boss.boost,
      xp: Math.max(1, Math.floor(zoneEquiv * 15)),
      gold: Math.max(1, Math.floor(zoneEquiv * 8)),
      zoneEquiv: zoneEquiv,
      stats: stats
    };
  }

  // ── Raid ───────────────────────────────────────────────────────────────────

  function calcRaid(raidId) {
    var boss = RAID_BOSSES_DATA.filter(function(b){ return b.id === raidId; })[0] || RAID_BOSSES_DATA[0];
    var zoneEquiv = boss.level * 1000;
    var mult = 3.0 + (zoneEquiv - 101) * 0.15;
    var stats = scaleStatsAvg(mult);
    stats.hp *= 15;
    if (raidId === 'raid_10') {
      ['p_atk','m_atk','p_def','m_def','p_pen','m_pen'].forEach(function(k){
        stats[k] = Math.floor(stats[k] * 2);
      });
    }
    return {
      name: boss.name, nameNote: null,
      cls: boss.cls, theme: 'Raid', themeEmoji: boss.emoji,
      typeLabel: 'Raid ' + boss.level + ' — Niveau requis : ' + boss.req,
      typeBadge: 'Raid ' + boss.level, typeEmoji: boss.emoji,
      passif: boss.passif, req: boss.req,
      xp: Math.floor(zoneEquiv * 150),
      gold: Math.floor(zoneEquiv * 50),
      stats: stats
    };
  }

  // ── World Boss ─────────────────────────────────────────────────────────────

  function calcWorldBoss(tour) {
    var zoneEquiv = Math.max(1000, tour * 1000);
    var mult = 1 + (zoneEquiv - 1) * 0.15;
    var stats = scaleStatsAvg(mult);
    stats.hp *= 50;
    return {
      name: 'Bot Suprême', nameNote: null,
      cls: 'Titan', theme: 'World Boss', themeEmoji: '🐉',
      typeLabel: 'World Boss — Tour ' + tour + ' (zone ≈ ' + fmt(zoneEquiv) + ')',
      typeBadge: 'World Boss T' + tour, typeEmoji: '🐉',
      passif: "Escalade de Puissance : chaque tour, ses stats augmentent de l'équivalent de 1 000 zones supplémentaires.",
      xp: zoneEquiv * 500, gold: zoneEquiv * 200,
      stats: stats
    };
  }

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

  var BADGE_COLORS = {
    'Emblématique': '#d97706', 'Antique': '#dc2626',
    'BOSS FINAL': '#9333ea', 'World Boss T1': '#16a34a'
  };

  function badgeColor(badge) {
    if (BADGE_COLORS[badge]) return BADGE_COLORS[badge];
    if (badge.indexOf('World Boss') === 0) return '#16a34a';
    if (badge.indexOf('Raid') === 0)       return '#2563eb';
    if (badge.indexOf('Donjon') === 0)     return '#0891b2';
    return '#6b7280';
  }

  function renderEnemy(data, resultEl) {
    var s = data.stats;
    var statsHtml = '';
    STAT_ORDER.forEach(function(k){
      var v = s[k]; if (v === undefined) return;
      var valStr = (k === 'crit_chance' || k === 'crit_damage') ? v + '%' : fmt(v);
      var isBoosted = data.boostStat === k;
      var isHp = k === 'hp';
      statsHtml += '<div class="ec-stat' +
        (isHp ? ' ec-stat-hp' : '') +
        (isBoosted ? ' ec-stat-boosted' : '') + '">' +
        '<span class="ec-stat-icon">' + STAT_EMOJIS[k] + '</span>' +
        '<span class="ec-stat-name">' + STAT_LABELS[k] + '</span>' +
        '<span class="ec-stat-val">' + valStr + (isBoosted ? ' ★' : '') + '</span></div>';
    });

    var passifHtml = data.passif
      ? '<div class="ec-passif"><div class="ec-passif-lbl">⚡ Passif</div>' +
        '<div class="ec-passif-txt">' + data.passif + '</div></div>'
      : '';

    var noteHtml = data.nameNote
      ? '<div class="ec-note">ℹ️ ' + data.nameNote + '</div>' : '';

    var reqHtml = data.req
      ? '<div class="ec-req">🔓 Niveau requis : <strong>' + data.req + '</strong></div>' : '';

    var zoneHtml = data.zoneEquiv
      ? '<div class="ec-note">⚙️ Zone équivalente : ' + fmt(data.zoneEquiv) + '</div>' : '';

    var bc = badgeColor(data.typeBadge);
    resultEl.innerHTML =
      '<div class="ec-header">' +
        '<div class="ec-emoji">' + data.themeEmoji + '</div>' +
        '<div class="ec-title-block">' +
          '<div class="ec-name">' + data.name + '</div>' +
          '<div class="ec-meta">' + (CLASS_EMOJI[data.cls] || '👹') + ' ' + data.cls +
            ' &nbsp;·&nbsp; ' + data.theme + '</div>' + noteHtml +
        '</div>' +
        '<div class="ec-badge" style="background:' + bc + '">' + data.typeBadge + '</div>' +
      '</div>' +
      reqHtml +
      '<div class="ec-stats-grid">' + statsHtml + '</div>' +
      passifHtml + zoneHtml +
      '<div class="ec-rewards">' +
        '<span>✨ XP : <strong>' + fmt(data.xp) + '</strong></span>' +
        '<span>🪙 Or : <strong>' + fmt(data.gold) + '</strong></span>' +
      '</div>';

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

    tabs.forEach(function(t){
      t.addEventListener('click', function(){ showPanel(t.dataset.mode); });
    });

    function refresh() {
      try {
        var data;
        if (mode === 'monde') {
          var zone = Math.max(1, Math.min(10000,
            parseInt(container.querySelector('#ec-zone').value, 10) || 1));
          var stageVal  = container.querySelector('#ec-stage').value;
          var bossClass = container.querySelector('#ec-boss-class').value || null;
          var classRow  = container.querySelector('#ec-class-row');

          // Montrer/cacher le sélecteur de classe pour boss emblématique/antique
          var showClass = stageVal === 'boss' && zone > 0 && zone % 100 === 0 && zone !== 10000;
          if (classRow) classRow.style.display = showClass ? '' : 'none';

          if (stageVal === 'boss') {
            if (zone === 10000)           data = calcFinalBoss();
            else if (zone % 1000 === 0)   data = calcAntique(zone, bossClass);
            else if (zone % 100 === 0)    data = calcEmblematique(zone, bossClass);
            else                          data = calcMondeBossClassique(zone);
          } else {
            data = calcMondeEnemy(zone, parseInt(stageVal, 10));
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
        data = calcWorldBoss(parseInt(wbInput.value, 10) || 1);
        }

        renderEnemy(data, resultEl);
      } catch(e) {
        console.error('[EnemyCalc]', e);
      }
    }

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
      val = Math.max(1, parseInt(val, 10) || 1);
      if (wbVal)       wbVal.textContent   = val;
      if (wbTour)      wbTour.value        = Math.min(val, 50);
      if (wbTourInput) wbTourInput.value   = val;
    }

    if (wbTour) {
      wbTour.addEventListener('input', function(){ syncWbTour(wbTour.value); refresh(); });
    }
    if (wbTourInput) {
      wbTourInput.addEventListener('input',  function(){ syncWbTour(wbTourInput.value); refresh(); });
      wbTourInput.addEventListener('change', function(){ syncWbTour(wbTourInput.value); refresh(); });
    }

    // Tous les autres inputs
    container.querySelectorAll('input:not([type="range"]):not([type="radio"]), select').forEach(function(el){
      el.addEventListener('change', refresh);
      el.addEventListener('input', refresh);
    });
    container.querySelectorAll('input[type="radio"]').forEach(function(el){
      el.addEventListener('change', refresh);
    });

    // Render initial
    showPanel('monde');
  }

  // ─── Point d'entrée ───────────────────────────────────────────────────────

  function init() {
    var el = document.getElementById('enemy-calculator');
    if (!el || el.dataset.calcInit) return;
    el.dataset.calcInit = '1';
    setupCalculator(el);
  }

  // MkDocs Material instant navigation + chargement initial
  if (typeof document$ !== 'undefined') {
    document$.subscribe(init);
  }
  document.addEventListener('DOMContentLoaded', init);

})();
