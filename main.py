# --------------------------- PLATFORMER PROJECT ----------------------------
# ------- TO-DO ------
# - background set-up
# - character set-up
# DINOUSAUR GAME FROM CHROME

import pygame
import time
import random
pygame.init()

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
        self.image = pygame.image.load("Sprite/Sprite.png").convert_alpha()
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
            self.velocity_y = -15
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


def main():
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("Platformer Project")
    clock = pygame.time.Clock()

    collision = False
    player = Player(100, 300)
    # crea la hitbox con le misure che hai scritto (precise)
    hitbox = Hitbox(player.x, player.y, 15, 80)
    # list to hold multiple obstacles
    obstacles = []

    # create a custom event for spawning obstacles every 2000 milliseconds (2s)
    SPAWN_OBSTACLE = pygame.USEREVENT + 1
    pygame.time.set_timer(SPAWN_OBSTACLE, 2000)

    running = True
    while running:
        # cap the frame rate but do not block while waiting for spawns
        clock.tick(FPS)

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
                h = random.randint(30, 80)
                x = SCREEN_WIDTH + 10
                y = SCREEN_HEIGHT - h
                obstacles.append(Obstacle(x, y, w, h))
            
                    

        player.update()
        # aggiorna la hitbox per seguirlo (centrata sul corpo)
        hitbox.update(player.rect)

        screen.fill((0, 0, 0))  # Clear the screen with black
        player.draw(screen)     # Draw the player
        # disegna la hitbox (verde) per verificare il posizionamento
        hitbox.draw(screen)
        # update and draw all obstacles
        for obs in list(obstacles):
            obs.run()
            obs.draw(screen)
            if collisions := [o for o in obstacles if hitbox.rect.colliderect(o.rect)]:
                print("AAAAAAAAA!")
                collision = True
                if collision == True:
                    running = False
        # remove obstacles that moved o
        # ff-screen to the left
        obstacles = [o for o in obstacles if o.rect.right > 0]

        # flip once per frame
        pygame.display.flip() # Update the display

if __name__ == "__main__":
    main()
    pygame.quit()
