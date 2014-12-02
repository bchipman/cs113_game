import math

import pygame
from pygame.locals import *

from globals import *
import classes

SKILLS_TABLE = {}

# Skill ID guide:
#     -1 : meditate
#      0 : empty
#   1-99 : for auto attacks
# 100-999: for skills
# 1000+  : for ultimate

# IMPORTANT:: These attributes are MANDATORY
#   Cooldown: How long it locks your character
#   Duration: How long the particle lives
#   Energy: How much energy it costs; put 0 if no cost

# ADDING DEBUFFS TO PARTICLES (ex: slow on hit):
#   Example: DiseaseBall, id = 999
#       Create the base:
#           SKILLS_TABLE[999] = _auto_range(50,50,5,2,500,10000, YELLOW, 10, 2)
#       Add the debuffs:
#           SKILLS_TABLE[999]['conditions'] = [classes.Stun(5000), classes.Slow(5000,0.5), etc]

# CONDITIONS (Buff and DEBUFF):
# ALL DURATION IS IN MILLISECONDS.
#   Stun(duration)
#       Disables ALL inputs. They may still trickle move and gravity affects stunned.
#   Slow(duration, magnitude)
#       Reduces movement by magnitude; doesn't affect gravity.
#       Magnitude should be decimal between 0 and 1.
#   Snare(duration)
#       Freezes target in place; affects gravity
#   Dot(magnitude, ticks, frequency)
#       Deals <magnitude> damage every <frequency> for <ticks> times
#       Magnitude should be the flat dmg applied every tick.
#       Tick should be an integer.
#       Frequency should be milliseconds, factor of 250. (Ex: 1000, 500, etc.)
#   Silence(duration)
#       Doesn't affect Monsters. Prevents all attacks/skill inputs.
#   Wounded(duration)
#       Doesn't affect Monsters. Reduces Health regen by half.
#   Weakened(duration)
#       Doesn't affect Monsters. Reduces Energy regen by half.
#   Speed(duration, magnitude)
#       Increases movement by magnitude; doesn't affect gravity.
#   Shield(duration,magnitude)
#       Places a protective shield that takes damage instead of hit_points
#   Invigorate(duration)
#       Doesn't affect Monsters. Increases Health regen to 2x.
#   Empowered(duration)
#       Doesn't affect Monsters. Increases Energy regen to 2x.

# More information:
#   Do not worry about subtracting energy costs,
#   player input function will handle that.

#   RangeParticles can have two paths. The default
#   which just uses velocity and acceleration
#   It also pays attention to 'up' and 'down',
#   whether player pressed up or down.
#   Melee particles do not care about up or down.

#   "on_hit_f(current_particle, target, time)": Is the additional effects it will do on the
#   player instantly. All particle hits already deal damage
#   and place debuffs without 'on_hit_f'. Should be used for
#   instantaneous effects such as knock-back. Keep as 'None'
#   if not used.

#   "on_expire_f(current_particle)" : Additional effects it will do when the particle expires

#   "on_terrain_f(current_particle)" : Additional effects it will do when the particle hits wall


def initialize_skill_table():
    # Meditate
    SKILLS_TABLE[-1] = {'type': None, 'start': blank_function, 'cooldown': 3000, 'energy': 0}

    #-----------------------------------------------------------------------------------------
    # AUTO ATTACKS 1-99
    #-----------------------------------------------------------------------------------------

    # Slap (Default auto attack)
    SKILLS_TABLE[1] = _auto_melee(30, 30, math.pi / 2, 35, 500, 500, YELLOW, 10, 0)
    # Peashooter
    SKILLS_TABLE[2] = _auto_range(10, 10, 20, 0, 500, 5000, GREEN, 10, 0)

    #-----------------------------------------------------------------------------------------
    # SKILLS 100-999
    #-----------------------------------------------------------------------------------------

    # Teleport
    SKILLS_TABLE[100] = {'type': None, 'start': teleport_start, 'cooldown': 200, 'energy': 5}
    # Fireball
    SKILLS_TABLE[101] = _auto_range(50, 50, 5, 2, 500, 10000, RED, 10, 2)
    # Static Bolt
    SKILLS_TABLE[102] = _auto_range(50, 50, 5, 2, 500, 10000, BLUE, 10, 2)
    SKILLS_TABLE[102]["special_path"] = lightning_bolt_path
    # Boulder Toss
    ADD_BOULDER_TOSS(103)
    # Mines
    SKILLS_TABLE[104] = _auto_range(40, 40, 0, 0, 500, 10000, DKGREEN, 25, 3)
    # Shrapnel Bomb
    ADD_SHRAPNEL_BOMB(105)
    # Shield
    ADD_SHIELD(106)
    # Revolving Yo-yo
    SKILLS_TABLE[107] = _auto_melee(20, 20, math.pi*10, 35, 200, 5000, RED, 3, 5)
    # Napalm
    ADD_NAPALM(108)
    # Fire and Ice
    ADD_FIRE_AND_ICE(109)
    # Machine Gun
    SKILLS_TABLE[110] = _auto_range(10, 10, 7, 0.2, 20, 2000, BLACK, 2, 0)
    
    #-----------------------------------------------------------------------------------------
    # ULTIMATES 1000+
    #-----------------------------------------------------------------------------------------

    # Big-Hammer
    ADD_BIG_HAMMER(1000)

# Templates=================================================
def _auto_melee(width, height, arc, radius, cooldown, duration, color, dmg, energy):
    return {'type': MELEE, 'start': (lambda sid, p, u, d: classes.MeleeParticle(sid, p)),
            'width': width, 'height': height, 'arc': arc, 'radius': radius, 'cooldown': cooldown,
            'duration': duration, 'color': color, 'dmg': dmg, 'energy': energy}


def _auto_range(width, height, speed, acceleration, cooldown, duration, color, dmg, energy):
    return {'type': RANGE,
            'start': (lambda sid, player, up, down: classes.RangeParticle(sid, player, up, down)),
            'width': width, 'height': height, 'speed': speed, 'acceleration': acceleration,
            'cooldown': cooldown, 'duration': duration, 'color': color, 'dmg': dmg,
            'energy': energy}


# Individual skills =========================================

# Used for meditation
def blank_function(sid, player, up=False, down=False):
    return None

#'start' function for teleport
def teleport_start(sid, player, up, down):
    if up and not down:
        player.top -= 100
    elif down and not up:
        player.top += 100
    if player.facing_direction == RIGHT:
        player.left += 100
    else:
        player.left -= 100
    out_of_arena_fix(player)
    return None

def shield_start(sid, player, up, down):
    sh = classes.Shield(10000, 10)
    return None

# Example of a special function
# Takes in two parameters: the particle object, and time
# Returns new x and y
def lightning_bolt_path(particle, time):
    x = particle.centerx
    if particle.direction == RIGHT:
        x += 10
    else:
        x -= 10
    y = particle.originy + 10 * math.cos(x / 10)
    return x, y

def lob_motion(particle, time):
    x = particle.centerx + particle.dx
    particle.dy += particle.ddy
    y = particle.centery + particle.dy
    return x,y

def ADD_BIG_HAMMER(i):
    SKILLS_TABLE[i] = _auto_melee(75, 75, math.pi / 2, 125, 500, 500, DGREY, 20, 5)
    SKILLS_TABLE[i]['on_hit_f'] = knock_back
    SKILLS_TABLE[i]['conditions'] = [classes.Stun(3000)]
    SKILLS_TABLE[i]['start'] = big_hammer
    SKILLS_TABLE["bighammer0"] = _auto_melee(30, 30, math.pi / 2, 30, 500, 500, BROWN, 10, 0)
    SKILLS_TABLE["bighammer1"] = _auto_melee(30, 30, math.pi / 2, 60, 500, 500, BROWN, 10, 0)
def big_hammer(sid, player, up=False, down=False):
    return [classes.MeleeParticle("bighammer0", player),
            classes.MeleeParticle("bighammer1", player), classes.MeleeParticle(sid, player)]
def knock_back(particle,target,time):
    if target.dx >= 0:
        target.x -= 50
    else:
        target.x += 50
    out_of_arena_fix(target)


def ADD_BOULDER_TOSS(i):
    SKILLS_TABLE[i] = {'type': None, 'start':boulder_toss_start, 'cooldown':200, 'energy': 6}
    SKILLS_TABLE["boulder_toss"] = _auto_range(30, 30, 5, 0, 500, 3000, BLACK, 2, 0)
    SKILLS_TABLE["boulder_toss"]["conditions"] = [classes.Stun(2000)]
    SKILLS_TABLE["boulder_toss"]["special_path"] = lob_motion
def boulder_toss_start(sid, player, up=False, down=False):
    obj = classes.RangeParticle("boulder_toss", player, up, down)
    obj.dy = -15
    if player.facing_direction == RIGHT:
        obj.dx = 15
    else:
        obj.dx = -15
    obj.ddy = 1
    return obj

def ADD_SHRAPNEL_BOMB(i):
    SKILLS_TABLE[i] = {'type': None, 'start': shrapnel_bomb_start, 'cooldown': 200, 'energy':2}
    SKILLS_TABLE["shrapnel_base"] = _auto_range(25, 25, 5, 0, 200, 3000, DGREY, 10, 0)
    SKILLS_TABLE["shrapnel_base"]["special_path"] = lob_motion
    SKILLS_TABLE["shrapnel_base"]["on_hit_f"] = shrapnel_on_hit
    SKILLS_TABLE["shrapnel_base"]["on_expire_f"] = shrapnel_on_expire
    SKILLS_TABLE["shrapnel_base"]["on_terrain_f"] = shrapnel_on_terrain
    SKILLS_TABLE["shrapnel_trigger"] = {'type': None, 'start':shrapnel_trigger_start, 'cooldown':100, 'energy':0}
    SKILLS_TABLE["shrapnel0"] = _auto_range(10, 10, 2, 0, 500, 1000, DGREY, 5, 0)
    SKILLS_TABLE["shrapnel0"]["special_path"] = (lambda p,t: (p.centerx+10, p.centery))
    SKILLS_TABLE["shrapnel1"] = _auto_range(10, 10, 2, 0, 500, 1000, DGREY, 5, 0)
    SKILLS_TABLE["shrapnel1"]["special_path"] = (lambda p,t: (p.centerx-10, p.centery))
    SKILLS_TABLE["shrapnel2"] = _auto_range(10, 10, 2, 0, 500, 1000, DGREY, 5, 0)
    SKILLS_TABLE["shrapnel2"]["special_path"] = (lambda p,t: (p.centerx, p.centery+10))
    SKILLS_TABLE["shrapnel3"] = _auto_range(10, 10, 2, 0, 500, 1000, DGREY, 5, 0)
    SKILLS_TABLE["shrapnel3"]["special_path"] = (lambda p,t: (p.centerx, p.centery-10))
    SKILLS_TABLE["shrapnel4"] = _auto_range(10, 10, 2, 0, 500, 1000, DGREY, 5, 0)
    SKILLS_TABLE["shrapnel5"] = _auto_range(10, 10, 2, 0, 500, 1000, DGREY, 5, 0)
    SKILLS_TABLE["shrapnel6"] = _auto_range(10, 10, 2, 0, 500, 1000, DGREY, 5, 0)
    SKILLS_TABLE["shrapnel7"] = _auto_range(10, 10, 2, 0, 500, 1000, DGREY, 5, 0)
    SKILLS_TABLE["shrapnel4"]["special_path"] = (lambda p,t: (p.centerx+10, p.centery+10))
    SKILLS_TABLE["shrapnel5"]["special_path"] = (lambda p,t: (p.centerx+10, p.centery-10))
    SKILLS_TABLE["shrapnel6"]["special_path"] = (lambda p,t: (p.centerx-10, p.centery+10))
    SKILLS_TABLE["shrapnel7"]["special_path"] = (lambda p,t: (p.centerx-10, p.centery-10))
def shrapnel_bomb_start(sid, player, up=False, down=False):
    if player.skill1_id == 105:
        player.skill1_id = "shrapnel_trigger"
    elif player.skill2_id == 105:
        player.skill2_id = "shrapnel_trigger"
    elif player.skill3_id == 105:
        player.skill3_id = "shrapnel_trigger"
    obj = classes.RangeParticle("shrapnel_base", player, up, down)
    obj.dy = -15
    if player.facing_direction == RIGHT:
        obj.dx = 10
    else:
        obj.dx = -10
    obj.ddy = 1
    player.temp_shrapnel = obj
    return obj
def shrapnel_trigger_start(sid, player, up=False, down=False):
    if player.skill1_id == 'shrapnel_trigger':
        player.skill1_id = 105
    elif player.skill2_id == 'shrapnel_trigger':
        player.skill2_id = 105
    elif player.skill3_id == 'shrapnel_trigger':
        player.skill3_id = 105

    obj = player.__dict__['temp_shrapnel']
    del player.__dict__['temp_shrapnel']
    if not obj.expired:
        x = obj.centerx
        y = obj.centery
        obj.expired = True

        p0 = classes.RangeParticle("shrapnel0", player, up, down)
        p1 = classes.RangeParticle("shrapnel1", player, up, down)
        p2 = classes.RangeParticle("shrapnel2", player, up, down)
        p3 = classes.RangeParticle("shrapnel3", player, up, down)
        p4 = classes.RangeParticle("shrapnel4", player, up, down)
        p5 = classes.RangeParticle("shrapnel5", player, up, down)
        p6 = classes.RangeParticle("shrapnel6", player, up, down)
        p7 = classes.RangeParticle("shrapnel7", player, up, down)

        p0.centerx = p1.centerx = p2.centerx = p3.centerx = p4.centerx = p5.centerx = p6.centerx = p7.centerx = x
        p0.centery = p1.centery = p2.centery = p3.centery = p4.centery = p5.centery = p6.centery = p7.centery = y
        
        return [p0,p1,p2,p3,p4,p5,p6,p7]
    else:
        return None
def shrapnel_on_hit(particle,target,time):
    p = particle.belongs_to
    if p.skill1_id == "shrapnel_trigger":
        p.skill1_id = 105
    elif p.skill2_id == "shrapnel_trigger":
        p.skill2_id = 105
    elif p.skill3_id == "shrapnel_trigger":
        p.skill3_id = 105
    if 'temp_shrapnel' in p.__dict__.keys():
        del p.__dict__['temp_shrapnel']
def shrapnel_on_expire(particle):
    p = particle.belongs_to
    if p.skill1_id == "shrapnel_trigger":
        p.skill1_id = 105
    elif p.skill2_id == "shrapnel_trigger":
        p.skill2_id = 105
    elif p.skill3_id == "shrapnel_trigger":
        p.skill3_id = 105
    if 'temp_shrapnel' in p.__dict__.keys():
        del p.__dict__['temp_shrapnel']
def shrapnel_on_terrain(particle):
    p = particle.belongs_to
    if p.skill1_id == "shrapnel_trigger":
        p.skill1_id = 105
    elif p.skill2_id == "shrapnel_trigger":
        p.skill2_id = 105
    elif p.skill3_id == "shrapnel_trigger":
        p.skill3_id = 105
    if 'temp_shrapnel' in p.__dict__.keys():
        del p.__dict__['temp_shrapnel']


def ADD_SHIELD(i):
    SKILLS_TABLE[i] = {'type': None, 'start': shield_start, 'cooldown': 200, 'energy':2}
def shield_start(sid, player, up=False, down=False):
    sh = classes.Shield(10000,10)
    sh.begin(-1,player)
    return None
def ADD_NAPALM(i):
    SKILLS_TABLE[i] = {'type': None, 'start': napalm_start, 'cooldown': 500, 'energy':5}
    SKILLS_TABLE['napalm_main'] = _auto_range(30, 30, 2, 0, 500, 500, RED, 10, 0)
    SKILLS_TABLE['napalm0'] = _auto_range(20, 20, 2, 0, 500, 3000, RED, 10, 0)
    SKILLS_TABLE['napalm1'] = _auto_range(20, 20, 2, 0, 500, 3000, RED, 10, 0)
    SKILLS_TABLE['napalm2'] = _auto_range(20, 20, 2, 0, 500, 3000, RED, 10, 0)
    SKILLS_TABLE['napalm_main']['special_path'] = lob_motion
    SKILLS_TABLE['napalm_main']['conditions'] = [classes.Dot(3, 5, 1000)]
    SKILLS_TABLE['napalm_main']['on_expire_f'] = napalm_on_expire
    SKILLS_TABLE['napalm0']['special_path'] = lob_motion
    SKILLS_TABLE['napalm1']['special_path'] = lob_motion
    SKILLS_TABLE['napalm0']['special_path'] = lob_motion
    SKILLS_TABLE['napalm1']['special_path'] = lob_motion

def napalm_start(sid,player,up=False,down=False):
    obj = classes.RangeParticle("napalm_main", player, up, down)
    obj.dy = -15
    if player.facing_direction == RIGHT:
        obj.dx = 10
    else:
        obj.dx = -10
    obj.ddy = 1
    return obj
def napalm_on_expire(p):
    sx = p.centerx
    sy = p.centery
    obj0 = classes.RangeParticle("napalm0",p.belongs_to,False,False)
    obj1 = classes.RangeParticle("napalm0",p.belongs_to,False,False)
    obj2 = classes.RangeParticle("napalm0",p.belongs_to,False,False)
    obj0.centerx = obj1.centerx = obj2.centerx = sx
    obj0.centery = obj1.centery = obj2.centery = sy
    obj0.dy = -15
    obj1.dy = -10
    obj2.dy = -5
    if p.dx > 0:
        obj0.dx = 4
        obj1.dx = 8
        obj2.dx = 12
    else:
        obj0.dx = -4
        obj1.dx = -8
        obj2.dx = -12
    obj0.ddy = obj1.ddy = obj2.ddy = 1
    if p.belongs_to.new_particle == None:
        p.belongs_to.new_particle = [obj0, obj1, obj2]
    elif isinstance(p.belongs_to.new_particle,list):
        p.belongs_to.new_particle.append(obj0)
        p.belongs_to.new_particle.append(obj1)
        p.belongs_to.new_particle.append(obj2)
    else:
        temp = p.belongs_to.new_particle
        p.belongs_to.new_particle = [temp, obj0, obj1, obj2]

def ADD_FIRE_AND_ICE(i):
    SKILLS_TABLE[i] = {'type': None, 'start': fai_start, 'cooldown': 200, 'energy':5}
    SKILLS_TABLE['fai_fire'] = _auto_range(20, 20, 5, 2, 500, 10000, RED, 10, 2)
    SKILLS_TABLE['fai_fire']['special_path'] = fai_fire_path
    SKILLS_TABLE['fai_fire']['conditions'] = [classes.Dot(5, 3, 1000)]
    SKILLS_TABLE['fai_ice']  = _auto_range(20, 20, 5, 2, 500, 10000, LBLUE, 10, 2)
    SKILLS_TABLE['fai_ice']['special_path'] = fai_ice_path
    SKILLS_TABLE['fai_ice']['conditions'] = [classes.Snare(2500)]
def fai_start(sid,player,up=False,down=False):
    ice = classes.RangeParticle('fai_ice', player, up, down)
    fire = classes.RangeParticle('fai_fire', player, up, down)
    return [ice, fire]
def fai_fire_path(particle, time):
    x = particle.centerx
    if particle.direction == RIGHT:
        x += 10
    else:
        x -= 10
    y = particle.originy + 20 * math.cos(x / 50)
    return x, y
def fai_ice_path(particle, time):
    x = particle.centerx
    if particle.direction == RIGHT:
        x += 10
    else:
        x -= 10
    y = particle.originy + 20 * math.sin(x / 50)
    return x, y