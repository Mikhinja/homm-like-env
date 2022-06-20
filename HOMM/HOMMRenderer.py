# pip install pywin32
# pip install pillow

#from fileinput import filename
from sqlite3 import Timestamp
import threading
from PIL import ImageGrab, Image
import win32gui

from datetime import datetime
import sys
from time import sleep, time
# from turtle import back, clear
from colorama import init, Fore, Back, Style

# from pynput.keyboard import Key, Listener
import keyboard

from HOMM.HOMMUnitTypes import UnitUtils
from HOMM.HOMMAPI import HOMMActionLogger, HOMMMap, HOMMRenderer, HOMMResourceObject
from HOMM.HOMMBuiltInAI_Battle import BattleAction
from HOMM.HOMMData.HOMMMapData import MapObjTypeById, MapObjectTypes, MapResPileToIdx, TileTypes, TileTypesByName, TownTiles
from HOMM.Hero import Hero
from HOMM.Town import TownBase

import os

def cls():
    os.system('cls' if os.name=='nt' else 'clear')

battle_txt = 'Battle: '
# colors attempt to best match specifications https://heroes.thelazy.net/index.php/Kingdom
PlayerColors = [
    Fore.RED,
    Fore.BLUE,
    Fore.LIGHTYELLOW_EX, # closest to Tan
    Fore.GREEN,
    Fore.YELLOW, # closest to Orange
    Fore.MAGENTA, # closest to Purple
    Fore.CYAN, # closest to Teal
    Fore.LIGHTRED_EX, # closest to pink
]
PlayerBColors = [
    Back.RED,
    Back.BLUE,
    Back.LIGHTYELLOW_EX, # closest to Tan
    Back.GREEN,
    Back.YELLOW, # closest to Orange
    Back.MAGENTA, # closest to Purple
    Back.CYAN, # closest to Teal
    Back.LIGHTRED_EX, # closest to pink
]

ResourceColors = {
    'Gold pile':      Fore.LIGHTYELLOW_EX,
    'Wood pile':      Fore.YELLOW, # lacking brown
    'Ore pile':       Fore.LIGHTBLACK_EX,
    'Mercury pile':   Fore.LIGHTBLACK_EX,
    'Sulfur pile':    Fore.LIGHTYELLOW_EX,
    'Crystal pile':   Fore.LIGHTRED_EX,
    'Gems pile':      Fore.LIGHTMAGENTA_EX,
    'Treasure Chest': Back.YELLOW + Fore.BLACK,
    'Artifact':       Fore.WHITE,
}

class HOMMColorTextConsoleRender(HOMMRenderer):
    def __init__(self, env, actions_log:HOMMActionLogger, num_actions:int=1,
                print_adventure_map:bool=True, print_AIVals:bool=True,
                clear_screen:bool=True, skip_invalid_actions:bool=False,
                frame_delay:float=0.5, frame_delay_battle:float=-1,
                record_animation:bool=False, animation_frame_delay:float=0.3, animation_filename:str='HOMMTextAnimation',
                accumulate_until_end:bool=True, interactive_play:bool=True) -> None:
        super().__init__(env=env, num_actions=num_actions, actions_log=actions_log, frame_delay=frame_delay,
            record_animation=record_animation, animation_frame_delay=animation_frame_delay, animation_filename=animation_filename)
        self.print_adventure_map = print_adventure_map
        self.print_battles = True
        self.print_AIVals = print_AIVals
        self.clear_screen = clear_screen
        self.skip_invalid_actions = skip_invalid_actions

        self.accumulate_until_end = accumulate_until_end
        self.text_frames:list[str] = []
        self.interactive_play = interactive_play
        if (self.interactive_play):
            assert(self.accumulate_until_end)
        self.curr_interactive_pos = 0
        
        self.hwnd:tuple = None
        self.images = []
        if frame_delay_battle > 0:
            self.frame_delay_battle = frame_delay_battle
        else:
            self.frame_delay_battle = self.frame_delay
        self.actions_log = actions_log
        
        self.curr_action_idx = 0
        # perhaps this should not assert, but set it if not set
        assert(self.actions_log)
        self.actions_log.callback = self.CallBack
        self.inited = False
        self.key_hooks = []
        # inspired from https://blog.miguelgrinberg.com/post/how-to-make-python-wait
        # might be useful in the future, for displaying progress
        self.end_event = threading.Event()
    
    def __init_console_render__(self):
        if not self.inited:
            self.inited = True
            init(convert=True)
            if self.record_animation:
                assert(not self.interactive_play)
                self.__init_image_capture__()
            if self.interactive_play:
                assert(not self.record_animation)
                self.key_hooks.append(keyboard.on_press_key("left", self.__interactive_prev__))
                self.key_hooks.append(keyboard.on_press_key("up", self.__interactive_prev__))

                self.key_hooks.append(keyboard.on_press_key("right", self.__interactive_next__))
                self.key_hooks.append(keyboard.on_press_key("down", self.__interactive_next__))

                self.key_hooks.append(keyboard.on_press_key("space", self.__interactive_stop__))
                self.key_hooks.append(keyboard.on_press_key("q", self.__interactive_stop__))
                self.key_hooks.append(keyboard.on_press_key("esc", self.__interactive_stop__))

                self.key_hooks.append(keyboard.on_press_key("home", self.__interactive_first__))
                self.key_hooks.append(keyboard.on_press_key("end", self.__interactive_last__))
                
                self.key_hooks.append(keyboard.on_press_key("b", self.__interactive_toggle_print_battles__))
                self.key_hooks.append(keyboard.on_press_key("s", self.__interactive_save_animation__))

                self.key_hooks.append(keyboard.on_press_key("h", self.__interactive_help__))

    def __init_image_capture__(self):
        toplist, winlist = [], []
        def enum_cb(hwnd, results):
            winlist.append((hwnd, win32gui.GetWindowText(hwnd)))
        win32gui.EnumWindows(enum_cb, toplist)
        cmd_python_window = next(((hwnd, title) for hwnd, title in winlist if 'command prompt - python' in title.lower()), None)
        if cmd_python_window:
            self.hwnd = cmd_python_window[0]

    def CallBack(self, force:bool=True):
        if not self.inited:
            self.__init_console_render__()
            
        if force or len(self.actions_log.actions) - self.curr_action_idx >= self.num_actions:
            txtcanvas = self.__print_all__()
            
            if self.accumulate_until_end:
                self.text_frames.append(txtcanvas)
            else:
                if self.clear_screen:
                    cls()
                
                sys.stdout.write("\x1b7\x1b[%d;%df%s\x1b8" % (1, 1, txtcanvas))
                sys.stdout.flush()

                the_map:HOMMMap = self.env.map
                delay = self.frame_delay if not (self.print_battles and the_map.battle) else self.frame_delay_battle
                sleep(max(delay, 0.03))

                if self.record_animation:
                    self.__capture_screen__()

    def __print_all__(self) -> str:
        # do all the prints, including actions
        txtcanvas = self.__print_title__() + '\n'

        the_map:HOMMMap = self.env.map
        for i in range(len(the_map.players)):
            txtcanvas += PlayerColors[i]
            if the_map.players[i].IsDefeated():
                txtcanvas += Style.DIM
            txtcanvas += self.__print_player_resources__(i) + '\n'
            txtcanvas += self.__print_player_towns__(i) + '\n'
            txtcanvas += self.__print_player_heroes__(i) + '\n'
            txtcanvas += Style.RESET_ALL
        
        if self.print_adventure_map and not the_map.battle:
            txtcanvas += self.__print_map__()# + '\n'
        
        if self.print_battles and the_map.battle:
            txtcanvas += self.__print_battle__()# + '\n'
        
        txtcanvas += self.__print_actions__()
        return txtcanvas

    def __print_title__(self) -> str:
        the_map:HOMMMap = self.env.map
        ret = f'Map size = {the_map.size} Players: '
        for i in range(len(the_map.players)):
            ret += '[' if the_map.curr_player_idx == i else ' '
            if the_map.players[i].IsDefeated():
                ret += Back.LIGHTBLACK_EX
            ret += f'{PlayerColors[i]}{i+1}'
            if self.print_AIVals:
                ret += f' ({the_map.players[i].GetAIVal():>7})'
            ret += Style.RESET_ALL
            ret += ']' if the_map.curr_player_idx == i else ' '
        ret += f' Day = {the_map.GetDayStr()}  End by {the_map.DayToStr(self.env.max_day)}'
        #ret += PlayerColors[the_map.curr_player_idx] + 'Current Player ' + str(the_map.curr_player_idx+1) + Style.RESET_ALL
        return ret

    def __print_player_resources__(self, player_idx:int) -> str:
        ret = ''
        the_map:HOMMMap = self.env.map
        if self.env.ended and the_map.players[player_idx] in self.env.winners:
            ret = f' {Back.LIGHTYELLOW_EX}{Fore.BLACK} WINNER {Style.RESET_ALL} '
        elif the_map.players[player_idx].IsDefeated():
            ret += ' DEFEATED '
        elif player_idx == the_map.curr_player_idx:
            ret += f'Curr {Back.WHITE}{Fore.BLACK} -> {Style.RESET_ALL} '
        else:
            ret += '          '
        ret += f'{PlayerColors[player_idx]}Player {player_idx+1}  DaysLeft: {the_map.players[player_idx].days_to_get_town} '
        if not the_map.players[player_idx].IsDefeated():
            ret += '  [ '
            for idx, val in enumerate(the_map.players[player_idx].resources):
                res_id = next(rid for rid in MapResPileToIdx if MapResPileToIdx[rid] == idx)
                ret += ResourceColors[MapObjTypeById[res_id]]
                # if idx == 6:
                #     # pretty print Gems
                #     ret += f'G{Fore.LIGHTYELLOW_EX}e{Fore.LIGHTGREEN_EX}m{Fore.LIGHTBLUE_EX}s{Fore.LIGHTMAGENTA_EX}'
                # else:
                ret += MapObjTypeById[res_id].split(' ')[0]
                if MapObjTypeById[res_id] == 'Gold pile':
                    ret += f':{val:>7}'
                else:
                    ret += f':{val:>3}'
                if idx < 6:
                    ret += PlayerColors[player_idx]+', '
            ret += PlayerColors[player_idx] + ' ]'
        return ret

    def __print_player_towns__(self, player_idx:int) -> str:
        the_map:HOMMMap = self.env.map
        if the_map.players[player_idx].IsDefeated():
            return f' {PlayerColors[player_idx]}DEFEATED '
        else:
            if self.print_AIVals:
                return PlayerColors[player_idx]+'Towns: ' + ', '.join(type(t).__name__ + f' ({t.army.GetAIVal() if t.army else 0:>7}) at ({t.x:>2}, {t.y:>2})' for t in the_map.players[player_idx].towns)
            else:
                return PlayerColors[player_idx]+'Towns: ' + ', '.join(type(t).__name__ + f' at ({t.x:>2}, {t.y:>2})' for t in the_map.players[player_idx].towns)

    def __print_player_heroes__(self, player_idx:int) -> str:
        ret = PlayerColors[player_idx]
        the_map:HOMMMap = self.env.map
        if the_map.players[player_idx].IsDefeated():
            ret += ' DEFEATED '
            ret += '\n' * (HOMMMap.MAX_PLAYER_HEROES-1)
        else:
            if len(the_map.players[player_idx].heroes) > 0:
                lines_heroes = []
                for hero in the_map.players[player_idx].heroes:
                    l = f'{hero.name:25} Level {hero.GetLevel()} (xp {hero.xp:>7}) at ({hero.x:>2}, {hero.y:>2}) {[hero.attack, hero.defense, hero.power, hero.knowledge, hero.curr_mana]}'
                    if self.print_AIVals:
                        l += f' Army({hero.army.GetAIVal():>7}): '
                    else:
                        l += ' Army: '
                    l += ', '.join(str(stack.num) + ' ' + stack.GetUnitName() for stack in hero.army if stack)
                    lines_heroes.append(l)
                ret += '\n'.join(lines_heroes)
                ret += '\n' * (HOMMMap.MAX_PLAYER_HEROES - len(the_map.players[player_idx].heroes))
            else:
                ret += 'No heroes :\'('
                ret += '\n' * (HOMMMap.MAX_PLAYER_HEROES-1)
        return ret

    def __print_map__(self) -> str:
        the_map:HOMMMap = self.env.map
        txt_map = [['.' if the_map.tiles[0, i,j] == TileTypesByName['road'] else ' ' for j in range(the_map.size[1])] for i in range(the_map.size[0])]
        for obstacle in the_map.fixed_obstacles:
            txt_map[obstacle[0]][ obstacle[1]] = '#'
        
        for army in the_map.neutral_armies:
            txt_map[army.x][army.y] = 'x' #TileTypes[TileTypesByName['hero or army']]['symbol']
        for town in the_map.towns:
            disp = '#'
            ttown:TownBase = town
            if ttown.player_idx >= 0:
                disp = f'{PlayerColors[ttown.player_idx]}#{Style.RESET_ALL}'
            for dx,dy in TownTiles:
                txt_map[town.x+dx][town.y+dy] = disp
        for pos in the_map.resources:
            res:HOMMResourceObject = the_map.resources[pos]
            res_name = MapObjTypeById[res.res_type]
            symbol = MapObjectTypes[res_name]['symbol']
            txt_map[pos[0]][pos[1]] = ResourceColors[res_name] + symbol + Style.RESET_ALL
        for hero in the_map.heroes:
            if hero.player_idx >= 0:
                txt_map[hero.x][hero.y] = PlayerBColors[hero.player_idx] + Fore.WHITE + 'h' + Style.RESET_ALL
        
        # TODO: optimize this a bit
        if self.curr_action_idx < len(self.actions_log.actions):
            player = the_map.players[the_map.curr_player_idx]
            for x in range(the_map.size[0]):
                for y in range(the_map.size[1]):
                    if not player.CanSee(x, y):
                        txt_map[x][y] = PlayerColors[player.idx] + '?' + Style.RESET_ALL
        ret = ''
        for x in range(the_map.size[0]):
            ret += '|'
            for y in range(the_map.size[1]):
                ret += txt_map[x][y] + ' '
            ret += '|\n'
        return ret
        #return '\n'.join(['|' + ' '.join(txt_map[x][y] for x in range(the_map.size[0]) for y in range(the_map.size[1])) + '|'])

    def __print_battle__(self) -> str:
        the_map:HOMMMap = self.env.map
        assert(the_map.battle)
        heroA:Hero = the_map.battle.heroA
        colorA = PlayerColors[heroA.player_idx]
        heroD:Hero = None
        townD:TownBase = None
        colorD = ''
        if the_map.battle.armyD.hero:
            heroD = the_map.battle.armyD.hero
            colorD = PlayerColors[heroD.player_idx]
        elif the_map.battle.armyD.town:
            townD = the_map.battle.armyD.town
            if townD.player_idx >= 0:
                colorD = PlayerColors[townD.player_idx]
        ret = f'{battle_txt}{colorA}{heroA.name} ({heroA.curr_mana} mana)'
        if self.print_AIVals:
            ret += f'({the_map.battle.armyA.GetAIVal():>7})'
        ret += Style.RESET_ALL + ' vs '
        if heroD:
            ret += f'{colorD}{heroD.name} ({heroD.curr_mana} mana)'
        elif townD:
            ret += f'{colorD}{townD.faction} at ({townD.x}, {townD.y}) '
        else:
            ret += 'neutral army' # TODO: replace this with more information about "wandering creatures", aka "monsters", "neutral stacks"
        if self.print_AIVals:
            ret += f'({the_map.battle.armyD.GetAIVal():>7})'
        ret += '\n'+Style.RESET_ALL

        arr = [[['    ' for k in range(3)] for j in range(15)] for i in range(11)]
        curr_stack = None
        if the_map.battle.prev_stack:
            # we have the prev_stack because the callback happens after the action is done,
            #   and the curr_stack might temporarily be None
            curr_stack = the_map.battle.prev_stack
        for stack in the_map.battle.armyA:
            arr[stack.x][stack.y] = [
                #' '*4,
                f'{colorA}{str(stack.curr_num):>4}{Style.RESET_ALL}',
                f'{colorA}{stack.stack.GetUnitName()[:4]}{Style.RESET_ALL}',
                ' '*4 if stack != curr_stack else ' ^^ ' # mark current stack
            ]
        for stack in the_map.battle.armyD:
            arr[stack.x][stack.y] = [
                #' '*4,
                f'{colorD}{str(stack.curr_num):>4}{Style.RESET_ALL}',
                f'{colorD}{stack.stack.GetUnitName()[:4]}{Style.RESET_ALL}',
                ' '*4 if stack != curr_stack else ' ^^ ' # mark current stack
            ]
        lines=[]
        for i in range(11):
            for k in range(3):
                lines.append('  |' if i % 2 == 0 else '|')
                lines[(i*3)+k] += ''.join(arr[i][j][k] for j in range(15))
                lines[(i*3)+k] += '|'
        ret += '\n'.join(lines)
        return ret

    def __print_actions__(self) -> str:
        ret = ''
        the_map:HOMMMap = self.env.map
        for idx in range(self.curr_action_idx, len(self.actions_log.actions)):
            ret += f'\n[{idx:>4}] '
            action = self.actions_log.actions[idx]
            if not action.is_valid:
                if self.skip_invalid_actions:
                    continue
                ret += f'{Fore.WHITE}{Back.RED} SKIPPED INVALID {Style.RESET_ALL} '
            if action.player_idx >= 0:
                ret += PlayerColors[action.player_idx]
            
            ret += str(action)
            
            ret += Style.RESET_ALL
        
        self.curr_action_idx = len(self.actions_log.actions)
        return ret

    def __capture_screen__(self):
        # TODO: to improve this to work with window minimized, check out https://learncodebygaming.com/blog/fast-window-capture
        if self.record_animation and self.hwnd:
            assert(self.inited)
            bbox = win32gui.GetWindowRect(self.hwnd)
            img = ImageGrab.grab(bbox)
            self.images.append(img)
    
    def GameEnded(self):
        txtcanvas = self.__print_all__()
        txtcanvas += f'     {Fore.BLACK}{Back.WHITE} Game Ended. {Style.RESET_ALL}'
        txtcanvas += f'     {Fore.LIGHTMAGENTA_EX}Winners:{Style.RESET_ALL}  {", ".join(PlayerColors[player.idx]+"Player "+str(player.idx+1)+Style.RESET_ALL for player in self.env.winners)}'
        if self.accumulate_until_end:
            self.text_frames.append(txtcanvas)
        else:
            if self.clear_screen:
                cls()
            sys.stdout.write("\x1b7\x1b[%d;%df%s\x1b8" % (1, 1, self.text_frames[self.curr_interactive_pos]))
            sys.stdout.flush()

    def Playback(self):
        assert(self.interactive_play)
        if self.interactive_play:
            self.end_event.clear() # make sure we prevent infinite wait

            # display something at the start
            #self.__interactive_prev__()
            self.__interactive_help__()
            
            # while self.interactive_play:
            #     sleep(0.1)
            self.end_event.wait()
            self.end_event.clear()
            keyboard.unhook_all_hotkeys()
            if self.clear_screen:
                cls()
            print(f'{Fore.CYAN}Exited{Style.RESET_ALL}.')
            sleep(0.5)
    
    def SaveAnimation(self, specific_filename:str=None):
        if self.record_animation:
            frame_one:Image = self.images[0]
            filename = specific_filename if specific_filename else self.animation_filename
            frame_one.save(filename+'.gif', format="GIF", append_images=self.images, save_all=True, duration=1000*self.animation_frame_delay, loop=0)
    
    def __interactive_prev__(self, *args):
        if self.hwnd and self.hwnd == win32gui.GetForegroundWindow():
            self.curr_interactive_pos = max(self.curr_interactive_pos - 1, 0)
            if not self.print_battles:
                while battle_txt in self.text_frames[self.curr_interactive_pos]:
                    self.curr_interactive_pos = max(self.curr_interactive_pos - 1, 0)
                    if self.curr_interactive_pos == 0:
                        break
            if self.clear_screen:
                cls()
            sys.stdout.write("\x1b7\x1b[%d;%df%s\x1b8" % (1, 1, self.text_frames[self.curr_interactive_pos]))
            sys.stdout.flush()
    
    def __interactive_next__(self, *args):
        if self.hwnd and self.hwnd == win32gui.GetForegroundWindow():
            self.curr_interactive_pos = min(self.curr_interactive_pos + 1, len(self.text_frames)-1)
            if not self.print_battles:
                while battle_txt in self.text_frames[self.curr_interactive_pos]:
                    self.curr_interactive_pos = min(self.curr_interactive_pos + 1, len(self.text_frames)-1)
                    if self.curr_interactive_pos == len(self.text_frames)-1:
                        break
            if self.clear_screen:
                cls()
            sys.stdout.write("\x1b7\x1b[%d;%df%s\x1b8" % (1, 1, self.text_frames[self.curr_interactive_pos]))
            sys.stdout.flush()
    
    def __interactive_first__(self, *args):
        if self.hwnd and self.hwnd == win32gui.GetForegroundWindow():
            self.curr_interactive_pos = 0
            if self.clear_screen:
                cls()
            sys.stdout.write("\x1b7\x1b[%d;%df%s\x1b8" % (1, 1, self.text_frames[self.curr_interactive_pos]))
            sys.stdout.flush()
    
    def __interactive_last__(self, *args):
        if self.hwnd and self.hwnd == win32gui.GetForegroundWindow():
            self.curr_interactive_pos = len(self.text_frames)-1
            if self.clear_screen:
                cls()
            sys.stdout.write("\x1b7\x1b[%d;%df%s\x1b8" % (1, 1, self.text_frames[self.curr_interactive_pos]))
            sys.stdout.flush()
    
    def __interactive_toggle_print_battles__(self, *args):
        self.print_battles = not self.print_battles
        self.__interactive_help__()

    
    def __interactive_stop__(self, *args):
        self.interactive_play = False
        self.end_event.set()
    
    def __interactive_save_animation__(self, *args):
        assert(self.interactive_play and self.animation_frame_delay > 0 and self.text_frames)
        if self.hwnd and self.hwnd == win32gui.GetForegroundWindow():
            print(f'Saving gif animation. This will quickly play through the entire game, it will take roughly {(0.2 * len(self.text_frames)):>3.1f} seconds')
            sleep(2)
            if not self.images:
                start = time()
                prev = self.record_animation
                self.record_animation = True
                if not prev:
                    self.__init_image_capture__()
                for txtcanvas in self.text_frames:
                    if not self.print_battles and battle_txt in txtcanvas:
                        continue
                    if self.clear_screen:
                        cls()
                    sys.stdout.write("\x1b7\x1b[%d;%df%s\x1b8" % (1, 1, txtcanvas))
                    sys.stdout.flush()
                    sleep(0.02)
                    self.__capture_screen__()
                
                time_stamp = str(datetime.today())
                time_stamp = time_stamp[:time_stamp.index('.')].replace(':', '.')
                filename = self.animation_filename + ' ' + time_stamp
                self.SaveAnimation(filename)
                self.record_animation = prev
                curr_time = time()-start
                print(f'Saved as: {filename}.gif   it took {curr_time:>3.1f} seconds.')
            else:
                print('Looks like it was already saved.')
        #sleep(0.5)
    
    def __interactive_help__(self, *args):
        if self.hwnd and self.hwnd == win32gui.GetForegroundWindow():
            if self.clear_screen:
                cls()
            newline_tab = '\n\t'
            tab = '\t'
            txtcanvas = f"""
        {Fore.LIGHTYELLOW_EX}Heroes Of Might and Magic{Style.RESET_ALL} environment with color text rendering

    Hotkeys:
        {Fore.BLUE}{'left, up arrows':20}{Style.RESET_ALL} - Move back one step in the game history
        {Fore.BLUE}{'right, down arrows':20}{Style.RESET_ALL} - Move forward one step in the game history
        {Fore.GREEN}{'home':20}{Style.RESET_ALL} - Go to the beginning of this game, after the first action(s)
        {Fore.GREEN}{'end':20}{Style.RESET_ALL} - Go to the end of this game
        {Fore.RED}{'Esc, q, space':20}{Style.RESET_ALL} - Exit
        {Fore.LIGHTGREEN_EX}{'b':20}{Style.RESET_ALL} - Toggle print/skip battles. Currently show battles is {Back.WHITE}{Fore.BLACK}{'ON' if self.print_battles else 'OFF'}{Style.RESET_ALL}
        {Fore.LIGHTGREEN_EX}{'s':20}{Style.RESET_ALL} - Save .gif animation of the entire game.
                                Note: This will quickly replay the game, and can take many seconds (appox {(0.2 * len(self.text_frames)):>3.1f} seconds).
                                    The resulting .gif will usually be 10 to 100 MB, and have a 0.3 seconde between frames.
                                    The file size and time it takes are usually more than halved is battles are skipped.
        {Fore.CYAN}{'h':20}{Style.RESET_ALL} - Print this menu

    Just for fun, here are all the player colors: {', '.join(f'{PlayerColors[i]}Player {i+1}{Style.RESET_ALL}' for i in range(8))}
    The number next to players, hero and town armies are the summed up "AI-values" of the units, a measure of army strength.
    Adventure map legend:
{tab}{PlayerBColors[0]}{Fore.WHITE}h{Style.RESET_ALL} - hero, the color indicates the player, for example a hero of player 2 is {PlayerBColors[1]}{Fore.WHITE}h{Style.RESET_ALL}
{tab}{newline_tab.join(f'{ResourceColors[res_name]}{MapObjectTypes[res_name]["symbol"]}{Style.RESET_ALL} - {ResourceColors[res_name]}{res_name}{Style.RESET_ALL}' for res_name in ResourceColors)}
{tab}x - neutral army (wantering monsters)
{tab}# - unpassable terrain or part of a map object such as a town

    Recommendations:
        CLI window minimum size: 52 lines, 144 columns. Map size 36 x 36, 2 players, 1 action at a time.
        Print 1-2 actions at a time. Use small maps, and few players (2 recommended).
        Disable map of larger map sizes or more than 3 players.

    How it (currently) works:
        While the game is playing it inspects the game state on each action taken.
        This means that the game must finish first for this to properly work.


{tab}Made by {Fore.LIGHTBLUE_EX}Vlad Catalina{Style.RESET_ALL}
    """
            sys.stdout.write("\x1b7\x1b[%d;%df%s\x1b8" % (1, 1, txtcanvas))
            sys.stdout.flush()