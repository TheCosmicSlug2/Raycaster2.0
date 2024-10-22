import pygame as pg
from commands.command_prompt import GameCommand
from user_input.input_handler import InputHandler
from maze_solving.solver import Solver
from physics_engine.physics import Physics
from level_master import LevelMaster
from settings import *
from state_master import StateMaster
from player import Player
from renderer import Renderer
from raycaster import Raycaster

#from profilehooks import profile
#@profile(stdout=False, filename='basic.prof')  # <== Profiling

def main():

    pg.init()
    pg.mouse.set_visible(False)

    level_master = LevelMaster()
    renderer = Renderer(level_master=level_master)
    player = Player(level_master=level_master)
    raycaster = Raycaster(player=player, level_master=level_master, renderer=renderer)
    input_handler = InputHandler(screen_dims=SCREEN_DIMS)
    command_prompt = GameCommand(raycaster=raycaster, player=player, level_master=level_master)
    state_master = StateMaster()
    global_physics = Physics()

    game_running = True
    solving = False

    while game_running:

        # Mettre à jour la direction de la FOV
        player.is_moving = False
        if not state_master.mouse_visible:
            delta_mousex, delta_mousey = input_handler.get_mouse_movement_since_last_frame()
        player.update_x_angle(delta_mousex)
        player.update_y_angle(delta_mousey)

        mouse_event = input_handler.get_mouse_event()
        if mouse_event == "quit_game":
            game_running = False

        # Handling des keys
        pressed_keys = input_handler.get_keyboard_events()
        
        if "haut" in pressed_keys and not solving:
            player.move(global_physics.forward)
        if "bas" in pressed_keys and not solving:
            player.move(global_physics.backward)
        if "gauche" in pressed_keys and not solving:
            player.move(global_physics.left)
        if "droite" in pressed_keys and not solving:
            player.move(global_physics.right)
        if "r" in pressed_keys and state_master.check_solving_update_possible():
            solving = not(solving)
            if solving:
                solver = Solver(player=player, level_master=level_master)
        
        if solving:
            solver.update()

            if not solver.is_solving:
                solving = False

        if "map" in pressed_keys:
            state_master.check_map_update_possible()

        if "cmd" in pressed_keys:
            pg.mouse.set_visible(True)
            pg.display.update()

            input_command = input(
                f"\nListe des commandes : \n"
                f" => change_wall_coord \"x\" \"y\" \"couleur\"\n"
                f" => change_wall_dir \"couleur\"\n"
                f" => add_wall_dir \"couleur\"\n"
                f" => change_every_wall_in_dir \"couleur\"\n"
                f"\n >> ")
            command_prompt.receive_command(input_command)

            if command_prompt.command_title == "change_wall_coord":
                command_prompt.change_wall_coord()
            if command_prompt.command_title in ["change_wall_dir", "add_wall_dir"]:
                command_prompt.alter_wall_dir()
            if command_prompt.command_title == "change_every_wall_in_dir":
                command_prompt.change_every_wall_in_dir()
            
            if command_prompt.execution_sucess:
                renderer.render_minimap()
                print("Commande executée avec succès - Changement de la carte")
            else:
                print("Commande non exécutée")

            pg.mouse.set_visible(False)
        
        if "esc" in pressed_keys:
            state_master.check_mouse_update_possible()
            pg.mouse.set_visible(state_master.mouse_visible)
        
        # Raycasting et dessin
        raycaster.raycast(map_shown=state_master.map_shown)

        # Ici, checker si le joueur a atteint la sortie
        if global_physics.check_player_reached_exit(
            player_pos=(player.posx, player.posy),
            exit_grid_pos=level_master.end,
            cell_dims=level_master.cell_dims
        ):
            print("Reached exit !")

        if state_master.map_shown:
            renderer.render_minimap_on_screen(player, raycaster)
        else:
            renderer.render_3D_foreground(raycaster.raycast_distances, raycaster.raycast_colors)
            renderer.render_3D_foreground_on_screen(player_moving=player.is_moving, y_angle=player.y_angle, tick=state_master.global_tick)
        
        renderer.update()
        state_master.update()
        
    pg.quit()


if __name__ == "__main__":
    main()
