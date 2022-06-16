import math
from HOMM.HOMMAPI import HOMMArmy, HOMMArmyInCombat, HOMMArmyStackInCombat, HOMMBattlefield

from HOMM.Hero import Hero

class Battlefield(HOMMBattlefield):
    # Battle field is 11 rows of 15 tiles arranged in hexagonal “even-r” horizontal layout
    # This is according to https://heroes.thelazy.net/index.php/Combat
    
    def __init__(self, armyA:HOMMArmyInCombat, armyD:HOMMArmyInCombat, obstacles:list=[]) -> None:
        assert(any(armyA) and any(armyD))
        self.armyA = armyA
        self.armyD = armyD
        self.obstacles = obstacles
    def __get_obstacles__(self, exclude_target:tuple[int,int]=None):
        ret = self.obstacles + [(stack.x, stack.y) for stack in self.armyA] + [(stack.x, stack.y) for stack in self.armyD]
        if exclude_target and exclude_target in ret:
            ret.remove(exclude_target)
        return ret
    def StackPathTo(self, stack:HOMMArmyStackInCombat, dest:tuple[int,int]) -> list:
        return [Battlefield.CubeToEvenR(*pos) for pos in self.FindPathTo_impl(stack.x, stack.y, *dest, self.__get_obstacles__(dest))]
    def GetClosestToTarget(self, stack:HOMMArmyStackInCombat, dest:HOMMArmyStackInCombat) -> tuple[int, int]:
        return self.GetClosestToTarget_old(stack.x, stack.y, dest.x, dest.y, self.__get_obstacles__((dest.x, dest.y)), stack.GetUnitSpeed())
    def AreNeighbors(self, source:tuple[int,int], dest:tuple[int,int]) -> bool:
        return self.AreNeighborsCube(*self.EvenRToCube(*source), *self.EvenRToCube(*dest))
    
    @staticmethod
    def GetDistanceEvenR(x1:int, y1:int, x2:int, y2:int) -> int:
        return Battlefield.HexCubeDistance(*Battlefield.EvenRToCube(x1, y1), *Battlefield.EvenRToCube(x2, y2))
    
    # inspiration: https://www.redblobgames.com/grids/hexagons/
    # conversions between hex coord systems
    @staticmethod
    def AxialToCube(q:int, r:int):
        return q, r, -q-r
    @staticmethod
    def CubeToAxial(q:int, r:int, s:int):
        return q, r
    @staticmethod
    def CubeToEvenR(q:int, r:int, s:int):
        return r, int(q + (r + (r & 1)) / 2)
    @staticmethod
    def EvenRToCube(row:int, col:int):
        q = col - int((row + (row & 1)) / 2)
        r = row
        return q, r, -q-r
    
    # cube coord system
    HEX_CUBE_DIRECTION_VECTORS = [
        [ 0,-1,+1], [ 0,+1,-1],
        [-1, 0,+1], [+1, 0,-1],
        [+1,-1, 0], [-1,+1, 0]
    ]
    @staticmethod
    def AreNeighborsCube(q1:int, r1:int, s1:int, q2:int, r2:int, s2:int) -> bool:
        return [q1-q2, r1-r2, s1-s2] in Battlefield.HEX_CUBE_DIRECTION_VECTORS
    @staticmethod
    def GetNeighbors(q:int, r:int, s:int):
        return [[a+b for a,b in zip([q,r,s], vec)] for vec in Battlefield.HEX_CUBE_DIRECTION_VECTORS]
    @staticmethod
    def HexCubeDistance(q1:int, r1:int, s1:int, q2:int, r2:int, s2:int) -> int:
        return int(sum([abs(x) for x in [q2-q1, r2-r1, s2-s1]]) / 2)
    
    @staticmethod
    def IsInsideBattlefield(x:int, y:int) -> bool:
        return x>=0 and x<11 and y>=0 and y<15
    @staticmethod
    def IsInsideBattlefieldCube(q:int, r:int, s:int) -> bool:
        return Battlefield.IsInsideBattlefield(*Battlefield.CubeToEvenR(q, r, s))
    @staticmethod
    def GetNeighborsInsideBattlefield(q:int, r:int, s:int):
        return [pos for pos in Battlefield.GetNeighbors(q, r, s) if Battlefield.IsInsideBattlefieldCube(*pos)]

    @staticmethod
    def GetNeighborsNotObstacles(q:int, r:int, s:int, obstacles:list):
        neighbor_cells = Battlefield.GetNeighborsInsideBattlefield(q, r, s)
        dbg_ever_pos = [Battlefield.CubeToEvenR(*pos) for pos in neighbor_cells if Battlefield.CubeToEvenR(*pos) not in obstacles]
        ret = [pos for pos in neighbor_cells if Battlefield.CubeToEvenR(*pos) not in obstacles]
        return ret

    # utilitary method that gets the closest available spot next to a target
    @staticmethod
    def GetClosestNextToTarget(x1:int, y1:int, x2:int, y2:int, obstacles:list):
        available_pos = Battlefield.GetNeighborsNotObstacles(*Battlefield.EvenRToCube(x2, y2), obstacles)# [pos for pos in neighbor_cells if [*Battlefield.CubeToEvenR(*pos)] not in obstacles]
        if len(available_pos)>0:
            cube_src = Battlefield.EvenRToCube(x1, y1)
            cube_closest = min(available_pos, key=lambda pos:Battlefield.HexCubeDistance(*cube_src, *pos))
            return Battlefield.CubeToEvenR(*cube_closest)
        return None
    
    @staticmethod
    def ArmiesAsObstacles(army1:list, army2:list=[]) -> list:
        return [a[2:4] for a in army1] + [a[2:4] for a in army2]

    @staticmethod
    def FindPathTo_impl(x1:int, y1:int, x2:int, y2:int, obstacles) -> list:
        # my attempt at an A* implementation
        # the heuristic is just the Battlefield.HexCubeDistance
        cube_start = Battlefield.EvenRToCube(x1, y1)
        cube_end = Battlefield.EvenRToCube(x2, y2)
        
        openSet = [cube_start]
        gScore = {cube_start: 0}
        dbg_gScore = {Battlefield.CubeToEvenR(*cube_start): 0}
        fScore = {cube_start: Battlefield.HexCubeDistance(*cube_start, *cube_end)}
        cameFrom = {}
        while len(openSet) > 0:
            curr = min(openSet, key=lambda k: fScore[tuple(k)])
            if tuple(curr) == cube_end:
                path = []
                while tuple(curr) in cameFrom:
                    path.append(curr)
                    curr = cameFrom[tuple(curr)]
                path.reverse()
                return path
            openSet.remove(curr)
            for neigh in Battlefield.GetNeighborsNotObstacles(*curr, obstacles):
                neigh_as_key = tuple(neigh)
                tentative_score = gScore.get(tuple(curr), math.inf) + 1 # dist to a neighbor will always be 1 in hex grid
                if tentative_score < gScore.get(neigh_as_key, math.inf):
                    cameFrom[neigh_as_key] = curr
                    gScore[neigh_as_key] = tentative_score
                    dbg_gScore[Battlefield.CubeToEvenR(*neigh_as_key)] = tentative_score
                    fScore[neigh_as_key] = tentative_score + Battlefield.HexCubeDistance(*neigh, *cube_end)
                    if neigh not in openSet:
                        openSet.append(neigh)

        return False

    @staticmethod
    def GetClosestToTarget_old(x1:int, y1:int, x2:int, y2:int, obstacles:list, max_dist:int):
        path = Battlefield.FindPathTo_impl(x1, y1, x2, y2, obstacles)
        if path:
            if len(path) > 1:
                if len(path) > (max_dist + 1):
                    return Battlefield.CubeToEvenR(*path[max_dist])
                else:
                    return Battlefield.CubeToEvenR(*path[-2])
            else:
                return (x1, y1)
        return False
    

