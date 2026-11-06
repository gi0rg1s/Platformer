# --------------------------- PLATFORMER PROJECT ----------------------------
# DINOSAUR GAME FROM CHROME

import pygame
import random
import sys
pygame.init()
pygame.mixer.init()

# =====================================================================
#   🎮  GAME SETTINGS  (change the numbers, run the game, see what happens!)
# =====================================================================

# ---- JUMP -----------------------------------------------------------
JUMP_STRENGTH = -10      # jump power: more NEGATIVE = HIGHER jump (try -15)
GRAVITY = 0.5            # gravity: higher = you fall faster (try 0.3 for moon gravity!)

# ---- FLOWER SPEED ---------------------------------------------------
OBSTACLE_SPEED = -5          # pixels per frame, NEGATIVE because flowers move left (try -8 for fast flowers)
SPEED_INCREASE_STEP = 0.1    # how much faster the flowers get each time (0.1 = +10%)
SPEED_INCREASE_EVERY = 100   # how many points you need to score before the speed goes up

# ---- FLOWER SPAWNING ------------------------------------------------
SPAWN_INTERVAL = 2000        # milliseconds between two flowers (2000 = 2 seconds)
MIN_SPAWN_INTERVAL = 800     # lowest allowed value: flowers never appear faster than this
SPAWN_REDUCTION_PER_STEP = 100  # milliseconds removed from the spawn time at each speed increase

# =====================================================================
#   End of settings: the game code starts below this line
# =====================================================================

SCREEN_WIDTH = 1400
SCREEN_HEIGHT = 600
FPS = 60
# fixed obstacle size so only the texture changes between obstacles
OBSTACLE_WIDTH = 50
OBSTACLE_HEIGHT = 70

alive = True
collision = False

# -------------------- HITBOX CLASS --------------------
class Hitbox: 
    def __init__(self, x, y, width, height):
        # store the size so we can re-center the box on the player every frame
        self.width = width
        self.height = height
        self.rect = pygame.Rect(0, 0, width, height)
        # the initial position will be set by update(player_rect)

    def draw(self, screen):
        pygame.draw.rect(screen, (0, 255, 0), self.rect, 2)

    def update(self, player_rect):
        # keep the hitbox size fixed and center it on the player's image
        self.rect.size = (self.width, self.height)
        self.rect.center = player_rect.center

#----------------------PLAYER CLASS-----------------------
class Player:
    def __init__(self, x, y, scale=1, anim_delay=150):
        self.y = y
        self.x = x

        # configuration: scale factor and animation timing (in ms)
        self.scale = scale
        self.anim_delay = anim_delay

        # load and scale the animation frames
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

        # movement variables (values come from the settings at the top)
        self.velocity_y = 0
        self.is_jump = False
        self.jump_strength = JUMP_STRENGTH
        self.gravity = GRAVITY
        self.coyote_time = 100          # ms you can still jump after leaving the ground
        self.coyote_timer = 0
        self.jump_buffer_time = 150     # ms a jump press is remembered before landing
        self.jump_buffer_timer = 0
        self.last_update_time = pygame.time.get_ticks()

        # load the jump sound once (if available)
        try:
            self.jump_sound = pygame.mixer.Sound("Music/JumpSound.wav")
            self.jump_sound.set_volume(0.08)
        except Exception:
            self.jump_sound = None

        # set on_ground correctly if the player starts on the ground
        self.on_ground = (self.y + self.height >= SCREEN_HEIGHT)
        if self.on_ground:
            self.y = SCREEN_HEIGHT - self.height
            self.velocity_y = 0

    def draw(self, screen):
        screen.blit(self.image, self.rect)

    def update(self):
        # time passed since the last frame (used by the timers)
        now = pygame.time.get_ticks()
        delta = now - self.last_update_time
        self.last_update_time = now

        # count the timers down
        if self.coyote_timer > 0:
            self.coyote_timer = max(0, self.coyote_timer - delta)
        if self.jump_buffer_timer > 0:
            self.jump_buffer_timer = max(0, self.jump_buffer_timer - delta)

        self.velocity_y += self.gravity       # gravity pulls the player down
        self.y += self.velocity_y

        self.on_ground = False
        if self.y + self.height >= SCREEN_HEIGHT:  # ground collision
            self.y = SCREEN_HEIGHT - self.height
            self.velocity_y = 0
            self.on_ground = True
            # refill the coyote timer while standing on the ground
            self.coyote_timer = self.coyote_time
            # if a jump was buffered, perform it immediately
            if self.jump_buffer_timer > 0:
                self.do_jump()

        # animation: change frames only on the ground (walking)
        if self.on_ground:
            if now - self.last_anim_time >= self.anim_delay:
                self.anim_index = (self.anim_index + 1) % len(self.frames)
                self.image = self.frames[self.anim_index]
                self.last_anim_time = now
        else:
            # keep a stable frame while in the air
            self.image = self.frames[0]

        # update the rect to match the current image size and position
        self.rect = self.image.get_rect()
        self.rect.topleft = (self.x, int(self.y))
        self.height = self.rect.height

    def press_jump(self):
        """Call this when the player presses the jump key (buffers the input)."""
        self.jump_buffer_timer = self.jump_buffer_time
        # jump right away if allowed (on the ground or within coyote time)
        if self.on_ground or self.coyote_timer > 0:
            self.do_jump()

    def do_jump(self):
        # actually perform the jump
        try:
            if self.jump_sound:
                self.jump_sound.play()
        except Exception:
            pass
        self.velocity_y = self.jump_strength
        self.is_jump = True
        self.on_ground = False
        # reset the timers
        self.coyote_timer = 0
        self.jump_buffer_timer = 0

    def jump(self):
        # compatibility wrapper: jump immediately if allowed
        if self.on_ground or self.coyote_timer > 0:
            self.do_jump()
        
#---------------OBSTACLE CLASS------------------
class Obstacle:
    def __init__(self, x, y, width, height, base_speed=OBSTACLE_SPEED, image_path=None):
        # speed in pixels per frame (negative = moves to the left)
        self.base_speed = base_speed
        self.velocity_x = base_speed
        self.image = None
        # real position stored as a float, so decimal speeds (like -5.5) are not cut off
        self.x = float(x)

        # if an image path is given, try to load it and scale it to the wanted size
        if image_path:
            try:
                img = pygame.image.load(image_path).convert_alpha()
                img = pygame.transform.scale(img, (max(1, int(width)), max(1, int(height))))
                self.image = img
                self.rect = self.image.get_rect(topleft=(x, y))
            except Exception:
                # fall back to a plain rectangle if the image fails to load
                self.rect = pygame.Rect(x, y, width, height)
        else:
            self.rect = pygame.Rect(x, y, width, height)

        # the hitbox is a separate rect, so it can be tweaked independently of the image
        self.hitbox = self.rect.copy()

    def draw(self, screen):
        if self.image:
            screen.blit(self.image, self.rect)
        else:
            pygame.draw.rect(screen, (255, 0, 0), self.rect)

    def run(self):
        self.x += self.velocity_x
        self.rect.x = int(self.x)
        # keep the hitbox in sync with the visible rect (only the position matters)
        self.hitbox.topleft = self.rect.topleft
        
    def update_speed(self, speed_multiplier):
        # update the speed while keeping the original direction
        self.velocity_x = self.base_speed * speed_multiplier

#---------------------MENU FUNCTION-----------------------
def menu():
    pygame.mixer.music.load("Music/MenuMusic.wav")
    pygame.mixer.music.set_volume(0.05)
    pygame.mixer.music.play(-1)                                                 # loop the music forever
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
                    # start the game loop; when it returns, leave the menu
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
    pygame.mixer.music.play(-1)                                                      # loop the music forever
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    font = pygame.font.SysFont(None, 36)
    lose_str = font.render("Game Over! Your score is : " + str(score//100) + "!", True, (255, 255, 255))
    screen.fill((0, 0, 0))
    screen.blit(lose_str, lose_str.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 40)))
    pygame.display.flip()
    pygame.time.wait(3000)
    menu()

#------------------------PLAY MODE------------------------------
def play_mode():
    background = pygame.image.load("Sprite/background.png").convert()
    background = pygame.transform.scale(background, (SCREEN_WIDTH, SCREEN_HEIGHT))
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("Jojo Runner")
    clock = pygame.time.Clock()
    font = pygame.font.SysFont(None, 36)
    intro_text = font.render("Help me to avoid flowers!", True, (255, 255, 255))
    screen.blit(intro_text, (550, 100))
    pygame.display.flip()
    pygame.time.wait(2000)
    pygame.mixer.music.load("Music/BackgroundMusic.wav")
    pygame.mixer.music.set_volume(0.04)
    pygame.mixer.music.play(-1)                                                 # loop the music forever

    player = Player(100, 300)
    
    # create a hitbox for collisions
    hitbox = Hitbox(player.x - 20, player.y, 25, 80)
    # list that holds all the obstacles currently on screen
    obstacles = []
    
    # the list of obstacle textures
    obstacle_images = [
        "Sprite/obstacle1.png",
        "Sprite/obstacle2.png",
        "Sprite/obstacle3.png",
    ]

    # custom event used to spawn obstacles
    SPAWN_OBSTACLE = pygame.USEREVENT + 1

    # progressive difficulty (values come from the settings at the top)
    base_obstacle_speed = OBSTACLE_SPEED
    current_speed_multiplier = 1.0
    last_speed_increase_score = 0
    speed_steps = 0

    current_spawn_interval = SPAWN_INTERVAL

    pygame.time.set_timer(SPAWN_OBSTACLE, current_spawn_interval)
    game_start_time = pygame.time.get_ticks()
    running = True
    prev_space = False

    while running:
        # cap the frame rate without blocking while waiting for spawns
        clock.tick(FPS)
        current_time = pygame.time.get_ticks()
        score = (current_time - game_start_time)
        current_score_units = score // 100
        screen.blit(background, (0, 0))
        
        # PROGRESSIVE DIFFICULTY
        if current_score_units > last_speed_increase_score and current_score_units % SPEED_INCREASE_EVERY == 0:
            last_speed_increase_score = current_score_units
            speed_steps += 1
            current_speed_multiplier += SPEED_INCREASE_STEP
            pygame.mixer.Sound("Music/SpeedUp.wav").play().set_volume(0.05)
            
            # update the speed of all the obstacles already on screen
            for obs in obstacles:
                obs.update_speed(current_speed_multiplier)
            
            # shorten the spawn interval so flowers appear more often
            if current_spawn_interval > MIN_SPAWN_INTERVAL:
                current_spawn_interval = max(MIN_SPAWN_INTERVAL,
                                             SPAWN_INTERVAL - speed_steps * SPAWN_REDUCTION_PER_STEP)
                pygame.time.set_timer(SPAWN_OBSTACLE, 0)  # turn the timer off for a moment
                pygame.time.set_timer(SPAWN_OBSTACLE, current_spawn_interval)
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    # buffer the jump on key press (it happens immediately if allowed)
                    player.press_jump()
            # handle the spawn event without blocking the main loop
            if event.type == SPAWN_OBSTACLE:
                # spawn at the right edge with a fixed size, so only the texture changes
                w = OBSTACLE_WIDTH
                h = OBSTACLE_HEIGHT
                x = SCREEN_WIDTH - 50
                y = SCREEN_HEIGHT - h 
                image_path = random.choice(obstacle_images) if obstacle_images else None
                new_obstacle = Obstacle(x, y, w, h, base_obstacle_speed, image_path=image_path)
                new_obstacle.update_speed(current_speed_multiplier)
                obstacles.append(new_obstacle)            
            
        # also detect the key press directly, in case an event was missed
        keys = pygame.key.get_pressed()
        if keys[pygame.K_SPACE] and not prev_space:
            player.press_jump()
        prev_space = keys[pygame.K_SPACE]

        player.update()
        # move the hitbox so it follows the player (centered on the body)
        hitbox.update(player.rect)
        
        player.draw(screen)     # draw the player
        
        # draw the hitbox (green) to check its position
        #hitbox.draw(screen)
        # update and draw all the obstacles
        for obs in list(obstacles):
            obs.run()
            obs.draw(screen)
            # check collision with this obstacle's hitbox
            if hitbox.rect.colliderect(obs.hitbox):
                running = False
                lose_display(score)  # game over on collision
        
        # remove obstacles that have left the screen on the left
        obstacles = [o for o in obstacles if o.rect.right > 0]
        
        # show the score and the speed multiplier
        text = pygame.font.SysFont(None, 36).render(f"Score: {score // 100}", True, (255, 255, 255))
        speed_text = pygame.font.SysFont(None, 36).render(f"Speed: {current_speed_multiplier:.1f}x", True, (255, 255, 255))
        screen.blit(text, (1250, 50))
        screen.blit(speed_text, (1250, 90))
        
        # update the display once per frame
        pygame.display.flip()

if __name__ == "__main__":
    menu()
    pygame.quit()