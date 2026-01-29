import pygame
import os
import random
import csv

pygame.init()

# Global Constants
SCREEN_HEIGHT = 600
SCREEN_WIDTH = 1100
SCREEN = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))

# Assets loading
RUNNING = [pygame.image.load(os.path.join("Assets/Dino", "DinoRun1.png")),
           pygame.image.load(os.path.join("Assets/Dino", "DinoRun2.png"))]
JUMPING = pygame.image.load(os.path.join("Assets/Dino", "DinoJump.png"))
DUCKING = [pygame.image.load(os.path.join("Assets/Dino", "DinoDuck1.png")),
           pygame.image.load(os.path.join("Assets/Dino", "DinoDuck2.png"))]

SMALL_CACTUS = [pygame.image.load(os.path.join("Assets/Cactus", "SmallCactus1.png")),
                pygame.image.load(os.path.join("Assets/Cactus", "SmallCactus2.png")),
                pygame.image.load(os.path.join("Assets/Cactus", "SmallCactus3.png"))]
LARGE_CACTUS = [pygame.image.load(os.path.join("Assets/Cactus", "LargeCactus1.png")),
                pygame.image.load(os.path.join("Assets/Cactus", "LargeCactus2.png")),
                pygame.image.load(os.path.join("Assets/Cactus", "LargeCactus3.png"))]

BIRD = [pygame.image.load(os.path.join("Assets/Bird", "Bird1.png")),
        pygame.image.load(os.path.join("Assets/Bird", "Bird2.png"))]

CLOUD = pygame.image.load(os.path.join("Assets/Other", "Cloud.png"))
BG = pygame.image.load(os.path.join("Assets/Other", "Track.png"))

class Dinosaur:
    X_POS = 80
    Y_POS = 310
    Y_POS_DUCK = 340
    JUMP_VEL = 8.5

    def __init__(self):
        self.duck_img, self.run_img, self.jump_img = DUCKING, RUNNING, JUMPING
        self.dino_duck, self.dino_run, self.dino_jump = False, True, False
        self.step_index = 0
        self.jump_vel = self.JUMP_VEL
        self.image = self.run_img[0]
        self.dino_rect = self.image.get_rect()
        self.dino_rect.x, self.dino_rect.y = self.X_POS, self.Y_POS

    def update(self, userInput):
        if self.dino_duck: self.duck()
        if self.dino_run: self.run()
        if self.dino_jump: self.jump()
        if self.step_index >= 10: self.step_index = 0

        if userInput[pygame.K_UP] and not self.dino_jump:
            self.dino_duck, self.dino_run, self.dino_jump = False, False, True
        elif userInput[pygame.K_DOWN] and not self.dino_jump:
            self.dino_duck, self.dino_run, self.dino_jump = True, False, False
        elif not (self.dino_jump or userInput[pygame.K_DOWN]):
            self.dino_duck, self.dino_run, self.dino_jump = False, True, False

    def duck(self):
        self.image = self.duck_img[self.step_index // 5]
        self.dino_rect = self.image.get_rect()
        self.dino_rect.x, self.dino_rect.y = self.X_POS, self.Y_POS_DUCK
        self.step_index += 1

    def run(self):
        self.image = self.run_img[self.step_index // 5]
        self.dino_rect = self.image.get_rect()
        self.dino_rect.x, self.dino_rect.y = self.X_POS, self.Y_POS
        self.step_index += 1

    def jump(self):
        self.image = self.jump_img
        if self.dino_jump:
            self.dino_rect.y -= self.jump_vel * 4
            self.jump_vel -= 0.8
        if self.jump_vel < -self.JUMP_VEL:
            self.dino_jump = False
            self.jump_vel = self.JUMP_VEL

    def draw(self, SCREEN):
        SCREEN.blit(self.image, (self.dino_rect.x, self.dino_rect.y))

class Obstacle:
    def __init__(self, image, type):
        self.image, self.type = image, type
        self.rect = self.image[self.type].get_rect()
        self.rect.x = SCREEN_WIDTH
    def update(self):
        self.rect.x -= game_speed
        if self.rect.x < -self.rect.width: obstacles.pop(0)
    def draw(self, SCREEN):
        SCREEN.blit(self.image[self.type], self.rect)

class SmallCactus(Obstacle):
    def __init__(self, image):
        super().__init__(image, random.randint(0, 2))
        self.rect.y = 325

class LargeCactus(Obstacle):
    def __init__(self, image):
        super().__init__(image, random.randint(0, 2))
        self.rect.y = 300

class Bird(Obstacle):
    def __init__(self, image):
        super().__init__(image, 0)
        self.rect.y = 250 # L'oiseau est plus haut que les cactus
        self.index = 0
    def draw(self, SCREEN):
        if self.index >= 9: self.index = 0
        SCREEN.blit(self.image[self.index//5], self.rect)
        self.index += 1

def main():
    global game_speed, x_pos_bg, y_pos_bg, points, obstacles
    run = True
    clock = pygame.time.Clock()
    player = Dinosaur()
    game_speed, x_pos_bg, y_pos_bg, points = 20, 0, 380, 0
    font = pygame.font.Font('freesansbold.ttf', 20)
    obstacles = []
    death_count = 0
    
    # --- INITIALISATION DE LA COLLECTE ---
    data_log = [] 

    while run:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit(); quit()

        SCREEN.fill((255, 255, 255))
        userInput = pygame.key.get_pressed()

        # --- LOGIQUE DE COLLECTE DES DONNÉES ---
        if len(obstacles) > 0:
            obs = obstacles[0]
            dist_x = obs.rect.x - player.dino_rect.x
            obs_y = obs.rect.y
            
            # Définition de l'action : 0=Run, 1=Jump, 2=Duck
            action = 0
            if userInput[pygame.K_UP]: action = 1
            if userInput[pygame.K_DOWN]: action = 2
            
            # Filtrage : On n'enregistre que si l'obstacle est proche (< 600px)
            # Et on évite d'enregistrer quand le dino est déjà en l'air (bruit)
            if dist_x < 600 and not player.dino_jump:
                data_log.append([dist_x, obs_y, game_speed, action])

        # Mise à jour du décor et du joueur
        player.draw(SCREEN)
        player.update(userInput)

        if len(obstacles) == 0:
            choice = random.randint(0, 2)
            if choice == 0: obstacles.append(SmallCactus(SMALL_CACTUS))
            elif choice == 1: obstacles.append(LargeCactus(LARGE_CACTUS))
            elif choice == 2: obstacles.append(Bird(BIRD))

        for obstacle in obstacles:
            obstacle.draw(SCREEN)
            obstacle.update()
            if player.dino_rect.colliderect(obstacle.rect):
                # --- SAUVEGARDE LORS DE LA MORT ---
                if len(data_log) > 0:
                    os.makedirs("data", exist_ok=True)
                    with open("data/dino_data.csv", "a", newline="") as f:
                        csv.writer(f).writerows(data_log)
                
                pygame.time.delay(500)
                death_count += 1
                menu(death_count)

        # Background & Score
        image_width = BG.get_width()
        SCREEN.blit(BG, (x_pos_bg, y_pos_bg))
        SCREEN.blit(BG, (image_width + x_pos_bg, y_pos_bg))
        if x_pos_bg <= -image_width: x_pos_bg = 0
        x_pos_bg -= game_speed

        points += 1
        if points % 100 == 0: game_speed += 1
        text = font.render(f"Points: {points} | Data: {len(data_log)}", True, (0, 0, 0))
        SCREEN.blit(text, (900, 40))

        clock.tick(30)
        pygame.display.update()

def menu(death_count):
    global points
    while True:
        SCREEN.fill((255, 255, 255))
        font = pygame.font.Font('freesansbold.ttf', 30)
        text = font.render("Press any Key to Start", True, (0, 0, 0))
        SCREEN.blit(text, (SCREEN_WIDTH // 2 - 150, SCREEN_HEIGHT // 2))
        pygame.display.update()
        for event in pygame.event.get():
            if event.type == pygame.QUIT: pygame.quit(); quit()
            if event.type == pygame.KEYDOWN: main()

menu(death_count=0)