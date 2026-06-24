import pygame
import sys
import random
import math

class Main: # Main class contains primary functions and variables -- live zombies / bullets, display, time, cleanup, etc.
    def __init__(self):
        self.liveZombies = [] 
        self.liveBullets = []
        self.level = 1
        self.score = 0

    def display(self): #displays scoreboard, and calls the individual movement / display functions for surfaces
        screen.fill("white")

        self.cleanup()

        scoreboard_surface = main_font.render(f"lvl:{self.level}, score:{self.score}, {pygame.time.get_ticks() / 1000:.1f}", True, "black")
        screen.blit(scoreboard_surface, scoreboard_rect) #update and print score / time / level

        user.turn() #turn user to face mouse, print them on screen again
        user.update()

        for shot in self.liveBullets: #move and print bullets on screen
            shot.move()
            shot.update()

        for mob in self.liveZombies: #move and print zombies on screen (also turn them towards player)
            mob.turn()
            mob.move(user.x_pos, user.y_pos)
            mob.update()

        if self.score > 1: #check the score and derive the level from it
            self.level = int(self.score / 2)
        
        pygame.display.update() #update all changes 

    def time(self): #used to tick the game clock (60fps)
        delta_time = clock.tick(60) / 1000
        delta_time = max(0.001, min(0.1, delta_time))

    def events(self): #function used for listening for input, quitting the game, and spawning zombies
        for event in pygame.event.get():
            if event.type == pygame.QUIT: #X button on window
                pygame.quit()
                sys.exit()
                running = False
            if event.type == pygame.MOUSEBUTTONDOWN: #click to make a bullet
                shot = Bullet(bullet_surface, user.x_pos, user.y_pos, user.angle)
                self.liveBullets.append(shot)
            if event.type == spawn: #global timer creates custom event for zombie spawns
                self.makeZombie(self.level)

        keys = pygame.key.get_pressed() #user input, happens as long as the key stays depressed
        if keys[pygame.K_a]:
            user.moveLeft()
        if keys[pygame.K_d]:
            user.moveRight()
        if keys[pygame.K_w]:
            user.moveUp()
        if keys[pygame.K_s]:
            user.moveDown()

        self.collisions() #run the function to check for collisions

    def collisions(self):
        for mob in self.liveZombies: #check each zombie for collisions
            if pygame.Rect.colliderect(user.rect, mob.rect): #Zombie x player collisions
                mob.kill()

            for shot in self.liveBullets: #zombie x bullet collisions
                if pygame.Rect.colliderect(mob.rect, shot.rect):
                    mob.kill()
                    shot.kill()

    def cleanup(self): #loop through both live lists and remove anything that's collided
        for thing in self.liveZombies:
            if thing.alive == False:
                self.liveZombies.remove(thing)
                self.score += 1

        for shot in self.liveBullets:
            if shot.alive == False:
                self.liveBullets.remove(shot)

    def makeZombie(self, quant): #make a certain number of zombies (goes up as game progresses)
        for count in range(quant):
            x_pos = random.randint(0, 1) #pick one of the four corners of the screen randomly
            y_pos = random.randint(0, 1)

            if x_pos == 1:
                x_pos = 800

            if y_pos == 1:
                y_pos = 800

            mob = Zombie(zombie_surface, x_pos, y_pos, 0, self.level)
            self.liveZombies.append(mob) #make a zombie object and put it in the live list

class Thing: #parent class for things with position and collision boxes
    def __init__(self, image, x_pos, y_pos, angle):
        self.x_pos = x_pos
        self.y_pos = y_pos #x,y position
        self.alive = True
        self.image = image #pygame surface
        self.originalImage = image #second copy so that image isn't torn when rotating
        self.angle = angle #starting angle
        self.rect = self.image.get_rect(center=(self.x_pos, self.y_pos)) #collision box
        self.image = pygame.transform.rotate(self.image, self.angle)

    def move(self): #stub for polymorphism
        pass

    def kill(self):
        self.alive = False

    def update(self): #move collision box based on x,y and update on screen
        self.rect.center = (self.x_pos, self.y_pos)
        screen.blit(self.image, self.rect)

    def turn(self): #stub for polymorphism (player turns towards mouse, zombies turn towards player)
        pass

class Zombie(Thing): #class used for zombie objects
    def __init__(self, image, x_pos, y_pos, angle, level):
        super().__init__(image, x_pos, y_pos, angle)
        self.health = 2 #health determines number of bullets to kill
        self.level = level #used for health and amount of time before despawn
        self.age = int(pygame.time.get_ticks() / 1000) #used for despawn time

    def move(self, playerx, playery): #get player position, move towards them
        if self.x_pos < playerx:
            self.x_pos += 10 * delta_time
        elif self.x_pos > playerx:
            self.x_pos -= 10 * delta_time

        if self.y_pos < playery:
            self.y_pos += 10 * delta_time
        elif self.y_pos > playery:
            self.y_pos -= 10 * delta_time

    def turn(self): #Get player position, turn towards them
        dx = user.x_pos - self.x_pos
        dy = -(user.y_pos - self.y_pos)
        angle = math.degrees(math.atan2(dy, dx)) - 90
        self.angle = angle
        self.image = pygame.transform.rotate(self.originalImage, angle)

        if int(pygame.time.get_ticks() / 1000) - self.age > 3 + (self.level / 2): #check age and kill if too old
            self.kill()

    def kill(self): #different from parent class, check health before killing
        self.health = self.health - 1

        if self.health <= 0:
            self.alive = False

class Bullet(Thing): #class for bullet objects
    def __init__(self, image, x_pos, y_pos, angle):
        super().__init__(image, x_pos, y_pos, angle)
        self.image = pygame.transform.rotate(self.originalImage, angle) #turn in same direction as player (when created)
        mouse = pygame.mouse.get_pos()
        dx = mouse[0] - self.x_pos
        dy = -(mouse[1] - self.y_pos)
        self.angle = math.atan2(dy, dx) #get angle again to calculate movement
        self.age = int(pygame.time.get_ticks() / 1000) #use for despawn time
        

    def move(self): #calculates new coordinates based on angle 
        dx = math.cos(self.angle) * (50 * delta_time)
        dy = math.sin(self.angle) * (50 * delta_time)

        self.x_pos = self.x_pos + dx
        self.y_pos = self.y_pos - dy

        if int(pygame.time.get_ticks() / 1000) - self.age > 3: #check age 
            self.kill()

class Player(Thing): #class of player object
    def __init__(self, image, x_pos, y_pos, angle):
        super().__init__(image, x_pos, y_pos, angle)
    
    def moveUp(self): #movement functions -- loop around edges of screen
        self.y_pos -= 50 * delta_time
        if self.y_pos <= -1:
            self.y_pos = 800

    def moveDown(self):
        self.y_pos += 50 * delta_time
        if self.y_pos >= 801:
            self.y_pos = 0

    def moveLeft(self):
        self.x_pos -= 50 * delta_time
        if self.x_pos <= -1:
            self.x_pos = 801

    def moveRight(self):
        self.x_pos += 50 * delta_time
        if self.x_pos >= 800:
            self.x_pos = 0

    def turn(self): #turn towards mouse
        mouse = pygame.mouse.get_pos()
        dx = mouse[0] - self.x_pos
        dy = -(mouse[1] - self.y_pos)
        angle = math.degrees(math.atan2(dy, dx)) - 90
        self.angle = angle
        self.image = pygame.transform.rotate(self.originalImage, angle)


core = Main() #create object containing main functions
running = True

pygame.init() #initialize pygame

clock = pygame.time.Clock() #start clock
delta_time = 0.1 #modifier for determining movement speed

screen = pygame.display.set_mode((800, 800)) #create window
pygame.display.set_caption("Shoot!")
main_font = pygame.font.SysFont("cambria", 50)

player_surface = pygame.image.load('./player.png').convert_alpha() #load and scale player, bullet and zombie surfaces
player_surface = pygame.transform.scale_by(player_surface, .25)

bullet_surface = pygame.image.load('./bullet.png').convert_alpha()
bullet_surface = pygame.transform.scale_by(bullet_surface, .25)

zombie_surface = pygame.image.load('./zombie.png').convert_alpha()
zombie_surface = pygame.transform.scale_by(zombie_surface, .25)

scoreboard_surface = main_font.render("TEST", True, "black") #load scoreboard surface
scoreboard_rect = scoreboard_surface.get_rect(center=(400, 50))

user = Player(player_surface, 400, 400, 0) #make player object global so coordinates are available everywhere

spawn = pygame.USEREVENT #make custom event for spawning zombies global

pygame.time.set_timer(spawn, 5000) #global timer for regulating zombie creation (every 2sec)

while running: #Game loop
    core.events()

    core.display()

    core.time()