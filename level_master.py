from random import randint
from settings import *
from maze_solving.dead_end_fill import DeadEndFill
from maze_solving.wall_follower import WallFollower
from maze_creation.depth_first import DepthFirst
from cell import Cell


class LevelMaster:
    def __init__(self):
        depth_first = DepthFirst(grid_dims=grid_dims)
        depth_first.generate_maze()
        
        self.map_data = depth_first.map_data
        #self.map_data = [[Cell(nature=0) for _ in range(grid_dims[0])] for _ in range(grid_dims[1])]
        self.player_starting_pos = depth_first.furthest_pos

        self.end = depth_first.starting_cell

        self.screen_dims = SCREEN_DIMS
        self.half_screen_dims = HALF_CELL_DIMS
        
        self.cell_dims = CELL_DIMS
        self.half_cell_dims = HALF_CELL_DIMS
        
        self.end = depth_first.starting_cell

        self.add_colors_to_wall()

        cell_end = self.map_data[self.end[1]][self.end[0]]
        cell_end.nature = 2
        cell_end.color = EXIT_COLOR

        self.map_data_dims = (len(self.map_data[0]), len(self.map_data))

        self.exit_path = []

        self.wall_idx = 0
        
        # Constante pour normaliser la distance aux murs
        # Ex : si la grille est grande, la distance au prochain mur va être petite, et on divise donc par une toute petite taille de cellule
        # Ex : si la grille est petite, la distance au prochain mur va être grande, et on divise ainsi par une grande taille de cellule
        self.normalised_wall_height = self.cell_dims[0] * const_wall_height
    
    def add_colors_to_wall(self):
        for row in self.map_data:
            for cell in row:
                if cell.nature == 1:
                    cell.color = (randint(120, 255), randint(120, 255), randint(120, 127))
    

    def solve_maze(self, current_player_grid_pos):
        if solver_name == "dead_end_fill":
            solver = DeadEndFill(
                map_data=self.map_data, 
                grid_dims=self.map_data_dims, 
                starting_grid_pos=current_player_grid_pos, 
                ending_grid_pos=self.end
            )

        if solver_name.startswith("wall_follower_"):
            if solver_name.endswith("right"):
                solver = WallFollower(
                    level_master=self,
                    side="right", 
                    starting_pos=current_player_grid_pos,
                )
            if solver_name.endswith("left"):
                solver = WallFollower(
                    level_master=self,
                    side="left", 
                    starting_pos=current_player_grid_pos
                )

        solver.solve_maze()
        self.exit_path = solver.exit_path


    def add_wall(self):
        self.map_data[self.wall_idx//self.map_data_dims[0]][self.wall_idx%self.map_data_dims[0]] = Cell(nature=1, color=self.random_rgb())
        self.wall_idx += 1
