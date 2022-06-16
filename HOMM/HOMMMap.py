import json
import csv
import numpy as np
from HOMM.HOMMAPI import HOMMArmy, HOMMArmyStack, HOMMHero, HOMMMap
from HOMM.HOMMData.HOMMMapData import MapObjTypeById, MapObjectTypes, MapResPileToIdx, MapResPileTypicalValues, TileTypesByName, TownTiles
from HOMM.HOMMData.HOMMUnitData import UnitTypes
from HOMM.HOMMUnitTypes import UnitUtils

from HOMM.HOMMEnv import HOMMSimpleEnv
from HOMM.Town import CastleTown

#from Town import Town

TOWN_TYPES = [
    'Castle',
    'Rampart', # not supported yet
    'Tower',  # not supported yet
    'Inferno',  # not supported yet
    'Necropolis',  # not supported yet
    'Dungeon',  # not supported yet
    'Stronghold',  # not supported yet
    'Fortress',  # not supported yet
    'Conflux',  # not supported yet
    'Cove', # not supported yet
]

# TODO: implement proper reading of template files (.tsv) and generate according
class HOMMTemplate(object):
    SIZES = {
        "T":  ( 19,  19), # not sure if viable
        "S-": ( 27,  27), # might not be small enough, or might not be viable
        "S":  ( 36,  36),
        "S+": ( 36,  56),
        "M":  ( 72,  72),
        "L":  (108, 108),
        "XL": (144, 144),
        "H":  (180, 180),
        "XH": (216, 216),
        "G":  (252, 252)
    }
    def __init__(self, filename:str=None):
        if filename:
            if filename.endswith('.tsv'):
                self.__read_tsv__(filename)
            self.filename = filename
        else:
            self.name = '2Empty'
            self.min_size = HOMMTemplate.SIZES["S"]
            self.max_size = HOMMTemplate.SIZES["XL"]
            self.filename = None
    
    def __read_tsv__(self, filename):
        tsv_file = open(filename)
        read_tsv = csv.reader(tsv_file, delimiter='\t')
        
        column_indexes = {}
        cur_row_num = 0
        cur_row_context = {}
        for row in read_tsv:
            if cur_row_num == 0:
                column_indexes['Map'] = row.index('Map')
                column_indexes['Zone'] = row.index('Zone')
                column_indexes['Connections'] = row.index('Connections')

            elif cur_row_num == 1:
                column_indexes['Zone Type'] = row.index('Type', column_indexes['Zone'])
                column_indexes['Zone Restrictions'] = row.index('Restrictions', column_indexes['Zone'])
                column_indexes['Zone Player towns'] = row.index('Player towns', column_indexes['Zone'])
                column_indexes['Zone Neutral towns'] = row.index('Neutral towns', column_indexes['Zone'])
                column_indexes['Zone Town types'] = row.index('Town types', column_indexes['Zone'])
                column_indexes['Zone Minimum mines'] = row.index('Minimum mines', column_indexes['Zone'])
                column_indexes['Zone Mine Density'] = row.index('Mine Density', column_indexes['Zone'])
                column_indexes['Zone Terrain'] = row.index('Terrain', column_indexes['Zone'])
                column_indexes['Zone Monsters'] = row.index('Monsters', column_indexes['Zone'])
                column_indexes['Zone Treasure'] = row.index('Treasure', column_indexes['Zone'])
                column_indexes['Zone Options'] = row.index('Options', column_indexes['Zone'])
                
                column_indexes['Connections Zones'] = row.index('Zones', column_indexes['Connections'])
                column_indexes['Connections Options'] = row.index('Options', column_indexes['Connections'])
                
            elif cur_row_num == 2:
                # map
                column_indexes['Name'] = row.index('Name', column_indexes['Map'])
                column_indexes['Minimum Size'] = row.index('Minimum Size', column_indexes['Map'])
                column_indexes['Maximum Size'] = row.index('Maximum Size', column_indexes['Map'])

                # zone
                column_indexes['Zone Id'] = row.index('Id', column_indexes['Zone'])
                # zone type
                column_indexes['Zone Type human start'] = row.index('human start', column_indexes['Zone Type'])
                column_indexes['Zone Type computer start'] = row.index('computer start', column_indexes['Zone Type'])
                column_indexes['Zone Type Treasure'] = row.index('Treasure', column_indexes['Zone Type'])
                column_indexes['Zone Type Base Size'] = row.index('Base Size', column_indexes['Zone Type'])
                # zone player towns
                column_indexes['Zone Player towns Ownership'] = row.index('Ownership', column_indexes['Zone Player towns'])
                column_indexes['Zone Player towns Minimum towns'] = row.index('Minimum towns', column_indexes['Zone Player towns'])
                column_indexes['Zone Player towns Minimum castles'] = row.index('Minimum castles', column_indexes['Zone Player towns'])
                column_indexes['Zone Player towns Town Density'] = row.index('Town Density', column_indexes['Zone Player towns'])
                column_indexes['Zone Player towns Castle Density'] = row.index('Castle Density', column_indexes['Zone Player towns'])
                # zone neutral towns
                column_indexes['Zone Neutral towns Ownership'] = row.index('Ownership', column_indexes['Zone Neutral towns'])
                column_indexes['Zone Neutral towns Minimum towns'] = row.index('Minimum towns', column_indexes['Zone Neutral towns'])
                column_indexes['Zone Neutral towns Minimum castles'] = row.index('Minimum castles', column_indexes['Zone Neutral towns'])
                column_indexes['Zone Neutral towns Town Density'] = row.index('Town Density', column_indexes['Zone Neutral towns'])
                column_indexes['Zone Neutral towns Castle Density'] = row.index('Castle Density', column_indexes['Zone Neutral towns'])
                # zone town types
                column_indexes['Zone Town types Castle'] = row.index('Castle', column_indexes['Zone Town types'])
                column_indexes['Zone Town types Rampart'] = row.index('Rampart', column_indexes['Zone Town types'])
                column_indexes['Zone Town types Tower'] = row.index('Tower', column_indexes['Zone Town types'])
                column_indexes['Zone Town types Inferno'] = row.index('Inferno', column_indexes['Zone Town types'])
                column_indexes['Zone Town types Necropolis'] = row.index('Necropolis', column_indexes['Zone Town types'])
                column_indexes['Zone Town types Dungeon'] = row.index('Dungeon', column_indexes['Zone Town types'])
                column_indexes['Zone Town types Stronghold'] = row.index('Stronghold', column_indexes['Zone Town types'])
                column_indexes['Zone Town types Fortress'] = row.index('Fortress', column_indexes['Zone Town types'])
                column_indexes['Zone Town types Conflux'] = row.index('Conflux', column_indexes['Zone Town types'])
                column_indexes['Zone Town types Cove'] = row.index('Cove', column_indexes['Zone Town types'])
                # zone minimum mines
                column_indexes['Zone Minimum mines Wood'] = row.index('Wood', column_indexes['Zone Minimum mines'])
                column_indexes['Zone Minimum mines Mercury'] = row.index('Mercury', column_indexes['Zone Minimum mines'])
                column_indexes['Zone Minimum mines Ore'] = row.index('Ore', column_indexes['Zone Minimum mines'])
                column_indexes['Zone Minimum mines Sulfur'] = row.index('Sulfur', column_indexes['Zone Minimum mines'])
                column_indexes['Zone Minimum mines Crystal'] = row.index('Crystal', column_indexes['Zone Minimum mines'])
                column_indexes['Zone Minimum mines Gems'] = row.index('Gems', column_indexes['Zone Minimum mines'])
                column_indexes['Zone Minimum mines Gold'] = row.index('Gold', column_indexes['Zone Minimum mines'])
                # zone terrain
                column_indexes['Zone Terrain Match to town'] = row.index('Match to town', column_indexes['Zone Terrain'])
                column_indexes['Zone Terrain Dirt'] = row.index('Dirt', column_indexes['Zone Terrain'])
                column_indexes['Zone Terrain Sand'] = row.index('Sand', column_indexes['Zone Terrain'])
                column_indexes['Zone Terrain Grass'] = row.index('Grass', column_indexes['Zone Terrain'])
                column_indexes['Zone Terrain Snow'] = row.index('Snow', column_indexes['Zone Terrain'])
                column_indexes['Zone Terrain Swamp'] = row.index('Swamp', column_indexes['Zone Terrain'])
                column_indexes['Zone Terrain Rough'] = row.index('Rough', column_indexes['Zone Terrain'])
                column_indexes['Zone Terrain Cave'] = row.index('Cave', column_indexes['Zone Terrain'])
                column_indexes['Zone Terrain Lava'] = row.index('Lava', column_indexes['Zone Terrain'])
                column_indexes['Zone Terrain Highlands'] = row.index('Highlands', column_indexes['Zone Terrain'])
                column_indexes['Zone Terrain Wasteland'] = row.index('Wasteland', column_indexes['Zone Terrain'])
                # zone monsters
                column_indexes['Zone Monsters Strength'] = row.index('Strength', column_indexes['Zone Monsters'])
                column_indexes['Zone Monsters Match to town'] = row.index('Match to town', column_indexes['Zone Monsters'])
                column_indexes['Zone Monsters Neutral'] = row.index('Neutral', column_indexes['Zone Monsters'])
                column_indexes['Zone Monsters Castle'] = row.index('Castle', column_indexes['Zone Monsters'])
                column_indexes['Zone Monsters Rampart'] = row.index('Rampart', column_indexes['Zone Monsters'])
                column_indexes['Zone Monsters Tower'] = row.index('Tower', column_indexes['Zone Monsters'])
                column_indexes['Zone Monsters Inferno'] = row.index('Inferno', column_indexes['Zone Monsters'])
                column_indexes['Zone Monsters Necropolis'] = row.index('Necropolis', column_indexes['Zone Monsters'])
                column_indexes['Zone Monsters Dungeon'] = row.index('Dungeon', column_indexes['Zone Monsters'])
                column_indexes['Zone Monsters Stronghold'] = row.index('Stronghold', column_indexes['Zone Monsters'])
                column_indexes['Zone Monsters Fortress'] = row.index('Fortress', column_indexes['Zone Monsters'])
                column_indexes['Zone Monsters Conflux'] = row.index('Conflux', column_indexes['Zone Monsters'])
                column_indexes['Zone Monsters Cove'] = row.index('Cove', column_indexes['Zone Monsters'])
                # zone treasure
                column_indexes['Zone Treasure 1 Low'] = row.index('Low', column_indexes['Zone Treasure'])
                column_indexes['Zone Treasure 1 High'] = row.index('High', column_indexes['Zone Treasure'])
                column_indexes['Zone Treasure 1 Density'] = row.index('Density', column_indexes['Zone Treasure'])
                try:
                    column_indexes['Zone Treasure 2 Low'] = row.index('Low', column_indexes['Zone Treasure'] + 3)
                    column_indexes['Zone Treasure 2 High'] = row.index('High', column_indexes['Zone Treasure'] + 3)
                    column_indexes['Zone Treasure 2 Density'] = row.index('Density', column_indexes['Zone Treasure'] + 3)
                except:
                    pass
                try:
                    column_indexes['Zone Treasure 3 Low'] = row.index('Low', column_indexes['Zone Treasure'] + 6)
                    column_indexes['Zone Treasure 3 High'] = row.index('High', column_indexes['Zone Treasure'] + 6)
                    column_indexes['Zone Treasure 3 Density'] = row.index('Density', column_indexes['Zone Treasure'] + 6)
                except:
                    pass
                # zone options
                column_indexes['Zone Treasure 1 Low'] = row.index('Low', column_indexes['Zone Treasure'])

                # connections
                column_indexes['Connections Zone 1'] = row.index('Zone 1', column_indexes['Connections Zones'])
                column_indexes['Connections Zone 2'] = row.index('Zone 2', column_indexes['Connections Zones'])
                column_indexes['Connections Options Value'] = row.index('Value', column_indexes['Connections Options'])
                column_indexes['Connections Options Border Guard'] = row.index('Border Guard', column_indexes['Connections Options'])
                column_indexes['Connections Options Road'] = row.index('Road', column_indexes['Connections Options'])

            else:
                if cur_row_num == 3:
                    self.name = row[column_indexes['Name']]
                    self.min_size = row[column_indexes['Minimum Size']]
                    self.max_size = row[column_indexes['Maximum Size']]
                pass

            cur_row_num += 1

        tsv_file.close()


class HardcodedTemplate(object):
    ARMY_STRENGTH_AIVALS = {
        'weak': 1000,
        'normal': 2000,
        'strong': 3000,
    }
    def __init__(self, areas:int=2, size:str="S", max_day='2:1:1', monster_strength:str='weak',
                max_heroes:int=4, allowed_actions_per_turn:int=50) -> None:
        assert areas in [1, 2, 4], f'hardcoded template only knows 1, 2, or 4 areas, given: {areas}'
        assert size in HOMMTemplate.SIZES, f'size not recognized: {size}'
        assert monster_strength in HardcodedTemplate.ARMY_STRENGTH_AIVALS, f'invalid monster strength: {monster_strength}'
        self.sizet:tuple[int,int] = HOMMTemplate.SIZES[size]
        self.sizes = size
        self.areas = areas
        self.max_day = max_day
        self.monster_strength = monster_strength
        self.max_heroes = max_heroes
        self.allowed_actions_per_turn = allowed_actions_per_turn
        
    def Generate(self, seed:int=None) -> HOMMSimpleEnv:
        env = HOMMSimpleEnv(map_size=self.sizet, num_players=2, max_day=self.max_day,
                starting_resources=HOMMSimpleEnv.STARTING_RESOURCES_EASY, seed=seed,
                max_actions_turn=self.allowed_actions_per_turn)

        env.map.MAX_PLAYER_HEROES = self.max_heroes

        _areas, _guards = self.__generate_walls__(env=env)

        self.__generate_towns_and_start_heroes__(env=env, areas=_areas, guards=_guards)

        # add guards between areas
        for guard_pos in _guards:
            ok = env.map.AddNeutralArmy(self.__generate_army__(env=env, pos=guard_pos))
            assert ok

        self.__add_resources__(env=env, areas=_areas)

        return env

    @staticmethod
    def __add_resource_pile__(env:HOMMSimpleEnv, area:tuple[tuple[int,int]], res_type:str, val_avg:int=None, exact:bool=False) -> tuple:
        val = val_avg if val_avg else MapResPileTypicalValues[MapObjectTypes[res_type]['id']]
        val = val if exact else env.rs.randint(int(val * 0.8), int(val * 1.2))
        pos = env.rs.randint(area[0][0], area[0][1]), env.rs.randint(area[1][0], area[1][1])
        if env.map.AddResource(*pos, MapObjectTypes[res_type]['id'], val):
            return pos
        return False
    
    def __add_resources__(self, env:HOMMSimpleEnv, areas:list):
        assert len(areas) == self.areas, 'Error: inconsistent number of areas'
        # average "density" 1 resource every 70 positions
        if self.sizes == 'S-':
            num_iterations = 2
        elif self.sizes == 'T':
            num_iterations = 1
        else:
            num_iterations = int(((self.sizet[0] * self.sizet[1]) / 70) / (3 * len(areas)))

        for _ in range(num_iterations):
            for area in areas:
                self.__add_resource_pile__(env, area, 'Gold pile')
                self.__add_resource_pile__(env, area, 'Wood pile')
                self.__add_resource_pile__(env, area, 'Ore pile')
                self.__add_resource_pile__(env, area, MapObjTypeById[env.rs.choice([res_id for res_id in MapResPileToIdx])])
                self.__add_resource_pile__(env, area, MapObjTypeById[env.rs.choice([res_id for res_id in MapResPileToIdx])])
                self.__add_resource_pile__(env, area, MapObjTypeById[env.rs.choice([res_id for res_id in MapResPileToIdx])])
                self.__add_resource_pile__(env, area, 'Treasure Chest', env.rs.choice([500, 1000, 1500]), exact=True)
                self.__add_resource_pile__(env, area, 'Treasure Chest', env.rs.choice([500, 1000, 1500]), exact=True)
            

    def __generate_towns_and_start_heroes__(self, env:HOMMSimpleEnv, areas:list, guards:list[tuple[int,int]]):
        assert len(areas) == self.areas, 'Error in generation of areas'

        areas2 = areas.copy()
        if self.areas == 1:
            start_area1 = start_area2 = areas2[0]
        else:
            start_area1 = areas2[env.rs.choice(list(range(len(areas2))))]
            areas2.remove(start_area1)
            start_area2 = areas2[env.rs.choice(list(range(len(areas2))))]
            areas2.remove(start_area2)

        # sanitize to allow pathing and to avoid conflicts with walls
        start_area1 = (start_area1[0][0]+3, start_area1[0][1]-1), (start_area1[1][0]+3, start_area1[1][1]-3)
        start_area2 = (start_area2[0][0]+3, start_area2[0][1]-1), (start_area2[1][0]+3, start_area2[1][1]-3)

        start_pos_1 = env.rs.randint(*start_area1[0]), env.rs.randint(*start_area1[1])
        blocked_pos = [(start_pos_1[0]+dx, start_pos_1[1]+dy) for dx,dy in TownTiles]
        while any(guard for guard in guards if guard in blocked_pos):
            start_pos_1 = env.rs.randint(*start_area1[0]), env.rs.randint(*start_area1[1])
            blocked_pos = [(start_pos_1[0]+dx, start_pos_1[1]+dy) for dx,dy in TownTiles]

        start_pos_2 = env.rs.randint(*start_area2[0]), env.rs.randint(*start_area2[1])
        blocked_pos = [(start_pos_2[0]+dx, start_pos_2[1]+dy) for dx,dy in TownTiles]
        while any(guard for guard in guards if guard in blocked_pos):
            start_pos_2 = env.rs.randint(*start_area2[0]), env.rs.randint(*start_area2[1])
            blocked_pos = [(start_pos_2[0]+dx, start_pos_2[1]+dy) for dx,dy in TownTiles]

        town = CastleTown(*start_pos_1, rng=env.rs)
        ok = env.map.AddTown(town)
        town.Build('Guardhouse')
        town.Build('Archer\'s Tower')
        town.Build('Mage Guild Level 1')
        env.map.players[0].TakeTown(town)

        town = CastleTown(*start_pos_2, rng=env.rs)
        ok = env.map.AddTown(town)
        town.Build('Guardhouse')
        town.Build('Archer\'s Tower')
        town.Build('Mage Guild Level 1')
        env.map.players[1].TakeTown(town)

        # make roads between towns
        road_ends = [HOMMHero(*start_pos_1, 0, None), HOMMHero(*start_pos_2, 1, None)]
        
        # add neutral towns
        if self.areas == 4: # maybe always do this?
            neutral_area_1, neutral_area_2 = areas2
            # sanitize to allow pathing and to avoid conflicts with walls
            neutral_area_1 = (neutral_area_1[0][0]+3, neutral_area_1[0][1]-1), (neutral_area_1[1][0]+3, neutral_area_1[1][1]-3)
            neutral_area_2 = (neutral_area_2[0][0]+3, neutral_area_2[0][1]-1), (neutral_area_2[1][0]+3, neutral_area_2[1][1]-3)

            neutral_pos_1 = env.rs.randint(*neutral_area_1[0]), env.rs.randint(*neutral_area_1[1])
            blocked_pos = [(neutral_pos_1[0]+dx, neutral_pos_1[1]+dy) for dx,dy in TownTiles]
            while any(guard for guard in guards if guard in blocked_pos):
                neutral_pos_1 = env.rs.randint(*start_area1[0]), env.rs.randint(*start_area1[1])
                blocked_pos = [(neutral_pos_1[0]+dx, neutral_pos_1[1]+dy) for dx,dy in TownTiles]

            neutral_pos_2 = env.rs.randint(*neutral_area_2[0]), env.rs.randint(*neutral_area_2[1])
            blocked_pos = [(neutral_pos_2[0]+dx, neutral_pos_2[1]+dy) for dx,dy in TownTiles]
            while any(guard for guard in guards if guard in blocked_pos):
                neutral_pos_2 = env.rs.randint(*start_area1[0]), env.rs.randint(*start_area1[1])
                blocked_pos = [(neutral_pos_2[0]+dx, neutral_pos_2[1]+dy) for dx,dy in TownTiles]

            town = CastleTown(*neutral_pos_1, rng=env.rs)
            env.map.AddTown(town)
            town.Build('Guardhouse')
            
            town = CastleTown(*neutral_pos_2, rng=env.rs)
            env.map.AddTown(town)
            town.Build('Guardhouse')

            road_ends.append(HOMMHero(*neutral_pos_1, 0, None))
            road_ends.append(HOMMHero(*neutral_pos_2, 1, None))
                
        for idx1 in range(len(road_ends)-1):
            for idx2 in range(idx1+1, len(road_ends)):
                path = env.map.FindPathTo(road_ends[idx1], road_ends[idx2].x, road_ends[idx2].y, ignore_visibility=True)
                if path:
                    env.map.AddRoad(path=path)
        
        # give starting heroes
        assert len(env.map.heroes) > 1, 'Error: not enough heroes defined for 2 players!'
        num_all_heroes = len(env.map.heroes)
        h1 = env.map.heroes[env.rs.choice(list(range(num_all_heroes)))]
        h2 = env.map.heroes[env.rs.choice(list(range(num_all_heroes)))]
        while h2 == h1:
            h2 = env.map.heroes[env.rs.choice(list(range(num_all_heroes)))]
        ok  = env.map.GiveHeroTo(h1, env.map.players[0], start_pos_1)
        ok &= env.map.GiveHeroTo(h2, env.map.players[1], start_pos_2)
        assert ok, 'Error: giving starting heroes'
    
    def __generate_walls__(self, env:HOMMSimpleEnv):
        size_x = self.sizet[0]
        size_y = self.sizet[1]
        half_x = int(size_x / 2)
        half_y = int(size_y / 2)
        num_steps_x = int(size_x / 5)
        num_steps_y = int(size_y / 5)
        deviations_x = []
        for _ in range(num_steps_x):
            deviations_x.append((env.rs.choice([-1, 1]), env.rs.randint(0, size_y)))
        deviations_x.sort(key=lambda t: t[1])
        obstacle_wall = TileTypesByName['wall']

        ret_areas = [((0,size_x-1), (0,size_y-1))]

        guards = []
        walls = []
        walls_x = walls_y = None

        if self.areas in [2, 4]:
            walls_x = [(half_x, y) for y in range(size_y)]
            corners = []
            for dev_x in deviations_x:
                corners.append(walls_x[dev_x[1]]) # re-add this after moving
                for idx in range(dev_x[1], size_y):
                    walls_x[idx] = (walls_x[idx][0] + dev_x[0], walls_x[idx][1])
            walls_x += corners
            
            min_x = min(wall[0] for wall in walls_x)
            max_x = max(wall[0] for wall in walls_x)
            ret_areas = [(    (0,   min_x), (0,size_y-1)),
                         ((max_x,size_x-1), (0,size_y-1))]
        
        if self.areas == 2:
            num_entrances = env.rs.randint(1, int(size_y / 9))
            for _ in range(num_entrances):
                idx = env.rs.randint(0, len(walls_x))
                guards.append(walls_x[idx])
                walls_x = [w for w in walls_x if w != walls_x[idx]]
            walls = walls_x
        elif self.areas == 4:
            deviations_y = []
            for _ in range(num_steps_y):
                deviations_y.append((env.rs.choice([-1, 1]), env.rs.randint(0, size_x)))
            deviations_y.sort(key=lambda t: t[1])
            walls_y = [(x, half_y) for x in range(size_x)]
            corners = []
            for dev_y in deviations_y:
                corners.append(walls_y[dev_y[1]]) # re-add this after moving
                for idx in range(dev_y[1], size_x):
                    walls_y[idx] = (walls_y[idx][0], dev_y[0] + walls_y[idx][1])
            walls_y += corners

            intersections = [pos for pos in walls_x if pos in walls_y]
            assert(len(intersections) >= 1) # TODO: verify everything still works when there are 2
            intersection = intersections[0]
            num_entrances_segment_x = 1+env.rs.randint(0, size_y // 13)
            num_entrances_segment_y = 1+env.rs.randint(0, size_x // 13)

            for _ in range(num_entrances_segment_x):
                tmp = [w for w in walls_x if w[1] < intersection[1] and w not in guards]
                guards.append(tmp[env.rs.choice(list(range(len(tmp))))])
                tmp = [w for w in walls_x if w[1] > intersection[1] and w not in guards]
                guards.append(tmp[env.rs.choice(list(range(len(tmp))))])
            for _ in range(num_entrances_segment_y):
                tmp = [w for w in walls_y if w[0] < intersection[0] and w not in guards]
                guards.append(tmp[env.rs.choice(list(range(len(tmp))))])
                tmp = [w for w in walls_y if w[0] > intersection[0] and w not in guards]
                guards.append(tmp[env.rs.choice(list(range(len(tmp))))])
            
            walls = [w for w in walls_x + walls_y if w not in guards]
            
            min_y = min(wall[1] for wall in walls_y)
            max_y = max(wall[1] for wall in walls_y)

            ret_areas = [(    (0,   min_x),     (0,   min_y)),
                         (    (0,   min_x), (max_y,size_y-1)),
                         ((max_x,size_x-1),     (0,   min_y)),
                         ((max_x,size_x-1), (max_y,size_y-1))]
        
        # put the walls in the map
        assert len(walls) <= HOMMMap.MAX_OBSTACLES
        for wall in walls:
            x,y = wall
            env.map.tiles[0, x,y] = obstacle_wall
            env.map.fixed_obstacles.append(wall)
        
        # validate pathing between all corners
        mock_hero = HOMMHero(x=0,y=0,player_idx=0,rng=None)
        path1 = env.map.FindPathTo(mock_hero,        0, size_y-1, ignore_visibility=True)
        path2 = env.map.FindPathTo(mock_hero, size_x-1,        0, ignore_visibility=True)
        path3 = env.map.FindPathTo(mock_hero, size_x-1, size_y-1, ignore_visibility=True)
        attempts = 0
        while not (path1 and path2 and path3) and attempts < 4:
            attempts += 1
            idx = env.rs.randint(0, len(walls_x))
            guards.append(walls_x[idx])
            del walls_x[idx]
            if intersection and walls_y:
                try:
                    idx = env.rs.randint(0, len(walls_y))
                    guards.append(walls_y[idx])
                    del walls_y[idx]
                except:
                    pass
            path1 = env.map.FindPathTo(mock_hero,        0, size_y-1, ignore_visibility=True)
            path2 = env.map.FindPathTo(mock_hero, size_x-1,        0, ignore_visibility=True)
            path3 = env.map.FindPathTo(mock_hero, size_x-1, size_y-1, ignore_visibility=True)
        assert path1 and path2 and path3, 'Error in map generation, area unreachable!'

        # guards may still have duplicates at this point, between walls_x and walls_y
        return ret_areas, set(guards)
    
    def __generate_army__(self, env:HOMMSimpleEnv, pos:tuple[int,int]) -> HOMMArmy:
        assert pos, 'Error: army position can not be None'
        strength = int((0.8 + env.rs.random() * (1.3 - 0.8)) * HardcodedTemplate.ARMY_STRENGTH_AIVALS[self.monster_strength])
        possible_unit_types = [unit_type for unit_type in UnitTypes if UnitUtils.GetAIValue(unit_type) < strength and unit_type > 0]
        unit_type = env.rs.choice(possible_unit_types)
        total_creatures = int(strength / UnitUtils.GetAIValue(unit_type))
        stacks:list[HOMMArmyStack] = []

        num_stacks = 1 # weak
        if self.monster_strength == 'normal' and total_creatures >= 2:
            num_stacks = 2
        elif self.monster_strength == 'strong' and total_creatures >= 3:
            num_stacks = 3
        creatures_per_stack = int(total_creatures / num_stacks)
        creatures_leftover = total_creatures % num_stacks

        for _ in range(num_stacks):
            stacks.append(HOMMArmyStack(num=creatures_per_stack, unit_id=unit_type))
        stacks[0].num += creatures_leftover
        return HOMMArmy(stacks, *pos)


# class HOMMGameSettings(object):
#     def __init__(self, players_num:int=2) -> None:
#         self.players_num = players_num
#         self.starting_towns_per_player = 1
#         # TODO: starting bonuses -- not supported yed
    
#     def NumberOfTowns(self):
#         return self.players_num * self.starting_towns_per_player

#x = HOMMTemplate("D:\\Work\\personal\\school\\2021-2022\\licenta\\homm3 research\\8XM12a_rmg.tsv")
#print(x)

