# --------------------------- PLATFORMER PROJECT ----------------------------
# ------- TO-DO ------
# - background set-up
# - character set-up
# - character jumping
# - background sliding
#scusa devo commitare
import pygame
pygame.init()

SCREEN_WIDTH = 1400
SCREEN_HEIGHT = 600
FPS = 60

# -------------------- PLAYER CLASS --------------------
class Player:
    def __init__(self, x, y):
        self.y = y
        self.x = x
        # carica e scala lo sprite subito, così il rect rispecchia la dimensione disegnata
        self.image = pygame.image.load("Sprite/Sprite.png").convert_alpha()
        self.image = pygame.transform.scale(self.image, (self.image.get_rect().width * 3, self.image.get_rect().height * 3))
        self.rect = self.image.get_rect()
        self.rect.topleft = (x, y)

        #ingradisci sprite
        self.image = pygame.transform.scale(self.image, (self.rect.width * 3, self.rect.height * 3))

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
                if event.key == pygame.K_SPACE and player.on_ground == True:
                    player.jump()

        player.update()

        screen.fill((0, 0, 0))  # Clear the screen with black
        player.draw(screen)     # Draw the player
        pygame.display.flip()    # Update the display

if __name__ == "__main__":
    main()
    pygame.quit()
