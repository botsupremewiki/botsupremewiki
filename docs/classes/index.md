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
    | PV | 6 000 | +60.0 |
    | ATK Phy | 200 | +2.0 |
    | ATK Mag | 0 | — |
    | Pén. Phy | 90 | +0.9 |
    | Pén. Mag | 0 | — |
    | Déf. Phy | 100 | +1.0 |
    | Déf. Mag | 100 | +1.0 |
    | Vitesse | 100 | +1.0 |
    | Crit. % | 20% | — |
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
    | PV | 5 000 | +50.0 |
    | ATK Phy | 200 | +2.0 |
    | ATK Mag | 0 | — |
    | Pén. Phy | 90 | +0.9 |
    | Pén. Mag | 0 | — |
    | Déf. Phy | 100 | +1.0 |
    | Déf. Mag | 100 | +1.0 |
    | Vitesse | 100 | +1.0 |
    | Crit. % | 20% | — |
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
    | PV | 5 000 | +50.0 |
    | ATK Phy | 0 | — |
    | ATK Mag | 220 | +2.2 |
    | Pén. Phy | 0 | — |
    | Pén. Mag | 90 | +0.9 |
    | Déf. Phy | 100 | +1.0 |
    | Déf. Mag | 100 | +1.0 |
    | Vitesse | 100 | +1.0 |
    | Crit. % | 20% | — |
    | Crit. DMG | 150% | — |
    | 🔵 **Ressource** | **Mana** · max 100 | +15 au début de ton tour |

    **Passif — Concentration Arcanique :** +0.25% de dégâts magiques par % de HP actuels (max +25%). À pleine vie : +25% de dégâts.

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
    | PV | 5 000 | +50.0 |
    | ATK Phy | 200 | +2.0 |
    | ATK Mag | 0 | — |
    | Pén. Phy | 99 | +0.99 |
    | Pén. Mag | 0 | — |
    | Déf. Phy | 100 | +1.0 |
    | Déf. Mag | 100 | +1.0 |
    | Vitesse | 100 | +1.0 |
    | Crit. % | 20% | — |
    | Crit. DMG | 150% | — |
    | 🟡 **Ressource** | **Combo** · max 10 | +1 fin de ton tour · +1 fin tour ennemi |

    **Passif — Double Tir :** 20% de chance de doubler ses dégâts à chaque attaque.

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
    | PV | 5 000 | +50.0 |
    | ATK Phy | 150 | +1.5 |
    | ATK Mag | 150 | +1.5 |
    | Pén. Phy | 90 | +0.9 |
    | Pén. Mag | 90 | +0.9 |
    | Déf. Phy | 100 | +1.0 |
    | Déf. Mag | 110 | +1.1 |
    | Vitesse | 100 | +1.0 |
    | Crit. % | 20% | — |
    | Crit. DMG | 150% | — |
    | 🔵 **Ressource** | **Mana** · max 100 | +15 au début de ton tour |

    **Passif — Instinct Protecteur :** 30% de chance de générer automatiquement un bouclier absorbant 8% des PV max chaque tour.

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
    | PV | 5 000 | +50.0 |
    | ATK Phy | 220 | +2.2 |
    | ATK Mag | 0 | — |
    | Pén. Phy | 90 | +0.9 |
    | Pén. Mag | 0 | — |
    | Déf. Phy | 100 | +1.0 |
    | Déf. Mag | 100 | +1.0 |
    | Vitesse | 100 | +1.0 |
    | Crit. % | 20% | — |
    | Crit. DMG | 150% | — |
    | 🔴 **Ressource** | **Rage** · max 100 | +5 début tour · +15 fin tour ennemi |

    **Passif — Instinct Prédateur :** 20% de chance de vol de vie à chaque attaque, récupérant 25% des dégâts infligés en PV.

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
    | PV | 5 000 | +50.0 |
    | ATK Phy | 150 | +1.5 |
    | ATK Mag | 150 | +1.5 |
    | Pén. Phy | 90 | +0.9 |
    | Pén. Mag | 90 | +0.9 |
    | Déf. Phy | 100 | +1.0 |
    | Déf. Mag | 100 | +1.0 |
    | Vitesse | 120 | +1.2 |
    | Crit. % | 20% | — |
    | Crit. DMG | 150% | — |
    | 🟡 **Ressource** | **Combo** · max 10 | +1 fin de ton tour · +1 fin tour ennemi |

    **Passif — Distorsion Temporelle :** 35% de chance de réduire une stat ennemie aléatoire de 5% chaque tour (cumulatif, max −20% par stat).

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
    | PV | 5 000 | +50.0 |
    | ATK Phy | 150 | +1.5 |
    | ATK Mag | 150 | +1.5 |
    | Pén. Phy | 90 | +0.9 |
    | Pén. Mag | 90 | +0.9 |
    | Déf. Phy | 100 | +1.0 |
    | Déf. Mag | 100 | +1.0 |
    | Vitesse | 100 | +1.0 |
    | Crit. % | 30% | — |
    | Crit. DMG | 150% | — |
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
    | PV | 5 000 | +50.0 |
    | ATK Phy | 0 | — |
    | ATK Mag | 200 | +2.0 |
    | Pén. Phy | 0 | — |
    | Pén. Mag | 99 | +0.99 |
    | Déf. Phy | 100 | +1.0 |
    | Déf. Mag | 100 | +1.0 |
    | Vitesse | 100 | +1.0 |
    | Crit. % | 20% | — |
    | Crit. DMG | 150% | — |
    | 🔵 **Ressource** | **Mana** · max 100 | +15 au début de ton tour |

    **Passif — Embrasement Perpétuel :** 30% de chance d'appliquer 1 stack de brûlure à chaque attaque (15% ATK Mag de dégâts par stack actif).

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
    | PV | 5 000 | +50.0 |
    | ATK Phy | 200 | +2.0 |
    | ATK Mag | 0 | — |
    | Pén. Phy | 90 | +0.9 |
    | Pén. Mag | 0 | — |
    | Déf. Phy | 110 | +1.1 |
    | Déf. Mag | 100 | +1.0 |
    | Vitesse | 100 | +1.0 |
    | Crit. % | 20% | — |
    | Crit. DMG | 150% | — |
    | 🔴 **Ressource** | **Rage** · max 100 | +5 début tour · +15 fin tour ennemi |

    **Passif — Bénédiction de Combat :** 30% de chance d'augmenter une stat aléatoire de 5% (max +20%, permanent ce combat). En raid, le boost s'applique à tous les alliés.

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
