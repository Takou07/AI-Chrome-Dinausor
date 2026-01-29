import pygame
import os
import random
import csv
import joblib  # <--- Important pour charger ton modèle .pkl

pygame.init()

# Global Constants
SCREEN_HEIGHT = 600
SCREEN_WIDTH = 1100
SCREEN = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))

# Asset loading (assumé que les dossiers Assets existent)
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
        self.duck_img = DUCKING
        self.run_img = RUNNING
        self.jump_img = JUMPING
        self.dino_duck = False
        self.dino_run = True
        self.dino_jump = False
        self.step_index = 0
        self.jump_vel = self.JUMP_VEL
        self.image = self.run_img[0]
        self.dino_rect = self.image.get_rect()
        self.dino_rect.x = self.X_POS
        self.dino_rect.y = self.Y_POS

    def update(self, userInput):
        if self.dino_duck: self.duck()
        if self.dino_run: self.run()
        if self.dino_jump: self.jump()
        if self.step_index >= 10: self.step_index = 0

        if userInput[pygame.K_UP] and not self.dino_jump:
            self.dino_duck = False
            self.dino_run = False
            self.dino_jump = True
        elif userInput[pygame.K_DOWN] and not self.dino_jump:
            self.dino_duck = True
            self.dino_run = False
            self.dino_jump = False
        elif not (self.dino_jump or userInput[pygame.K_DOWN]):
            self.dino_duck = False
            self.dino_run = True
            self.dino_jump = False

    def duck(self):
        self.image = self.duck_img[self.step_index // 5]
        self.dino_rect = self.image.get_rect()
        self.dino_rect.x = self.X_POS
        self.dino_rect.y = self.Y_POS_DUCK
        self.step_index += 1

    def run(self):
        self.image = self.run_img[self.step_index // 5]
        self.dino_rect = self.image.get_rect()
        self.dino_rect.x = self.X_POS
        self.dino_rect.y = self.Y_POS
        self.step_index += 1

    def jump(self):
        self.image = self.jump_img
        if self.dino_jump:
            self.dino_rect.y -= self.jump_vel * 4
            self.jump_vel -= 0.8
        if self.jump_vel < - self.JUMP_VEL:
            self.dino_jump = False
            self.jump_vel = self.JUMP_VEL

    def draw(self, SCREEN):
        SCREEN.blit(self.image, (self.dino_rect.x, self.dino_rect.y))

# [Classes Cloud, Obstacle, SmallCactus, LargeCactus, Bird restent identiques...]
class Cloud:
    def __init__(self):
        self.x = SCREEN_WIDTH + random.randint(800, 1000)
        self.y = random.randint(50, 100)
        self.image = CLOUD
        self.width = self.image.get_width()
    def update(self):
        self.x -= game_speed
        if self.x < -self.width:
            self.x = SCREEN_WIDTH + random.randint(2500, 3000)
            self.y = random.randint(50, 100)
    def draw(self, SCREEN):
        SCREEN.blit(self.image, (self.x, self.y))

class Obstacle:
    def __init__(self, image, type):
        self.image = image
        self.type = type
        self.rect = self.image[self.type].get_rect()
        self.rect.x = SCREEN_WIDTH
    def update(self):
        self.rect.x -= game_speed
        if self.rect.x < -self.rect.width:
            obstacles.pop(0) # Correction pop(0) pour enlever le premier
    def draw(self, SCREEN):
        SCREEN.blit(self.image[self.type], self.rect)

class SmallCactus(Obstacle):
    def __init__(self, image):
        self.type = random.randint(0, 2)
        super().__init__(image, self.type)
        self.rect.y = 325

class LargeCactus(Obstacle):
    def __init__(self, image):
        self.type = random.randint(0, 2)
        super().__init__(image, self.type)
        self.rect.y = 300

class Bird(Obstacle):
    def __init__(self, image):
        self.type = 0
        super().__init__(image, self.type)
        self.rect.y = 250
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
    cloud = Cloud()
    game_speed = 20
    x_pos_bg = 0
    y_pos_bg = 380
    points = 0
    font = pygame.font.Font('freesansbold.ttf', 20)
    obstacles = []
    death_count = 0
    data_log = [] 

    # --- TENTATIVE DE CHARGEMENT DE L'IA ---
    brain = None
    try:
        brain = joblib.load('models/dino_brain.pkl')
    except:
        pass

    def score():
        global points, game_speed
        points += 1
        if points % 100 == 0: game_speed += 1
        text = font.render(f"Points: {points} | IA: {'Active' if brain else 'Off'}", True, (0, 0, 0))
        SCREEN.blit(text, (900, 40))

    def background():
        global x_pos_bg, y_pos_bg
        image_width = BG.get_width()
        SCREEN.blit(BG, (x_pos_bg, y_pos_bg))
        SCREEN.blit(BG, (image_width + x_pos_bg, y_pos_bg))
        if x_pos_bg <= -image_width: x_pos_bg = 0
        x_pos_bg -= game_speed

    while run:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
                pygame.quit()
                quit()

        SCREEN.fill((255, 255, 255))
        
        # --- LOGIQUE DE DÉCISION (IA vs HUMAIN) ---
        if brain and len(obstacles) > 0:
            obstacle = obstacles[0]
            dist_x = obstacle.rect.x - player.dino_rect.x
            # On envoie EXACTEMENT les mêmes features que dans train.py
            # ['distance_x', 'obstacle_y', 'game_speed']
            prediction = brain.predict([[dist_x, obstacle.rect.y, game_speed]])[0]
            
            # Simulation d'input pour l'update du dino
            userInput = {pygame.K_UP: False, pygame.K_DOWN: False}
            if prediction == 1: userInput[pygame.K_UP] = True
            if prediction == 2: userInput[pygame.K_DOWN] = True
        else:
            userInput = pygame.key.get_pressed()

        player.draw(SCREEN)
        player.update(userInput)

        if len(obstacles) == 0:
            rand_val = random.randint(0, 2)
            if rand_val == 0: obstacles.append(SmallCactus(SMALL_CACTUS))
            elif rand_val == 1: obstacles.append(LargeCactus(LARGE_CACTUS))
            elif rand_val == 2: obstacles.append(Bird(BIRD))

        # --- COLLECTE SI PAS D'IA ---
        if not brain and len(obstacles) > 0:
            obstacle = obstacles[0]
            dist_x = obstacle.rect.x - player.dino_rect.x
            action = 0
            if userInput[pygame.K_UP]: action = 1
            if userInput[pygame.K_DOWN]: action = 2
            data_log.append([dist_x, obstacle.rect.y, game_speed, action])

        for obstacle in obstacles:
            obstacle.draw(SCREEN)
            obstacle.update()
            if player.dino_rect.colliderect(obstacle.rect):
                # Sauvegarde uniquement en mode collecte
                if not brain and len(data_log) > 0:
                    if not os.path.exists("data"): os.makedirs("data")
                    with open("data/dino_data.csv", "a", newline="") as f:
                        csv.writer(f).writerows(data_log)
                
                pygame.time.delay(500)
                death_count += 1
                menu(death_count)

        background()
        cloud.draw(SCREEN)
        cloud.update()
        score()
        clock.tick(30)
        pygame.display.update()

def menu(death_count):
    global points
    run = True
    while run:
        SCREEN.fill((255, 255, 255))
        font = pygame.font.Font('freesansbold.ttf', 30)
        if death_count == 0:
            text = font.render("Press any Key to Start", True, (0, 0, 0))
        else:
            text = font.render("Press any Key to Restart", True, (0, 0, 0))
            score_label = font.render(f"Your Score: {points}", True, (0, 0, 0))
            SCREEN.blit(score_label, (SCREEN_WIDTH // 2 - 100, SCREEN_HEIGHT // 2 + 50))
        
        SCREEN.blit(text, (SCREEN_WIDTH // 2 - 150, SCREEN_HEIGHT // 2))
        pygame.display.update()
        for event in pygame.event.get():
            if event.type == pygame.QUIT: pygame.quit(); quit()
            if event.type == pygame.KEYDOWN: main()

menu(death_count=0)