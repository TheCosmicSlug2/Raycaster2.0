from settings import *
from physics_engine.physics import Physics
from math import pi

class Player:
    def __init__(self, level_master):
        self.level_master = level_master
        self.physics = Physics()
        self.dims = PLAYER_DIMS
        self.x_angle = 0
        self.y_angle = 0
        self.posx = level_master.player_starting_pos[0] * CELL_DIMS[0]
        self.posy = level_master.player_starting_pos[1] * CELL_DIMS[1]
        self.rect_sprite = None
        self.is_moving = False

    def spawn_player_random(self):
        """ Fait appraître le joueur dans un endroit aléatoire et vide """
        for row_idx in range(grid_dims[1]):
            for column_idx in range(grid_dims[0]):
                if self.level_master.map_data[row_idx][column_idx] == 0:

                    self.posx = column_idx * CELL_DIMS[0] + CELL_DIMS[0] // 2
                    self.posy = row_idx * CELL_DIMS[1] + CELL_DIMS[1] // 2
                    return True

        return False


    def spawn_player_center(self):
        """ Supprime un possible mur central et fait appraître le joueur à cet endroit """

        center_row = grid_dims[0] // 2
        center_column = grid_dims[1] // 2
        self.level_master.map_data[center_row][center_column] = 0

        self.posx = center_column * CELL_DIMS[0] // 2
        self.posy = center_row * CELL_DIMS[1] // 2

        return True


    def move(self, mvt_dir) -> None:
        """ Déplace le joueur selon un angle """
        self.is_moving = True
        lg_x, lg_y = self.physics.trouver_longueurs_trigo(self.x_angle + mvt_dir)
        next_x, next_y = self.posx + (lg_x * PLAYER_SPEED), self.posy + (lg_y * PLAYER_SPEED)
        # si le movement suivant collide un mur
        if self.physics.check_4_side_collision(
            top_left_pos=(next_x, next_y), 
            object_dims=self.dims,
            cell_dims=CELL_DIMS,
            map_data=self.level_master.map_data,
            map_data_dims=self.level_master.map_data_dims
            ):
            self.is_moving = False
            return
        self.posx, self.posy = next_x, next_y
        self.check_collisions_border()

    def check_collisions_border(self) -> None:
        """ Checke les collisions avec les bordures de la carte """
        # collisions horizontales
        if self.posx > SCREEN_DIMS[0] - self.dims[0]:
            self.posx = SCREEN_DIMS[0] - self.dims[0]
        if self.posx < 0:
            self.posx = 0
        # collisions verticales
        if self.posy > SCREEN_DIMS[1] - self.dims[1]:
            self.posy = SCREEN_DIMS[1] - self.dims[1]
        if self.posy < 0:
            self.posy = 0

    def update_x_angle(self, add_x):
        self.x_angle += add_x

        if self.x_angle < 0:
            self.x_angle += 2 * pi
        if self.x_angle > 2 * pi:
            self.x_angle -= 2 * pi

    def update_y_angle(self, add_y):
        self.y_angle = min(max(self.y_angle + add_y, 0), SCREEN_DIMS[1])