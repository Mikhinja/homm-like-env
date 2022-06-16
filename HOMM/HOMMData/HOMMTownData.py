#from HOMMUnitData import UnitTypes

# terrains give +1 attack, +1 defense, +1 speed to creatures native to that terrain type

TownTypes = {
    'Castle': {
        'id': 0,
        'Native terrain': {'name':'Grass', 'id':1},
        'Buildings': {
            # cost: [0]=gold, [1]=wood, [2]=ore, [3]=mercuri, [4]=sulfur, [5]=crystal, [6]=gems
            'Village Hall':          {'id':  0, 'cost':[    0,  0,  0,  0,  0,  0,  0], 'income':[ 500, 0, 0, 0, 0, 0, 0]},
            'Tavern':                {'id':  1, 'cost':[  500,  0,  0,  0,  0,  0,  0],                                    'requires':[]},
            'Town Hall':             {'id':  2, 'cost':[ 2500,  0,  0,  0,  0,  0,  0], 'income':[1000, 0, 0, 0, 0, 0, 0], 'requires':['Village Hall', 'Tavern']},
            'City Hall':             {'id':  3, 'cost':[ 5000,  0,  0,  0,  0,  0,  0], 'income':[2000, 0, 0, 0, 0, 0, 0], 'requires':['Town Hall', 'Blacksmith', 'Mage Guild', 'Marketplace']},
            'Capitol':               {'id':  4, 'cost':[10000,  0,  0,  0,  0,  0,  0], 'income':[4000, 0, 0, 0, 0, 0, 0], 'requires':['City Hall', 'Castle']},
            'Fort':                  {'id':  5, 'cost':[ 5000, 20, 20,  0,  0,  0,  0],                                    'requires':['Village Hall']},
            'Citadel':               {'id':  6, 'cost':[ 2500,  0,  5,  0,  0,  0,  0],                                    'requires':['Fort']},
            'Castle':                {'id':  7, 'cost':[ 5000, 10, 10,  0,  0,  0,  0],                                    'requires':['Citadel']},
            'Marketplace':           {'id': 12, 'cost':[  500,  5,  0,  0,  0,  0,  0]},
            'Resource Silo':         {'id': 13, 'cost':[ 5000,  0,  5,  0,  0,  0,  0], 'income':[   0, 1, 1, 0, 0, 0, 0], 'requires':['Marketplace']},
            
            'Mage Guild Level 1':    {'id': 40, 'cost':[ 2000,  5,  5,  0,  0,  0,  0],                                    'requires':['Village Hall']},
            'Mage Guild Level 2':    {'id': 41, 'cost':[ 2000,  5,  5,  4,  4,  4,  4],                                    'requires':['Mage Guild Level 1']},
            'Mage Guild Level 3':    {'id': 42, 'cost':[ 2000,  5,  5,  6,  6,  6,  6],                                    'requires':['Mage Guild Level 2']},
            'Mage Guild Level 4':    {'id': 43, 'cost':[ 2000,  5,  5,  8,  8,  8,  8],                                    'requires':['Mage Guild Level 3']},
            'Mage Guild Level 5':    {'id': 44, 'cost':[ 2000,  5,  5, 10, 10, 10, 10],                                    'requires':['Mage Guild Level 4']},

            'Guardhouse':            {'id':  8, 'cost':[  500,  0, 10,  0,  0,  0,  0], 'prod':'Pikeman',                  'requires':['Fort']},
            'Upg. Guardhouse':       {'id':  9, 'cost':[ 1000,  0,  5,  0,  0,  0,  0], 'prod':'Halberdier',               'requires':['Guardhouse']},
            'Archer\'s Tower':       {'id': 10, 'cost':[ 1000,  5,  5,  0,  0,  0,  0], 'prod':'Archer',                   'requires':['Fort', 'Guardhouse']},
            'Upg. Archer\'s Tower':  {'id': 11, 'cost':[ 1000,  5,  5,  0,  0,  0,  0], 'prod':'Marksman',                 'requires':['Fort', 'Archer\'s Tower']},
            'Griffin Tower':         {'id': 14, 'cost':[ 1000,  0,  5,  0,  0,  0,  0], 'prod':'Griffin',                  'requires':['Fort', 'Barracks']},
            'Upg. Griffin Tower':    {'id': 15, 'cost':[ 1000,  0,  5,  0,  0,  0,  0], 'prod':'Royal Griffin',            'requires':['Fort', 'Griffin Tower']},
            'Barracks':              {'id': 16, 'cost':[ 2000,  0,  5,  0,  0,  0,  0], 'prod':'Swordsman',                'requires':['Fort', 'Blacksmith', 'Guardhouse']},
            'Upg. Barracks':         {'id': 17, 'cost':[ 2000,  0,  5,  0,  0,  5,  0], 'prod':'Crusader',                 'requires':['Fort', 'Barracks']},
            'Monastery':             {'id': 18, 'cost':[ 3000,  5,  5,  2,  2,  2,  2], 'prod':'Monk',                     'requires':['Fort', 'Barracks', 'Mage Guild Level 1']},
            'Upg. Monastery':        {'id': 19, 'cost':[ 1000,  2,  2,  2,  2,  2,  2], 'prod':'Zealot',                   'requires':['Fort', 'Monastery']},
            'Training Grounds':      {'id': 20, 'cost':[ 5000, 20,  0,  0,  0,  0,  0], 'prod':'Cavalier',                 'requires':['Fort', 'Barracks', 'Stables']},
            'Upg. Training Grounds': {'id': 21, 'cost':[ 3000,  0,  0,  0,  0,  0,  0], 'prod':'Champion',                 'requires':['Fort', 'Training Grounds']},
            'Portal of Glory':       {'id': 22, 'cost':[20000,  0,  0, 10, 10, 10, 10], 'prod':'Angel',                    'requires':['Fort', 'Monastery', 'Mage Guild Level 1']},
            'Upg. Portal of Glory':  {'id': 23, 'cost':[20000,  0,  0, 10, 10, 10, 10], 'prod':'Archangel',                'requires':['Fort', 'Portal of Glory']},
        },
        'Units': [ 1,  2,  3,  4,  5,  6,  7,  8,  9, 10, 11, 12, 13, 14]
    }
}
