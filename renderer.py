import pygame as pg
from settings import *
from math import sin


class Renderer:
    def __init__(self, level_master) -> None:
        self.level_master = level_master
        self.SCREEN = pg.display.set_mode(SCREEN_DIMS)
        self.clock = pg.time.Clock()
        pg.display.set_caption("2.5D Engine")

        pg.font.init()
        self.font = pg.font.SysFont('Arial', 30)

        self.render_background_command()
        self.render_minimap()
        self.render_3D_background()


    def render_background_command(self):
        self.background_command = pg.Surface(SCREEN_DIMS)
        self.background_command.fill(BLACK)
        # Créer une surface de texte
        text = "Exécutez la commande dans le cmd"
        text_color = GREEN
        text_surface = self.font.render(text, True, text_color)

        # Définir la position du texte
        text_rect = text_surface.get_rect()
        text_rect.center = (self.background_command.get_width() // 2, self.background_command.get_height() // 2)
        self.background_command.blit(text_surface, text_rect)


    @staticmethod
    def draw_vertical_gradient(surface, rect, color_start, color_end):
        """Dessine un dégradé vertical sur un rectangle."""
        r1, g1, b1 = color_start
        r2, g2, b2 = color_end

        rect_height = rect.height

        for y in range(rect_height):
            ratio = y / rect_height
            r = r1 + (r2 - r1) * ratio
            g = g1 + (g2 - g1) * ratio
            b = b1 + (b2 - b1) * ratio

            pg.draw.line(surface, (int(r), int(g), int(b)), (rect.x, rect.y + y), (rect.x + rect.width, rect.y + y))


    def render_3D_background(self):
        self._3D_background = pg.Surface(SCREEN_DIMS_Y_ENLARGED)

        up_rect = pg.Rect(0, 0, SCREEN_DIMS[0], SCREEN_DIMS[1])
        self.draw_vertical_gradient(self._3D_background, up_rect, BLUE, CYAN) #BLACK, ORANGE)#
        down_rect = pg.Rect(0, SCREEN_DIMS[1], SCREEN_DIMS[0], SCREEN_DIMS[1])
        self.draw_vertical_gradient(self._3D_background, down_rect, DARK2GRAY, DARKGRAY)
    

    def render_3D_foreground(self, liste_raycast: list, wall_colors: list):
        """ Dessine en 3D avec une liste des distances + "couleurs" pour chque distance """

        self._3D_foreground = pg.Surface(SCREEN_DIMS_Y_ENLARGED)

        # Mettre l'arrière plan 3d
        self._3D_foreground.blit(self._3D_background, (0, 0))

        nb_of_rays = len(liste_raycast)
        ray_width = SCREEN_DIMS[0] / nb_of_rays

        for ray_idx, ray_dst in enumerate(liste_raycast):
            if ray_dst is None:  # ne pas dessiner les rayons qui vont à l'infini
                continue
               
            # Calculer la hauteur à l'écran du mur
            wall_height = self.level_master.normalised_wall_height / ray_dst

            # Calculer la position et la largeur du rayon en flottant
            ray_x = ray_idx * ray_width
            ray_x_int = int(ray_x)
            next_ray_x_int = int(ray_x + ray_width)

            # Calculer la largeur en pixels
            ray_width_int = next_ray_x_int - ray_x_int

            # Calculer la couleur
            ray_color = wall_colors[ray_idx]
            wall_color_with_shades = (
                int(max(0, ray_color[0] - ray_dst // 2)), 
                int(max(0, ray_color[1] - ray_dst // 2)), 
                int(max(0, ray_color[2] - ray_dst // 2))
            )

            # Dessiner le mur
            wall_slice = pg.Rect(ray_x_int, SCREEN_DIMS[1] - int(wall_height / 2), ray_width_int, int(wall_height))
            try:

                pg.draw.rect(self._3D_foreground, wall_color_with_shades, wall_slice)
            except:
                print(ray_dst // 2)
                print(wall_color_with_shades)



    def render_minimap(self):
        self.minimap = pg.Surface(SCREEN_DIMS)
        self.minimap.fill(WHITE1)

        for idx_row, row in enumerate(self.level_master.map_data):
            for idx_column, cell in enumerate(row):

                if cell.nature == 0:
                    continue

                if cell.nature == 1:
                    rect_color = cell.color

                if cell.nature == 2: # Sortie
                    rect_color = EXIT_COLOR
                

                rect = pg.Rect(idx_column * CELL_DIMS[0], idx_row * CELL_DIMS[1], CELL_DIMS[0], CELL_DIMS[1])
                pg.draw.rect(self.minimap, rect_color, rect)
    
    def show_minimap(self):
        self.SCREEN.blit(self.minimap)

    def render_minimap_on_screen(self, player, raycaster):

        # Render les rays
        self.SCREEN.blit(self.minimap, (0, 0))
        player_center = (player.posx + HALF_PLAYER_DIMS[0], player.posy + HALF_PLAYER_DIMS[1])

        for ray_pos in raycaster.rays_final_pos:
            pg.draw.line(self.SCREEN, (255, 0, 0), (player_center[0], player_center[1]), (ray_pos[0], ray_pos[1]))
            #pg.draw.rect(self.SCREEN, BLUE, pg.Rect(ray_pos[0], ray_pos[1], RAY_DIMS[0], RAY_DIMS[1]))

        # Render le joueur
        pg.draw.rect(self.SCREEN, BLACK, pg.Rect(player.posx, player.posy, PLAYER_DIMS[0], PLAYER_DIMS[1]))
    

    def render_command_background_on_screen(self):
        self.SCREEN.blit(self.background_command, (0, 0))
    
    
    def render_3D_foreground_on_screen(self, player_moving, y_angle, tick):
        y_offset = -y_angle

        if player_moving:
            y_offset += sin(tick // 2) * 4
        
        self.SCREEN.blit(self._3D_foreground, (0, y_offset))
    

    def update(self):
        pg.display.flip()
        self.clock.tick(FPS)