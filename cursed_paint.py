import pygame
import numpy as np

from utils import Vec, Timer


# Width, height
WINDOW_SIZE = Vec(1280, 720)
DRAWING_BOARD_SIZE = Vec(512, 512)
DRAWING_BOARD_OFFSET = Vec(60, 60)
COLOR_SQUARES_Y_OFFSET = 30
COLOR_SQUARE_SIZE = 30
COLOR_SQUARE_BORDER = 2
COLOR_SQUARES_COLORS = [
    # RGB
    (255, 0,   0),
    (0,   255, 0),
    (0,   0,   255),
    # CMY
    (0,   255, 255),
    (255, 0,   255),
    (255, 255, 0),
    # BW
    (1,   1,   1), # In case alpha mask is black
    (254, 254, 254), # In case alpha mask is white
]

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


    def stamp(self, surf: pygame.Surface, offset: Vec = Vec(0, 0), with_border: bool = False):
        # First draw border
        if with_border:
            #border_color = tuple(255 - x for x in self.color)
            border_color = (0, 0, 0)
            pygame.draw.circle(surf, border_color, center=tuple(self.pos + offset), radius=self.radius + 1)
        
        # Actual stamp
        pygame.draw.circle(surf, self.color, center=tuple(self.pos + offset), radius=self.radius)
    

    def draw_line(self, surf: pygame.Surface, pos: Vec):
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


    def stamp(self, surf: pygame.Surface, bordered: bool):
        border_color = (255, 255, 255) if bordered else (0, 0, 0) 
        pygame.draw.rect(surf, border_color, pygame.Rect(tuple(self.pos - 2), tuple(self.shape + 4)))
        pygame.draw.rect(surf, self.color, pygame.Rect(tuple(self.pos), tuple(self.shape)))


def get_checkerboard(shape: Vec[int], rect_shape: Vec[float], color1 = (250, 250, 250), color2 = (230, 230, 230)) -> pygame.Surface:
    surf = pygame.Surface(tuple(shape))
    n_rects = (shape / rect_shape).ceil()
    for x_rect in range(n_rects.X):
        for y_rect in range(n_rects.Y):
            rect_start = (rect_shape * Vec(x_rect, y_rect)).floor()
            rect_stop = (rect_shape * (Vec(x_rect, y_rect) + 1)).floor()
            rect_color = color1 if (x_rect + y_rect) % 2 else color2
            pygame.draw.rect(surf, rect_color, pygame.Rect(tuple(rect_start), tuple(rect_stop - rect_start)))
    return surf


def main():
    # Initialize pygame
    pygame.init()
    window = pygame.display.set_mode(tuple(WINDOW_SIZE))
    surf_checkerboard = get_checkerboard(DRAWING_BOARD_SIZE, DRAWING_BOARD_SIZE / 16)
    surf_canvas = pygame.Surface(tuple(DRAWING_BOARD_SIZE), flags=pygame.SRCALPHA)
    canvas_blank_color = (0, 0, 0, 0)
    surf_canvas.fill(canvas_blank_color)
    # TODO: Could do surf_canvas.set_colorkey((255,255,255)) to just make white transparent 

    # Game objects
    cursor = Cursor(pos = DRAWING_BOARD_SIZE / 2)
    cursor_is_active = False
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
    selected_csq_index = 0

    # Main game loop
    should_run = True
    frame_timer = Timer(1 / FPS)
    while should_run:
        frame_timer.wait()

        # Get all new events
        events = pygame.event.get()
        
        # Process events
        for event in events:
            if event.type == pygame.QUIT:
                should_run = False
            elif event.type == pygame.KEYDOWN:
                match event.key:
                    case pygame.K_SPACE: # Clear canvas
                        surf_canvas.fill(canvas_blank_color)
                    case pygame.K_t: # Toggle cursor down
                        cursor_is_active = not cursor_is_active
                    case pygame.K_w: # Next color
                        selected_csq_index = (selected_csq_index + 1) % n_color_squares
        
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

        # Account for cursor drawing
        cursor.color = color_squares[selected_csq_index].color
        if cursor_is_active:
            cursor.stamp(surf_canvas, with_border=False)
        cursor.modify_pos(frame_cursor_delta)
        
        # Draw!
        window.fill((0, 0, 0)) # TODO: Maybe replace with blitting black rectangle? Unsure if faster
        window.blit(surf_checkerboard, tuple(DRAWING_BOARD_OFFSET)) # TODO: Maybe draw directly onto checkerboard?
        window.blit(surf_canvas, tuple(DRAWING_BOARD_OFFSET))
        cursor.stamp(window, DRAWING_BOARD_OFFSET, with_border=True)

        # Draw color squares
        for i, csq in enumerate(color_squares):
            csq: ColorSquare
            csq.stamp(window, i == selected_csq_index)
        
        # Update the display
        pygame.display.flip()
        


if __name__ == "__main__":
    main()
