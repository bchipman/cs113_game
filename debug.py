from collections import namedtuple

collision_points = namedtuple('collision_points', 'T, TR, R, BR, B, BL, L, TL')
collision_sides = namedtuple('collision_sides', 'T, R, B, L')
collision_data = namedtuple('collision_data', 'terrain, points, sides')


def get_collision_data(player, arena):

    def _determine_collision_points(player, terr):
        return collision_points(terr.collidepoint(player.midtop),
                                terr.collidepoint(player.topright),
                                terr.collidepoint(player.midright),
                                terr.collidepoint(player.bottomright),
                                terr.collidepoint(player.midbottom),
                                terr.collidepoint(player.bottomleft),
                                terr.collidepoint(player.midleft),
                                terr.collidepoint(player.topleft))

    def _determine_collision_sides(player, terr):
        return collision_sides(int(terr.top < player.top < terr.bottom),
                               int(terr.left < player.right < terr.right),
                               int(terr.top < player.bottom < terr.bottom),
                               int(terr.left < player.left < terr.right))

    all_collision_data = []
    for terr in arena.rects:
        all_collision_data.append(
            collision_data(terr, _determine_collision_points(player, terr), _determine_collision_sides(player, terr)))
    return all_collision_data
