# --------------------------- PLATFORMER PROJECT ----------------------------
#By Manuel Gizzi and Giorgia Folloni
#Music and Sounds By Gibbo
# ------- TO-DO ------3
# - background set-up
# - character set-up - - almost done
# DINOUSAUR GAME FROM CHROME

import pygame
import random
import sys
pygame.init()
pygame.mixer.init()

SCREEN_WIDTH = 1400
SCREEN_HEIGHT = 600
FPS = 60

alive = True
collision = False

# -------------------- PLAYER CLASS --------------------
class Hitbox:
    def __init__(self, x, y, width, height):
        # store size so we can re-center relative to the player each frame
        self.width = width
        self.height = height
        self.rect = pygame.Rect(0, 0, width, height)
        # initial position will be set by update(player_rect)

    def draw(self, screen):
        pygame.draw.rect(screen, (0, 255, 0), self.rect, 2)

    def update(self, player_rect):
        # keep hitbox size fixed and center it on the player's visual rect
        self.rect.size = (self.width, self.height)
        self.rect.center = player_rect.center


class Player:
    def __init__(self, x, y):
        self.y = y
        self.x = x
        # carica e scala lo sprite subito, così il rect rispecchia la dimensione disegnata
        self.image = pygame.image.load("Sprite/Camminata1.png").convert_alpha()
        
        self.image = pygame.transform.scale(self.image, (self.image.get_rect().width * 3, self.image.get_rect().height * 3))
        self.rect = self.image.get_rect()
        self.rect.topleft = (x, y)
        self.height = self.rect.height

        # variabili movimento
        self.velocity_y = 0
        self.is_jump = False
        # inizializza on_ground correttamente se il player parte per terra
        self.on_ground = (self.y + self.height >= SCREEN_HEIGHT)
        if self.on_ground:
            self.y = SCREEN_HEIGHT - self.height
            self.velocity_y = 0

    def draw(self, screen):
        screen.blit(self.image, self.rect)

    def update(self):

        self.velocity_y += 0.5       # gravity   
        self.y += self.velocity_y

        self.on_ground = False
        if self.y + self.height >= SCREEN_HEIGHT:  # ground collision
            self.y = SCREEN_HEIGHT - self.height
            self.velocity_y = 0
            self.on_ground = True
        # keep rect in sync with logical position so draw() reflects movement
        self.rect.topleft = (self.x, int(self.y))

    def jump(self):
        if self.on_ground:
            pygame.mixer.Sound("Music/JumpSound.wav").play().set_volume(0.08)
            self.velocity_y = -10
            self.is_jump = True
            self.on_ground = False
        
class Obstacle:
    
    def __init__(self, x, y, width, height):
        self.rect = pygame.Rect(x, y, width, height)
        # velocity in pixels per frame (negative to move left)
        self.velocity_x = -5

    def draw(self, screen):
        pygame.draw.rect(screen, (255, 0, 0), self.rect)

    def run(self):
        self.rect.x += self.velocity_x

def menu():
    pygame.mixer.music.load("Music/MenuMusic.wav")
    pygame.mixer.music.set_volume(0.05)
    pygame.mixer.music.play(-1)  # Loop the music indefinitely
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("Menu")
    clock = pygame.time.Clock()
    font = pygame.font.SysFont(None, 36)
    title = font.render("Welcome to the Platformer!", True, (255, 255, 255))
    btn_text = font.render("Play", True, (0, 0, 0))
    button = pygame.Rect((SCREEN_WIDTH // 2) - 50, (SCREEN_HEIGHT // 2) + 40, 100, 50)

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                if button.collidepoint(event.pos):
                    pygame.mixer.music.stop()
                    pygame.mixer.music.unload()
                    pygame.mixer.music.load("Music/StartSound.wav")
                    pygame.mixer.music.play()
                    pygame.mixer.music.set_volume(0.05)
                    pygame.time.delay(700)  # wait for the start sound to finish
                    # start game loop; when it returns, exit menu
                    play_mode()
                    running = False

        screen.fill((0, 0, 0))
        screen.blit(title, title.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 40)))
        pygame.draw.rect(screen, (0, 255, 0), button)
        screen.blit(btn_text, btn_text.get_rect(center=button.center))
        pygame.display.flip()
        clock.tick(FPS)

def lose_display(score):
    pygame.mixer.music.load("Music/MenuMusic.wav")
    pygame.mixer.music.set_volume(0.05)
    pygame.mixer.music.play(-1)  # Loop the music indefinitely
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    clock = pygame.time.Clock()
    font = pygame.font.SysFont(None, 36)
    lose_str = font.render("Game Over! Your score is : " + str(score//100) + "!", True, (255, 255, 255))
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    screen.fill((0, 0, 0))
    screen.blit(lose_str, lose_str.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 40)))
    pygame.display.flip()
    pygame.time.wait(3000)
    menu()


def play_mode():
    pygame.mixer.music.load("Music/BackgroundMusic.wav")
    pygame.mixer.music.set_volume(0.04)
    pygame.mixer.music.play(-1)  # Loop the music indefinitely
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("Platformer Project")
    clock = pygame.time.Clock()

    collision = False
    player = Player(100, 300)
    
    # crea la hitbox con le misure che hai scritto (precise)
    hitbox = Hitbox(player.x - 20, player.y, 25, 80)
    # list to hold multiple obstacles
    obstacles = []

    # create a custom event for spawning obstacles every 2000 milliseconds (2s)
    SPAWN_OBSTACLE = pygame.USEREVENT + 1

    parametro = 100
    velocity = -0.25            # variazione di velocità da applicare agli ostacoli
    spawn_interval_ms = 2000   # intervallo spawn (ms) positivo e intero

    pygame.time.set_timer(SPAWN_OBSTACLE, spawn_interval_ms)
    game_start_time = pygame.time.get_ticks()
    running = True

    while running:
        # cap the frame rate but do not block while waiting for spawns
        clock.tick(FPS)
        current_time = pygame.time.get_ticks()
        score = (current_time - game_start_time)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE and player.on_ground == True:
                    player.jump()
            # handle the spawn event without blocking the main loop
            if event.type == SPAWN_OBSTACLE:
                # spawn at right edge, random height/size (you can change values)
                w = random.randint(30, 60)
                h = random.randint(30, 50)
                x = SCREEN_WIDTH - 50
                y = SCREEN_HEIGHT - h
                obstacles.append(Obstacle(x, y, w, h))
    
                    
            
        player.update()
        # aggiorna la hitbox per seguirlo (centrata sul corpo)
        hitbox.update(player.rect)
        
        screen.fill((0, 0, 0))  # Clear the screen with black
        player.draw(screen)     # Draw the player
        
        # disegna la hitbox (verde) per verificare il posizionamento
        #hitbox.draw(screen)
        # update and draw all obstacles
        for obs in list(obstacles):
            obs.run()
            obs.draw(screen)
            # check collision with the current obstacle
            if hitbox.rect.colliderect(obs.rect):
                lose_display(score)  # end game on collision
            if (score // 100) >= parametro:  
                obs.velocity_x  += velocity
                parametro += 100
        # remove obstacles that moved
        # ff-screen to the left
        obstacles = [o for o in obstacles if o.rect.right > 0]
        
        
         
        text = pygame.font.SysFont(None, 36).render(f"Score: {score // 100}", True, (255, 255, 255))
        screen.blit(text, (1250, 50))  # Draw score at top-left corner
        
        

        # flip once per frame
        pygame.display.flip() # Update the display

if __name__ == "__main__":
    menu()
    pygame.quit()

