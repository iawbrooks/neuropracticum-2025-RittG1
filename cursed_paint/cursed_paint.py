from pathlib import Path
from typing import NamedTuple
import threading
import getpass
import time
import datetime

import pygame
from pygame import Surface
import numpy as np

from utils import Vec, Timer

IS_RPI = getpass.getuser() == "neuropracticum"
if IS_RPI:
    print(f"Running on Raspberry Pi!")
    from utils import serial_utils
    serial_thread = threading.Thread(target=serial_utils.read_from_port, args=(serial_utils.serial_port, ))
    serial_thread.start()
else:
    print(f"NOT running on Raspberry Pi! (I think)")
PROJECT_DIR = Path(__file__).parent


# Width, height
WINDOW_SIZE = Vec(1280, 720)
DRAWING_BOARD_SIZE = Vec(512, 512)
DRAWING_BOARD_OFFSET = Vec(60, 60)
COLOR_SQUARES_Y_OFFSET = 30
COLOR_SQUARE_SIZE = 30
COLOR_SQUARE_BORDER = 2
COLOR_SQUARES_COLORS = [
    (255, 0,   0),   # Red
    (0,   170, 50),  # Green
    (10,  10,  200), # Blue
    (255, 255, 0),   # Yellow
    (255, 180, 180), # Pink
    (255, 150, 0),   # Orange
    (130, 0,   200), # Purple
    (1,   1,   1),   # Black
    (140, 70,  0),   # Brown
]

IMAGE_SHOW_PERIOD_SEC = 30
FPS = 60

CURSOR_VELOCITY = 150 / FPS # How many pixels per second should the cursor move?
CURSOR_MAX_RADIUS = 64

class Cursor():
    """
    Keeps track of the drawing cursor.

    Note: `pos` is relative to the top-left of the drawing board!
    """
    pos: Vec
    radius: int
    color: tuple[float, float, float]


    def __init__(self,
                 pos: Vec = Vec(0, 0),
                 radius: int = 8,
                 color: tuple[float, float, float] = (255, 0, 0),
                 ):
        self.pos = pos
        self.radius = radius
        self.color = color


    def modify_radius(self, by: float):
        self.radius = max(min(self.radius + by, CURSOR_MAX_RADIUS), 1)
    

    def modify_pos(self, by: Vec):
        self.pos = Cursor.bound_valid_pos(self.pos + by)


    def stamp(self, surf: Surface, offset: Vec = Vec(0, 0), with_border: bool = False):
        # First draw border
        if with_border:
            #border_color = tuple(255 - x for x in self.color)
            border_color = (0, 0, 0)
            pygame.draw.circle(surf, border_color, center=tuple(self.pos + offset), radius=self.radius + 1)
        
        # Actual stamp
        pygame.draw.circle(surf, self.color, center=tuple(self.pos + offset), radius=self.radius)
    

    def draw_line(self, surf: Surface, pos: Vec):
        """
        Looks awful lol don't use
        """
        pygame.draw.line(surf, self.color, tuple(pos.astype(int)), tuple(self.pos.astype(int)), self.radius * 2 + 1)


    def bound_valid_pos(pos: Vec) -> Vec:
        return Vec.min(DRAWING_BOARD_SIZE, Vec.max(Vec(0, 0), pos))
    


class ColorSquare():
    color: tuple[int, int, int]
    pos: Vec[int]
    shape: Vec[int]

    def __init__(self, color: tuple[int, int, int], pos: Vec[int], shape: Vec[int]):
        self.color = color
        self.pos = pos
        self.shape = shape


    def stamp(self, surf: Surface, bordered: bool):
        border_color = (255, 255, 255) if bordered else (0, 0, 0) 
        pygame.draw.rect(surf, border_color, pygame.Rect(tuple(self.pos - 2), tuple(self.shape + 4)))
        pygame.draw.rect(surf, self.color, pygame.Rect(tuple(self.pos), tuple(self.shape)))


class ReferenceDrawing(NamedTuple):
    surf: Surface
    name: str


class GameState():
    cursor: Cursor
    reference_drawings: list[ReferenceDrawing]
    color_squares: list[ColorSquare]
    selected_drawing: ReferenceDrawing

    cursor_is_active: bool
    remaining_drawing_indices: list[int]
    selected_color_square_index: int
    n_color_squares: int
    
    t_last_reference_drawing: float

    def __init__(self):
        self.cursor = Cursor(pos = DRAWING_BOARD_SIZE / 2)
        self.reference_drawings = load_drawings()
        self.color_squares = get_color_squares()

        self.cursor_is_active = False
        self.remaining_drawing_indices = list(range(len(self.reference_drawings)))
        self.selected_color_square_index = 0
        self.n_color_squares = len(self.color_squares)

        self.t_last_reference_drawing = time.time()


    def draw_squares(self, surf: Surface):
        for i, csq in enumerate(self.color_squares):
            csq.stamp(surf, i == self.selected_color_square_index)
    

    def draw_cursor(self, surf: Surface):
        self.cursor.color = self.color_squares[self.selected_color_square_index].color
        if self.cursor_is_active:
            self.cursor.stamp(surf, with_border=False)


    def select_next_drawing(self):
        self.t_last_reference_drawing = time.time()
        idx: int = np.random.choice(self.remaining_drawing_indices)
        self.selected_drawing = self.reference_drawings[idx]
        self.remaining_drawing_indices.remove(idx)
        print(f"Selected new drawing '{self.selected_drawing.name}'; {len(self.remaining_drawing_indices)} left")
    

    def save_current_drawing(self, from_surf: Surface):
        save_dir = PROJECT_DIR / "output_art"
        now = datetime.datetime.now()
        filename = f"[{now.year}-{now.month:02}-{now.day}] [{now.hour:02}h{now.minute:02}m{now.second:02}s] {self.selected_drawing.name}.png"
        filepath = save_dir / filename
        pygame.image.save(from_surf, filepath)


    def select_next_color(self):
        self.selected_color_square_index = (self.selected_color_square_index + 1) % self.n_color_squares

    
    def toggle_cursor(self):
        self.cursor_is_active = not self.cursor_is_active



def get_checkerboard(shape: Vec[int], rect_shape: Vec[float], color1 = (250, 250, 250), color2 = (230, 230, 230)) -> Surface:
    surf = Surface(tuple(shape))
    n_rects = (shape / rect_shape).ceil()
    for x_rect in range(n_rects.X):
        for y_rect in range(n_rects.Y):
            rect_start = (rect_shape * Vec(x_rect, y_rect)).floor()
            rect_stop = (rect_shape * (Vec(x_rect, y_rect) + 1)).floor()
            rect_color = color1 if (x_rect + y_rect) % 2 else color2
            pygame.draw.rect(surf, rect_color, pygame.Rect(tuple(rect_start), tuple(rect_stop - rect_start)))
    return surf


def load_drawings() -> list[ReferenceDrawing]:
    """
    Loads all images and scales to size of the drawing board
    """
    images = []
    for file in (PROJECT_DIR / "resources/drawings").iterdir():
        image = pygame.image.load(file)
        image = pygame.transform.scale(image, tuple(DRAWING_BOARD_SIZE))
        images.append(ReferenceDrawing(image, file.stem))
    print(f"Loaded {len(images)} reference drawings")
    return images


def get_color_squares():
    n_color_squares = len(COLOR_SQUARES_COLORS)
    color_squares = np.empty(n_color_squares, dtype=object)
    csq_xstart = DRAWING_BOARD_OFFSET.X
    csq_ystart = DRAWING_BOARD_OFFSET.Y + DRAWING_BOARD_SIZE.Y + COLOR_SQUARES_Y_OFFSET
    for i in range(n_color_squares):
        color_squares[i] = ColorSquare(
            COLOR_SQUARES_COLORS[i],
            pos = Vec(csq_xstart + i*(COLOR_SQUARE_SIZE + COLOR_SQUARE_BORDER * 2), csq_ystart),
            shape = Vec(COLOR_SQUARE_SIZE, COLOR_SQUARE_SIZE)
        )
    return color_squares


def main():
    # Initialize pygame
    pygame.init()
    window = pygame.display.set_mode(tuple(WINDOW_SIZE))
    surf_checkerboard = get_checkerboard(DRAWING_BOARD_SIZE, DRAWING_BOARD_SIZE / 16)
    surf_canvas = Surface(tuple(DRAWING_BOARD_SIZE), flags=pygame.SRCALPHA)
    surf_blacksquare = Surface(tuple(DRAWING_BOARD_SIZE))
    surf_blacksquare.set_alpha(255)
    canvas_blank_color = (0, 0, 0, 0)
    surf_canvas.fill(canvas_blank_color)
    # TODO: Could do surf_canvas.set_colorkey((255,255,255)) to just make white transparent 
    
    # Drawings
    game = GameState()
    game.select_next_drawing()

    # Main game loop
    should_run = True
    frame_timer = Timer(1 / FPS)
    while should_run:
        frame_timer.wait()
        t_frame = time.time()

        # Get all new events
        events = pygame.event.get()
        
        ######################
        ### Process events ###
        ######################
        for event in events:
            if event.type == pygame.QUIT:
                should_run = False
            elif event.type == pygame.KEYDOWN:
                match event.key:
                    case pygame.K_SPACE: # Clear canvas
                        surf_canvas.fill(canvas_blank_color)
                    case pygame.K_t: # Toggle cursor down
                        game.toggle_cursor()
                    case pygame.K_w: # Next color
                        game.select_next_color()
        
        # Process continuous keyboard inputs
        keys = pygame.key.get_pressed()
        frame_cursor_delta = Vec(0, 0)
        if keys[pygame.K_UP]:
            frame_cursor_delta.Y -= CURSOR_VELOCITY
        if keys[pygame.K_DOWN]:
            frame_cursor_delta.Y += CURSOR_VELOCITY
        if keys[pygame.K_LEFT]:
            frame_cursor_delta.X -= CURSOR_VELOCITY
        if keys[pygame.K_RIGHT]:
            frame_cursor_delta.X += CURSOR_VELOCITY
        game.cursor.modify_pos(frame_cursor_delta)
        
        #########################
        ### Raspberry Pi Shit ###
        #########################

        if IS_RPI:
            emg = serial_utils.get_emg_activation()
            print(emg)

        ###############
        ### Drawing ###
        ###############

        # Draw drawings
        window.fill((0, 0, 0)) # TODO: Maybe replace with blitting black rectangle? Unsure if faster
        window.blit(surf_checkerboard, tuple(DRAWING_BOARD_OFFSET)) # TODO: Maybe draw directly onto checkerboard?
        window.blit(surf_canvas, tuple(DRAWING_BOARD_OFFSET))

        # Draw cursor & color squares
        game.cursor.stamp(window, DRAWING_BOARD_OFFSET, with_border=True)
        game.draw_cursor(surf_canvas)
        game.draw_squares(window)
        
        # Currently shown drawing logic
        pos_shown_drawing = tuple(DRAWING_BOARD_OFFSET + Vec(DRAWING_BOARD_SIZE.X + DRAWING_BOARD_OFFSET.X, 0))
        surf_blacksquare.set_alpha(255 * (t_frame - game.t_last_reference_drawing) / IMAGE_SHOW_PERIOD_SEC)
        if t_frame - game.t_last_reference_drawing > IMAGE_SHOW_PERIOD_SEC:
            game.save_current_drawing(surf_canvas)
            surf_canvas = get_checkerboard(DRAWING_BOARD_SIZE, DRAWING_BOARD_SIZE / 16)
            game.select_next_drawing()
        window.blit(game.selected_drawing.surf, pos_shown_drawing)
        window.blit(surf_blacksquare, pos_shown_drawing)
        
        # Update the display
        pygame.display.flip()
    
    # Cleanup
    if IS_RPI:
        serial_utils.thread_should_run = False
        time.sleep(0.5)


if __name__ == "__main__":
    main()
