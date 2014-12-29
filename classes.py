import collections
import copy

# noinspection PyPep8Naming
import globals as GL
from skills import *

# ----------------------------------------------------------------------------
class Deque2(collections.deque):
    def __call__(self, i=0):
        return self[i]

    def __pos__(self):
        self.rotate()
        return self()

    def __neg__(self):
        self.rotate(-1)
        return self()

# -------------------------------------------------------------------------
class Rect2(pygame.Rect):
    def __init__(self, *args, **kargs):
        if args != tuple():
            if isinstance(args[0], pygame.Rect):
                super().__init__(tuple(args[0]))
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
        """follows same logic as pygame.Rect.collidelist, but customized to
        look at center coords"""
        for i in range(len(li)):
            if li[i].left < self.centerx < li[i].right and li[i].top < self.centery < li[i].bottom:
                return i
        return -1

    def p_collidelistall(self, li):
        """follows same logic as pygame.Rect.collidelistall, but customized
        to look at center coords"""
        hit_indices = []
        for i, r in enumerate(li):
            # if self.collidepoint(r.center): #Using this is causing particles to pass through terrain
            if li[i].left < self.centerx < li[i].right and li[i].top < self.centery < li[i].bottom:
                hit_indices.append(i)
        return hit_indices

# -------------------------------------------------------------------------
class Player(Rect2):
    def __init__(self, id, topleft, sprite=None):
        self.id = id  # 1 for player1, 2 for player2

        # position
        super().__init__(topleft, (30, 40))
        self.topleft_initial = self.topleft

        # speed
        self.dx = 10 if self.id == 1 else -10  # initial speed
        self.dx_initial = self.dx
        self.dy = 4  # initial fall rate
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
        self.level = 1
        self.current_exp = 0

        # used for skill pickup
        self.pickup_time = -1
        self.pickup_slot = None
        self.pickup_skill = None
        self.overlapping_skill = None

        # skills
        self.attack_id = 1
        self.skill1_id = self.skill2_id = self.skill3_id = self.ult_id = 0

        # for debugging/testing:
        # self.attack_id = random.randint(1,3)
        # self.skill1_id = random.randint(100,115)
        # self.skill2_id = random.randint(100,115)
        # self.skill3_id = random.randint(100,115)
        # self.ult_id = random.randint(1000,1003)

        # specific testing:
        # self.attack_id = 10
        # self.skill1_id = 113
        # self.skill2_id = 102
        # self.skill3_id = 123
        # self.ult_id = 1007
        # self.hit_points = 0

        # attacking
        self.facing_direction = RIGHT if self.id == 1 else LEFT
        self.facing_direction_initial = self.facing_direction
        self.attack_cooldown_expired = True
        self.new_particle = None

        # scrolling text
        self.st_buffer = []

        # sprite information
        self.state = STAND
        self.previous_state = STAND
        self.sprite = sprite
        self.wait_frames = 0
        self.animation_key = -1
        self.attack_state = ONEHAND
        self.attack_frame = 1

    @property
    def input(self):
        return GL.INPUT1 if self.id == 1 else GL.INPUT2 if self.id == 2 else None

    def play_sound(self, path, i):
        """play the skill's sound"""
        print(SKILLS_TABLE[i]['sound'])
        if SKILLS_TABLE[i]['sound'] is not 'none' and AUDIO.sound_on:
            global SOUNDS
            sound = SOUNDS.get(path)
            if sound is None:
                sound = pygame.mixer.Sound(path)
                SOUNDS[path] = sound
            sound.play()

    @property
    def skills(self):
        return [self.attack_id, self.skill1_id, self.skill2_id, self.skill3_id, self.ult_id]

    def copy(self):
        return Player(self.left, self.top, self.width, self.height)

    def shield_trigger(self, damage_taken):
        """Handles how shield works
        Call this after any damage is taken"""
        if self.hit_points < self.hit_points_max and self.conditions[SHIELD]:
            sorted(self.conditions[SHIELD], key=lambda k: k.remaining)  # Will subtract from lowest remaining time shield first
            for s in self.conditions[SHIELD]:
                damage_taken = s.exchange(damage_taken)
                if damage_taken == 0:
                    break

    def is_dead(self):
        return self.hit_points <= 0

    def handle_exp(self, exp_gain, time):
        if self.level < 10:
            self.current_exp += exp_gain
            if self.current_exp >= LEVEL_THRESHOLDS[self.level]:
                self.level += 1
                self.st_buffer.append((ST_LEVEL_UP, "LEVEL " + str(self.level) + "!", time + 1000))

    def move_ip(self, dxdy):
        super().move_ip(dxdy)

    def distance_from(self, other):
        a = self.centerx - other.centerx
        b = self.centery - other.centery
        return math.sqrt(a * a + b * b)

    def __call__(self, arena_map):
        self._handle_facing_direction()
        if not self.conditions[STUN] and not self.conditions[SILENCE]:
            self._handle_inputs(arena_map)
        self._handle_acceleration()
        self._handle_movement(arena_map)
        self._determine_state()

    def _handle_facing_direction(self):
        if self.attack_cooldown_expired and not self.conditions[STUN]:
            self.facing_direction = RIGHT if self.input.RIGHT \
                else LEFT if self.input.LEFT \
                else self.facing_direction

    def _handle_acceleration(self):

        def _apply_accel_left_right_input():
            self.dx += self.dx_movement if self.input.RIGHT \
                else -self.dx_movement if self.input.LEFT \
                else 0
            if self.input.RIGHT or self.input.LEFT:
                self.pickup_time = -1

        def _apply_friction():
            self.dx += self.dx_friction if self.dx < 0 \
                else -self.dx_friction if self.dx > 0 \
                else 0

        def _apply_accel_jump_input():
            if self.input.JUMP:
                self.pickup_time = -1
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
            if -5 < self.dy < 8:  # This helps make the jump arc smoother at the top
                self.dy += self.dy_gravity * 0.5
            else:
                self.dy += self.dy_gravity

        def _apply_limits():
            self.dx = eval('{:+}'.format(self.dx)[0] + str(min(abs(self.dx), self.dx_max)))
            self.dy = min(self.dy, self.dy_max)
            self.dy = max(self.dy, -self.dy_jump)

        if self.attack_cooldown_expired and not self.conditions[STUN]:
            # These can only be used if not attacking
            _apply_accel_left_right_input()
            _apply_accel_jump_input()

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
            for terrain in arena.non_spawn_points:
                # Check if touching ground
                if (terrain.left < self.left < terrain.right or terrain.left < self.right < terrain.right) or (self.left < terrain.left < self.right or self.left < terrain.right < self.right):
                    if self.top < terrain.top < self.bottom:
                        if self.ptop + self.height - 5 <= terrain.top:
                            self.bottom = terrain.top
                            self.dy, self.touching_ground = 0, True
                        if isinstance(self, Monster):
                            self.hit_wall_from = False
                            self.touching_ground = True
                    if self.top < terrain.bottom < self.bottom and self.dy < 0:
                        if self.ptop >= terrain.bottom:
                            self.top = terrain.bottom
                            self.dy *= 0.4  # Prevents immediate drop when player hits ceiling
                if (terrain.top < self.bottom < terrain.bottom or terrain.top < self.top < terrain.bottom) or (self.top < terrain.top < self.bottom or self.top < terrain.bottom < self.bottom):
                    if self.left < terrain.right < self.right and self.dx <= 0:
                        self.left = terrain.right
                        self.hit_wall_from = LEFT
                        self.dx = 0
                        # Sliding
                        if self.dy > 0 and not isinstance(self, Monster):
                            self.dy = 0
                    elif self.left < terrain.left < self.right and self.dx >= 0:
                        self.right = terrain.left
                        self.hit_wall_from = RIGHT
                        self.dx = 0
                        # Sliding
                        if self.dy > 0 and not isinstance(self, Monster):
                            self.dy = 0

        def _check_for_skill_pick_ups(arena):
            if not isinstance(self, Monster):
                self.overlapping_skill = None
                for skill in arena.dropped_skills:
                    if self.colliderect(skill):
                        # skill_type = get_skill_type(skill.id)
                        # if skill_type == WEAK:
                        #     self.attack_id = skill.id
                        # elif skill_type == MEDIUM:
                        #     n = random.choice((1, 2, 3))
                        #     exec('self.skill{}_id = skill.id'.format(str(n)))
                        # elif skill_type == ULTIMATE:
                        #     self.ult_id = skill.id
                        # arena.dropped_skills.remove(skill)
                        self.overlapping_skill = skill

        _move()  # move then check for collisions
        _check_for_collisions()
        _check_for_skill_pick_ups(arena)
        out_of_arena_fix(self)  # otherwise, player can jump up and over arena

    def _handle_inputs(self, arena):
        """ Handles attacks, skill buttons, and meditate
            If multiple pushed, priority is:
            ultimate > skill3 > skill2 > skill1 > attack > meditate
            Dropping/picking up skills also handled here"""

        i, button = self._priority_inputs()
        if self.input.DROP_SKILL and i != -1:  # Drop skill pressed
            self.__dict__[button] = 0 if button != ATTACKBUTTON else 1

        elif not self.input.DROP_SKILL:  # Drop skill not pressed
            # If a valid skill is pressed
            if (isinstance(i, str) or i > 0) and self.attack_cooldown_expired:
                self.pickup_time = -1
                if self.energy >= SKILLS_TABLE[i]['energy']:
                    self.attack_state = SKILLS_TABLE[i]['state']
                    self.attack_frame = SKILLS_TABLE[i]['frame']
                    if not(self.attack_state == RUN or self.attack_state == BREATH):
                        self.state = RESET
                    self.energy -= SKILLS_TABLE[i]['energy']

                    self.play_sound(SKILLS_TABLE[i]['sound'], i)

                    self.new_particle = SKILLS_TABLE[i]['start'](i, self, self.input.UP, self.input.DOWN)
                    if SKILLS_TABLE[i]['cooldown']:
                        self.attack_cooldown_expired = False
                        pygame.time.set_timer(TIME_TICK_EVENT + self.id, SKILLS_TABLE[i]['cooldown'])
                    if i == -1:
                        pygame.time.set_timer(PLAYER2_LOCK_EVENT + self.id, SKILLS_TABLE[-1]['cooldown'])
            # If skill is 0, aka empty, and sitting over a skill
            elif (i == 0 or i == 1) and self.overlapping_skill:
                if button == ATTACKBUTTON and (0 < self.overlapping_skill.id < 99):
                    if self.overlapping_skill in arena.dropped_skills:
                        self.__dict__[ATTACKBUTTON] = self.overlapping_skill.id
                        arena.dropped_skills.remove(self.overlapping_skill)
                elif button in (SKILL1BUTTON, SKILL2BUTTON, SKILL3BUTTON) and (100 <= self.overlapping_skill.id <= 999):
                    if self.overlapping_skill in arena.dropped_skills:
                        self.__dict__[button] = self.overlapping_skill.id
                        arena.dropped_skills.remove(self.overlapping_skill)
                elif button == ULTBUTTON and (self.overlapping_skill.id >= 1000):
                    if self.overlapping_skill in arena.dropped_skills:
                        self.__dict__[ULTBUTTON] = self.overlapping_skill.id
                        arena.dropped_skills.remove(self.overlapping_skill)

                # If hasnt tried to pick up skill
                # print(self.pickup_time)
                # if self.pickup_time == -1:
                #    print("flag1")
                #    self.pickup_time = 0
                #    self.pickup_slot = button
                #    self.pickup_skill = self.overlapping_skill
                #    print(self.pickup_skill.id)

                # elif self.pickup_time != -1:
                #    if self.pickup_skill != self.overlapping_skill or button != self.pickup_slot:
                #        print("flag2")
                #        self.pickup_time = 0
                #        self.pickup_slot = button
                #        self.pickup_skill = self.overlapping_skill
                #    elif self.pickup_time == 9:
                #        print("flag3")
                #        self.pickup_time = 0
                #        self.__dict__[self.pickup_slot] = self.pickup_skill.id
                #    else:
                #        print("flag4")
                #        pygame.time.set_timer(USEREVENT+2+self.id, 250)

    def _priority_inputs(self):
        if self.input.ULT:
            return self.ult_id, ULTBUTTON
        elif self.input.SKILL3:
            return self.skill3_id, SKILL3BUTTON
        elif self.input.SKILL2:
            return self.skill2_id, SKILL2BUTTON
        elif self.input.SKILL1:
            return self.skill1_id, SKILL1BUTTON
        elif self.input.ATTACK:
            return self.attack_id, ATTACKBUTTON
        return -1, ''

    def _determine_state(self):
        """Determines the player state to be used for animations"""
        self.previous_state = self.state
        if self.hit_points <= 0:
            self.state = DEATH
        elif not self.attack_cooldown_expired:
            self.state = ATTACK  # or cast
        elif self.dy < 0:
            self.state = JUMP
        elif not self.touching_ground:
            # if self.hit_wall_from:
            #     self.state = SLIDE
            # Needed if we have slide animation
            self.state = FALL
        elif self.input.RIGHT:
            self.state = RWALK
        elif self.input.LEFT:
            self.state = LWALK
        else:
            self.state = STAND

# -------------------------------------------------------------------------
class Monster(Player):
    def __init__(self, info, topleft, player1, player2, color=ORANGE):
        super().__init__(0, topleft, (info.w, info.h))
        self.dx_max, self.dy_max = info.dx, info.dy
        self.hit_points = self.hit_points_max = info.hp
        self.chasing_time = info.chase
        self.idle_time = info.idle
        self.dx_friction, self.dy_gravity, self.dy_jump = 0.5, 2, 30
        self.p1, self.p2 = player1, player2
        self.target, self.status = None, IDLE
        self.last_status_change = 0
        self.ai_input = AI_Input()
        self.color = color
        self.kind = info.kind

        self.dmg = info.dmg
        self.exp_value = info.exp_value

        self.has_hit = []
        self.has_hit_time = []
        self.hit_by = {1: False, 2: False}
        self.hit_by_time = {1: 0, 2: 0}

    @property
    def input(self):
        return self.ai_input

    def __call__(self, time, arena_map):
        self._handle_last_hit(time)
        self._ai(time)
        self._handle_facing_direction()
        self._handle_acceleration()
        self._handle_movement(arena_map)

    def _handle_last_hit(self, time):
        for i, v in enumerate(self.has_hit_time):
            if (v + 2000) <= time:
                del self.has_hit[i]
                del self.has_hit_time[i]

        if self.hit_by_time[1] + 2000 <= time:
            self.hit_by[1] = False
        if self.hit_by_time[2] + 2000 <= time:
            self.hit_by[2] = False

    def _ai(self, time):
        self._switch_mode(time)
        if self.status == CHASING and self.target is not None:
            self.input.refresh()
            if self.target.centerx >= self.centerx:
                self.input.RIGHT = True
            else:
                self.input.LEFT = True

            if self.target.centery < self.centery:
                if random.randint(1, 50) == 1:
                    self.input.JUMP = True

        else:
            self.input.JUMP = False
            if random.randint(1, 30) < 5:
                if self.input.RIGHT:
                    self.input.RIGHT = False
                    self.input.LEFT = True
                else:
                    self.input.RIGHT = True
                    self.input.LEFT = False
            if random.randint(1, 100) == 2:
                self.input.JUMP = True

    def _switch_mode(self, time):
        time_spent_in_status = time - self.last_status_change
        if self.status == CHASING and time_spent_in_status > self.chasing_time:
            self.last_status_change = time
            self.status = IDLE
        elif self.status == IDLE and time_spent_in_status > self.idle_time:
            self.last_status_change = time
            self.status = CHASING
            self._pick_new_target()

    def _pick_new_target(self):
        d1 = self.distance_from(self.p1)
        d2 = self.distance_from(self.p2)
        if d1 != d2 and random.randint(1, 50) <= 30:
            if d1 > d2:
                self.target = self.p1
            elif d2 < d2:
                self.target = self.p2
        else:
            if random.randint(1, 2) == 1:
                self.target = self.p1
            else:
                self.target = self.p2

    def on_hit(self, target, time):
        if target not in self.has_hit:
            if self.kind != ULTIMATE and not self.hit_by[target.id]:
                self.has_hit.append(target)
                self.has_hit_time.append(time)
                handle_damage(target, self.dmg, time)

            elif self.kind == ULTIMATE:
                self.has_hit.append(target)
                self.has_hit_time.append(time)
                handle_damage(target, self.dmg, time)

# -------------------------------------------------------------------------
# noinspection PyPep8Naming
class AI_Input():
    def __init__(self):
        self.RIGHT = False
        self.LEFT = False
        self.JUMP = False

    def refresh(self):
        self.RIGHT = self.LEFT = self.JUMP = False

# -------------------------------------------------------------------------
class Arena:
    def __init__(self, arena_info):
        self.background = arena_info.background
        self.max_monsters = arena_info.max_monsters
        self.possible_monsters = tuple(MONSTER_TABLE.keys()) if arena_info.possible_monsters == ALL \
            else arena_info.possible_monsters

        self.floor = Rect2(0, arena_info.floor_y, 1280, 50, color=None, spawn_point=False, hits_to_destroy=-1)
        self.left_wall = Rect2(0, 0, arena_info.left_wall_x, 600, color=None, spawn_point=False, hits_to_destroy=-1)
        self.right_wall = Rect2(arena_info.right_wall_x, 0, 1280 - arena_info.right_wall_x, 600, color=None, spawn_point=False, hits_to_destroy=-1)

        play_area_color = SKYBLUE if arena_info.background is None else None
        play_area = Rect2(self.left_wall.right, 0, self.right_wall.left - self.left_wall.right, self.floor.top, color=play_area_color, spawn_point=False, hits_to_destroy=-1)
        self.p1_spawn = (arena_info.p1_spawn[0] + play_area.left, arena_info.p1_spawn[1])
        self.p2_spawn = (arena_info.p2_spawn[0] + play_area.left, arena_info.p1_spawn[1])
        platforms = [Rect2(tuple(terr)[0:4], color=terr.color, hits_to_destroy=terr.hits_to_destroy, spawn_point=terr.spawn_point) for terr in arena_info.platforms]

        rects = [play_area, self.floor, self.left_wall, self.right_wall] + platforms
        for rect in rects[4:]:  # don't shift the first 4 rects
            rect.move_ip((play_area.left, 0))  # to account for play area starting 65 pixels from left

        self.play_area_rect = rects[0]
        self.rects = rects[1:]
        self.dropped_skills = []

    def __iter__(self):
        # currently only time iteration is used is when the rects are drawn
        for rect in [self.play_area_rect] + self.rects:
            yield rect

    @property
    def spawn_points(self):
        return filter(lambda x: x.spawn_point, self)

    @property
    def non_spawn_points(self):
        return filter(lambda x: not x.spawn_point, self)

    @property
    def destructible_terrain(self):
        return filter(lambda x: x.hits_to_destroy > 0, self)

    @property
    def random_spawn_point(self):
        return random.choice(list(self.spawn_points))

# -------------------------------------------------------------------------
class Particle(Rect2):
    def __init__(self, sid, player):
        self.sid = sid
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
        self.persistent_f = None
        self.special_f = None

        if 'conditions' in SKILLS_TABLE[sid].keys():
            for c in SKILLS_TABLE[sid]['conditions']:
                self.conditions.append(c)
        if 'on_hit_f' in SKILLS_TABLE[sid].keys():
            self.on_hit_f = SKILLS_TABLE[sid]['on_hit_f']
        if 'on_expire_f' in SKILLS_TABLE[sid].keys():
            self.on_expire_f = SKILLS_TABLE[sid]['on_expire_f']
        if 'on_terrain_f' in SKILLS_TABLE[sid].keys():
            self.on_terrain_f = SKILLS_TABLE[sid]['on_terrain_f']
        if 'persistent_f' in SKILLS_TABLE[sid].keys():
            self.persistent_f = SKILLS_TABLE[sid]['persistent_f']
        if 'special_path' in SKILLS_TABLE[sid].keys():
            self.special_f = SKILLS_TABLE[sid]['special_path']

# -------------------------------------------------------------------------
class MeleeParticle(Particle):
    def __init__(self, sid, player):
        # super().__init__(particle.width, particle.height, particle.radius, particle.cooldown, particle.duration, particle.color)
        super().__init__(sid, player)
        self.arc = self.progress = SKILLS_TABLE[sid]['arc']
        self.radius = SKILLS_TABLE[sid]['start_radius']
        self.max_radius = SKILLS_TABLE[sid]['max_radius']
        self.has_hit = []  # Need this to keep track of what it has hit;
        # melee particles are not deleted upon hitting a target, so we need
        # to know who it has hit to prevent the same target being hit
        # multiple times
        self.has_hit_time = []
        self.extend = SKILLS_TABLE[sid]['extend']
        self.dradius = (self.max_radius - self.radius) * 35 / self.duration
        self.direction = player.facing_direction

    # def update(self, time, player):
    def update(self, time):
        """Let the particle know how it belongs to so it can rotate around
        that player and also in collision detection, will not hit the player
        who made particle"""
        if self.spawn_time == 0:
            self.spawn_time = time

        for i, v in enumerate(self.has_hit_time):
            if (v + 1000) <= time:
                del self.has_hit[i]
                del self.has_hit_time[i]

        elapsed_time = time - self.spawn_time
        self.expired = (elapsed_time >= self.duration)
        r = (elapsed_time / self.duration)
        self.progress = (1 - r) * self.arc

        if self.special_f:
            self.centerx, self.centery = self.special_f(self, time)
        else:
            if self.extend:
                self.width += self.dradius
                self.radius += self.dradius / 2
            else:
                self.radius += self.dradius

            if self.direction == RIGHT:
                self.centerx = self.belongs_to.centerx + self.radius * math.cos((1 - r) * self.arc)
            else:
                self.centerx = self.belongs_to.centerx - self.radius * math.cos((1 - r) * self.arc)

            self.centery = self.belongs_to.centery - 10 - self.radius * math.sin((1 - r) * self.arc)

        if self.persistent_f:
            self.persistent_f(self, time)

    def on_hit(self, target, time):  # DON'T delete time; will use later
        if target != self.belongs_to and target not in self.has_hit:
            self.has_hit.append(target)
            self.has_hit_time.append(time)

            handle_damage(target, self.dmg, time)

            for c in self.conditions:
                c.begin(time, target)

            # On hitting monster, small pushback
            if isinstance(target, Monster):
                target.centerx += -10 * target.dx
                target.dx *= -1
                target.hit_by[self.belongs_to.id] = True
                target.hit_by_time[self.belongs_to.id] = time
                target.last_hit_by = self.belongs_to

            if self.on_hit_f:
                self.on_hit_f(self, target, time)

# -------------------------------------------------------------------------
class RangeParticle(Particle):
    def __init__(self, sid, player, up, down):
        super().__init__(sid, player)
        self.has_special = False
        self.direction = player.facing_direction
        self.originx = player.centerx  # Where the particle started
        self.originy = player.centery  # These might be useful later on
        # If has special path, upload function to special_f
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
            self.dx *= -1
            self.ddx *= -1

    def update(self, time):
        if self.spawn_time == 0:
            self.spawn_time = time

        elapsed_time = time - self.spawn_time
        self.expired = (elapsed_time >= self.duration)

        if self.special_f:
            self.centerx, self.centery = self.special_f(self, time)
        else:
            self.dx += self.ddx
            self.dy += self.ddy
            self.centerx += self.dx
            self.centery += self.dy

        if self.persistent_f:
            self.persistent_f(self, time)

    def on_hit(self, target, time):  # DONT delete time; will use later
        if target != self.belongs_to:

            handle_damage(target, self.dmg, time)

            for c in self.conditions:
                c.begin(time, target)

            # On hitting monster, small pushback
            if isinstance(target, Monster):
                target.centerx += -5 * target.dx
                target.dx *= -1
                target.hit_by[self.belongs_to.id] = True
                target.hit_by_time[self.belongs_to.id] = time
                target.last_hit_by = self.belongs_to

            if self.on_hit_f:
                self.on_hit_f(self, target, time)

# -------------------------------------------------------------------------
class FieldParticle(Particle):
    def __init__(self, sid, player):
        super().__init__(sid, player)
        self.radius = SKILLS_TABLE[sid]['radius']
        self.frequency = None
        self.persistent_pulse_f = None  # (particle, time, target)

        self.originx = self.centerx = player.centerx
        self.originy = self.centery = player.centery

        self.has_hit = []  # Need this to keep track of what it has hit;
        # melee particles are not deleted upon hitting a target, so we need
        # to know who it has hit to prevent the same target being hit
        # multiple times
        self.has_hit_time = []

        if 'persistent_pulse_f' in SKILLS_TABLE[sid].keys():
            self.persistent_pulse_f = SKILLS_TABLE[sid]['persistent_pulse_f']
        if 'frequency' in SKILLS_TABLE[sid].keys():
            self.frequency = SKILLS_TABLE[sid]['frequency']

    def update(self, time):
        if self.spawn_time == 0:
            self.spawn_time = time

        for i, v in enumerate(self.has_hit_time):
            if (v + 200) <= time:
                del self.has_hit[i]
                del self.has_hit_time[i]

        elapsed_time = time - self.spawn_time
        self.expired = (elapsed_time >= self.duration)

        if self.persistent_f:
            self.persistent_f(self, time)

    def is_in_field(self, target):
        return target.distance_from(self) <= self.radius

    def on_hit(self, target, time):
        # If pulse function exists
        if target != self.belongs_to and self.frequency and target not in self.has_hit:
            self.has_hit.append(target)
            self.has_hit_time.append(time)
            # On pulse
            if (time - self.spawn_time) % self.frequency == 0:
                handle_damage(target, self.dmg, time)
                for c in self.conditions:
                    c.begin(time, target)

                if isinstance(target, Monster):
                    target.centerx += -5 * target.dx
                    target.dx *= -1
                    target.hit_by[self.belongs_to.id] = True
                    target.hit_by_time[self.belongs_to.id] = time
                    target.last_hit_by = self.belongs_to
                if self.on_hit_f:
                    self.on_hit_f(self, target, time)

        # If persistent pulse function exists
        if target != self.belongs_to and self.persistent_pulse_f:
            self.peristent_pulse_f(self, target, time)

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

    def is_expired(self, time):
        if self.start == -1:
            self.start = time
        return self.duration <= (time - self.start)

# ---------------------------------Debuffs------------------------------------
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
    def __init__(self, magnitude, ticks, frequency):
        """Magnitude = Dot flat dmg value
        Frequency = Every x seconds; make frequency a factor of 250 ms"""
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

class Wounded(Condition):
    """Reduces HP regen"""
    def __init__(self, duration):
        super().__init__(duration)
        self.type = WOUNDED

class Weakened(Condition):
    """Reduces Energy regen"""
    def __init__(self, duration):
        super().__init__(duration)
        self.type = WEAKENED

# ----------------------------------Buffs-------------------------------------
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

    def is_expired(self, time):
        if self.start == -1:
            self.start = time
        self.remaining = self.duration - time - self.start
        if self.duration <= (time - self.start):
            return True
        elif self.magnitude <= 0:
            return True
        return False

    def exchange(self, damage_taken):
        if self.magnitude > 0:
            if self.magnitude > damage_taken:
                self.target.hit_points += damage_taken
                self.magnitude -= damage_taken
                return 0
            elif self.magnitude <= damage_taken:
                self.target.hit_points += self.magnitude
                temp = damage_taken - self.magnitude
                self.magnitude -= damage_taken
                return temp

class Invigorated(Condition):
    """Increases HP regen"""
    def __init__(self, duration):
        super().__init__(duration)
        self.type = INVIGORATED

class Empowered(Condition):
    """Increases energy regen"""
    def __init__(self, duration):
        super().__init__(duration)
        self.type = EMPOWERED
