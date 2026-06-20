import pygame
import random
import math #for some attack patterns
from pygame.locals import *
from highscores import load_high_score, save_high_score

# Initialize pygame 
pygame.init()

#Logo
icon_image = pygame.image.load('img/LOGO.png')
pygame.display.set_icon(icon_image)
# Load and play intro music
pygame.mixer.music.set_volume(0.2)
pygame.mixer.music.load('sfx/bgmusicintro.wav')

pygame.mixer.music.play(-1)  # loop music
music_intro_looping = True
parry_sfx = pygame.mixer.Sound('sfx/perfect.wav')
death_sfx = pygame.mixer.Sound('sfx/death.wav')
error_sfx = pygame.mixer.Sound('sfx/error.wav')
coin_sfx = pygame.mixer.Sound('sfx/coin.wav')
buy_sfx = pygame.mixer.Sound('sfx/buy.wav')
lazer_sfx = pygame.mixer.Sound('sfx/lazer.wav')

clock = pygame.time.Clock()
fps = 60
screen_width = 864
screen_height = 936

# Set up display
screen = pygame.display.set_mode((screen_width, screen_height))
pygame.display.set_caption('Nightlight.')

# Game variables
paused = False
bg_scroll = 0
ground_scroll = 0
scroll_speed = 4
game_over = False
char_death_start_time = None
score = 0
score_font = pygame.font.SysFont('Daydream', 25)
game_state = "menu"

powerup_shield = False
shop_purchased_shield = False
shop_purchased_doubler = False
shield_invincible_time = 750  # milliseconds of invincibility
shield_last_used_time = 0     # when shield was used


powerup_score_doubler = False
shield_used = False
shop_button = pygame.Rect(screen_width // 2 - 100, screen_height // 2 + 50, 200, 50)
back_button = pygame.Rect(20, 20, 145, 55)

button_font = pygame.font.SysFont('Daydream', 28)
small_font = pygame.font.SysFont('Daydream', 20)

start_button = pygame.Rect(screen_width // 2 - 100, screen_height // 2 - 40, 200, 80)

high_score = load_high_score()


coins_collected = 0


# Intro music loop tracking
loop_start_time = pygame.time.get_ticks()
loop_duration_ms = 2000  # loop first 2 seconds

# Parry timing
parry_time = 0
parry_window = 300  # milliseconds it takes to parry before it hits you

# Load images
coin_img = pygame.transform.scale(pygame.image.load('img/coin.png').convert_alpha(), (24, 24))
bg = pygame.image.load('img/bg3.png')
ground_img = pygame.image.load('img/ground.png')
warning_img = pygame.transform.scale(pygame.image.load('img/exclaim.png').convert_alpha(), (24, 50))
missile_warning_img = pygame.transform.scale(pygame.image.load('img/warningmissile.png').convert_alpha(), (24, 50))
shield_shop_img = pygame.transform.scale(pygame.image.load('img/shield.png').convert_alpha(), (48, 58))
x2multiplier_img= pygame.transform.scale(pygame.image.load('img/2x.png').convert_alpha(), (68, 68))
title_img = pygame.image.load('img/title.png')

def load_total_coins():
    try:
        with open('coinsave.txt', 'r') as f:
            return int(f.read())
    except:
        return 0

def save_total_coins(total):
    with open('coinsave.txt', 'w') as f:
        f.write(str(total))

# Draw game over screen with overlay and text
def draw_game_over_screen():
    overlay = pygame.Surface((screen_width, screen_height))
    overlay.set_alpha(150)
    overlay.fill((0, 0, 0))
    screen.blit(overlay, (0, 0))

    # GAME OVER title
    text = button_font.render("GAME OVER", True, (255, 50, 50))
    screen.blit(text, text.get_rect(center=(screen_width // 2, screen_height // 2 - 100)))

    # Show score
    high_score_text = score_font.render(f"Score: {score}", True, (255, 255, 0))
    screen.blit(high_score_text, high_score_text.get_rect(center=(screen_width // 2, screen_height // 2 - 40)))

    # Show coins
    coins_text = score_font.render(f"Coins Collected: {coins_collected}", True, (255, 215, 0))
    screen.blit(coins_text, coins_text.get_rect(center=(screen_width // 2, screen_height // 2 + 10)))

    # Retry instructions
    retry_text = button_font.render("Press R to Restart", True, (255, 255, 255))
    screen.blit(retry_text, retry_text.get_rect(center=(screen_width // 2, screen_height // 2 + 70)))

def draw_shop_menu():
    screen.blit(bg, (0, 0))
    screen.blit(ground_img, (0, 768))
    overlay = pygame.Surface((screen_width, screen_height))
    overlay.set_alpha(150)
    overlay.fill((0, 0, 0))
    screen.blit(overlay, (0, 0))

    title = button_font.render("SHOP", True, (255, 255, 255))
    screen.blit(title, title.get_rect(center=(screen_width // 2, 100)))

    shield_text = button_font.render("Shield - 2000 Coins", True, (0, 255, 255))
    screen.blit(shield_shop_img, (screen_width // 2.5 - 250, 190))

    doubler_text = button_font.render("2x Score - 3000 Coins", True, (255, 215, 0))
    screen.blit(x2multiplier_img, (screen_width // 2.5 - 250, 300))
    back_text = button_font.render("Back", True, (255, 255, 255))

    screen.blit(shield_text, (screen_width // 2.5 - 150, 200))
    screen.blit(doubler_text, (screen_width // 2.5 - 150, 300))
    pygame.draw.rect(screen, (150, 150, 150), back_button, border_radius=10)
    screen.blit(back_text, back_button.move(10, 5))
    coins_text = score_font.render(f"Coins: {total_saved_coins}", True, (255, 215, 0))
    screen.blit(coins_text, (20, screen_height - 40))

# Draw start menu with dark overlay and start button
def draw_start_menu():
    #add bg ang ground image
    screen.blit(bg, (0, 0))
    screen.blit(ground_img, (0, 768))

    overlay = pygame.Surface((screen_width, screen_height))
    overlay.set_alpha(100)
    overlay.fill((0, 0, 0))
    screen.blit(overlay, (0, 0))
    pygame.draw.rect(screen, (201, 164, 191), start_button, border_radius=10)
    text = button_font.render("START", True, (255, 255, 255))
    text_rect = text.get_rect(center=start_button.center)
    screen.blit(text, text_rect)
    #title
    title_rect = title_img.get_rect(center=(screen_width // 2, 190))  # 190 is vertical (y) position
    screen.blit(title_img, title_rect)

    # Draw SHOP button
    pygame.draw.rect(screen, (180, 100, 255), shop_button, border_radius=10)
    shop_text = button_font.render("SHOP", True, (255, 255, 255))
    screen.blit(shop_text, shop_text.get_rect(center=shop_button.center))

# Main character class
class Chara(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.is_dead = False
        self.images = [pygame.transform.scale(pygame.image.load(f'img/char{num}.png'), (25, 48))                 
        for num in range(1, 9)]
        self.parry_images = [pygame.transform.scale(pygame.image.load(f'img/parry{num}.png'), (25, 48)) 
        for num in range(4, 7)]
        self.image = self.images[0]
        self.rect = self.image.get_rect(center=(x, y))
        self.index = self.counter = self.parry_index = self.parry_counter = 0
        self.is_parrying = False
        self.vel = 0

    def die(self):
        # Load death animation frames
        self.death_frames = [pygame.transform.scale(pygame.image.load(f'img/death{num}.png'), (48, 48)) 
        for num in range(1, 8)]
        self.death_index = self.death_counter = 0
        self.is_dead = True

    def parry(self):
        # Trigger parry animation
        self.is_parrying = True
        self.parry_index = self.parry_counter = 0
        self.image = self.parry_images[self.parry_index]

    def update(self):
        if self.is_dead:
            self.death_counter += 1
            if self.death_counter >= 10:
                self.death_counter = 0
                self.death_index += 1
                if self.death_index < len(self.death_frames):
                    self.image = self.death_frames[self.death_index]
            return

        # Apply gravity
        self.vel += 0.7
        if self.vel > 8:
            self.vel = 8
        self.rect.y += int(self.vel)

        # Ground and Sky collision
        if self.rect.bottom >= 772:
            self.rect.bottom = 772
            self.vel = 0
        if self.rect.top < 0:
            self.rect.top = 0
            self.vel = 0

        # Fly
        # Fly (left mouse button or Up arrow)
        keys = pygame.key.get_pressed()
        if pygame.mouse.get_pressed()[0] == 1 or keys[pygame.K_UP]:
            self.vel = -8

        # Animate character
        self.counter += 1
        run_cd = 5

        if self.is_parrying:
            if self.counter >= run_cd:
                self.counter = 0
                self.parry_index += 1
                if self.parry_index >= len(self.parry_images):
                    self.parry_index = 0
                    self.is_parrying = False
                self.image = self.parry_images[self.parry_index]
        else:
            if self.counter >= run_cd:
                self.counter = 0
                self.index = (self.index + 1) % len(self.images)
                self.image = self.images[self.index]

# Obstacle (missile) class
class Obstacle(pygame.sprite.Sprite):
    def __init__(self, x, target):
        super().__init__()
        self.image = pygame.transform.scale(pygame.image.load('img/missile.png').convert_alpha(), (114, 34))
        self.rect = self.image.get_rect(center=(x, target.rect.centery))
        self.direction = -1  # -1: moving left, 1: deflected to right

    def update(self):
        global parry_time

        self.rect.x += self.direction * missile_speed

        # Check for parry range
        if self.direction == -1 and abs(self.rect.centerx - char.rect.centerx) < 100 and abs(self.rect.centery - char.rect.centery) < 60:
            if pygame.time.get_ticks() - parry_time <= parry_window:
                self.direction = 1
                self.image = pygame.transform.flip(self.image, True, False)
                self.rect.x += 10
                parry_sfx.play()
                char.parry()
                                # Add score and floating text
                global score
                score += 200 if powerup_score_doubler else 100

                floating = FloatingText("+100", char.rect.centerx + 30, char.rect.centery)
                floating_text_group.add(floating)

        # Remove missile if off screen
        if self.rect.right < 0 or self.rect.left > screen_width:
            self.kill()

class Lazer(pygame.sprite.Sprite):
    def __init__(self, x, y, invert_wave=False):
        super().__init__()
        self.image = pygame.image.load('img/missilespike.png').convert_alpha()
        self.rect = self.image.get_rect(topleft=(x, y))
        self.base_y = y  # initial vertical position
        self.speed = 20
        self.direction = -1
        self.angle = 1  # angle for sine wave
        self.invert_wave = invert_wave  # para ma-embert(invert)

    def update(self):
        self.rect.x += self.direction * self.speed
        self.angle += 0.75
        wave_amplitude = 35

        # Flip the sine wave direction
        wave_offset = math.sin(self.angle) * wave_amplitude
        if self.invert_wave:
            wave_offset *= -1

        self.rect.y = self.base_y + wave_offset

        if self.rect.right < 0:
            self.kill()

class ClusterProjectile(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        # Load 4-frame animation (like other classes)
        self.frames = [
            pygame.transform.scale(pygame.image.load(f'img/cluster{num}.png').convert_alpha(), (30, 30))
            for num in range(1, 5)
        ]
        self.image = self.frames[0]
        self.rect = self.image.get_rect(center=(x, y))
        self.speed = scroll_speed

        self.index = 0
        self.counter = 0
        self.animation_cd = 5  # frames per update (adjust for speed)

    def update(self):
        if not game_over:
            self.rect.x -= scroll_speed
        if self.rect.right < 0:
            self.kill()

        # Animation logic (like Chara)
        self.counter += 1
        if self.counter >= self.animation_cd:
            self.counter = 0
            self.index = (self.index + 1) % len(self.frames)
            self.image = self.frames[self.index]

class FloatingText(pygame.sprite.Sprite):
    def __init__(self, text, x, y, color=(20, 255, 0)):
        super().__init__()
        self.font = pygame.font.SysFont('Daydream', 15)
        self.image = self.font.render(text, True, color)
        self.rect = self.image.get_rect(center=(x, y))
        self.lifetime = 40
        self.alpha = 255
        self.color = color
        self.text = text

    def update(self):
        self.rect.y -= 1  # move upward
        self.lifetime -= 1
        if self.lifetime <= 0:
            self.kill()
        else:
            self.image = self.font.render(self.text, True, self.color)  # fade out
            self.image.set_alpha(self.alpha)

class Coin(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = coin_img
        self.rect = self.image.get_rect(center=(x, y))

    def update(self):
        if not game_over:
            self.rect.x -= scroll_speed
        if self.rect.right < 0:
            self.kill()

# Sprite groups
char_group = pygame.sprite.Group()
obstacle_group = pygame.sprite.Group()
spiked_group = pygame.sprite.Group()
cluster_group = pygame.sprite.Group()
floating_text_group = pygame.sprite.Group()
coin_group = pygame.sprite.Group()

char = Chara(100, 700)
char_group.add(char)


coin_spawn_delay = 3000
last_coin_spawn = pygame.time.get_ticks()
missile_spawn_delay = 5000
last_missile_time = pygame.time.get_ticks()
cluster_spawn_delay = 1000
last_cluster_spawn = pygame.time.get_ticks()

pause_start_time = 0
total_paused_duration = 0
total_saved_coins = load_total_coins()
# For spikey missiles
laser_beam_active = False
show_laser_warning = False
laser_beam_start_time = 0
laser_beam_duration = 700  # milliseconds
laser_beam_interval = 1    # spacing between laser segments (ms)
last_laser_spawn = 0
next_laser_trigger_time = 0
laser_ready = False
laser_warning_start_time = 0
laser_warning_duration = 1000
laser_pair = (100, 650)  # default starting pair
last_cluster_zone = "middle"  # initial value

# For missile warning
missile_warning = False
missile_warning_start_time = 0
missile_warning_duration = 1000  # 1 second
missile_target_y = 0

# Game loop
run = True
while run:
    clock.tick(fps)

    for event in pygame.event.get():
        if game_state == "menu" and music_intro_looping:
            # Loop the intro music every 3 seconds
            if pygame.time.get_ticks() - loop_start_time >= loop_duration_ms:
                pygame.mixer.music.stop()
                pygame.mixer.music.play(-1, 0.0)
                loop_start_time = pygame.time.get_ticks()

        if event.type == pygame.QUIT:
            run = False

        # Start game on click
        if game_state == "menu" and event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if start_button.collidepoint(event.pos):
                game_state = "playing"

                # Apply shop powerups
                powerup_shield = shop_purchased_shield
                powerup_score_doubler = shop_purchased_doubler
                
                if music_intro_looping:
                    music_intro_looping = False
                    pygame.mixer.music.stop()
                    pygame.mixer.music.load('sfx/bg music mainsong.wav')
                    pygame.mixer.music.play(-1)
        
        if game_state == "menu" and event.type == pygame.MOUSEBUTTONDOWN:
            if shop_button.collidepoint(event.pos):
                    game_state = "shop"

        elif game_state == "shop" and event.type == pygame.MOUSEBUTTONDOWN:
            mx, my = event.pos
            if 200 <= my <= 240:
                if shop_purchased_shield:
                    error_sfx.play()
                elif total_saved_coins >= 2000:
                    shop_purchased_shield = True
                    total_saved_coins -= 2000
                    save_total_coins(total_saved_coins)
                    buy_sfx.play()
                else:
                    error_sfx.play()

            elif 300 <= my <= 340:
                if shop_purchased_doubler:
                    error_sfx.play()
                elif total_saved_coins >= 3000:
                    shop_purchased_doubler = True
                    total_saved_coins -= 3000
                    save_total_coins(total_saved_coins)
                    buy_sfx.play()
                else:
                    error_sfx.play()

            elif back_button.collidepoint(event.pos):
                game_state = "menu"
                save_total_coins(total_saved_coins)  # Save in case something was purchased

        # Parry input (right click)
        elif game_state == "playing" and event.type == pygame.MOUSEBUTTONDOWN and event.button == 3:
            if not char.is_dead: #para bawal magparry pag namatay na
                parry_time = pygame.time.get_ticks()

        # Parry input (Space key)
        elif game_state == "playing" and event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
            if not char.is_dead:
                parry_time = pygame.time.get_ticks()

        # Pause Game when pressing excape
        elif event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            paused = not paused
            if paused:
                pause_start_time = pygame.time.get_ticks()
                pygame.mixer.music.pause()
            else:
                total_paused_duration += pygame.time.get_ticks() - pause_start_time
                pygame.mixer.music.unpause()

        # Restart game after death
        elif game_state == "game_over" and event.type == pygame.KEYDOWN and event.key == pygame.K_r:
            game_state = "menu"
            game_over = False
            score = 0
            coins_collected = 0
            shop_purchased_shield = False
            shop_purchased_doubler = False

            char = Chara(100, 700)
            char_group.empty()
            char_group.add(char)
            obstacle_group.empty()
            coin_group.empty()
            cluster_group.empty()
            
            #reset laser variables
            powerup_shield = False
            powerup_score_doubler = False
            shield_used = False
            missile_warning = False
            show_laser_warning = False
            laser_beam_active = False
            next_laser_trigger_time = 0
            laser_beam_start_time = 0
            laser_warning_start_time = 0

            save_total_coins(total_saved_coins)


            music_intro_looping = True
            pygame.mixer.music.load('sfx/bgmusicintro.wav')
            pygame.mixer.music.play(-1)
            loop_start_time = pygame.time.get_ticks()

    screen.fill((0, 0, 0))
            
    # Menu state and shop
    if game_state == "menu":
        draw_start_menu()
    elif game_state == "shop":
        draw_shop_menu()
    
    elif game_state == "playing":
        # Draw scrolling background
        screen.blit(bg, (bg_scroll, 0))
        screen.blit(bg, (bg_scroll + screen_width, 0))
        if not game_over and not paused:
            bg_scroll -= scroll_speed // 2
            if abs(bg_scroll) >= screen_width:
                bg_scroll = 0

        # draw the warning for the lasers with respect to the chosen position options
        if show_laser_warning and (pygame.time.get_ticks() // 150) % 2 == 0:
            screen.blit(warning_img, (screen_width - 64, laser_pair[0]))
            screen.blit(warning_img, (screen_width - 64, laser_pair[1]))

        # Missile warning (before missile spawns)
        if missile_warning and (pygame.time.get_ticks() // 150) % 2 == 0:
            screen.blit(missile_warning_img, (screen_width - 64, missile_target_y - 24))
        
        # Update sprites only if not paused
        if not paused:
            char_group.update()
            obstacle_group.update()
            spiked_group.update()
            cluster_group.update()
            floating_text_group.update()
            coin_group.update()

        #Draw Sprites like usual so u can still see when paused
        floating_text_group.draw(screen)
        cluster_group.draw(screen)
        spiked_group.draw(screen)
        char_group.draw(screen)
        obstacle_group.draw(screen)
        coin_group.draw(screen)

        # Spawning 
        if not game_over:
            current_time = pygame.time.get_ticks()
        #  Coin Row Spawning 
            if current_time - last_coin_spawn >= coin_spawn_delay:
                if len(coin_group) < 30:

                    coin_y_positions = [150, 250, 350, 450, 550, 650]  # possible rows
                    y = random.choice(coin_y_positions)
                    coin_spacing = 35
                    num_coins = random.randint(5, 8)
                    for i in range(num_coins):
                        coin = Coin(screen_width + i * coin_spacing, y)
                        coin_group.add(coin)
                    last_coin_spawn = current_time

        # Spawn cluster of 3 projectiles in a vertical stack
            if current_time - last_cluster_spawn >= cluster_spawn_delay:
                cluster_y_options = [100, 400, 700]  # top, middle, bottom
                base_y = random.choice(cluster_y_options)

                # Track zone
                if base_y == 400:
                    last_cluster_zone = "middle"
                else:
                    last_cluster_zone = "top_bottom"

                spacing = 9
                projectile_height = 25  # height of one cluster projectile
                total_height = 3 * projectile_height + 2 * spacing  # total stack height

                # Function to spawn one stack
                def spawn_cluster_stack(center_y):
                    for i in range(3):
                        y_offset = center_y + (i - 1) * (projectile_height + spacing)
                        cluster = ClusterProjectile(screen_width + 50, y_offset)
                        cluster_group.add(cluster)

                # Spawn main stack
                spawn_cluster_stack(base_y)

                # If it's bottom, also spawn one on top
                if base_y == 700:
                    spawn_cluster_stack(100)

                last_cluster_spawn = current_time
                cluster_spawn_delay = random.randint(1000, 3000)

            # Show warning before missile spawns
            if score >= 350:
                if not missile_warning and current_time - last_missile_time > missile_spawn_delay:
                    missile_warning = True
                    missile_warning_start_time = current_time
                    missile_target_y = char.rect.centery  # Save player's Y at this moment

                # After warning duration, spawn missile
                if missile_warning and current_time - missile_warning_start_time >= missile_warning_duration:
                    obstacle = Obstacle(screen_width + 50, char)
                    obstacle.rect.centery = missile_target_y  # Set fixed Y position from warning
                    obstacle_group.add(obstacle)
                    last_missile_time = current_time
                    missile_warning = False
            
            # Trigger laser beams only after score reaches 1100 (PARA DI KA MAG CAMP SA BABA HAHAHA)
            if game_state == "playing" and pygame.time.get_ticks() - loop_start_time >= 19000:
                current_time = pygame.time.get_ticks()
                cluster_spawn_delay = random.randint(3500, 5000)
                # If no laser active and it's time, activate
                if not laser_beam_active and not show_laser_warning and current_time >= next_laser_trigger_time:
                    # Choose laser_pair before warning starts 
                    # Choose laser_pair based on last cluster zone
                    all_laser_positions = [
                        (100, 650), (200, 500),  # Top + bottom sets
                        (300, 400), (350, 470)   # Middle sets
                    ]

                    # Filter out laser positions that match cluster zones
                    if last_cluster_zone == "middle":
                        avoid_y = [400]  # Middle
                    else:
                        avoid_y = [100, 650]  # Top + bottom

                    # Remove laser pairs that would overlap with cluster projectiles
                    position_options = [pair for pair in all_laser_positions if not (pair[0] in avoid_y or pair[1] in avoid_y)]

                    # Fallback in case all options are filtered (safety net)
                    if not position_options:
                        position_options = all_laser_positions

                    laser_pair = random.choice(position_options)

                    
                    show_laser_warning = True
                    laser_warning_start_time = current_time

                elif show_laser_warning and current_time - laser_warning_start_time >= laser_warning_duration:
                    laser_beam_active = True
                    laser_beam_start_time = current_time
                    show_laser_warning = False
                    next_laser_trigger_time = current_time + random.randint(1000, 4000)

                # If laser is active, ibaratrat
                if laser_beam_active:
                    if current_time - laser_beam_start_time <= laser_beam_duration:
                        if current_time - last_laser_spawn >= laser_beam_interval:
                            missile_top = Lazer(screen_width + 50, laser_pair[0], invert_wave=True)
                            missile_bottom = Lazer(screen_width + 50, laser_pair[1], invert_wave=False)

                            spiked_group.add(missile_top)
                            spiked_group.add(missile_bottom)
                            last_laser_spawn = current_time
                    else:
                        laser_beam_active = False  # turn off after 2 seconds

            if not paused:
                score += 2 if powerup_score_doubler else 1

                speed_boost = min(score // 200, 10)
                scroll_speed = 4 + speed_boost
                missile_speed = 20 + speed_boost
                missile_spawn_delay = max(500, 2500 - score // 2)  # Gradually reduce delay
            
            # Collision detection for missile
            for missile in obstacle_group:
                if missile.direction == -1 and char.rect.colliderect(missile.rect):  
                    if not game_over:

                        if powerup_shield and not shield_used:
                            shield_used = True
                            floating = FloatingText("PUT THAT WEAK SHI AWAY!", char.rect.centerx, char.rect.centery, color=(0, 255, 255))
                            floating_text_group.add(floating)
                            missile.kill()
                        else:
                            char.die()
                            char_death_start_time = pygame.time.get_ticks()
                            game_over = True
                            pygame.mixer.music.stop()
                            death_sfx.play()

                            if score > high_score:
                                high_score = score
                                save_high_score(high_score)

            #Cluster Missile Collision
            for cluster in cluster_group:
                if char.rect.colliderect(cluster.rect):
                    if not game_over:
                        #shield logic

                        if powerup_shield and not shield_used:
                            shield_used = True
                            shield_last_used_time = current_time
                            floating = FloatingText("PUT THAT WEAK SHI AWAY!", char.rect.centerx, char.rect.centery, color=(0, 255, 255))
                            floating_text_group.add(floating)
                            cluster.kill()

                        elif shield_used and current_time - shield_last_used_time <= shield_invincible_time:
                            # Still invincible - ignore this hit
                            cluster.kill()
                        else:
                            char.die()
                            char_death_start_time = pygame.time.get_ticks()
                            game_over = True
                            pygame.mixer.music.stop()
                            death_sfx.play()

                            if score > high_score:
                                high_score = score
                                save_high_score(high_score)

            # Collision with spikey lazors          
            for laser in spiked_group:
                if char.rect.colliderect(laser.rect):
                    if not game_over:
                        #shield logic
                        
                        if powerup_shield and not shield_used:
                            shield_used = True
                            shield_last_used_time = current_time
                            floating = FloatingText("PUT THAT WEAK SHI AWAY!", char.rect.centerx, char.rect.centery, color=(0, 255, 255))
                            floating_text_group.add(floating)
                            laser.kill()
                        elif shield_used and current_time - shield_last_used_time <= shield_invincible_time:
                            # Still invincible - ignore this hit
                            laser.kill()
                        else:
                            char.die()
                            char_death_start_time = pygame.time.get_ticks()
                            game_over = True
                            pygame.mixer.music.stop()
                            death_sfx.play()

                            if score > high_score:
                                high_score = score
                                save_high_score(high_score)           
            # Coin collection
            for coin in coin_group:
                if char.rect.colliderect(coin.rect):
                    coin.kill()
                    coins_collected += 10
                    total_saved_coins += 10
                    floating = FloatingText("+10", coin.rect.centerx, coin.rect.centery, color=(255, 215, 0)) 
                    floating_text_group.add(floating)
                    coin_sfx.play()
   
        # Draw ground and scroll
        screen.blit(ground_img, (ground_scroll, 768))
        if not game_over and not paused:
            ground_scroll -= scroll_speed
            if abs(ground_scroll) > 35:
                ground_scroll = 0

        # Draw score & top score
        score_surface = score_font.render(f'Score: {score}', True, (255, 255, 255))
        screen.blit(score_surface, (10, 10))

        high_score_surface = score_font.render(f'Top Score: {high_score}', True, (255, 255, 0))
        screen.blit(high_score_surface, (10, 40))

        coin_surface = score_font.render(f'Coins: {coins_collected}', True, (255, 215, 0))
        screen.blit(coin_surface, (10, 70))

        #Draw pause
        if paused:
            overlay = pygame.Surface((screen_width, screen_height))
            overlay.set_alpha(100)
            overlay.fill((0, 0, 0))
            screen.blit(overlay, (0, 0))

            pause_text = button_font.render("PAUSED", True, (255, 255, 255))
            screen.blit(pause_text, pause_text.get_rect(center=(screen_width // 2, screen_height // 2)))

        # Switch to game over state after delay
        if game_over and char.is_dead and pygame.time.get_ticks() - char_death_start_time > 1000:
            game_state = "game_over"

    elif game_state == "game_over":
        obstacle_group.empty()     # Kill all missiles so that when it restarts the player isn't overwhelmed by the previous projectile
        spiked_group.empty()
        cluster_group.empty()       
        draw_game_over_screen()

    pygame.display.update()

pygame.quit()
