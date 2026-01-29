import pygame
import os
import random
import csv
import joblib  # Pour charger le modèle entraîné

pygame.init()

# --- CONFIGURATION DE LA FENÊTRE ---
SCREEN_HEIGHT = 500
GAME_WIDTH = 800  # Zone de jeu
DEBUG_WIDTH = 200  # Zone d'affichage des données IA
SCREEN_WIDTH = GAME_WIDTH + DEBUG_WIDTH
SCREEN = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))

# --- CHARGEMENT DES ASSETS ---
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

# --- CLASSES DU JEU ---

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
        self.rect.x = GAME_WIDTH
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
        self.rect.y = 250
        self.index = 0
    def draw(self, SCREEN):
        if self.index >= 9: self.index = 0
        SCREEN.blit(self.image[self.index//5], self.rect)
        self.index += 1

# --- LOGIQUE D'AFFICHAGE DEBUG ---

def draw_debug_panel(SCREEN, brain, obstacles, player, game_speed, points):
    # Fond du panneau latéral
    pygame.draw.rect(SCREEN, (20, 20, 20), (GAME_WIDTH, 0, DEBUG_WIDTH, SCREEN_HEIGHT))
    pygame.draw.line(SCREEN, (0, 255, 0), (GAME_WIDTH, 0), (GAME_WIDTH, SCREEN_HEIGHT), 2)
    
    debug_font = pygame.font.SysFont("monospace", 18)
    dist_x, obs_y = 0, 0
    if len(obstacles) > 0:
        dist_x = obstacles[0].rect.x - player.dino_rect.x
        obs_y = obstacles[0].rect.y

    prediction_text = "N/A"
    if brain and len(obstacles) > 0:
        # Inférence IA en temps réel
        pred = brain.predict([[dist_x, obs_y, game_speed]])[0]
        prediction_text = "JUMP" if pred == 1 else "DUCK" if pred == 2 else "WAIT"

    lines = [
        f">> IA STATUS",
        f"MODE: {'AUTONOME' if brain else 'COLLECTE'}",
        f"POINTS: {points}",
        f"SPEED:  {game_speed}",
        f"",
        f">> SENSORS",
        f"DIST_X: {dist_x}",
        f"OBS_Y:  {obs_y}",
        f"",
        f">> DECISION",
        f"ACTION: {prediction_text}"
    ]

    for i, line in enumerate(lines):
        color = (0, 255, 0) if ">>" not in line else (255, 255, 0)
        surface = debug_font.render(line, True, color)
        SCREEN.blit(surface, (GAME_WIDTH + 20, 40 + (i * 30)))

# --- BOUCLE PRINCIPALE ---

def main():
    global game_speed, x_pos_bg, y_pos_bg, points, obstacles
    run = True
    clock = pygame.time.Clock()
    player = Dinosaur()
    game_speed, x_pos_bg, y_pos_bg, points = 20, 0, 380, 0
    obstacles = []
    data_log = []
    
    # CHARGEMENT DU MODÈLE IA
    brain = None
    try:
        brain = joblib.load('models/dino_brain.pkl')
    except:
        pass

    while run:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit(); quit()

        SCREEN.fill((255, 255, 255))
        
        # LOGIQUE D'ENTRÉE (IA OU MANUEL)
        if brain and len(obstacles) > 0:
            obs = obstacles[0]
            dist_x = obs.rect.x - player.dino_rect.x
            pred = brain.predict([[dist_x, obs.rect.y, game_speed]])[0]
            userInput = {pygame.K_UP: pred == 1, pygame.K_DOWN: pred == 2}
        else:
            userInput = pygame.key.get_pressed()
            # Enregistrement pour la collecte si manuel
            if len(obstacles) > 0 and not player.dino_jump:
                obs = obstacles[0]
                action = 1 if userInput[pygame.K_UP] else 2 if userInput[pygame.K_DOWN] else 0
                if (obs.rect.x - player.dino_rect.x) < 600:
                    data_log.append([obs.rect.x - player.dino_rect.x, obs.rect.y, game_speed, action])

        # Background
        image_width = BG.get_width()
        SCREEN.blit(BG, (x_pos_bg, y_pos_bg))
        SCREEN.blit(BG, (image_width + x_pos_bg, y_pos_bg))
        if x_pos_bg <= -image_width: x_pos_bg = 0
        x_pos_bg -= game_speed

        player.draw(SCREEN)
        player.update(userInput)

        if len(obstacles) == 0:
            rand = random.randint(0, 2)
            if rand == 0: obstacles.append(SmallCactus(SMALL_CACTUS))
            elif rand == 1: obstacles.append(LargeCactus(LARGE_CACTUS))
            else: obstacles.append(Bird(BIRD))

        for obstacle in obstacles:
            obstacle.draw(SCREEN)
            obstacle.update()
            if player.dino_rect.colliderect(obstacle.rect):
                if not brain and len(data_log) > 0:
                    os.makedirs("data", exist_ok=True)
                    with open("data/dino_data.csv", "a", newline="") as f:
                        csv.writer(f).writerows(data_log)
                main() # Restart

        points += 1
        if points % 100 == 0: game_speed += 1
        
        draw_debug_panel(SCREEN, brain, obstacles, player, game_speed, points)
        pygame.display.update()
        clock.tick(30)

def menu():
    while True:
        SCREEN.fill((255, 255, 255))
        font = pygame.font.SysFont("arial", 30)
        text = font.render("APPUYEZ SUR UNE TOUCHE POUR LANCER", True, (0, 0, 0))
        SCREEN.blit(text, (GAME_WIDTH // 2 - 250, SCREEN_HEIGHT // 2))
        pygame.display.update()
        for event in pygame.event.get():
            if event.type == pygame.QUIT: pygame.quit(); quit()
            if event.type == pygame.KEYDOWN: main()

if __name__ == "__main__":
    menu()