
# levels are 1-indexed (first level is 1), while lists are 0-indexed
# experience per level is capped at 75, as per https://heroes.thelazy.net//index.php/Experience
# ... level 74 should be more than enough
HeroLevelExperience = [0, 1000, 2000, 3200, 4600, 6200, 8000, 10000, 12200, 14700, 17500, 20600, 24320, 28784, 34140, 40567, 48279, 57533, 68637, 81961, 97949, 117134, 140156, 167782, 200933, 240714, 288451, 345735, 414475, 496963, 595948, 714730, 857268, 1028313, 1233567, 1479871, 1775435, 2130111, 2555722, 3066455, 3679334, 4414788, 5297332, 6356384, 7627246, 9152280, 10982320, 13178368, 15813625, 18975933, 22770702, 27324424, 32788890, 39346249, 47215079, 56657675, 67988790, 81586128, 97902933, 117483099, 140979298, 169174736, 203009261, 243610691, 292332407, 350798466, 420957736, 505148860, 606178208, 727413425, 872895685, 1047474397, 1256968851, 1508362195, 1810034207]

# hero classes according to https://heroes.thelazy.net/index.php/Hero_class
HeroClasses = {
    'Knight': {
        'type' : 'Might',
        'faction': 'Castle',
        'primary stats': {
            'initial':  [   2,    2,    1,    1],
            'prob 2-9': [0.35, 0.45,  0.1,  0.1],
            'prob 10+': [ 0.3,  0.3,  0.2,  0.2]
        },
        'secondary skills': { # chances not probabilities, should be in total 112 (113 with 'Interference')
            'Air Magic':     3,
            'Archery':       5,
            'Armorer':       5,
            #'Artillery':     5, # not supported yet
            #'Ballistics':    8, # not supported yet
            #'Diplomacy':     4, # not supported yet
            #'Eagle Eye':     2, # not supported yet
            'Earth Magic':   2,
            #'Estates':       6, # not supported yet
            'Fire Magic':    1,
            #'First Aid':     2, # not supported yet
            'Intelligence':  1,
            #'Leadership':   10, # not supported yet
            #'Learning':      4, # not supported yet
            #'Logistics':     5, # not supported yet
            #'Luck':          3, # not supported yet
            #'Mysticism':     2, # not supported yet
            #'Navigation':    8, # not supported yet
            #'Necromancy':    0, # not supported yet
            'Offense':       7,
            #'Pathfinding':   4, # not supported yet
            'Resistance':    5,
            #'Scholar':       1, # not supported yet
            #'Scouting':      4, # not supported yet
            'Sorcery':       1,
            #'Tactics':       7, # not supported yet
            'Water Magic':   4,
            'Wisdom	':       3,
            #'Interference':  5, # not supported yet
        }
    },
    'Cleric': {
        'type' : 'Magic',
        'faction': 'Castle',
        'primary stats': {
            'initial':  [   1,    0,    2,    2],
            'prob 2-9': [ 0.2, 0.15,  0.3, 0.35],
            'prob 10+': [ 0.2,  0.2,  0.3,  0.3]
        },
        'secondary skills': { # chances not probabilities, should be in total 112 (113 with 'Interference')
            'Air Magic':     4,
            'Archery':       3,
            'Armorer':       3,
            #'Artillery':     2, # not supported yet
            #'Ballistics':    4, # not supported yet
            #'Diplomacy':     7, # not supported yet
            #'Eagle Eye':     6, # not supported yet
            'Earth Magic':   3,
            #'Estates':       3, # not supported yet
            'Fire Magic':    2,
            #'First Aid':    10, # not supported yet
            'Intelligence':  6,
            #'Leadership':    2, # not supported yet
            #'Learning':      4, # not supported yet
            #'Logistics':     4, # not supported yet
            #'Luck':          5, # not supported yet
            #'Mysticism':     4, # not supported yet
            #'Navigation':    5, # not supported yet
            #'Necromancy':    0, # not supported yet
            'Offense':       4,
            #'Pathfinding':   2, # not supported yet
            'Resistance':    2,
            #'Scholar':       6, # not supported yet
            #'Scouting':      3, # not supported yet
            'Sorcery':       5,
            #'Tactics':       2, # not supported yet
            'Water Magic':   4,
            'Wisdom	':       7,
            #'Interference':  0, # not supported yet
        }
    },
    'Ranger': { # not supported yet
        'type' : 'Might',
        'faction': 'Rampart',
        'primary stats': {
            'initial':  [   1,    3,    1,    1],
            'prob 2-9': [0.35, 0.45,  0.1,  0.1],
            'prob 10+': [ 0.3,  0.3,  0.2,  0.2]
        },
        'secondary skills': { # chances not probabilities, should be in total 112 (113 with 'Interference')
            'Air Magic':     1,
            'Archery':       8,
            'Armorer':       8,
            #'Artillery':     6, # not supported yet
            #'Ballistics':    4, # not supported yet
            #'Diplomacy':     4, # not supported yet
            #'Eagle Eye':     2, # not supported yet
            'Earth Magic':   3,
            #'Estates':       2, # not supported yet
            'Fire Magic':    0,
            #'First Aid':     3, # not supported yet
            'Intelligence':  2,
            #'Leadership':    6, # not supported yet
            #'Learning':      4, # not supported yet
            #'Logistics':     5, # not supported yet
            #'Luck':          6, # not supported yet
            #'Mysticism':     3, # not supported yet
            #'Navigation':    3, # not supported yet
            #'Necromancy':    0, # not supported yet
            'Offense':       5,
            #'Pathfinding':   7, # not supported yet
            'Resistance':    9,
            #'Scholar':       1, # not supported yet
            #'Scouting':      7, # not supported yet
            'Sorcery':       2,
            #'Tactics':       5, # not supported yet
            'Water Magic':   3,
            'Wisdom	':       3,
            #'Interference':  9, # not supported yet
        }
    },
    'Druid': { # not supported yet
        'type' : 'Magic',
        'faction': 'Rampart',
        'primary stats': {
            'initial':  [   0,    2,    1,    2],
            'prob 2-9': [ 0.1,  0.2, 0.35, 0.35],
            'prob 10+': [ 0.2,  0.2,  0.3,  0.3]
        },
        'secondary skills': { # chances not probabilities, should be in total 112 (113 with 'Interference')
            'Air Magic':     2,
            'Archery':       5,
            'Armorer':       3,
            #'Artillery':     1, # not supported yet
            #'Ballistics':    4, # not supported yet
            #'Diplomacy':     4, # not supported yet
            #'Eagle Eye':     7, # not supported yet
            'Earth Magic':   4,
            #'Estates':       3, # not supported yet
            'Fire Magic':    1,
            #'First Aid':     7, # not supported yet
            'Intelligence':  7,
            #'Leadership':    2, # not supported yet
            #'Learning':      4, # not supported yet
            #'Logistics':     5, # not supported yet
            #'Luck':          9, # not supported yet
            #'Mysticism':     6, # not supported yet
            #'Navigation':    2, # not supported yet
            #'Necromancy':    0, # not supported yet
            'Offense':       1,
            #'Pathfinding':   5, # not supported yet
            'Resistance':    1,
            #'Scholar':       8, # not supported yet
            #'Scouting':      2, # not supported yet
            'Sorcery':       6,
            #'Tactics':       1, # not supported yet
            'Water Magic':   4,
            'Wisdom	':       8,
            #'Interference':  0, # not supported yet
        }
    },
    'Alchemist': { # not supported yet
        'type' : 'Might',
        'faction': 'Tower',
        'primary stats': {
            'initial':  [   1,    1,    2,    2],
            'prob 2-9': [ 0.3,  0.3,  0.2,  0.2],
            'prob 10+': [ 0.3,  0.3,  0.2,  0.2]
        },
        'secondary skills': { # chances not probabilities, should be in total 112 (113 with 'Interference')
            'Air Magic':     4,
            'Archery':       5,
            'Armorer':       8,
            #'Artillery':     4, # not supported yet
            #'Ballistics':    6, # not supported yet
            #'Diplomacy':     3, # not supported yet
            #'Eagle Eye':     3, # not supported yet
            'Earth Magic':   3,
            #'Estates':       4, # not supported yet
            'Fire Magic':    1,
            #'First Aid':     2, # not supported yet
            'Intelligence':  4,
            #'Leadership':    3, # not supported yet
            #'Learning':     10, # not supported yet
            #'Logistics':     6, # not supported yet
            #'Luck':          2, # not supported yet
            #'Mysticism':     4, # not supported yet
            #'Navigation':    3, # not supported yet
            #'Necromancy':    0, # not supported yet
            'Offense':       6,
            #'Pathfinding':   4, # not supported yet
            'Resistance':    5,
            #'Scholar':       3, # not supported yet
            #'Scouting':      4, # not supported yet
            'Sorcery':       3,
            #'Tactics':       4, # not supported yet
            'Water Magic':   2,
            'Wisdom	':       6,
            #'Interference':  5, # not supported yet
        }
    },
    'Wizzard': { # not supported yet
        'type' : 'Magic',
        'faction': 'Tower',
        'primary stats': {
            'initial':  [   0,    0,    2,    3],
            'prob 2-9': [ 0.1,  0.1,  0.4,  0.4],
            'prob 10+': [ 0.3,  0.2,  0.2,  0.3]
        },
        'secondary skills': { # chances not probabilities, should be in total 112 (113 with 'Interference')
            'Air Magic':     6,
            'Archery':       2,
            'Armorer':       1,
            #'Artillery':     1, # not supported yet
            #'Ballistics':    4, # not supported yet
            #'Diplomacy':     4, # not supported yet
            #'Eagle Eye':     8, # not supported yet
            'Earth Magic':   3,
            #'Estates':       5, # not supported yet
            'Fire Magic':    2,
            #'First Aid':     7, # not supported yet
            'Intelligence': 10,
            #'Leadership':    4, # not supported yet
            #'Learning':      4, # not supported yet
            #'Logistics':     2, # not supported yet
            #'Luck':          4, # not supported yet
            #'Mysticism':     8, # not supported yet
            #'Navigation':    1, # not supported yet
            #'Necromancy':    0, # not supported yet
            'Offense':       1,
            #'Pathfinding':   2, # not supported yet
            'Resistance':    0,
            #'Scholar':       9, # not supported yet
            #'Scouting':      2, # not supported yet
            'Sorcery':       8,
            #'Tactics':       1, # not supported yet
            'Water Magic':   3,
            'Wisdom	':      10,
            #'Interference':  0, # not supported yet
        }
    },
    'Demoniac': { # not supported yet
        'type' : 'Might',
        'faction': 'Inferno',
        'primary stats': {
            'initial':  [   2,    2,    1,    1],
            'prob 2-9': [0.35, 0.35, 0.15, 0.15],
            'prob 10+': [ 0.3,  0.3,  0.2,  0.2]
        },
        'secondary skills': { # chances not probabilities, should be in total 112 (113 with 'Interference')
            'Air Magic':     2,
            'Archery':       6,
            'Armorer':       7,
            #'Artillery':     5, # not supported yet
            #'Ballistics':    7, # not supported yet
            #'Diplomacy':     4, # not supported yet
            #'Eagle Eye':     3, # not supported yet
            'Earth Magic':   3,
            #'Estates':       3, # not supported yet
            'Fire Magic':    4,
            #'First Aid':     2, # not supported yet
            'Intelligence':  2,
            #'Leadership':    3, # not supported yet
            #'Learning':      4, # not supported yet
            #'Logistics':    10, # not supported yet
            #'Luck':          2, # not supported yet
            #'Mysticism':     2, # not supported yet
            #'Navigation':    4, # not supported yet
            #'Necromancy':    0, # not supported yet
            'Offense':       8,
            #'Pathfinding':   4, # not supported yet
            'Resistance':    6,
            #'Scholar':       2, # not supported yet
            #'Scouting':      5, # not supported yet
            'Sorcery':       3,
            #'Tactics':       6, # not supported yet
            'Water Magic':   1,
            'Wisdom	':       4,
            #'Interference':  6, # not supported yet
        }
    },
    'Heretic': { # not supported yet
        'type' : 'Magic',
        'faction': 'Inferno',
        'primary stats': {
            'initial':  [   1,    1,    2,    1],
            'prob 2-9': [0.15, 0.15, 0.35, 0.35],
            'prob 10+': [ 0.2,  0.2,  0.3,  0.3]
        },
        'secondary skills': { # chances not probabilities, should be in total 112 (113 with 'Interference')
            'Air Magic':     3,
            'Archery':       4,
            'Armorer':       4,
            #'Artillery':     4, # not supported yet
            #'Ballistics':    6, # not supported yet
            #'Diplomacy':     3, # not supported yet
            #'Eagle Eye':     4, # not supported yet
            'Earth Magic':   4,
            #'Estates':       2, # not supported yet
            'Fire Magic':    5,
            #'First Aid':     5, # not supported yet
            'Intelligence':  6,
            #'Leadership':    2, # not supported yet
            #'Learning':      4, # not supported yet
            #'Logistics':     3, # not supported yet
            #'Luck':          2, # not supported yet
            #'Mysticism':    10, # not supported yet
            #'Navigation':    2, # not supported yet
            #'Necromancy':    0, # not supported yet
            'Offense':       4,
            #'Pathfinding':   4, # not supported yet
            'Resistance':    3,
            #'Scholar':       5, # not supported yet
            #'Scouting':      3, # not supported yet
            'Sorcery':       6,
            #'Tactics':       4, # not supported yet
            'Water Magic':   2,
            'Wisdom	':       8,
            #'Interference':  0, # not supported yet
        }
    },
    'Death Knight': { # not supported yet
        'type' : 'Might',
        'faction': 'Necropolis',
        'primary stats': {
            'initial':  [   1,    2,    2,    1],
            'prob 2-9': [ 0.3, 0.25,  0.2, 0.25],
            'prob 10+': [0.25, 0.25, 0.25, 0.25]
        },
        'secondary skills': { # chances not probabilities, should be in total 112 (113 with 'Interference')
            'Air Magic':     2,
            'Archery':       5,
            'Armorer':       5,
            #'Artillery':     5, # not supported yet
            #'Ballistics':    7, # not supported yet
            #'Diplomacy':     2, # not supported yet
            #'Eagle Eye':     4, # not supported yet
            'Earth Magic':   4,
            #'Estates':       0, # not supported yet
            'Fire Magic':    1,
            #'First Aid':     0, # not supported yet
            'Intelligence':  5,
            #'Leadership':    0, # not supported yet
            #'Learning':      4, # not supported yet
            #'Logistics':     5, # not supported yet
            #'Luck':          1, # not supported yet
            #'Mysticism':     4, # not supported yet
            #'Navigation':    8, # not supported yet
            #'Necromancy':   10, # not supported yet
            'Offense':       7,
            #'Pathfinding':   4, # not supported yet
            'Resistance':    5,
            #'Scholar':       2, # not supported yet
            #'Scouting':      4, # not supported yet
            'Sorcery':       4,
            #'Tactics':       5, # not supported yet
            'Water Magic':   3,
            'Wisdom	':       6,
            #'Interference':  5, # not supported yet
        }
    },
    'Necromancer': { # not supported yet
        'type' : 'Magic',
        'faction': 'Necropolis',
        'primary stats': {
            'initial':  [   1,    0,    2,    2],
            'prob 2-9': [0.15, 0.15, 0.35, 0.35],
            'prob 10+': [0.25, 0.25, 0.25, 0.25]
        },
        'secondary skills': { # chances not probabilities, should be in total 112 (113 with 'Interference')
            'Air Magic':     3,
            'Archery':       2,
            'Armorer':       2,
            #'Artillery':     3, # not supported yet
            #'Ballistics':    5, # not supported yet
            #'Diplomacy':     4, # not supported yet
            #'Eagle Eye':     7, # not supported yet
            'Earth Magic':   8,
            #'Estates':       3, # not supported yet
            'Fire Magic':    2,
            #'First Aid':     0, # not supported yet
            'Intelligence':  6,
            #'Leadership':    0, # not supported yet
            #'Learning':      4, # not supported yet
            #'Logistics':     4, # not supported yet
            #'Luck':          1, # not supported yet
            #'Mysticism':     6, # not supported yet
            #'Navigation':    5, # not supported yet
            #'Necromancy':   10, # not supported yet
            'Offense':       3,
            #'Pathfinding':   6, # not supported yet
            'Resistance':    1,
            #'Scholar':       6, # not supported yet
            #'Scouting':      2, # not supported yet
            'Sorcery':       6,
            #'Tactics':       2, # not supported yet
            'Water Magic':   3,
            'Wisdom	':       8,
            #'Interference':  0, # not supported yet
        }
    },
    'Overlord': { # not supported yet
        'type' : 'Might',
        'faction': 'Dungeon',
        'primary stats': {
            'initial':  [   2,    2,    1,    1],
            'prob 2-9': [0.35, 0.35, 0.15, 0.15],
            'prob 10+': [ 0.3,  0.3,  0.2,  0.2]
        },
        'secondary skills': { # chances not probabilities, should be in total 112 (113 with 'Interference')
            'Air Magic':     1,
            'Archery':       6,
            'Armorer':       6,
            #'Artillery':     8, # not supported yet
            #'Ballistics':    7, # not supported yet
            #'Diplomacy':     3, # not supported yet
            #'Eagle Eye':     2, # not supported yet
            'Earth Magic':   3,
            #'Estates':       4, # not supported yet
            'Fire Magic':    2,
            #'First Aid':     1, # not supported yet
            'Intelligence':  1,
            #'Leadership':    8, # not supported yet
            #'Learning':      4, # not supported yet
            #'Logistics':     8, # not supported yet
            #'Luck':          1, # not supported yet
            #'Mysticism':     3, # not supported yet
            #'Navigation':    4, # not supported yet
            #'Necromancy':    0, # not supported yet
            'Offense':       8,
            #'Pathfinding':   5, # not supported yet
            'Resistance':    6,
            #'Scholar':       1, # not supported yet
            #'Scouting':      5, # not supported yet
            'Sorcery':       2,
            #'Tactics':      10, # not supported yet
            'Water Magic':   0,
            'Wisdom	':       3,
            #'Interference':  6, # not supported yet
        }
    },
    'Warlock': { # not supported yet
        'type' : 'Magic',
        'faction': 'Dungeon',
        'primary stats': {
            'initial':  [   0,    0,    3,    2],
            'prob 2-9': [ 0.1,  0.1,  0.5,  0.3],
            'prob 10+': [ 0.2,  0.2,  0.3,  0.3]
        },
        'secondary skills': { # chances not probabilities, should be in total 112 (113 with 'Interference')
            'Air Magic':     2,
            'Archery':       2,
            'Armorer':       1,
            #'Artillery':     1, # not supported yet
            #'Ballistics':    6, # not supported yet
            #'Diplomacy':     4, # not supported yet
            #'Eagle Eye':     8, # not supported yet
            'Earth Magic':   5,
            #'Estates':       5, # not supported yet
            'Fire Magic':    5,
            #'First Aid':     6, # not supported yet
            'Intelligence':  8,
            #'Leadership':    3, # not supported yet
            #'Learning':      4, # not supported yet
            #'Logistics':     2, # not supported yet
            #'Luck':          2, # not supported yet
            #'Mysticism':     8, # not supported yet
            #'Navigation':    4, # not supported yet
            #'Necromancy':    0, # not supported yet
            'Offense':       1,
            #'Pathfinding':   2, # not supported yet
            'Resistance':    0,
            #'Scholar':       8, # not supported yet
            #'Scouting':      2, # not supported yet
            'Sorcery':      10,
            #'Tactics':       1, # not supported yet
            'Water Magic':   2,
            'Wisdom	':      10,
            #'Interference':  0, # not supported yet
        }
    },
    'Barbarian': { # not supported yet
        'type' : 'Might',
        'faction': 'Stronghold',
        'primary stats': {
            'initial':  [   4,    0,    1,    1],
            'prob 2-9': [0.55, 0.35, 0.05, 0.05],
            'prob 10+': [ 0.3,  0.3,  0.2,  0.2]
        },
        'secondary skills': { # chances not probabilities, should be in total 112 (113 with 'Interference')
            'Air Magic':     3,
            'Archery':       7,
            'Armorer':       6,
            #'Artillery':     8, # not supported yet
            #'Ballistics':    8, # not supported yet
            #'Diplomacy':     1, # not supported yet
            #'Eagle Eye':     2, # not supported yet
            'Earth Magic':   3,
            #'Estates':       2, # not supported yet
            'Fire Magic':    2,
            #'First Aid':     1, # not supported yet
            'Intelligence':  1,
            #'Leadership':    5, # not supported yet
            #'Learning':      4, # not supported yet
            #'Logistics':     7, # not supported yet
            #'Luck':          3, # not supported yet
            #'Mysticism':     3, # not supported yet
            #'Navigation':    2, # not supported yet
            #'Necromancy':    0, # not supported yet
            'Offense':      10,
            #'Pathfinding':   8, # not supported yet
            'Resistance':    6,
            #'Scholar':       1, # not supported yet
            #'Scouting':      8, # not supported yet
            'Sorcery':       1,
            #'Tactics':       8, # not supported yet
            'Water Magic':   0,
            'Wisdom	':       2,
            #'Interference':  6, # not supported yet
        }
    },
    'Battle Mage': { # not supported yet
        'type' : 'Magic',
        'faction': 'Stronghold',
        'primary stats': {
            'initial':  [   2,    1,    1,    1],
            'prob 2-9': [ 0.3,  0.2, 0.25, 0.25],
            'prob 10+': [0.25, 0.25, 0.25, 0.25]
        },
        'secondary skills': { # chances not probabilities, should be in total 112 (113 with 'Interference')
            'Air Magic':     3,
            'Archery':       4,
            'Armorer':       4,
            #'Artillery':     4, # not supported yet
            #'Ballistics':    6, # not supported yet
            #'Diplomacy':     3, # not supported yet
            #'Eagle Eye':     5, # not supported yet
            'Earth Magic':   3,
            #'Estates':       1, # not supported yet
            'Fire Magic':    3,
            #'First Aid':     4, # not supported yet
            'Intelligence':  5,
            #'Leadership':    4, # not supported yet
            #'Learning':      4, # not supported yet
            #'Logistics':     9, # not supported yet
            #'Luck':          2, # not supported yet
            #'Mysticism':     4, # not supported yet
            #'Navigation':    0, # not supported yet
            #'Necromancy':    0, # not supported yet
            'Offense':       8,
            #'Pathfinding':   4, # not supported yet
            'Resistance':    4,
            #'Scholar':       4, # not supported yet
            #'Scouting':      4, # not supported yet
            'Sorcery':       6,
            #'Tactics':       5, # not supported yet
            'Water Magic':   3,
            'Wisdom	':       6,
            #'Interference':  1, # not supported yet
        }
    },
    'Beastmaster': { # not supported yet
        'type' : 'Might',
        'faction': 'Fortress',
        'primary stats': {
            'initial':  [   0,    4,    1,    1],
            'prob 2-9': [ 0.3,  0.5,  0.1,  0.1],
            'prob 10+': [ 0.3,  0.3,  0.2,  0.2]
        },
        'secondary skills': { # chances not probabilities, should be in total 112 (113 with 'Interference')
            'Air Magic':     1,
            'Archery':       7,
            'Armorer':      10,
            #'Artillery':     8, # not supported yet
            #'Ballistics':    7, # not supported yet
            #'Diplomacy':     1, # not supported yet
            #'Eagle Eye':     1, # not supported yet
            'Earth Magic':   3,
            #'Estates':       1, # not supported yet
            'Fire Magic':    0,
            #'First Aid':     6, # not supported yet
            'Intelligence':  1,
            #'Leadership':    5, # not supported yet
            #'Learning':      4, # not supported yet
            #'Logistics':     8, # not supported yet
            #'Luck':          2, # not supported yet
            #'Mysticism':     2, # not supported yet
            #'Navigation':    8, # not supported yet
            #'Necromancy':    0, # not supported yet
            'Offense':       5,
            #'Pathfinding':   8, # not supported yet
            'Resistance':    5,
            #'Scholar':       1, # not supported yet
            #'Scouting':      7, # not supported yet
            'Sorcery':       1,
            #'Tactics':       6, # not supported yet
            'Water Magic':   2,
            'Wisdom	':       2,
            #'Interference':  5, # not supported yet
        }
    },
    'Witch': { # not supported yet
        'type' : 'Magic',
        'faction': 'Fortress',
        'primary stats': {
            'initial':  [   0,    1,    2,    2],
            'prob 2-9': [0.05, 0.15,  0.4,  0.4],
            'prob 10+': [ 0.2,  0.2,  0.3,  0.3]
        },
        'secondary skills': { # chances not probabilities, should be in total 112 (113 with 'Interference')
            'Air Magic':     3,
            'Archery':       3,
            'Armorer':       4,
            #'Artillery':     1, # not supported yet
            #'Ballistics':    8, # not supported yet
            #'Diplomacy':     2, # not supported yet
            #'Eagle Eye':    10, # not supported yet
            'Earth Magic':   3,
            #'Estates':       1, # not supported yet
            'Fire Magic':    3,
            #'First Aid':     8, # not supported yet
            'Intelligence':  7,
            #'Leadership':    1, # not supported yet
            #'Learning':      4, # not supported yet
            #'Logistics':     3, # not supported yet
            #'Luck':          4, # not supported yet
            #'Mysticism':     8, # not supported yet
            #'Navigation':    6, # not supported yet
            #'Necromancy':    0, # not supported yet
            'Offense':       2,
            #'Pathfinding':   2, # not supported yet
            'Resistance':    0,
            #'Scholar':       7, # not supported yet
            #'Scouting':      2, # not supported yet
            'Sorcery':       8,
            #'Tactics':       1, # not supported yet
            'Water Magic':   3,
            'Wisdom	':       8,
            #'Interference':  0, # not supported yet
        }
    },
    'Planeswalker': { # not supported yet
        'type' : 'Might',
        'faction': 'Conflux',
        'primary stats': {
            'initial':  [   3,    1,    1,    1],
            'prob 2-9': [0.45, 0.25, 0.15, 0.15],
            'prob 10+': [ 0.3,  0.3,  0.2,  0.2]
        },
        'secondary skills': { # chances not probabilities, should be in total 112 (113 with 'Interference')
            'Air Magic':     2,
            'Archery':       8,
            'Armorer':       5,
            #'Artillery':     8, # not supported yet
            #'Ballistics':    8, # not supported yet
            #'Diplomacy':     2, # not supported yet
            #'Eagle Eye':     2, # not supported yet
            'Earth Magic':   3,
            #'Estates':       3, # not supported yet
            'Fire Magic':    3,
            #'First Aid':     1, # not supported yet
            'Intelligence':  1,
            #'Leadership':    3, # not supported yet
            #'Learning':      8, # not supported yet
            #'Logistics':     8, # not supported yet
            #'Luck':          2, # not supported yet
            #'Mysticism':     3, # not supported yet
            #'Navigation':    5, # not supported yet
            #'Necromancy':    0, # not supported yet
            'Offense':       9,
            #'Pathfinding':   6, # not supported yet
            'Resistance':    2,
            #'Scholar':       1, # not supported yet
            #'Scouting':      6, # not supported yet
            'Sorcery':       1,
            #'Tactics':       8, # not supported yet
            'Water Magic':   2,
            'Wisdom	':       2,
            #'Interference':  2, # not supported yet
        }
    },
    'Elementalist': { # not supported yet
        'type' : 'Magic',
        'faction': 'Conflux',
        'primary stats': {
            'initial':  [   0,    0,    3,    3],
            'prob 2-9': [0.15, 0.15, 0.35, 0.35],
            'prob 10+': [0.25, 0.25, 0.25, 0.25]
        },
        'secondary skills': { # chances not probabilities, should be in total 112 (113 with 'Interference')
            'Air Magic':     6,
            'Archery':       2,
            'Armorer':       1,
            #'Artillery':     1, # not supported yet
            #'Ballistics':    4, # not supported yet
            #'Diplomacy':     4, # not supported yet
            #'Eagle Eye':     8, # not supported yet
            'Earth Magic':   6,
            #'Estates':       3, # not supported yet
            'Fire Magic':    6,
            #'First Aid':     4, # not supported yet
            'Intelligence':  8,
            #'Leadership':    3, # not supported yet
            #'Learning':      4, # not supported yet
            #'Logistics':     2, # not supported yet
            #'Luck':          2, # not supported yet
            #'Mysticism':     8, # not supported yet
            #'Navigation':    4, # not supported yet
            #'Necromancy':    0, # not supported yet
            'Offense':       1,
            #'Pathfinding':   2, # not supported yet
            'Resistance':    0,
            #'Scholar':       8, # not supported yet
            #'Scouting':      2, # not supported yet
            'Sorcery':       8,
            #'Tactics':       1, # not supported yet
            'Water Magic':   6,
            'Wisdom	':       8,
            #'Interference':  0, # not supported yet
        }
    },
    'Captain': { # not supported yet
        'type' : 'Might',
        'faction': 'Cove',
        'primary stats': {
            'initial':  [   3,    0,    2,    1],
            'prob 2-9': [0.45, 0.25,  0.2,  0.1],
            'prob 10+': [ 0.3,  0.3,  0.2,  0.2]
        },
        'secondary skills': { # chances not probabilities, should be in total 112 (113 with 'Interference')
            'Air Magic':     3,
            'Archery':       9,
            'Armorer':       2,
            #'Artillery':     5, # not supported yet
            #'Ballistics':    5, # not supported yet
            #'Diplomacy':     5, # not supported yet
            #'Eagle Eye':     4, # not supported yet
            'Earth Magic':   4,
            #'Estates':       4, # not supported yet
            'Fire Magic':    2,
            #'First Aid':     2, # not supported yet
            'Intelligence':  3,
            #'Leadership':    6, # not supported yet
            #'Learning':      2, # not supported yet
            #'Logistics':     6, # not supported yet
            #'Luck':          7, # not supported yet
            #'Mysticism':     1, # not supported yet
            #'Navigation':    6, # not supported yet
            #'Necromancy':    0, # not supported yet
            'Offense':       9,
            #'Pathfinding':   8, # not supported yet
            'Resistance':    3,
            #'Scholar':       1, # not supported yet
            #'Scouting':      4, # not supported yet
            'Sorcery':       2,
            #'Tactics':       6, # not supported yet
            'Water Magic':   2,
            'Wisdom	':       1,
            #'Interference':  3, # not supported yet
        }
    },
    'Navigator': { # not supported yet
        'type' : 'Magic',
        'faction': 'Cove',
        'primary stats': {
            'initial':  [   2,    0,    1,    2],
            'prob 2-9': [0.15,  0.1,  0.4, 0.35],
            'prob 10+': [ 0.3,  0.2,  0.2,  0.3]
        },
        'secondary skills': { # chances not probabilities, should be in total 112 (113 with 'Interference')
            'Air Magic':     6,
            'Archery':       6,
            'Armorer':       1,
            #'Artillery':     1, # not supported yet
            #'Ballistics':    2, # not supported yet
            #'Diplomacy':     2, # not supported yet
            #'Eagle Eye':     2, # not supported yet
            'Earth Magic':   5,
            #'Estates':       2, # not supported yet
            'Fire Magic':    2,
            #'First Aid':     4, # not supported yet
            'Intelligence':  8,
            #'Leadership':    2, # not supported yet
            #'Learning':      4, # not supported yet
            #'Logistics':     3, # not supported yet
            #'Luck':          4, # not supported yet
            #'Mysticism':     3, # not supported yet
            #'Navigation':    6, # not supported yet
            #'Necromancy':    0, # not supported yet
            'Offense':       4,
            #'Pathfinding':   6, # not supported yet
            'Resistance':    5,
            #'Scholar':       5, # not supported yet
            #'Scouting':      2, # not supported yet
            'Sorcery':       6,
            #'Tactics':       4, # not supported yet
            'Water Magic':   9,
            'Wisdom	':       8,
            #'Interference':  1, # not supported yet
        }
    },
}

# id: (base name,
#   basic    value,
#   advanced value,
#   expert   value,
#   description)
HeroSkills = {
    0:  ('Archery',       0.1,  0.25,   0.5,  'Increases the damage done by range attacking creatures'),
    1:  ('Offense',       0.1,   0.2,   0.3,  'Increases all hand-to-hand damage inflicted by the hero''s troops'),
    2:  ('Armorer',      0.05,   0.1,  0.15,  'Reduces all damage inflicted against the hero\'s troops'),
    9:  ('Resistance',   0.05,   0.1,   0.2,  'Endows a hero\'s troops with magic resistance'),
    3:  ('Air',          0.05,   0.1,  0.15,  'Increases the effectiveness and reduces the costs of spells from the School of Air Magic'),
    4:  ('Earth',        0.05,   0.1,  0.15,  'Increases the effectiveness and reduces the costs of spells from the School of Earth Magic'),
    5:  ('Fire',         0.05,   0.1,  0.15,  'Increases the effectiveness and reduces the costs of spells from the School of Fire Magic'),
    6:  ('Water',        0.05,   0.1,  0.15,  'Increases the effectiveness and reduces the costs of spells from the School of Water Magic'),
    7:  ('Wisdom',          3,     4,     5,  'Allows your hero to learn third, fourth, and fifth level spells'),
    # in vanilla game it's 0.05, 0.1, 0.15, but that is way to low!
    8:  ('Sorcery',       0.1,   0.2,   0.3,   'Causes a hero\'s spells to inflict an additional damage in combat'),
    10: ('Intelligence', 0.25,   0.5,     1,   'Increases a hero\'s normal maximum spell points'),
}

# id: (
#   [0]  base name,
#   [1]  basic    value,
#   [2]  advanced value,
#   [3]  expert   value,
#   [4]  value per spell power,
#   [5]  school of magic id (3=Air, 4=Earth, 5=Fire, 6=Water, -1=All/Any),
#   [6]  level,
#   [7]  target (0=No target, 1=Ally, 2=Enemy, 3=Ally/Enemy, 4=Ground),
#   [8]  radius,
#   [9]  cost full,
#   [10] cost reduced,
#   [11] description)
HeroSpells = {
    #    0                         1     2     3   4   5  6   7   8   9  10  11
    #
    # this spell is the only stupid exception   =-1 means it's of all 4 schools of magic
    2:  ('Magic Arrow',           10,   20,   30, 10, -1, 1,  2,  0,  5,  4, 'Causes a bolt of magical energy to strike the selected enemy unit, dealing magic damage'),
    
    # Air                                             =3
    4:  ('Haste',                  3,    5,    5,  0,  3, 1,  1,  0,  6,  5, 'Increases the speed of the selected allied unit'),
    3:  ('Lightning Bolt',        10,   20,   50, 25,  3, 2,  2,  0, 10,  8, 'Causes a bolt of lightning to strike the selected unit, dealing damage'),
    15: ('Precision',              3,    6,    6,  0,  3, 2,  1,  0,  8,  6, 'Increases the selected friendly ranged unit\'s attack strength for ranged attacks'),
    20: ('Protection from Air',  0.3,  0.5,  0.5,  0,  3, 2,  1,  0, 12,  9, 'Protects the selected friendly unit, reducing damage it received from Air spells'),
    1:  ('Air Shield',          0.25,  0.5,  0.5,  0,  3, 3,  1,  0, 12,  9, 'Target, allied troop takes less damage from ranged attacks'),
    # homm3 game has 17 Air spells (19 with Titan's Lightning Bolt, and Magic Arrow)
    
    # Earth                                           =4
    0:  ('Shield',              0.15,  0.3,  0.3,  0,  4, 1,  1,  0,  5,  4, 'Reduces melee damage done to target allied unit'),
    5:  ('Stone Skin',             3,    6,    6,  0,  4, 1,  1,  0,  5,  4, 'Increases the selected friendly unit\'s defense strength'),
    18: ('Slow',                0.25,  0.5,  0.5,  0,  4, 1,  2,  0,  6,  5, 'Reduces the speed of the selected enemy unit'),
    6:  ('Meteor Shower',         25,   50,  100, 25,  4, 4,  4,  1, 16, 12, 'Does damage to all creatures in target hex and all adjacent hexes'),
    7:  ('Implosion',            100,  200,  300, 75,  4, 5,  2,  0, 30, 25, 'Target enemy troop receives damage, the most destructive spell for a single creature stack'),
    # homm3 game has 19 Earth spells
    
    # Fire                                            =5
    8:  ('Bloodlust',              3,    6,    6,  0,  5, 1,  1,  0,  5,  4, 'Increases the attack skill of target allied creature for melee attacks'),
    16: ('Curse',                  0,   -1,   -1,  0,  5, 1,  2,  0, 16, 12, 'Causes the selected enemy unit to inflict minimum damage when attacking, less than minimum at greater skill levels'),
    9:  ('Fireball',              15,   30,   60, 10,  5, 3,  4,  1, 15, 12, 'Stacks in target hex and it\'s surrounding hexes take damage'),
    10: ('Frenzy',                 1,  1.5,    2,  0,  5, 4,  3,  0, 16, 12, 'Target allied troop\'s defense is reduced to 0, but attack is increased considerably'),
    19: ('Inferno',               20,   40,   80, 10,  5, 4,  4,  2, 16, 12, 'It creates massive flames, that covers the target hex and two hexes around it causing damage to all creatures within range'),
    # homm3 game has 17 Fire spells
    
    # Water                                           =6
    11: ('Bless',                  0,    1,    1,  0,  6, 1,  1,  0,  5,  4, 'Causes the selected friendly unit to inflict maximum damage when it attacks, more than maximum at greater skill levels'),
    12: ('Cure',                  10,   20,   30,  5,  6, 1,  1,  0,  6,  5, 'Removes all negative spell effects from the selected friendly unit and heals it'),
    13: ('Ice Bolt',              10,   20,   50, 20,  6, 2,  2,  0,  8,  6, 'Drains the body heat from the selected enemy unit, dealing damage'),
    17: ('Weakness',              -3,   -6,   -6,  0,  6, 2,  2,  0,  8,  6, 'Reduces the selected enemy unit\'s attack strength'),
    14: ('Prayer',                 2,    4,    4,  0,  6, 4,  1,  0, 16, 12, 'Target, allied troop\'s attack, defense, and speed (hexes per turn) ratings are increased'),
    # homm3 game has 19 Water spells
}

HeroDefinitions = {
    # name: (
    #   class
    #   starting skill 1,
    #   starting skill 2,
    #   list of starting army:
    #       unit type, min, max
    #   )
    # TODO: add hero specializations, 
    'Mig Off Arm':    ('Knight',  1,  2,  [(1, 10, 20), (1, 10, 20), (5,  2,  3)]),
    'Mig Arc Arm':    ('Knight',  0,  2,  [(3,  4,  7), (3,  4,  7), (5,  2,  3)]),
    'Mig Off Res':    ('Knight',  1,  9,  [(1, 10, 20), (3,  4,  7), (5,  2,  3)]),
    'Mig Arc Res':    ('Knight',  0,  9,  [(3,  4,  7), (3,  4,  7), (3,  4,  7)]),
    'Mig Arm Res':    ('Knight',  2,  9,  [(1, 10, 20), (3,  4,  7), (5,  2,  3)]),
    'Mag Wis Air':    ('Cleric',  3,  7,  [(1, 10, 20), (3,  4,  7), (5,  2,  3)]),
    'Mag Wis Ear':    ('Cleric',  4,  7,  [(1, 10, 20), (3,  4,  7), (5,  2,  3)]),
    'Mag Wis Fir':    ('Cleric',  5,  7,  [(1, 10, 20), (3,  4,  7), (5,  2,  3)]),
    'Mag Wis Wat':    ('Cleric',  6,  7,  [(1, 10, 20), (3,  4,  7), (5,  2,  3)]),
    'Mag Int Air':    ('Cleric',  3, 10,  [(1, 10, 20), (3,  4,  7), (5,  2,  3)]),
    'Mag Int Ear':    ('Cleric',  4, 10,  [(1, 10, 20), (3,  4,  7), (5,  2,  3)]),
}
