import pygame
from random import randint
from sys import exit

# Constants
SCREEN_DIMS = (144, 256)
PIPE_GAP = 50
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
    
    def input(self):
        keys = pygame.key.get_pressed()
        # Jump!
        if keys[pygame.K_SPACE]:
            self.jump()
    
    def jump(self):
        self.gravity = -2 # Restart gravity
    
    def apply_gravity(self):
        # Apply effect of gravity in the Y axis
        self.gravity += 0.1
        if self.rect.bottom < FLOOR_ORIGIN_Y:
            self.rect.y += self.gravity

    def update(self):
        # self.input()
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
            print("kill pipe")
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
            print("kill floor")
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

def generate_pipes():
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


def render_score(screen, font, score):
    # Enable bold and print the background of the font
    font.set_bold(True)
    score_surface = font.render(f"{score}", False, 'Black')
    score_rect = score_surface.get_rect(center = (SCREEN_DIMS[0] // 2, SCREEN_DIMS[1] // 8))
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

    # Enable texture manager
    TextureManager.load_texture('textures.png')

    # Font
    font = pygame.font.Font('PixelMillennium-1oBZ.ttf', 30)

    # Create game over and title sprites
    game_over_surface = TextureManager.texture_surface.subsurface(395, 59, 96, 21)
    game_over_rect = game_over_surface.get_rect(center = (SCREEN_DIMS[0] // 2, SCREEN_DIMS[1] // 4))

    # Ok button
    ok_button_surface = TextureManager.texture_surface.subsurface(462, 42, 40, 14)
    ok_button_rect = ok_button_surface.get_rect(center = (SCREEN_DIMS[0] // 2, SCREEN_DIMS[1] - (SCREEN_DIMS[1] // 3)))

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

    game_active = True
    while True:
        # Events catcher -->
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()
            
            if game_active:
                # Pipes generator
                if event.type == pipes_timer:
                    new_pipes = generate_pipes()
                    pipes.add(new_pipes)
                    points.add(Point(*new_pipes)) # Generate points for the new pair of pipes
            
                if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                    bird.sprite.jump()
            
            else:
                if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                    game_active = True
                    bird.sprite.reset()
                    score = 0 # Restart score

                    # Restart points
                    points.empty()

                    # Restart pipes
                    pipes.empty()

            
        # Game and screen flow -->
        if game_active:
            # Print the background
            screen.blit(background_surface, background_surface.get_rect())

            # Print the bird
            bird.draw(screen)
            bird.update()

            # Draw and update pipes
            pipes.draw(screen)
            pipes.update()
    
            # Draw and update the points
            points.draw(screen)
            points.update()
            if check_group_collision(bird, points, True):
                score += 1

            # Render score
            render_score(screen, font, score)

            # Print the floor (it goes over the pipes)
            floor_tiles.draw(screen)
            floor_tiles.update()
            if len(floor_tiles) < 2:
                floor_tiles.add(Floor(SCREEN_DIMS[0]))
        
            # Check collision with the floor
            if bird.sprite.rect.bottom >= FLOOR_ORIGIN_Y:
                game_active = False

            # Check collisiion between bird and pipes
            if check_group_collision(bird, pipes, False):
                game_active = False
        else:
            screen.blit(background_surface, background_surface.get_rect())
            bird.draw(screen)
            bird.update()
            pipes.draw(screen)
            floor_tiles.draw(screen)

            # Game over
            screen.blit(game_over_surface, game_over_rect)

            # Ok button
            screen.blit(ok_button_surface, ok_button_rect)
    
        pygame.display.update()
        clock.tick(60)

if __name__ == "__main__":
    main()