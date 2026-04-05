# ⚔️ Les Classes

10 classes jouables — 5 **Standard** et 5 **Premium ✨**. Chaque classe possède un passif unique, une ressource et 3 sorts (dont un ultime disponible dès le **tour 3**).

---

## Ressources

| Ressource | Régénération | Max |
|-----------|--------------|-----|
| 🔴 **Rage** — Guerrier, Vampire, Paladin | +5 au début de ton tour · +15 à la fin du tour ennemi | 100 |
| 🔵 **Mana** — Mage, Pyromancien, Support | +15 au début de ton tour | 100 |
| 🟡 **Combo** — Assassin, Tireur, Gardien du Temps, Ombre Venin | +1 à la fin de ton tour · +1 à la fin du tour ennemi | 10 |

---

## Classes

=== "⚔️ Guerrier"

    *Combattant brutal qui puise sa force dans sa souffrance. Plus il est blessé, plus il frappe fort.*

    | Stat | Niv. 1 | +/niv. |
    |------|-------:|-------:|
    | PV | 550 | +45.4 |
    | ATK Phy | 52 | +2.4 |
    | ATK Mag | 0 | — |
    | Pén. Phy | 8 | — |
    | Pén. Mag | 0 | — |
    | Déf. Phy | 32 | +0.8 |
    | Déf. Mag | 6 | +0.2 |
    | Vitesse | 80 | +0.2 |
    | Crit. % | 5% | — |
    | Crit. DMG | 150% | — |
    | 🔴 **Ressource** | **Rage** · max 100 | +5 début tour · +15 fin tour ennemi |

    **Passif — Rage du Blessé :** +0.5% de dégâts par % de HP manquants (max +30%). À 60% de PV perdus : cap atteint.

    **Sorts**

    === "⚔️ Châtiment Sanglant"

        **Coût :** 25 Rage — **Recharge :** 1 tour

        Inflige **×1.6 dégâts physiques**.

    === "🔄 Contre-Attaque"

        **Coût :** 30 Rage — **Recharge :** 4 tours

        Inflige **×1.8 dégâts physiques** puis riposte automatiquement à chaque attaque ennemie pendant **2 tours**.

    === "💢 Immortalité ✦ Ultime"

        **Coût :** 80 Rage — **Recharge :** 8 tours *(dès le tour 3)*

        Inflige **×2.0 dégâts physiques** puis devient immortel pendant **2 tours** — impossible de tomber sous 1 PV.

=== "🗡️ Assassin"

    *Ombre rapide frappant avec une précision mortelle. Hautes chances de critique et d'esquive.*

    | Stat | Niv. 1 | +/niv. |
    |------|-------:|-------:|
    | PV | 500 | +36.5 |
    | ATK Phy | 50 | +2.6 |
    | ATK Mag | 0 | — |
    | Pén. Phy | 10 | +0.5 |
    | Pén. Mag | 0 | — |
    | Déf. Phy | 4 | — |
    | Déf. Mag | 3 | — |
    | Vitesse | 105 | +0.4 |
    | Crit. % | 18% | — |
    | Crit. DMG | 175% | — |
    | 🟡 **Ressource** | **Combo** · max 10 | +1 fin de ton tour · +1 fin tour ennemi |

    **Passif — Ombre Furtive :** 20% de chance d'esquiver chaque attaque ennemie.

    **Sorts**

    === "🗡️ Frappe de l'Ombre"

        **Coût :** 2 Combo — **Recharge :** 1 tour

        Inflige **×1.4 dégâts physiques**. Double les chances d'esquive pour la **prochaine attaque ennemie**.

    === "✴️ Lame Perçante"

        **Coût :** 4 Combo — **Recharge :** 2 tours

        Inflige **×2.0 dégâts physiques** avec un **coup critique garanti**.

    === "💀 Exécution ✦ Ultime"

        **Coût :** 10 Combo — **Recharge :** 6 tours *(dès le tour 3)*

        Dégâts **×2.5 → ×5.0** selon les PV manquants de l'ennemi (×5.0 à 0% PV).

=== "🔮 Mage"

    *Maître de l'arcane dont la puissance croît avec sa vitalité. Plus il a de PV, plus il est dévastateur.*

    | Stat | Niv. 1 | +/niv. |
    |------|-------:|-------:|
    | PV | 420 | +39.6 |
    | ATK Phy | 0 | — |
    | ATK Mag | 42 | +2.8 |
    | Pén. Phy | 0 | — |
    | Pén. Mag | 8 | +0.6 |
    | Déf. Phy | 3 | — |
    | Déf. Mag | 10 | — |
    | Vitesse | 92 | +0.4 |
    | Crit. % | 12% | — |
    | Crit. DMG | 175% | — |
    | 🔵 **Ressource** | **Mana** · max 100 | +15 au début de ton tour |

    **Passif — Concentration Arcanique :** +0.5% de dégâts magiques par % de HP actuels (max +50%). À pleine vie : +50% de dégâts.

    **Sorts**

    === "⚡ Soif Arcane"

        **Coût :** 15 Mana — **Recharge :** 1 tour

        Inflige **×1.6 dégâts magiques** et récupère **+20 Mana** supplémentaire.

    === "🔵 Écran Magique"

        **Coût :** 25 Mana — **Recharge :** 3 tours

        Inflige **×2.0 dégâts magiques** et réduit les dégâts subis de **25% pendant 2 tours**.

    === "☄️ Nova Primordiale ✦ Ultime"

        **Coût :** 80 Mana — **Recharge :** 7 tours *(dès le tour 3)*

        Inflige **×4.5 dégâts magiques** en ignorant **toute la Déf. Mag.** ennemie.

=== "🏹 Tireur"

    *Archer agile dont le passif peut doubler ses dégâts à tout moment. Imprévisible et dévastateur.*

    | Stat | Niv. 1 | +/niv. |
    |------|-------:|-------:|
    | PV | 440 | +37.6 |
    | ATK Phy | 44 | +2.7 |
    | ATK Mag | 0 | — |
    | Pén. Phy | 8 | +0.6 |
    | Pén. Mag | 0 | — |
    | Déf. Phy | 4 | — |
    | Déf. Mag | 4 | — |
    | Vitesse | 105 | +0.4 |
    | Crit. % | 16% | — |
    | Crit. DMG | 175% | — |
    | 🟡 **Ressource** | **Combo** · max 10 | +1 fin de ton tour · +1 fin tour ennemi |

    **Passif — Double Tir :** 25% de chance de doubler ses dégâts à chaque attaque.

    **Sorts**

    === "🏹 Tir Rapide"

        **Coût :** 2 Combo — **Recharge :** 2 tours

        Inflige **×1.5 dégâts physiques** et augmente sa vitesse de **+30% pendant 2 tours**.

    === "🎯 Tir Marqué"

        **Coût :** 4 Combo — **Recharge :** 3 tours

        Inflige **×1.5 dégâts** et marque l'ennemi — il subit **+30% de dégâts pendant 3 tours**.

    === "💥 Tir Fatal ✦ Ultime"

        **Coût :** 10 Combo — **Recharge :** 6 tours *(dès le tour 3)*

        Inflige **×4.0 dégâts physiques** avec un **coup critique garanti**.

=== "🛡️ Support"

    *Protecteur polyvalent qui frappe, soigne et résiste. Classe la plus complète du jeu, indispensable en Raid.*

    | Stat | Niv. 1 | +/niv. |
    |------|-------:|-------:|
    | PV | 650 | +72.4 |
    | ATK Phy | 48 | +1.3 |
    | ATK Mag | 48 | +1.3 |
    | Pén. Phy | 6 | — |
    | Pén. Mag | 6 | — |
    | Déf. Phy | 25 | +0.6 |
    | Déf. Mag | 25 | +0.6 |
    | Vitesse | 80 | +0.2 |
    | Crit. % | 5% | — |
    | Crit. DMG | 140% | — |
    | 🔵 **Ressource** | **Mana** · max 100 | +15 au début de ton tour |

    **Passif — Instinct Protecteur :** 45% de chance de générer automatiquement un bouclier absorbant 10% des PV max chaque tour.

    **Sorts**

    === "💚 Frappe Régénérante"

        **Coût :** 15 Mana — **Recharge :** 1 tour

        Inflige **×1.5 dégâts physiques et magiques combinés**, puis se soigne de **12% des PV max**.

    === "💫 Frappe d'Affaiblissement"

        **Coût :** 20 Mana — **Recharge :** 3 tours

        Inflige **×2.5 dégâts (physiques + magiques)** et réduit les dégâts ennemis de **25% pendant 2 tours**.

    === "🌟 Renvoi Sacré ✦ Ultime"

        **Coût :** 80 Mana — **Recharge :** 7 tours *(dès le tour 3)*

        Inflige **×3.5 dégâts combinés**, puis active un bouclier pendant **3 tours** : renvoie **40% des dégâts reçus** à l'ennemi et réduit **35% des dégâts restants**.

=== "🧛 Vampire ✨"

    *Prédateur nocturne se nourrissant du sang ennemi. S'autosuffit grâce au vol de vie constant.*

    | Stat | Niv. 1 | +/niv. |
    |------|-------:|-------:|
    | PV | 580 | +50.0 |
    | ATK Phy | 60 | +2.6 |
    | ATK Mag | 0 | — |
    | Pén. Phy | 9 | +0.5 |
    | Pén. Mag | 0 | — |
    | Déf. Phy | 12 | +0.3 |
    | Déf. Mag | 7 | +0.2 |
    | Vitesse | 90 | +0.2 |
    | Crit. % | 15% | — |
    | Crit. DMG | 175% | — |
    | 🔴 **Ressource** | **Rage** · max 100 | +5 début tour · +15 fin tour ennemi |

    **Passif — Instinct Prédateur :** 25% de chance de vol de vie à chaque attaque, récupérant 30% des dégâts infligés en PV.

    **Sorts**

    === "🦷 Morsure"

        **Coût :** 20 Rage — **Recharge :** 1 tour

        Inflige **×1.5 dégâts physiques** et récupère **20% des dégâts infligés** en PV.

    === "🩸 Marque de Sang"

        **Coût :** 30 Rage — **Recharge :** 4 tours

        Sacrifie **15% de ses PV**, inflige **×2.5 dégâts** et applique **Marque de Sang** pendant **3 tours** (35% de vol de vie).

    === "💀 Festin Sanglant ✦ Ultime"

        **Coût :** 80 Rage — **Recharge :** 7 tours *(dès le tour 3)*

        Inflige **×4.0 dégâts** + stun **1 tour**. Si **Marque de Sang** est active : dégâts **×5.0** à la place.

=== "⏳ Gardien du Temps ✨"

    *Manipulateur du destin qui distord le temps. Affaiblit progressivement l'ennemi et contrôle le tempo du combat.*

    | Stat | Niv. 1 | +/niv. |
    |------|-------:|-------:|
    | PV | 480 | +41.6 |
    | ATK Phy | 35 | +1.4 |
    | ATK Mag | 35 | +1.4 |
    | Pén. Phy | 6 | +0.3 |
    | Pén. Mag | 6 | +0.3 |
    | Déf. Phy | 18 | +0.4 |
    | Déf. Mag | 18 | +0.4 |
    | Vitesse | 95 | +0.2 |
    | Crit. % | 8% | — |
    | Crit. DMG | 155% | — |
    | 🟡 **Ressource** | **Combo** · max 10 | +1 fin de ton tour · +1 fin tour ennemi |

    **Passif — Distorsion Temporelle :** 55% de chance de réduire une stat ennemie aléatoire de 5% chaque tour (cumulatif, max −20% par stat).

    **Sorts**

    === "⚡ Accélération Temporelle"

        **Coût :** 2 Combo — **Recharge :** 2 tours

        Inflige **×1.5 dégâts combinés** et augmente sa vitesse de **+25% pendant 2 tours**.

    === "⏳ Fissure du Temps"

        **Coût :** 4 Combo — **Recharge :** 3 tours

        Inflige **×2.0 dégâts combinés** et réduit la **Déf. Phy. et Mag. ennemie de 20% pendant 2 tours**.

    === "⏱️ Arrêt du Temps ✦ Ultime"

        **Coût :** 10 Combo — **Recharge :** 7 tours *(dès le tour 3)*

        Inflige **×4.0 dégâts combinés** et étourdit l'ennemi pendant **2 tours** — il ne peut pas agir.

=== "☠️ Ombre Venin ✨"

    *Assassin venimeux qui accumule du poison pour des explosions de dégâts massives. Classe la plus rapide du jeu.*

    | Stat | Niv. 1 | +/niv. |
    |------|-------:|-------:|
    | PV | 460 | +45.7 |
    | ATK Phy | 32 | +1.5 |
    | ATK Mag | 32 | +1.5 |
    | Pén. Phy | 5 | +0.3 |
    | Pén. Mag | 5 | +0.3 |
    | Déf. Phy | 5 | — |
    | Déf. Mag | 5 | — |
    | Vitesse | 115 | +0.3 |
    | Crit. % | 17% | — |
    | Crit. DMG | 170% | — |
    | 🟡 **Ressource** | **Combo** · max 10 | +1 fin de ton tour · +1 fin tour ennemi |

    **Passif — Venin Corrosif :** 30% de chance d'appliquer du poison à chaque attaque (+35% ATK Phy par stack actif).

    **Sorts**

    === "☠️ Injection"

        **Coût :** 2 Combo — **Recharge :** 1 tour

        Inflige **×1.6 dégâts physiques** et applique **2 stacks de poison** (+35% ATK Phy par stack actif).

    === "💨 Brume Toxique"

        **Coût :** 4 Combo — **Recharge :** 3 tours

        Inflige **×2.0 dégâts physiques**, applique **2 stacks de poison** et réduit la **Déf. Phy. ennemie de 20% pendant 2 tours**.

    === "💀 Nécrose ✦ Ultime"

        **Coût :** 10 Combo — **Recharge :** 7 tours *(dès le tour 3)*

        Inflige **×3.5 dégâts physiques + ×1.5 ATK Phy par stack de poison**. Consomme tous les stacks.

=== "🔥 Pyromancien ✨"

    *Sorcier des flammes dont la brûlure s'accumule inexorablement. L'Inferno explose avec chaque stack actif.*

    | Stat | Niv. 1 | +/niv. |
    |------|-------:|-------:|
    | PV | 500 | +43.6 |
    | ATK Phy | 0 | — |
    | ATK Mag | 58 | +3.1 |
    | Pén. Phy | 0 | — |
    | Pén. Mag | 9 | +0.6 |
    | Déf. Phy | 2 | — |
    | Déf. Mag | 10 | — |
    | Vitesse | 85 | +0.4 |
    | Crit. % | 13% | — |
    | Crit. DMG | 175% | — |
    | 🔵 **Ressource** | **Mana** · max 100 | +15 au début de ton tour |

    **Passif — Embrasement Perpétuel :** 45% de chance d'appliquer 1 stack de brûlure à chaque attaque (15% ATK Mag de dégâts par stack actif).

    **Sorts**

    === "🔥 Flammèche"

        **Coût :** 15 Mana — **Recharge :** 1 tour

        Inflige **×1.6 dégâts magiques** et applique **2 stacks de brûlure**.

    === "💥 Brasier"

        **Coût :** 25 Mana — **Recharge :** 3 tours

        Réduit la **Déf. Mag. ennemie de 20% pendant 2 tours**, inflige **×2.0 dégâts magiques** et applique **2 stacks de brûlure**.

    === "🌋 Inferno ✦ Ultime"

        **Coût :** 80 Mana — **Recharge :** 7 tours *(dès le tour 3)*

        Inflige **×3.5 dégâts magiques + 0.25×ATK Mag par stack de brûlure actif**.

=== "✝️ Paladin ✨"

    *Chevalier sacré dont la résistance se renforce au fil du combat. Tank absolu et amplificateur passif en Raid.*

    | Stat | Niv. 1 | +/niv. |
    |------|-------:|-------:|
    | PV | 560 | +71.5 |
    | ATK Phy | 42 | +2.4 |
    | ATK Mag | 0 | — |
    | Pén. Phy | 8 | — |
    | Pén. Mag | 0 | — |
    | Déf. Phy | 35 | +0.9 |
    | Déf. Mag | 22 | +0.4 |
    | Vitesse | 72 | +0.2 |
    | Crit. % | 5% | — |
    | Crit. DMG | 150% | — |
    | 🔴 **Ressource** | **Rage** · max 100 | +5 début tour · +15 fin tour ennemi |

    **Passif — Bénédiction de Combat :** 50% de chance d'augmenter une stat aléatoire de 5% (max +20%, permanent ce combat). En raid, le boost s'applique à tous les alliés.

    **Sorts**

    === "✝️ Frappe Sacrée"

        **Coût :** 20 Rage — **Recharge :** 1 tour

        Inflige **×1.6 dégâts physiques** et génère un **bouclier égal à 15% des PV max**.

    === "⚖️ Pénitence"

        **Coût :** 30 Rage — **Recharge :** 4 tours

        Réduit sa vitesse de **−30%**, génère un **bouclier de 20% des PV max**, et augmente **ATK Phy, Déf Phy+Mag et Pén Phy de +20% pendant 2 tours**.

    === "⚡ Châtiment Divin ✦ Ultime"

        **Coût :** 80 Rage — **Recharge :** 7 tours *(dès le tour 3)*

        Inflige des dégâts égaux à la **somme de toutes ses stats de combat** (ignore la défense).

---

## Prestige

Une fois au niveau max, tu peux [Prestiger](../prestige.md) pour obtenir des bonus permanents cumulatifs sur toutes tes stats.
