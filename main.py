# --------------------------- PLATFORMER PROJECT ----------------------------
# ------- TO-DO ------
# - background set-up
# - character set-up
# - 

import pygame

pygame.init()

SCREEN_WIDTH = 1400
SCREEN_HEIGHT = 600
FPS = 60

#create a class for the player
class Player:
    # initialize the player object
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.width = 40
        self.height = 60
        self.velocity_y = 0
        self.jump = False
        self.on_ground = False
        self.color = (135, 206, 235)

    # draw the player on the screen
    def draw(self, screen):
        pygame.draw.rect(screen, self.color, (self.x, self.y, self.width, self.height))

        #draw eyes
        pygame.draw.circle(screen, (255, 255, 255), (self.x + 10, self.y + 20), 2) 
        pygame.draw.circle(screen, (255, 255, 255), (self.x + 30, self.y + 20), 2)
        pygame.draw.circle(screen, (0, 0, 0), (self.x + 10, self.y + 20), 1)
        pygame.draw.circle(screen, (0, 0, 0), (self.x + 30, self.y + 20), 1) 
        #draw smile
        pygame.draw.arc(screen, (0, 0, 0), (self.x + 10, self.y + 30, 20, 10), 3.14, 0, 1)

    def update(self):

        self.velocity_y += 0.5       # gravity   
        self.y += self.velocity_y

        self.on_ground = False
        if self.y + self.height >= SCREEN_HEIGHT:  # ground collision
            self.y = SCREEN_HEIGHT - self.height
            self.velocity_y = 0
            self.on_ground = True

    def jump(self):
        if self.on_ground:
            self.velocity_y = -15
            self.jump = True
            self.on_ground = False

def main():
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("Platformer Project")
    clock = pygame.time.Clock()

    player = Player(100, 300) # create a player instance

    running = True
    while running:
        clock.tick(FPS)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE and player.on_ground == True:
                    player.jump

        player.update()

        screen.fill((0, 0, 0))  # Clear the screen with black
        player.draw(screen)     # Draw the player
        pygame.display.flip()    # Update the display

if __name__ == "__main__":
    main()
    pygame.quit()