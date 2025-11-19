# --------------------------- PLATFORMER PROJECT ----------------------------
#By Manuel Gizzi and Giorgia Folloni
#Music and Sounds By Gibbo
# ------- TO-DO ------
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
# fixed obstacle size so only texture changes between obstacles
OBSTACLE_WIDTH = 50
OBSTACLE_HEIGHT = 70

alive = True
collision = False

# -------------------- HITBOX CLASS --------------------
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

#----------------------PLAYER CLASS-----------------------
class Player:
    def __init__(self, x, y, scale=1, anim_delay=150):
        self.y = y
        self.x = x

        # Configuration: scale factor and animation timing (ms)
        self.scale = scale
        self.anim_delay = anim_delay

        # load and scale animation frames
        frame_paths = ["Sprite/Camminata1.png", "Sprite/Camminata2.png"]
        self.frames = []
        for path in frame_paths:
            img = pygame.image.load(path).convert_alpha()
            w, h = img.get_rect().size
            img = pygame.transform.scale(img, (int(w * self.scale//2), int(h * self.scale//2)))
            self.frames.append(img)

        # initial image/frame
        self.image = self.frames[0]
        self.rect = self.image.get_rect()
        self.rect.topleft = (x, y)
        self.height = self.rect.height

        # animation state
        self.anim_index = 0
        self.last_anim_time = pygame.time.get_ticks()

        # variabili movimento
        self.velocity_y = 0
        self.is_jump = False
        # load jump sound once (if available)
        try:
            self.jump_sound = pygame.mixer.Sound("Music/JumpSound.wav")
            self.jump_sound.set_volume(0.08)
        except Exception:
            self.jump_sound = None

        # inizializza on_ground correttamente se il player parte per terra
        self.on_ground = (self.y + self.height >= SCREEN_HEIGHT)
        if self.on_ground:
            self.y = SCREEN_HEIGHT - self.height
            self.velocity_y = 0

    def draw(self, screen):
        screen.blit(self.image, self.rect)

    def update(self):
        # time delta for timers
        now = pygame.time.get_ticks()
        if not hasattr(self, 'last_update_time'):
            self.last_update_time = now
        delta = now - self.last_update_time
        self.last_update_time = now

        # initialize timers if missing
        if not hasattr(self, 'coyote_time'):
            self.coyote_time = 100
        if not hasattr(self, 'coyote_timer'):
            self.coyote_timer = 0
        if not hasattr(self, 'jump_buffer_time'):
            self.jump_buffer_time = 150
        if not hasattr(self, 'jump_buffer_timer'):
            self.jump_buffer_timer = 0
        if not hasattr(self, 'jump_strength'):
            self.jump_strength = -10

        # decrement timers
        if self.coyote_timer > 0:
            self.coyote_timer = max(0, self.coyote_timer - delta)
        if self.jump_buffer_timer > 0:
            self.jump_buffer_timer = max(0, self.jump_buffer_timer - delta)

        self.velocity_y += 0.5       # gravity
        self.y += self.velocity_y

        prev_on_ground = self.on_ground
        self.on_ground = False
        if self.y + self.height >= SCREEN_HEIGHT:  # ground collision
            self.y = SCREEN_HEIGHT - self.height
            self.velocity_y = 0
            self.on_ground = True
            # reset coyote timer when on ground
            self.coyote_timer = self.coyote_time
            # if there is a buffered jump, perform it immediately
            if self.jump_buffer_timer > 0:
                self.do_jump()

        # animation: advance frames only when on ground (walking)
        if self.on_ground:
            if now - self.last_anim_time >= self.anim_delay:
                self.anim_index = (self.anim_index + 1) % len(self.frames)
                self.image = self.frames[self.anim_index]
                self.last_anim_time = now
        else:
            # keep a stable frame while in air
            self.image = self.frames[0]

        # update rect to match current image size and logical position
        self.rect = self.image.get_rect()
        self.rect.topleft = (self.x, int(self.y))
        self.height = self.rect.height

    def press_jump(self):
        """Call when the player presses the jump key (buffers input)."""
        # set buffer timer
        if not hasattr(self, 'jump_buffer_time'):
            self.jump_buffer_time = 150
        self.jump_buffer_timer = self.jump_buffer_time
        # try immediate jump if allowed (on ground or within coyote time)
        if self.on_ground or (hasattr(self, 'coyote_timer') and self.coyote_timer > 0):
            self.do_jump()

    def do_jump(self):
        # perform the actual jump
        try:
            if self.jump_sound:
                self.jump_sound.play()
        except Exception:
            pass
        if not hasattr(self, 'jump_strength'):
            self.jump_strength = -10
        self.velocity_y = self.jump_strength
        self.is_jump = True
        self.on_ground = False
        # reset timers
        self.coyote_timer = 0
        self.jump_buffer_timer = 0

    def jump(self):
        # compatibility wrapper: try to jump immediately if allowed
        if self.on_ground or (hasattr(self, 'coyote_timer') and self.coyote_timer > 0):
            self.do_jump()
        
#---------------OBSTACLE CLASS------------------
class Obstacle:
    def __init__(self, x, y, width, height, base_speed=-5, image_path=None):
        # velocity in pixels per frame (negative to move left)
        self.base_speed = base_speed
        self.velocity_x = base_speed
        self.image = None

        # If an image path is provided, attempt to load and scale it to the desired size
        if image_path:
            try:
                img = pygame.image.load(image_path).convert_alpha()
                img = pygame.transform.scale(img, (max(1, int(width)), max(1, int(height))))
                self.image = img
                self.rect = self.image.get_rect(topleft=(x, y))
            except Exception:
                # fallback to rect if image load fails
                self.rect = pygame.Rect(x, y, width, height)
        else:
            self.rect = pygame.Rect(x, y, width, height)

        # associate a hitbox rect with this obstacle (separate object so we can tweak it independently)
        # start with the same rect as the visual rect
        self.hitbox = self.rect.copy()

    def draw(self, screen):
        if self.image:
            screen.blit(self.image, self.rect)
        else:
            pygame.draw.rect(screen, (255, 0, 0), self.rect)

    def run(self):
        # velocity_x might be float; update rect.x with int increment
        self.rect.x += int(self.velocity_x)
        # keep hitbox synced to the visual rect (only position matters here)
        self.hitbox.topleft = self.rect.topleft
        
    def update_speed(self, speed_multiplier):
        # Aggiorna la velocità mantenendo la direzione originale
        self.velocity_x = self.base_speed * speed_multiplier

#---------------------MENU FUNCTION-----------------------
def menu():
    pygame.mixer.music.load("Music/MenuMusic.wav")
    pygame.mixer.music.set_volume(0.05)
    pygame.mixer.music.play(-1)                                                 # Loop the music indefinitely
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
                    running = False
                    play_mode()
                    

        screen.fill((0, 0, 0))
        screen.blit(title, title.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 40)))
        pygame.draw.rect(screen, (0, 255, 0), button)
        screen.blit(btn_text, btn_text.get_rect(center=button.center))
        pygame.display.flip()
        clock.tick(FPS)

#----------------------------LOSE DISPLAY----------------------------
def lose_display(score):
    pygame.mixer.music.load("Music/MenuMusic.wav")
    pygame.mixer.music.set_volume(0.05)
    pygame.mixer.music.play(-1)                                                      # Loop the music indefinitely
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

#------------------------PLAY MODE------------------------------
def play_mode():
    pygame.mixer.music.load("Music/BackgroundMusic.wav")
    pygame.mixer.music.set_volume(0.04)
    pygame.mixer.music.play(-1)                                                 # Loop the music indefinitely
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("Jojo Runner")
    clock = pygame.time.Clock()

    collision = False
    player = Player(100, 300)
    
    # create a hitbox for collisions
    hitbox = Hitbox(player.x - 20, player.y, 25, 80)
    # list to hold multiple obstacles
    obstacles = []
    # use the explicit list of obstacle textures provided by the user
    obstacle_images = [
        "Sprite/obstacle1.png",
        "Sprite/obstacle2.png",
        "Sprite/obstacle3.png",
    ]

    # create a custom event for spawning obstacles every 2000 milliseconds (2s)
    SPAWN_OBSTACLE = pygame.USEREVENT + 1

    # Variabili per il sistema di difficoltà progressiva
    base_obstacle_speed = -5
    current_speed_multiplier = 1.0
    last_speed_increase_score = 0
    speed_increase_interval = 100  # Aumenta la velocità ogni 100 punti
    
    # Variabili per lo spawn dinamico
    base_spawn_interval = 2000  # 2 secondi base
    current_spawn_interval = base_spawn_interval
    min_spawn_interval = 800   # Intervallo minimo di spawn

    pygame.time.set_timer(SPAWN_OBSTACLE, current_spawn_interval)
    game_start_time = pygame.time.get_ticks()
    running = True
    prev_space = False

    while running:
        # cap the frame rate but do not block while waiting for spawns
        clock.tick(FPS)
        current_time = pygame.time.get_ticks()
        score = (current_time - game_start_time)
        current_score_units = score // 100
        
        # AUMENTO DIFFICOLTÀ PROGRESSIVO
        # Aumenta la velocità ogni 100 punti
        if current_score_units > last_speed_increase_score and current_score_units % speed_increase_interval == 0:
            last_speed_increase_score = current_score_units
            current_speed_multiplier += 0.1  # Aumenta del 10% ogni 100 punti
            pygame.mixer.Sound("Music/SpeedUp.wav").play().set_volume(0.05)
            
            # Aggiorna la velocità di tutti gli ostacoli esistenti
            for obs in obstacles:
                obs.update_speed(current_speed_multiplier)
            
            # Riduci l'intervallo di spawn per aumentare la frequenza
            if current_spawn_interval > min_spawn_interval:
                current_spawn_interval = max(min_spawn_interval, base_spawn_interval - current_score_units)
                # Riavvia il timer con il nuovo intervallo
                pygame.time.set_timer(SPAWN_OBSTACLE, 0)  # Disabilita temporaneamente
                pygame.time.set_timer(SPAWN_OBSTACLE, current_spawn_interval)
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    # buffer the jump on keydown (will perform immediately if allowed)
                    player.press_jump()
            # handle the spawn event without blocking the main loop
            if event.type == SPAWN_OBSTACLE:
                # spawn at right edge using fixed size so only texture changes
                w = OBSTACLE_WIDTH
                h = OBSTACLE_HEIGHT
                x = SCREEN_WIDTH - 50
                y = SCREEN_HEIGHT - h
                # choose one of the obstacle textures (if available)
                image_path = random.choice(obstacle_images) if obstacle_images else None
                # Create obstacle with fixed size but with different texture
                new_obstacle = Obstacle(x, y, w, h, base_obstacle_speed, image_path=image_path)
                new_obstacle.update_speed(current_speed_multiplier)
                obstacles.append(new_obstacle)            
            
        # Also handle keyboard edge detection in case events are missed
        keys = pygame.key.get_pressed()
        if keys[pygame.K_SPACE] and not prev_space:
            player.press_jump()
        prev_space = keys[pygame.K_SPACE]

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
            # check collision with the current obstacle using each obstacle's hitbox
            if hitbox.rect.colliderect(obs.hitbox):
                running = False
                lose_display(score)  # end game on collision
        
        # remove obstacles that moved off-screen to the left
        obstacles = [o for o in obstacles if o.rect.right > 0]
        
        # Mostra anche il moltiplicatore di velocità
        text = pygame.font.SysFont(None, 36).render(f"Score: {score // 100}", True, (255, 255, 255))
        speed_text = pygame.font.SysFont(None, 36).render(f"Speed: {current_speed_multiplier:.1f}x", True, (255, 255, 255))
        screen.blit(text, (1250, 50))
        screen.blit(speed_text, (1250, 90))
        
        # flip once per frame
        pygame.display.flip() # Update the display

if __name__ == "__main__":
    menu()
    pygame.quit()