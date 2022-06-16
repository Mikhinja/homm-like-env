from HOMM.HOMMUnitTypes import UnitUtils
from HOMM.HOMMHeroes import HeroUtils, HeroSpellUtils, HeroSpells
from HOMM.HOMMData.HOMMMapData import MapObjTypeById, TileTypes, MapObjectTypes

def pprint_2d(matrix):
    s = [[str(e) for e in row] for row in matrix]
    lens = [max(map(len, col)) for col in zip(*s)]
    fmt = ' '.join('{{:{}}}'.format(x) for x in lens)
    table = [fmt.format(*row) for row in s]
    return '\n'.join(table)

def pprint_map(arr_3d):
    rows = arr_3d.shape[1]
    cols = arr_3d.shape[2]
    str_vals = [[MapObjectTypes[MapObjTypeById[arr_3d[2, x,y]]]['symbol'] if arr_3d[0, x,y] == 1
                else TileTypes[arr_3d[0, x,y]]['symbol']
            for y in range(cols)]
        for x in range(rows)]
    return pprint_2d(str_vals)

def pprint_army(armyStacks:list, in_combat:bool=False):
    if in_combat:
        s = [[  str(row[0]),
                str(row[1]),
                UnitUtils.GetUnitName(row[2]),
                str(row[3]),
                str(row[4])+','+str(row[5]),
                str([HeroSpellUtils.GetSpellName(i)+':'+str(x) for i, x in enumerate(row[-1]) if x > 0])]
            for row in armyStacks]
    else:
        s = [[UnitUtils.GetUnitName(row[0]),
                str(row[1]),
                str(row[2])+','+str(row[3]),
                str([HeroSpellUtils.GetSpellName(i)+':'+str(x) for i, x in enumerate(row[-1]) if x > 0])]
            for row in armyStacks]
    lens = [max(map(len, col)) for col in zip(*s)]
    fmt = '\t'.join('{{:{}}}'.format(x) for x in lens)
    table = [fmt.format(*row) for row in s]
    return '\n'.join(table)

def pprint_hero(hero:list, with_army=False):
    if not with_army:
        pass
    else:
        pass