import pygame
from random import randint
from sys import exit
from typing import Tuple

# Constants
SCREEN_DIMS = (144, 256)
PIPE_GAP = 40
FLOOR_ORIGIN_Y = 200
FLOOR_HEIGHT = 56
MIN_PIPE_HEIGHT = 30
MAX_PIPE_HEIGHT = SCREEN_DIMS[1] - FLOOR_HEIGHT - PIPE_GAP - MIN_PIPE_HEIGHT
BOARD_SPEED = 1 

class TextureManager:
    texture_surface = None

    @classmethod
    def load_texture(cls, texture_path):
        cls.texture_surface = pygame.image.load(texture_path).convert_alpha()

class Bird(TextureManager, pygame.sprite.Sprite):
    DEFAULT_ORIGIN = (SCREEN_DIMS[0] // 4,  SCREEN_DIMS[1] // 2)

    def __init__(self):
        pygame.sprite.Sprite.__init__(self)
        self.textures = [
            TextureManager.texture_surface.subsurface(3, 491, 17, 12),
            TextureManager.texture_surface.subsurface(31, 491, 17, 12),
            TextureManager.texture_surface.subsurface(59, 491, 17, 12)
        ]
        self.texture_index = 0
        self.texture_multiplier = 1
        self.image = self.textures[self.texture_index]
        self.rect = self.image.get_rect(center = Bird.DEFAULT_ORIGIN)
        
        # Animation parameters
        self.gravity = 0
    
    # Method to update the current texture of the bird
    def animate(self):
        if self.rect.bottom < FLOOR_ORIGIN_Y:
            self.texture_index += self.texture_multiplier / 5 
            if self.texture_index < 0 or self.texture_index >= 3:
                self.texture_multiplier *= -1
                self.texture_index += self.texture_multiplier

            self.image = self.textures[int(self.texture_index)] 
    
    def jump(self):
        self.gravity = -2 # Restart gravity
    
    def apply_gravity(self):
        # Apply effect of gravity in the Y axis
        self.gravity += 0.1
        if self.rect.bottom < FLOOR_ORIGIN_Y:
            self.rect.y += self.gravity

    def update(self):
        self.apply_gravity()
        self.animate()
    
    def reset(self):
        '''
        Reset parameters of the current instance of bird to start a new game 
        '''
        self.texture_index = 0
        self.gravity = 0
        self.rect.center = Bird.DEFAULT_ORIGIN

class Pipe(TextureManager, pygame.sprite.Sprite):
    def __init__(self, type: str, pipe_board_in_y: int):
        pygame.sprite.Sprite.__init__(self)

        match type:
            case 'top':
                self.image = TextureManager.texture_surface.subsurface(56, 323, 26, 160)
                self.rect = self.image.get_rect(midbottom = (SCREEN_DIMS[0] + 10, pipe_board_in_y))
            case 'bottom':
                self.image = TextureManager.texture_surface.subsurface(84, 323, 26, 160)
                self.rect = self.image.get_rect(midtop = (SCREEN_DIMS[0] + 10, pipe_board_in_y))

    def animate(self):
        self.rect.x -= BOARD_SPEED
    
    def update(self):
        self.animate()
        self.destroy()
    
    def destroy(self):
        if self.rect.right < 0: # Check if it is possible to destroy the pipe
            self.kill()

class Floor(TextureManager, pygame.sprite.Sprite):
    def __init__(self, floor_origin_x):
        pygame.sprite.Sprite.__init__(self)
        self.image = TextureManager.texture_surface.subsurface(292, 0, 168, 56)
        self.rect = self.image.get_rect(topleft = (floor_origin_x, FLOOR_ORIGIN_Y))
    
    def update(self):
        self.animate()
        self.destroy()

    def animate(self):
        self.rect.x -= BOARD_SPEED

    def destroy(self):
        if self.rect.right < 0:
            self.kill()

class Point(pygame.sprite.Sprite):
    def __init__(self, bottom_pipe, top_pipe):
        super().__init__()
        self.image = pygame.surface.Surface((1, PIPE_GAP))
        self.rect = self.image.get_rect()
        self.rect.midbottom = bottom_pipe.rect.midtop
        self.rect.midtop = top_pipe.rect.midbottom
        self.rect = self.image.get_rect(midbottom = bottom_pipe.rect.midtop)
    
    def animate(self):
        self.rect.x -= BOARD_SPEED 
    
    def update(self):
        self.animate()

# Additional functions
def generate_pipes() -> tuple[Pipe, Pipe]:
    # Generate pipe at the bottom
    height = randint(MIN_PIPE_HEIGHT, MAX_PIPE_HEIGHT)
    pipe_border = SCREEN_DIMS[1] - FLOOR_HEIGHT - height
    bottom_pipe = Pipe('bottom', pipe_border)

    # Generate top pipe
    top_pipe = Pipe('top', pipe_border - PIPE_GAP)
    return (bottom_pipe, top_pipe)

def check_group_collision(single: pygame.sprite.GroupSingle, group: pygame.sprite.Group, kill: bool) -> bool:
    '''
    Function that checks if a member of a single group collided with any of the members of a group.
    If kill is True, the collided member of group will be deleted, otherwise, the members won't be
    deleted by the execution of this function.
    Returns True if a collision happened between single and a member of group.
    '''
    if pygame.sprite.spritecollide(single.sprite, group, kill):
        return True
    return False

def render_score(screen: pygame.Surface, font: pygame.font.Font, score: int, position: str):
    '''
    screen is a surface in which the score will be printed, font is the font that will be used
    and int is the score integer number.
    position is a string in ("top", "bottom", "mid") 
    '''

    position_dict = {
        "top": (SCREEN_DIMS[0] // 2, SCREEN_DIMS[1] // 6),
        "mid": (SCREEN_DIMS[0] // 2, SCREEN_DIMS[1] // 2),
        "bottom": (SCREEN_DIMS[0] // 2, SCREEN_DIMS[1] - (SCREEN_DIMS[1] // 4))
    }

    # Enable bold and print the background of the font
    font.set_bold(True)
    score_surface = font.render(f"{score}", False, 'Black')
    score_rect = score_surface.get_rect(center = (position_dict[position]))
    screen.blit(score_surface, score_rect)
    
    # Disable font (regular) and print the front of the font
    font.set_bold(False)
    score_surface = font.render(f"{score}", False, 'White')
    screen.blit(score_surface, score_rect)


def main():
    pygame.init()
    screen = pygame.display.set_mode(SCREEN_DIMS, pygame.RESIZABLE | pygame.SCALED)
    pygame.display.set_caption('Flappy Bird')
    clock = pygame.time.Clock()

    # Load sounds
    sounds = {
        'point': pygame.mixer.Sound('sounds/sfx_point.wav'),
        'hit': pygame.mixer.Sound('sounds/sfx_hit.wav'),
        'die': pygame.mixer.Sound('sounds/sfx_die.wav'),
        'wing': pygame.mixer.Sound('sounds/sfx_wing.wav'),
        'tap': pygame.mixer.Sound('sounds/sfx_swooshing.wav')
    }

    # Enable texture manager
    TextureManager.load_texture('textures.png')

    # Font
    font = pygame.font.Font('PixelMillennium-1oBZ.ttf', 30)

    # Game over sprites 
    game_over = pygame.sprite.Sprite()
    game_over.image = TextureManager.texture_surface.subsurface(395, 59, 96, 21)
    game_over.rect = game_over.image.get_rect(center = (SCREEN_DIMS[0] // 2, SCREEN_DIMS[1] // 4))
    ok_button = pygame.sprite.Sprite()
    ok_button.image = TextureManager.texture_surface.subsurface(462, 42, 40, 14)
    ok_button.rect = ok_button.image.get_rect(center = (SCREEN_DIMS[0] // 2, SCREEN_DIMS[1] - (SCREEN_DIMS[1] // 3)))

    # Add game over sprites to a group
    game_over_sprites = pygame.sprite.Group()
    game_over_sprites.add(game_over, ok_button) # Index 1 is a button

    # Start screen sprites
    title = pygame.sprite.Sprite()
    title.image = TextureManager.texture_surface.subsurface(351, 91, 89, 24)
    title.rect = title.image.get_rect(center = (SCREEN_DIMS[0] // 2, SCREEN_DIMS[1] // 4))
    run_button = pygame.sprite.Sprite()
    run_button.image = TextureManager.texture_surface.subsurface(354, 118, 52, 29)
    run_button.rect = run_button.image.get_rect(center = (SCREEN_DIMS[0] // 2, SCREEN_DIMS[1] // 2))

    # Add start screen sprites to a group
    start_sprites = pygame.sprite.Group()
    start_sprites.add(title, run_button) # index 1 is a button

    # Instruction screen sprites
    ready = pygame.sprite.Sprite()
    ready.image = TextureManager.texture_surface.subsurface(295, 59, 92, 25)
    ready.rect = ready.image.get_rect(center = (SCREEN_DIMS[0] // 2, SCREEN_DIMS[1] // 4))
    tap = pygame.sprite.Sprite()
    tap.image = TextureManager.texture_surface.subsurface(292, 91, 57, 49)
    tap.rect = tap.image.get_rect(center = (SCREEN_DIMS[0] // 2, SCREEN_DIMS[1] // 2))

    # Add instruction screen sprites to a group
    instruction_sprites = pygame.sprite.Group()
    instruction_sprites.add(ready, tap)

    # Create background
    background_surface = TextureManager.texture_surface.subsurface(0, 0, *SCREEN_DIMS)

    # Create floor tiles
    floor_tiles = pygame.sprite.Group()
    floor_tiles.add(Floor(0), Floor(SCREEN_DIMS[0] + 1))

    # Create bird group
    bird = pygame.sprite.GroupSingle()
    bird.add(Bird())
    score = 0

    # Create pipes group
    pipes = pygame.sprite.Group()

    # Create points group (points between pipes)
    points = pygame.sprite.Group()
    
    # Set timer for pipes generation
    pipes_timer = pygame.USEREVENT + 1
    pygame.time.set_timer(pipes_timer, 1500) # 2 seconds

    game_state = 0
    while True:
        # Events catcher -->
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()
            
            # Intro screen
            if game_state == 0:
                if event.type == pygame.MOUSEBUTTONDOWN:
                    if start_sprites.sprites()[1].rect.collidepoint(pygame.mouse.get_pos()):
                        sounds['tap'].play()
                        game_state = 1
            
            # Instructions screen
            elif game_state == 1:
                if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE or event.type == pygame.MOUSEBUTTONDOWN: 
                    game_state = 2
                    sounds['wing'].play()
                    bird.sprite.jump()

            # Game screen
            elif game_state == 2:
                # Pipes generator
                if event.type == pipes_timer:
                    new_pipes = generate_pipes()
                    pipes.add(new_pipes)
                    points.add(Point(*new_pipes)) # Generate points for the new pair of pipes
            
                # Jump!
                if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE or event.type == pygame.MOUSEBUTTONDOWN:
                    sounds['wing'].play()
                    bird.sprite.jump()
            
            # Game over screen
            elif game_state == 3:
                if event.type == pygame.MOUSEBUTTONDOWN:
                    if game_over_sprites.sprites()[1].rect.collidepoint(pygame.mouse.get_pos()):
                        sounds['tap'].play()
                        game_state = 0 
                        bird.sprite.reset()
                        score = 0 # Restart score
                        points.empty() # Delete all the remaining points
                        pipes.empty() # Delete all the remaining pipes
            
        # Intro screen
        if game_state == 0:
            screen.blit(background_surface, background_surface.get_rect())
            start_sprites.draw(screen)
            floor_tiles.draw(screen)
            floor_tiles.update()
            if len(floor_tiles) < 2:
                floor_tiles.add(Floor(SCREEN_DIMS[0]))
        
        # Instructions state
        elif game_state == 1:
            screen.blit(background_surface, background_surface.get_rect())
            bird.draw(screen)
            bird.sprite.animate()
            instruction_sprites.draw(screen)
            floor_tiles.draw(screen)
            floor_tiles.update()
            if len(floor_tiles) < 2:
                floor_tiles.add(Floor(SCREEN_DIMS[0]))

        # Game running state
        elif game_state == 2:
            # Draw and update the points
            points.draw(screen)
            points.update()

            # Print the background
            screen.blit(background_surface, background_surface.get_rect())

            # Draw and update pipes
            pipes.draw(screen)
            pipes.update()
    
            # Print the bird
            bird.draw(screen)
            bird.update()

            # Check collision with points to see if its possible to score a point
            if check_group_collision(bird, points, True):
                sounds['point'].play()
                score += 1

            # Render score
            render_score(screen, font, score, "top")

            # Print the floor (it goes over the pipes)
            floor_tiles.draw(screen)
            floor_tiles.update()
            if len(floor_tiles) < 2:
                floor_tiles.add(Floor(SCREEN_DIMS[0]))
        
            # Check collision with the floor
            if bird.sprite.rect.bottom >= FLOOR_ORIGIN_Y:
                sounds['hit'].play()
                game_state = 3

            # Check collisiion between bird and pipes
            if check_group_collision(bird, pipes, False):
                sounds['hit'].play()
                sounds['die'].play()
                game_state = 3

        # Game over state
        elif game_state == 3:
            screen.blit(background_surface, background_surface.get_rect())
            pipes.draw(screen)
            floor_tiles.draw(screen)
            bird.draw(screen)
            bird.update()
            game_over_sprites.draw(screen)
            render_score(screen, font, score, "mid")

        pygame.display.update()
        clock.tick(60)

if __name__ == "__main__":
    main()