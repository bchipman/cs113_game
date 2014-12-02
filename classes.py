import copy
import math
import random
from collections import namedtuple

import pygame
from pygame.locals import *

from globals import *
from skills import *

# -------------------------------------------------------------------------
class Rect2(pygame.Rect):
    def __init__(self, *args, **kargs):
        if args != tuple():
            if all_isinstance(args, tuple) and len(args) is 2:
                super().__init__(args[0], args[1])
            if all_isinstance(args, tuple) and len(args) is 1:
                super().__init__(args[0][0], args[0][1], args[0][2], args[0][3])
            elif all_isinstance(args, int):
                super().__init__(args[0], args[1], args[2], args[3])
        else:
            if all_in('left,top,width,height'.split(','), kargs.keys()):
                super().__init__(kargs['left'], kargs['top'], kargs['width'], kargs['height'])
            elif all_in(('topleft', 'size'), kargs):
                super().__init__(kargs['topleft'], kargs['size'])
            for i in 'left,top,width,height,topleft,size'.split(','):
                try:
                    kargs.pop(i)
                except KeyError:
                    pass
        for k, v in kargs.items():
            exec('self.{} = {}'.format(k, repr(v)))

    def p_collidelist(self, li):
        # follows same logic as pygame.Rect.collidelist, but customized to look at center coords
        for i in range(len(li)):
            if li[i].left < self.centerx < li[i].right and li[i].top < self.centery < li[i].bottom:
                return i
        return -1

    def p_collidelistall(self, li):
        # follows same logic as pygame.Rect.collidelistall, but customized to look at center coords
        hit_indices = []
        for i, r in enumerate(li):
            #if self.collidepoint(r.center): #Using this is causing particles to pass through terrain
            if li[i].left < self.centerx < li[i].right and li[i].top < self.centery < li[i].bottom:
                hit_indices.append(i)
        return hit_indices

    def __getattr__(self, name):
        if name == 'hits_to_destroy':
            return -1
        elif name == 'spawn_point':
            return None

# -------------------------------------------------------------------------
class Player(Rect2):
    def __init__(self, id, left, top, width, height):
        # id = 1 if player 1, id = 2 if player 2
        self.id = id

        # position
        super().__init__(left, top, width, height)
        self.topleft_initial = self.topleft

        # speed
        self.dx, self.dy = 10, 4  # initial rates
        self.dx_max, self.dy_max = 12, 15  # max speed, max fall rate

        # acceleration - player input
        self.dx_movement = 2  # +/- applied when player moves
        self.dy_jump = 35  # applied when player jumps
        self.dx_wall_jump = 15  # +/- applied when player wall jumps

        # acceleration - physics
        self.dx_friction = 0.5  # applied every frame
        self.dy_gravity = 4  # applied every frame

        # misc.
        self.touching_ground = False  # for jumping
        self.hit_wall_from = None  # for wall jumping
        self.conditions = {STUN: [], SLOW: [], SNARE: [], DOT: [], SILENCE: [], WOUNDED: [],
                           WEAKENED: [], SPEED: [], SHIELD: [], INVIGORATED: [], EMPOWERED: []}

        # character stats
        self.hit_points = self.hit_points_max = 100
        self.energy = self.energy_max = 10
        self.level = 10

        # skills
        self.attack_id = 1
        self.skill1_id = self.skill2_id = self.skill3_id = self.ult_id = 0

        # for debugging/testing:
        self.attack_id = 1
        self.skill1_id = 103
        self.skill2_id = 108
        self.skill3_id = 110
        self.ult_id = 1000

        # attacking
        self.facing_direction = RIGHT
        self.attack_cooldown_expired = True
        self.new_particle = None

        # scrolling text
        self.st_buffer = []

        # Player State
        self.state = STAND
        self.previous_state = STAND

    def copy(self):
        return Player(self.left, self.top, self.width, self.height)

    # Handles how shield works
    # Call this after any damage is taken
    def shield_trigger(self):
        if self.hit_points < self.hit_points_max and self.conditions[SHIELD]:
            sorted(self.conditions[SHIELD], key=lambda k: k.remaining)  # Will subtract from lowest remaining time shield first
            for s in self.conditions[SHIELD]:
                s.exchange()

    def is_dead(self):
        return self.hit_points <= 0

    def move_ip(self, dxdy):
        super().move_ip(dxdy)

    def distance_from(self, other):
        a = self.centerx - other.centerx
        b = self.centery - other.centery
        return math.sqrt(a * a + b * b)

    def __call__(self, input, arena_map):
        self._handle_facing_direction(input)
        if not self.conditions[STUN] and not self.conditions[SILENCE]:
            self._handle_inputs(input)
        self._handle_acceleration(input)
        self._handle_movement(arena_map)
        self._determine_state(input)

    def _handle_facing_direction(self, input):
        if self.attack_cooldown_expired and not self.conditions[STUN]:
            self.facing_direction = RIGHT if input.RIGHT \
                else LEFT if input.LEFT \
                else self.facing_direction

    def _handle_acceleration(self, input):

        def _apply_accel_left_right_input(input):
            self.dx += self.dx_movement if input.RIGHT \
                else -self.dx_movement if input.LEFT \
                else 0

        def _apply_friction():
            self.dx += self.dx_friction if self.dx < 0 \
                else -self.dx_friction if self.dx > 0 \
                else 0

        def _apply_accel_jump_input(input):
            if input.JUMP:
                if not isinstance(self, Monster):
                    self.dy -= self.dy_jump if self.touching_ground or self.hit_wall_from \
                        else 0
                    if not self.touching_ground:
                        self.dx += self.dx_wall_jump if self.hit_wall_from == LEFT \
                            else -self.dx_wall_jump if self.hit_wall_from == RIGHT \
                            else 0
                else:
                    self.dy -= self.dy_jump if self.touching_ground \
                        else 0

        def _apply_gravity():
            if (-5 < self.dy < 8): # This helps make the jump arc smoother at the top
                self.dy += self.dy_gravity * 0.5
            else:
                self.dy += self.dy_gravity

        def _apply_limits():
            self.dx = eval('{:+}'.format(self.dx)[0] + str(min(abs(self.dx), self.dx_max)))
            self.dy = min(self.dy, self.dy_max)
            self.dy = max(self.dy, -self.dy_jump)

        if self.attack_cooldown_expired and not self.conditions[STUN]:
            # These can only be used if not attacking
            _apply_accel_left_right_input(input)
            _apply_accel_jump_input(input)

        _apply_friction()
        _apply_gravity()
        _apply_limits()

    def _handle_movement(self, arena):

        def _move():
            self.ptop = self.top
            self.pleft = self.left
            if self.conditions[SNARE]:
                self.move_ip((0, 0))
            elif self.conditions[SLOW] or self.conditions[SPEED]:
                max_slow = max(self.conditions[SLOW], key=lambda x: x.magnitude).magnitude if \
                    self.conditions[SLOW] else 0
                max_speed = max(self.conditions[SPEED], key=lambda y: y.magnitude).magnitude if \
                    self.conditions[SPEED] else 0
                delta = 1.0 + max_speed - max_slow
                self.move_ip((self.dx * delta, (self.dy * delta) if self.dy < 0 else self.dy))
            else:
                self.move_ip((self.dx, self.dy))

        def _check_for_collisions():
            self.hit_wall_from, self.touching_ground = None, False  # reset every frame
            for terrain in arena.rects:
                if not terrain.spawn_point:
                    if (terrain.left < self.left < terrain.right or terrain.left < self.right < terrain.right) or (self.left < terrain.left < self.right or self.left < terrain.right < self.right):
                        if self.top < terrain.top < self.bottom:
                            if self.ptop + self.height - 5 <= terrain.top:
                                self.bottom = terrain.top
                                self.dy, self.touching_ground = 0, True
                        if self.top < terrain.bottom < self.bottom and self.dy < 0:
                            if self.ptop >= terrain.bottom:
                                self.top = terrain.bottom
                                self.dy *= 0.4  # Prevents immediate drop when player hits ceiling
                    if (terrain.top < self.bottom < terrain.bottom or terrain.top < self.top < terrain.bottom) or (self.top < terrain.top < self.bottom or self.top < terrain.bottom < self.bottom):
                        if self.left < terrain.right < self.right and self.dx <= 0:
                            self.left = terrain.right
                            self.hit_wall_from = LEFT
                            self.dx = 0
                            if self.dy > 0:
                                self.dy = 0
                        elif self.left < terrain.left < self.right and self.dx >= 0:
                            self.right = terrain.left
                            self.hit_wall_from = RIGHT
                            self.dx = 0
                            if self.dy > 0:
                                self.dy = 0

        _move()  # move then check for collisions
        _check_for_collisions()
        out_of_arena_fix(self)  # otherwise, player can jump up and over arena


    # Handles attacks, skill buttons, and meditate
    # If multiple pushed, priority is:
    #   ultimate > skill3 > skill2 > skill1 > attack > meditate
    # Dropping skills and picking up skills can be handled here later on
    def _handle_inputs(self, input):
        if input.DROP_SKILL:  # Drop skill pressed
            pass

        else:  # Drop skill not pressed
            i = self._priority_inputs(input)
            if i and self.attack_cooldown_expired:
                if self.energy >= SKILLS_TABLE[i]['energy']:
                    self.energy -= SKILLS_TABLE[i]['energy']
                    self.attack_cooldown_expired = False
                    self.new_particle = SKILLS_TABLE[i]['start'](i, self, input.UP, input.DOWN)
                    pygame.time.set_timer(TIME_TICK_EVENT + self.id, SKILLS_TABLE[i]['cooldown'])
                    if i == -1:
                        pygame.time.set_timer(PLAYER2_LOCK_EVENT + self.id, SKILLS_TABLE[-1]['cooldown'])

    def _priority_inputs(self, input):
        if input.ULT:
            return self.ult_id
        elif input.SKILL3:
            return self.skill3_id
        elif input.SKILL2:
            return self.skill2_id
        elif input.SKILL1:
            return self.skill1_id
        elif input.ATTACK:
            return self.attack_id
        elif input.MEDITATE:
            return -1
        return 0

    # Determines the player state to be used for animations
    def _determine_state(self, input):
        self.previous_state = self.state
        if self.hit_points <= 0:
            self.state = DEATH
        elif not self.attack_cooldown_expired:
            self.state = ATTACK # or cast
        elif self.dy < 0:
            self.state = JUMP
        elif not self.touching_ground:
            # if self.hit_wall_from:
            #     self.state = SLIDE
            # Needed if we have slide animation
            self.state = FALL
        elif input.RIGHT:
            self.state = RWALK
        elif input.LEFT:
            self.state = LWALK        
        else:
            self.state = STAND   

# -------------------------------------------------------------------------
class Monster(Player):
    def __init__(self, info, left, top, player1, player2):
        super().__init__(0, left, top, info.w, info.h)
        self.dx_max, self.dy_max = info.dx, info.dy
        self.hit_points = self.hit_points_max = info.hp
        self.chasing_time = info.chase
        self.idle_time = info.idle
        self.dx_friction, self.dy_gravity, self.dy_jump = 0.5, 2, 30
        self.p1, self.p2 = player1, player2
        self.target, self.status = None, IDLE
        self.last_status_change = 0
        self.ai_input = AI_Input()

    def _pick_new_target(self):
        d1 = self.distance_from(self.p1)
        d2 = self.distance_from(self.p2)
        if d1 > d2:
            self.target = self.p1
        elif d2 < d2:
            self.target = self.p2
        else:
            if random.randint(1, 2) == 1:
                self.target = self.p1
            else:
                self.target = self.p2

    def _switch_mode(self,time):
        time_spent_in_status = time - self.last_status_change
        if self.status == CHASING and time_spent_in_status > self.chasing_time:
            self.last_status_change = time
            self.status = IDLE
            self.target = None
        elif self.status == IDLE and time_spent_in_status > self.idle_time:
            self.last_status_change = time
            self.status = CHASING
            self._pick_new_target()

    def _ai(self,time):
        self._switch_mode(time)
        if self.status == CHASING:
            self.ai_input.refresh()
            if self.target.centerx >= self.centerx:
                self.ai_input.RIGHT = True
            else:
                self.ai_input.LEFT = True

            if self.target.centery < self.centery:
                if random.randint(1, 10) == 1:
                    self.ai_input.JUMP = True

        else:
            self.ai_input.JUMP = False
            if random.randint(1, 30) < 5:
                if self.ai_input.RIGHT:
                    self.ai_input.RIGHT = False
                    self.ai_input.LEFT = True
                else:
                    self.ai_input.RIGHT = True
                    self.ai_input.LEFT = False
            if random.randint(1, 10) == 2:
                self.ai_input.JUMP = True

    def __call__(self, time, arena_map):
        self._ai(time)
        self._handle_facing_direction(self.ai_input)
        self._handle_acceleration(self.ai_input)
        self._handle_movement(arena_map)

# -------------------------------------------------------------------------
class AI_Input():
    def __init__(self):
        self.RIGHT = False
        self.LEFT = False
        self.JUMP = False

    def refresh(self):
        self.RIGHT = self.LEFT = self.JUMP = False

# -------------------------------------------------------------------------
class Input:
    def __init__(self):
        try:
            self.gamepad = pygame.joystick.Joystick(0)
            self.gamepad.init()
            self.gamepad_found = True
        except pygame.error:
            self.gamepad_found = False
        self.DEBUG_VIEW = True
        self.PAUSED = False
        self.ENTER_LEAVE = False


    def refresh(self):
        self._get_gamepad_axis_buttons_pressed()
        self._get_keyboard_keys_pressed()
        self._handle_gamepad_updown_events()
        self._handle_keyboard_updown_events()
        self._update_attributes()
 
    def _get_gamepad_axis_buttons_pressed(self):
        if self.gamepad_found:
            self.gp_input = {
                GP_LEFT: round(self.gamepad.get_axis(0)) == -1,
                GP_RIGHT: round(self.gamepad.get_axis(0)) == +1,
                GP_UP: round(self.gamepad.get_axis(1)) == -1,
                GP_DOWN: round(self.gamepad.get_axis(1)) == +1,
                #     Y
                #   X   B
                #     A
                GP_Y: self.gamepad.get_button(3),
                GP_X: self.gamepad.get_button(0),
                GP_B: self.gamepad.get_button(2),
                GP_A: self.gamepad.get_button(1),
                GP_START: self.gamepad.get_button(9),
                GP_BACK: self.gamepad.get_button(8), }

    def _get_keyboard_keys_pressed(self):
        self.kb_input = pygame.key.get_pressed()

    def _handle_keyboard_updown_events(self):
        for event in pygame.event.get(KEYDOWN):
            if event.key in (K_BACKQUOTE, K_F12):
                self.DEBUG_VIEW = not self.DEBUG_VIEW
            if event.key == K_PAUSE:
                self.PAUSED = not self.PAUSED
            if event.key == K_RETURN:
                self.ENTER_LEAVE = not self.ENTER_LEAVE

    def _handle_gamepad_updown_events(self):
        if self.gamepad_found:
            # Push A and Y at same time in order for the ENTER_LEAVE input to register from gamepad
            # ENTER_LEAVE input enters game/menu from menu/game
            joy_button_down_events = pygame.event.get(JOYBUTTONDOWN)
            if len(list(filter(lambda e: e.button in [self.G_A_BUTTON, self.G_Y_BUTTON], joy_button_down_events))) == 2:
                self.ENTER_LEAVE = not self.ENTER_LEAVE
            for event in joy_button_down_events:
                if event.button == GP_START:
                    self.PAUSED = not self.PAUSED
                if event.button == GP_BACK:
                    self.DEBUG_VIEW = not self.DEBUG_VIEW

    def _update_attributes(self):
        self.LEFT = self.kb_input[K_LEFT]# or self.gp_input[GP_LEFT]
        self.RIGHT = self.kb_input[K_RIGHT]# or self.gp_input[GP_RIGHT]
        self.UP = self.kb_input[K_UP]# or self.gp_input[GP_UP]
        self.DOWN = self.kb_input[K_DOWN]# or self.gp_input[GP_DOWN]
        self.JUMP = self.kb_input[K_SPACE]# or self.gp_input[GP_A]
        self.ATTACK = self.kb_input[K_a]# or self.gp_input[GP_X]
        self.RESPAWN = self.kb_input[K_r]# or self.gp_input[GP_Y]
        self.EXIT = self.kb_input[K_q] or self.kb_input[K_ESCAPE]# or (self.gp_input[GP_START] and self.gp_input[GP_BACK])
        self.SKILL1 = self.kb_input[K_s]
        self.SKILL2 = self.kb_input[K_d]
        self.SKILL3 = self.kb_input[K_f]
        self.ULT = self.kb_input[K_g]
        self.DROP_SKILL = self.kb_input[K_q]
        self.MEDITATE = self.kb_input[K_w]
        self.ENTER = self.kb_input[K_RETURN]

    def __getattr__(self, name):
        return None

# -------------------------------------------------------------------------
class Arena:
    def __init__(self, arena_info):
        self.max_monsters = arena_info.max_monsters
        self.possible_monsters = tuple(MONSTER_TABLE.keys()) if arena_info.possible_monsters == ALL \
            else arena_info.possible_monsters

        required = [Rect2(65, 0, 1150, 475, color=SKYBLUE),  # play_area
                    Rect2(0, 475, 1280, 50, color=None),  # floor
                    Rect2(15, 0, 50, 600, color=None),  # left wall
                    Rect2(1215, 0, 50, 600, color=None)]  # right wall

        part2 = [Rect2(tuple(terr)[0:4], color=terr.color, hits_to_destroy=terr.hits_to_destroy, spawn_point=terr.spawn_point) for terr in arena_info.all_terr]
        rects = required + part2

        for rect in rects[4:]:  # don't shift amazthe first 4 rects
            rect.move_ip((65, 0))  # to account for play area starting 65 pixels from left
        self.play_area_rect = rects[0]
        self.rects = rects[1:]

    def __iter__(self):
        # currently only time iteration is used is when the rects are drawn
        for rect in [self.play_area_rect] + self.rects:
            yield rect

# -------------------------------------------------------------------------
class Particle(Rect2):
    # def __init__(self, width, height, radius, cooldown, duration, color):
    def __init__(self, sid, player):
        # super().__init__(left=0, top=0, width=width, height=height)
        self.left = 0
        self.top = 0
        self.width = SKILLS_TABLE[sid]['width']
        self.height = SKILLS_TABLE[sid]['height']
        self.cooldown = SKILLS_TABLE[sid]['cooldown']
        self.duration = SKILLS_TABLE[sid]['duration']
        self.color = SKILLS_TABLE[sid]['color']
        self.spawn_time = 0
        self.expired = False
        self.dmg = SKILLS_TABLE[sid]['dmg']
        self.energy = SKILLS_TABLE[sid]['energy']
        self.belongs_to = player
        self.conditions = []
        self.on_hit_f = None
        self.on_expire_f = None
        self.on_terrain_f = None

        if 'conditions' in SKILLS_TABLE[sid].keys():
            for c in SKILLS_TABLE[sid]['conditions']:
                self.conditions.append(c)
        if 'on_hit_f' in SKILLS_TABLE[sid].keys():
            self.on_hit_f = SKILLS_TABLE[sid]['on_hit_f']
        if 'on_expire_f' in SKILLS_TABLE[sid].keys():
            self.on_expire_f = SKILLS_TABLE[sid]['on_expire_f']
        if 'on_terrain_f' in SKILLS_TABLE[sid].keys():
            self.on_terrain_f = SKILLS_TABLE[sid]['on_terrain_f']

# -------------------------------------------------------------------------
class MeleeParticle(Particle):
    def __init__(self, sid, player):
        # super().__init__(particle.width, particle.height, particle.radius, particle.cooldown, particle.duration, particle.color)
        super().__init__(sid, player)
        self.arc = SKILLS_TABLE[sid]['arc']
        self.radius = SKILLS_TABLE[sid]['radius']
        self.has_hit = []  # Need this to keep track of what it has hit;
                           # melee particles are not delete upon hitting
                           # a target, so we need to know who it has hit
                           # to prevent the same target being hit multiple
                           # times

    # def update(self, time, player):
    # Let the particle know how it belongs to so it can
    # rotate around that player and also in collision
    # detection, will not hit the player who made particle
    def update(self, time):
        if self.spawn_time == 0:
            self.spawn_time = time

        elapsed_time = time - self.spawn_time
        self.expired = (elapsed_time >= self.duration)
        r = (elapsed_time / self.duration)

        if self.belongs_to.facing_direction == RIGHT:
            self.centerx = self.belongs_to.centerx + self.radius * math.cos((1 - r) * self.arc)
        else:
            self.centerx = self.belongs_to.centerx - self.radius * math.cos((1 - r) * self.arc)

        self.centery = self.belongs_to.centery - self.radius * math.sin((1 - r) * self.arc)

    def on_hit(self, target, time):  # DON'T delete time; will use later
        if target != self.belongs_to and target not in self.has_hit:
            self.has_hit.append(target)
            handle_damage(target, self.dmg, time)

            for c in self.conditions:
                c.begin(time, target)

            # On hitting monster, small pushback
            if isinstance(target, Monster):
                target.centerx += -5 * target.dx
                target.dx *= -1

            if self.on_hit_f:
                self.on_hit_f(self,target,time)

# -------------------------------------------------------------------------
class RangeParticle(Particle):
    def __init__(self, sid, player, up, down):
        super().__init__(sid,player)
        self.has_special = False
        self.direction = player.facing_direction
        self.originx = player.centerx  # Where the particle started
        self.originy = player.centery  # These might be useful later on

        # If has special path, upload function to special_f
        if 'special_path' in SKILLS_TABLE[sid].keys():
            self.has_special = True
            self.special_f = SKILLS_TABLE[sid]['special_path']
        else:  # Using standard linear path
            self.dx = SKILLS_TABLE[sid]['speed']
            self.ddx = SKILLS_TABLE[sid]['acceleration']

            # if player pressed up
            if up:
                self.dy = SKILLS_TABLE[sid]['speed'] * -1
                self.ddy = SKILLS_TABLE[sid]['acceleration'] * -1
            elif down:
                self.dy = SKILLS_TABLE[sid]['speed']
                self.ddy = SKILLS_TABLE[sid]['acceleration']
            elif not up and not down:
                self.dy = 0
                self.ddy = 0

        # initial position
        if player.facing_direction == RIGHT:
            self.centerx = player.centerx + 40
        else:
            self.centerx = player.centerx - 40
        self.centery = player.centery

        if self.direction == RIGHT:
            self.centerx -= 30
        else:
            self.centerx += 30
            if not self.has_special:
                self.dx *= -1
                self.ddx *= -1

    def update(self, time):
        if self.spawn_time == 0:
            self.spawn_time = time

        elapsed_time = time - self.spawn_time
        self.expired = (elapsed_time >= self.duration)

        if self.has_special:
            self.centerx,self.centery = self.special_f(self,time)
        else:
            self.dx += self.ddx
            self.dy += self.ddy
            self.centerx += self.dx
            self.centery += self.dy

    def on_hit(self, target, time):  # DONT delete time; will use later
        if target != self.belongs_to:
            handle_damage(target, self.dmg, time)

            for c in self.conditions:
                c.begin(time, target)

            # On hitting monster, small pushback
            if isinstance(target, Monster):
                target.centerx += -5 * target.dx
                target.dx *= -1

            if self.on_hit_f:
                self.on_hit_f(self, target, time)

# -------------------------------------------------------------------------
class GameTime:
    def __init__(self):
        self.qsec = 0

    def __call__(self):
        return self.qsec

    def inc(self):
        self.qsec += 1

    @property
    def msec(self):
        return self.qsec * 250

    def as_seconds(self):
        return self.qsec / 4

    def as_half_seconds(self):
        return self.qsec / 2

    def as_quarter_seconds(self):
        return self.qsec

    def __str__(self):
        sec = self.qsec / 4
        return '{:>2}:{:0>2}'.format(str(int(sec / 60)), str(int(sec % 60)))

# ------------------------------------------------------------------------
class Condition:
    def __init__(self, duration):
        self.start = -1
        self.duration = duration

    def begin(self, time, target):
        c = copy.copy(self)
        c.start = time
        c.target = target
        target.conditions[c.type].append(c)

    def is_expired(self,time):
        if self.start == -1:
            self.start = time
        return self.duration <= (time - self.start)

#---Debuffs-----------------------------------------------------------------
class Stun(Condition):
    def __init__(self, duration):
        super().__init__(duration)
        self.type = STUN

class Slow(Condition):
    # Magnitude = 0 to 1
    def __init__(self, duration, magnitude):
        super().__init__(duration)
        self.magnitude = magnitude
        self.type = SLOW

class Snare(Condition):
    def __init__(self, duration):
        super().__init__(duration)
        self.type = SNARE

class Dot(Condition):
    # Magnitude = Dot flat dmg value
    # Frequency = Every x seconds; make frequency a factor of 250 ms
    def __init__(self, magnitude, ticks, frequency):
        super().__init__(ticks * frequency)
        self.magnitude = magnitude
        self.frequency = frequency
        self.last_tick = self.start
        self.ticks = ticks
        self.type = DOT

    def begin(self, time, target):
        c = copy.copy(self)
        c.start = time
        c.target = target
        c.last_tick = time
        target.conditions[c.type].append(c)

    def is_expired(self, time):
        t = time - self.last_tick
        if t >= self.frequency:
            self.last_tick = time
            handle_damage(self.target, self.magnitude, time)
            self.ticks -= 1
        return self.ticks <= 0

class Silence(Condition):
    def __init__(self, duration):
        super().__init__(duration)
        self.type = SILENCE

# Reduces HP regen
class Wounded(Condition):
    def __init__(self, duration):
        super().__init__(duration)
        self.type = WOUNDED

# Reduces Energy regen
class Weakened(Condition):
    def __init__(self, duration):
        super().__init__(duration)
        self.type = WEAKENED

#---Buffs-------------------------------------------------------------------
class Speed(Condition):
    def __init__(self, duration, magnitude):
        super().__init__(duration)
        self.type = SPEED
        self.magnitude = magnitude

class Shield(Condition):
    def __init__(self, duration, magnitude):
        super().__init__(duration)
        self.magnitude = magnitude
        self.type = SHIELD
        self.remaining = self.duration  # used for sorting

    def is_expired(self,time):
        if self.start == -1:
            self.start = time
        self.remaining = self.duration - time - self.start
        if self.duration <= (time - self.start):
            return True
        elif self.magnitude <= 0:
            return True
        return False

    def exchange(self):
        if self.magnitude > 0 and (self.target.hit_points != self.target.hit_points_max):
            diff = min(self.target.hit_points_max - self.target.hit_points, self.magnitude)
            self.target.hit_points += diff
            self.magnitude -= diff

# Increases HP regen
class Invigorated(Condition):
    def __init__(self, duration):
        super().__init__(duration)
        self.type = INVIGORATED

# Increases energy regen
class Empowered(Condition):
    def __init__(self, duration):
        super().__init__(duration)
        self.type = EMPOWERED