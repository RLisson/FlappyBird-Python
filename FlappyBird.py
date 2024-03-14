import pygame
import os
import random

# TAMANHO DA TELA
WIDTH_SCREEN = 500
HEIGHT_SCREEN = 800

# IMAGENS
IMAGE_PIPE = pygame.transform.scale2x(pygame.image.load(os.path.join('imgs', 'pipe.png')))
IMAGE_GROUND = pygame.transform.scale2x(pygame.image.load(os.path.join('imgs', 'base.png')))
IMAGE_BG = pygame.transform.scale2x(pygame.image.load(os.path.join('imgs', 'bg.png')))
IMAGE_BIRD = [
    pygame.transform.scale2x(pygame.image.load(os.path.join('imgs', 'bird1.png'))),
    pygame.transform.scale2x(pygame.image.load(os.path.join('imgs', 'bird2.png'))),
    pygame.transform.scale2x(pygame.image.load(os.path.join('imgs', 'bird3.png')))
]

# FONTE
pygame.font.init()
POINTS_FONT = pygame.font.SysFont('arial', 50)


class Bird:
    IMGS = IMAGE_BIRD
    # ANIMACOES
    MAX_ROTATION = 25
    ROTATION_SPEED = 20
    ANIMATION_TIME = 5

    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.angle = 0
        self.speed = 0
        self.height = self.y
        self.time = 0
        self.img_count = 0
        self.image = self.IMGS[0]

    def jump(self):
        self.speed = -10.5
        self.time = 0
        self.height = self.y

    def move(self):
        self.time += 1
        movement = 1.5 * (self.time ** 2) + self.speed * self.time

        if movement > 16:
            movement = 16
        elif movement < 0:
            movement -= 2

        self.y += movement

        if movement < 0 or self.y < (self.height + 50):
            if self.angle < self.MAX_ROTATION:
                self.angle = self.MAX_ROTATION
        else:
            if self.angle > -90:
                self.angle -= self.ROTATION_SPEED

    def draw(self, screen):
        self.img_count += 1

        if self.img_count < self.ANIMATION_TIME:
            self.image = self.IMGS[0]
        elif self.img_count < self.ANIMATION_TIME * 2:
            self.image = self.IMGS[1]
        elif self.img_count < self.ANIMATION_TIME * 3:
            self.image = self.IMGS[2]
        elif self.img_count < self.ANIMATION_TIME * 4:
            self.image = self.IMGS[1]
        elif self.img_count < self.ANIMATION_TIME * 4 + 1:
            self.image = self.IMGS[0]
            self.img_count = 0

        if self.angle <= 80:
            self.image = self.IMGS[1]
            self.img_count = self.ANIMATION_TIME * 2

        rotated_img = pygame.transform.rotate(self.image, self.angle)
        pos_center = self.image.get_rect(topleft=(self.x, self.y)).center
        rectangle = rotated_img.get_rect(center=pos_center)
        screen.blit(rotated_img, rectangle.topleft)

    def get_mask(self):
        return pygame.mask.from_surface(self.image)


class Pipe:
    DISTANCE = 200
    SPEED = 5

    def __init__(self, x):
        self.x = x
        self.height = 0
        self.top_pos = 0
        self.bot_pos = 0
        self.TOP_PIPE = pygame.transform.flip(IMAGE_PIPE, False, True)
        self.BOT_PIPE = IMAGE_PIPE
        self.Pass = False
        self.define_height()

    def define_height(self):
        self.height = random.randrange(50, 450)
        self.top_pos = self.height - self.TOP_PIPE.get_height()
        self.bot_pos = self.height + self.DISTANCE

    def move(self):
        self.x -= self.SPEED

    def draw(self, screen):
        screen.blit(self.TOP_PIPE, (self.x, self.top_pos))
        screen.blit(self.BOT_PIPE, (self.x, self.bot_pos))

    def collide(self, bird):
        bird_mask = bird.get_mask()
        top_mask = pygame.mask.from_surface(self.TOP_PIPE)
        bot_mask = pygame.mask.from_surface(self.BOT_PIPE)

        top_dist = (self.x - bird.x, self.top_pos - round(bird.y))
        bot_dist = (self.x - bird.x, self.bot_pos - round(bird.y))

        bot_point = bird_mask.overlap(bot_mask, bot_dist)
        top_point = bird_mask.overlap(top_mask, top_dist)

        if bot_point or top_point:
            return True
        else:
            return False


class Ground:
    SPEED = 5
    WIDTH = IMAGE_GROUND.get_width()
    IMAGE = IMAGE_GROUND

    def __init__(self, y):
        self.y = y
        self.x0 = 0
        self.x1 = self.WIDTH

    def move(self):
        self.x0 -= self.SPEED
        self.x1 -= self.SPEED

        if self.x0 + self.WIDTH < 0:
            self.x0 = self.x1 + self.WIDTH
        if self.x1 + self.WIDTH < 0:
            self.x1 = self.x0 + self.WIDTH

    def draw(self, screen):
        screen.blit(self.IMAGE, (self.x0, self.y))
        screen.blit(self.IMAGE, (self.x1, self.y))


def draw_screen(screen, birds, pipes, ground, points):
    screen.blit(IMAGE_BG, (0, 0))
    for bird in birds:
        bird.draw(screen)
    for pipe in pipes:
        pipe.draw(screen)

    text = POINTS_FONT.render(f"Pontuação: {points}", 1, (255, 255, 255))
    screen.blit(text, (WIDTH_SCREEN - 10 - text.get_width(), 10))
    ground.draw(screen)
    pygame.display.update()


def main():
    birds = [Bird(230, 350)]
    ground = Ground(730)
    pipes = [Pipe(700)]
    screen = pygame.display.set_mode((WIDTH_SCREEN, HEIGHT_SCREEN))
    points = 0
    clock = pygame.time.Clock()

    running = True
    while running:
        clock.tick(30)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
                pygame.quit()
                quit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    for bird in birds:
                        bird.jump()

        for bird in birds:
            bird.move()
        ground.move()

        addPipe = False
        remove_pipe = []
        for pipe in pipes:
            for i, bird in enumerate(birds):
                if pipe.collide(bird):
                    birds.pop(i)
                if not pipe.Pass and bird.x > pipe.x:
                    pipe.Pass = True
                    addPipe = True
            pipe.move()
            if pipe.x + pipe.TOP_PIPE.get_width() < 0:
                remove_pipe.append(pipe)

        if addPipe:
            points += 1
            pipes.append(Pipe(600))
        for pipe in remove_pipe:
            pipes.remove(pipe)

        for i, bird in enumerate(birds):
            if (bird.y + bird.image.get_height()) > ground.y or bird.y < 0:
                birds.pop(i)

        if len(birds) < 1:
            running = False
            pygame.quit()
            print("Fim de Jogo!")
            print(f"Pontuação: {points}")
            quit()

        draw_screen(screen, birds, pipes, ground, points)


if __name__ == '__main__':
    main()
