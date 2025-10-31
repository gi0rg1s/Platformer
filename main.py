# --------------------------- PLATFORMER PROJECT ----------------------------
# ------- TO-DO ------
# - background set-up
# - character set-up

import pygame
pygame.init()

SCREEN_WIDTH = 1400
SCREEN_HEIGHT = 600
FPS = 60

# -------------------- PLAYER CLASS --------------------
class Player:
    def __init__(self, x, y):
        #carica sprite
        self.image = pygame.image.load("Sprite/Sprite.png").convert_alpha()
        self.rect = self.image.get_rect()
        self.rect.topleft = (x, y)
        #ingradisci sprite
        self.image = pygame.transform.scale(self.image, (self.rect.width * 3, self.rect.height * 3))

        # variabili movimento
        self.velocity_y = 0
        self.jumping = False
        self.on_ground = False

    def draw(self, screen):
        screen.blit(self.image, self.rect)

# -------------------- MAIN GAME LOOP --------------------
def main():
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("Platformer Project")
    clock = pygame.time.Clock()

    player = Player(100, 300)

    running = True
    while running:
        clock.tick(FPS)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False

        screen.fill((0, 0, 0))  # sfondo nero
        player.draw(screen)     # disegna player
        pygame.display.flip()   # aggiorna display

main()
pygame.quit()
