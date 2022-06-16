
TileTypes = {
    0: {'name':'free', 'symbol': ' '},
    1: {'name':'resource'},
    2: {'name':'hero or army', 'symbol': 'h'},
    3: {'name':'road', 'symbol':'.'},
    4: {'name':'wall', 'symbol': '#'},
    5: {'name':'subterannean'},
}
TileTypesByName = {
    'free':0,
    'resource':1,
    'hero or army':2,
    'road':3,
    'wall':4,
    'subterannean':5,
}
def is_valid_dest_tile(tyle_type:int) -> bool:
    return tyle_type in [TileTypesByName['free'], TileTypesByName['resource'], TileTypesByName['hero or army'], TileTypesByName['road']]
def can_step_on(tyle_type:int) -> bool:
    return tyle_type in [TileTypesByName['free'], TileTypesByName['road']]

# source https://heroes.thelazy.net/index.php/Adventure_Map

TownTiles = [
                        (-2,-1),(-2, 0),(-2,+1),
                (-1,-2),(-1,-1),(-1, 0),(-1,+1),(-1,+2),
                ( 0,-2),( 0,-1),        ( 0,+1),( 0,+2),
            ]

# these are not implemented yet
TerrainTypes = {
     1: { 'name': 'Grass',            'factor': 1 },
     2: { 'name': 'Highlands ',       'factor': 1 },
     3: { 'name': 'Dirt',             'factor': 1 },
     4: { 'name': 'Lava',             'factor': 1 },
     5: { 'name': 'Rock',             'factor': -1 }, # this cannot be moved on at all
     6: { 'name': 'Rough',            'factor': 1.25 },
     7: { 'name': 'Wasteland',        'factor': 1.25 },
     8: { 'name': 'Sand',             'factor': 1.5 },
     9: { 'name': 'Snow',             'factor': 1.5 },
    10: { 'name': 'Swamp',            'factor': 1.75 },
    #'Subterranean': { 'id':  11, 'movement cost': 1 },
    11: { 'name': 'Dirt road',        'factor': 0.75 },
    12: { 'name': 'Gravel road',      'factor': 0.65 },
    13: { 'name': 'Cobblestone road', 'factor': 0.5 },
}
TerrainTypesByName = {
    'Grass'           :  1,
    'Highlands '      :  2,
    'Dirt'            :  3,
    'Lava'            :  4,
    'Rock'            :  5,
    'Rough'           :  6,
    'Wasteland'       :  7,
    'Sand'            :  8,
    'Snow'            :  9,
    'Swamp'           : 10,
    'Dirt road'       : 11,
    'Gravel road'     : 12,
    'Cobblestone road': 13,
}

MapObjectTypes = {
    'Gold pile':      { 'id': 12, 'symbol': 'g'},
    'Wood pile':      { 'id': 13, 'symbol': 'w'},
    'Ore pile':       { 'id': 14, 'symbol': 'o'},
    'Mercury pile':   { 'id': 15, 'symbol': 'm'},
    'Sulfur pile':    { 'id': 16, 'symbol': 's'},
    'Crystal pile':   { 'id': 17, 'symbol': 'c'},
    'Gems pile':      { 'id': 18, 'symbol': 'e'},
    'Treasure Chest': { 'id': 19, 'symbol': 't'},
    'Artifact':       { 'id': 20, 'symbol': '*'},

    'Castle Town':    { 'id': 30, 'symbol': 'T'},
}
MapObjTypeById = {
    12: 'Gold pile',
    13: 'Wood pile',
    14: 'Ore pile',
    15: 'Mercury pile',
    16: 'Sulfur pile',
    17: 'Crystal pile',
    18: 'Gems pile',
    19: 'Treasure Chest',
    20: 'Artifact',
    30: 'Castle Town', # TODO: refactor these
}
MapResPileToIdx = {
    12: 0, # Gold pile
    13: 1, # Wood pile
    14: 2, # Ore pile
    15: 3, # Mercury pile
    16: 4, # Sulfur pile
    17: 5, # Crystal pile
    18: 6, # Gems pile
}

MapResPileTypicalValues = {
    12: 500, # Gold pile
    13: 7, # Wood pile
    14: 7, # Ore pile
    15: 4, # Mercury pile
    16: 4, # Sulfur pile
    17: 4, # Crystal pile
    18: 4, # Gems pile
}

ResourcesConversionToGoldByIdx = {
    0:  1, # Gold to gold is 1:1
    1: 25, # Wood sold as 25 gold
    2: 25, # Ore sold as 25 gold
    3: 50, # Mercury sold as 50 gold
    4: 50, # Sulfur sold as 50 gold
    5: 50, # Crystal sold as 50 gold
    6: 50, # Gems sold as 50 gold
}
