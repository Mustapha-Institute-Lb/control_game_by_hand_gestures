import pygame
import sys
import random
from ai_controller import AIController, Controlles
import cv2

# Initialize Pygame
pygame.init()

# Set up game window
width, height = 800, 600
screen = pygame.display.set_mode((width, height))
pygame.display.set_caption("Alien Shooter Game")

# Define colors
white = (255, 255, 255)
red = (255, 0, 0)

# Define player properties
player_size = 80
player_x = width // 2 - player_size // 2
player_y = height - 2 * player_size
player_speed = 5

# Define bullet properties
bullet_size = 10
bullet_speed = 7
bullets = []

# Define alien properties
alien_size = 80
alien_speed = 2
aliens = []

# Load background image
background = pygame.image.load("../assets/background.jpg")  # Replace "background.jpg" with your image file
background = pygame.transform.scale(background, (width, height))

# Load player, alien, and bullet GIFs
player_gif = pygame.image.load("../assets/player.gif")  # Replace "player.gif" with your player GIF file
alien_gif = pygame.image.load("../assets/alien.gif")    # Replace "alien.gif" with your alien GIF file
bullet_gif = pygame.image.load("../assets/bullet.gif")  # Replace "bullet.gif" with your bullet GIF file

# Function to draw the player
def draw_player(x, y):
    adjusted = pygame.transform.scale(player_gif, (player_size, player_size))
    adjusted = pygame.transform.rotate(adjusted, 180)
    screen.blit(adjusted, (x, y))

# Function to draw a bullet
def draw_bullet(x, y):
    adjusted = pygame.transform.scale(bullet_gif, (bullet_size, bullet_size))
    adjusted = pygame.transform.rotate(adjusted, 90)
    screen.blit(adjusted, (x, y))

# Function to draw an alien
def draw_alien(x, y):
    adjusted = pygame.transform.scale(alien_gif, (alien_size, alien_size))
    screen.blit(adjusted, (x, y))

clock = pygame.time.Clock()

# Set the cooldown for shooting in milliseconds
bullet_cooldown = 200  # 500 milliseconds (0.5 seconds)

# Variables to track the last time a bullet was fired
last_bullet_time = pygame.time.get_ticks()

# initilize ai controller detector
ai_controller = AIController(cv2.VideoCapture(0), "../assets/hand_landmarker_model.task", True)

# Custome events
LEFT = pygame.USEREVENT + 1
RIGHT = pygame.USEREVENT + 2
SHOOT = pygame.USEREVENT + 3
STRAIGHT = pygame.USEREVENT + 4

# Main game loop
while True:

    movement = ai_controller.control()
    #print(movement)
    if movement == Controlles.LEFT:
        pygame.event.post(pygame.event.Event(LEFT)) 
    elif movement == Controlles.RIGHT:
        pygame.event.post(pygame.event.Event(RIGHT))
    elif movement == Controlles.SHOOT:
        pygame.event.post(pygame.event.Event(SHOOT))
    elif movement == Controlles.STRAIGHT:
        pygame.event.post(pygame.event.Event(STRAIGHT))

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            ai_controller.close()
            pygame.quit()
            sys.exit()

    # Move player
    if event.type == LEFT and player_x > 0:
        player_x -= player_speed

    if event.type == RIGHT and player_x < width - player_size:
        player_x += player_speed

    # Shoot bullets with cooldown
    current_time = pygame.time.get_ticks()
    if event.type == SHOOT and current_time - last_bullet_time > bullet_cooldown:
        bullet_x = player_x + player_size // 2 - bullet_size // 2
        bullet_y = player_y
        bullets.append((bullet_x, bullet_y))
        last_bullet_time = current_time  # Update the last bullet time


    # Move bullets
    bullets = [(x, y - bullet_speed) for x, y in bullets]

    # Spawn aliens
    if random.randint(1, 100) <= 2:
        alien_x = random.randint(0, width - alien_size)
        alien_y = 0
        aliens.append((alien_x, alien_y))

    # Move aliens
    aliens = [(x, y + alien_speed) for x, y in aliens]

    # Check for collisions
    for bullet in bullets[:]:
        for alien in aliens[:]:
            if (
                bullet[0] < alien[0] + alien_size
                and bullet[0] + bullet_size > alien[0]
                and bullet[1] < alien[1] + alien_size
                and bullet[1] + bullet_size > alien[1]
            ):
                bullets.remove(bullet)
                aliens.remove(alien)

    # print("bg")
    # Draw the background
    screen.blit(background, (0, 0))

    draw_player(player_x, player_y)

    # print("draw")

    for bullet in bullets:
        draw_bullet(*bullet)
    
    for alien in aliens:
        draw_alien(*alien)

    # Update the display
    pygame.display.flip()
    # print("flip")

    # Cap the frame rate
    clock.tick(20)
    # print("clock")
