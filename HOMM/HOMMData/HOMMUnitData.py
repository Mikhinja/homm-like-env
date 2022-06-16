# first iteration, does not yet support:
#   special abilities
#       * note: workaround for marksmen's special ability to shoot twice, damage doubled and number of shots not doubled compared to archers (un-upgraded unit type)
#       * note: same workaround for crusaders, except they do not have shots, damage simply doubled
#   number of shots for ranged units
#   2-hex units
#   costs other than gold.


UnitTypes = {
    # id: (
    #   [0]  base unit type id -- for upgraded unit types; the same as its own id if not upgraded,
    #   [1]  name,
    #   [2]  attack,
    #   [3]  defense,
    #   [4]  damage min,
    #   [5]  damage max,
    #   [6]  max health,
    #   [7]  speed,
    #   [8]  movement (Ground/Flying) -- not used,
    #   [9]  size (1 or 2) -- not used,
    #   [10] shots (0 for melee),
    #   [11] level,
    #   [12] growth,
    #   [13] cost per troop,
    #   [14] AI value)
    #0:   (  0, 'Peasants',         1,  1,  1,  1,   1,  3, 'Ground', 1,  0, 1, 25,   10,    25),
    0:   (  0, 'Invalid',          0,  0,  0,  0,   0,  0, 'Ground', 1,  0, 1,  0,    0,     0),

    # Castle                     Att  Def   D-  D+  HP  Spd         Size Sh Lvl Grow Cost  AIVal
    1:   (  1, 'Pikeman',          4,  5,  1,  3,  10,  4, 'Ground', 1,  0, 1, 14,   60,    80),
    2:   (  1, 'Halberdier',       6,  5,  2,  3,  10,  5, 'Ground', 1,  0, 1, 14,   75,   115),
    3:   (  3, 'Archer',           6,  3,  2,  3,  10,  4, 'Ground', 1, 12, 2,  9,  100,   126),
    4:   (  3, 'Marksman',         6,  3,  4,  6,  10,  6, 'Ground', 1, 12, 2,  9,  150,   184),
    5:   (  5, 'Griffin',          8,  8,  3,  6,  25,  6, 'Flying', 2,  0, 3,  7,  200,   351),
    6:   (  5, 'Royal Griffin',    9,  9,  3,  6,  25,  9, 'Flying', 2,  0, 3,  7,  240,   448),
    7:   (  7, 'Swordsman',       10, 12,  6,  9,  35,  5, 'Ground', 1,  0, 4,  4,  300,   445),
    8:   (  7, 'Crusader',        12, 12, 14, 20,  35,  6, 'Ground', 1,  0, 4,  4,  400,   588),
    9:   (  9, 'Monk',            12,  7, 10, 12,  30,  5, 'Ground', 1, 12, 5,  3,  400,   485),
    10:  (  9, 'Zealot',          12, 10, 10, 12,  30,  7, 'Ground', 1, 24, 5,  3,  450,   750),
    11:  ( 11, 'Cavalier',        15, 15, 15, 25, 100,  7, 'Ground', 2,  0, 6,  2, 1000,  1946),
    12:  ( 11, 'Champion',        16, 16, 20, 25, 100,  9, 'Ground', 2,  0, 6,  2, 1200,  2100),
    13:  ( 13, 'Angel',           20, 20, 50, 50, 200, 12, 'Flying', 1,  0, 7,  1, 3000,  5019), # TODO: implement additional resource costs
    14:  ( 13, 'Archangel',       30, 30, 50, 50, 250, 18, 'Flying', 2,  0, 7,  1, 5000,  8776), # TODO: implement additional resource costs
    
    # Rampart                    Att  Def   D-  D+  HP  Spd         Size Sh Lvl Grow Cost  AIVal
    15:  ( 15, 'Centaur',          5,   3,  2,  3,   8,  6, 'Ground', 2,  0, 1, 14,   70,   100),
    16:  ( 15, 'Centaur Captain',  6,   3,  2,  3,  10,  8, 'Ground', 2,  0, 1, 14,   90,   138),
    17:  ( 17, 'Dwarf',            6,   7,  2,  4,  20,  3, 'Ground', 1,  0, 2,  8,  120,   138),
    18:  ( 17, 'Battle Dwarf',     7,   7,  2,  4,  20,  5, 'Ground', 1,  0, 2,  8,  150,   209),
    19:  ( 19, 'Wood Elf',         9,   5,  3,  5,  15,  6, 'Ground', 1, 24, 3,  7,  200,   234),
    20:  ( 19, 'Grand Elf',        9,   5,  6, 10,  15,  7, 'Ground', 1, 12, 3,  7,  225,   331),
    21:  ( 21, 'Pegasus',          9,   8,  5,  9,  30,  8, 'Flying', 2,  0, 4,  5,  250,   518),
    22:  ( 21, 'Silver Pegasus',   9,  10,  5,  9,  30, 12, 'Flying', 2,  0, 4,  5,  275,   532),
    23:  ( 23, 'Dendroig Guard',   9,  12, 10, 14,  55,  3, 'Ground', 1,  0, 5,  3,  350,   517),
    24:  ( 23, 'Dendroig Soldier', 9,  12, 10, 14,  65,  4, 'Ground', 1,  0, 5,  3,  425,   803),
    25:  ( 25, 'Unicorn',         15,  14, 18, 22,  90,  7, 'Ground', 2,  0, 6,  2,  850,  1806),
    26:  ( 25, 'War Unicorn',     15,  14, 18, 22, 110,  9, 'Ground', 2,  0, 6,  2,  950,  2030),
    27:  ( 27, 'Green Dragon',    18,  18, 40, 50, 180, 10, 'Flying', 2,  0, 7,  1, 2400,  4872), # TODO: implement additional resource costs
    28:  ( 27, 'Gold Dragon',     27,  27, 40, 50, 250, 16, 'Flying', 2,  0, 7,  1, 4000,  8613), # TODO: implement additional resource costs
}
