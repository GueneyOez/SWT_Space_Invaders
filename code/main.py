import pygame, sys
from player import Player
import obstacle
from alien import Alien, Ufo
from random import choice, randint
from laser import Laser


class Game:
    def __init__(self):
        # Player setup
        player_sprite = Player((screen_width / 2, screen_height), screen_width, 5)
        self.player = pygame.sprite.GroupSingle(player_sprite)

        # Health setup
        self.lives = 3
        self.live_surf = pygame.image.load("graphics/player.png").convert_alpha()
        self.live_x_start_pos = screen_width - (self.live_surf.get_size()[0] * 3 + 30)

        # Score setup
        self.score = 0
        self.font = pygame.font.Font("graphics/Pixeled.ttf", 20)

        # Obstacle setup
        self.shape = obstacle.shape
        self.block_size = 6
        self.blocks = pygame.sprite.Group()
        self.obstacle_amount = 4
        self.obstacle_x_positions = [
            num * (screen_width / self.obstacle_amount)
            for num in range(self.obstacle_amount)
        ]
        self.create_multiple_obstacles(
            *self.obstacle_x_positions, x_start=screen_width / 18, y_start=480
        )

        # Alien setup
        self.aliens = pygame.sprite.Group()
        self.alien_lasers = pygame.sprite.Group()
        self.alien_setup(rows=5, columns=8)
        self.alien_direction = 1

        # Ufo setup
        self.ufo = pygame.sprite.GroupSingle()
        self.ufo_spawn_time = randint(400, 800)

    def create_obstacle(self, x_start, y_start, offset_x):
        for row_index, row in enumerate(self.shape):
            for col_index, col in enumerate(row):
                if col == "x":
                    x = x_start + col_index * self.block_size + offset_x
                    y = y_start + row_index * self.block_size
                    block = obstacle.Block(self.block_size, (241, 79, 80), x, y)
                    self.blocks.add(block)

    def create_multiple_obstacles(self, *offset, x_start, y_start):
        for offset_x in offset:
            self.create_obstacle(x_start, y_start, offset_x)

    def alien_setup(
        self, rows, columns, x_distance=60, y_distance=48, x_offset=70, y_offset=100
    ):
        for row_index, row in enumerate(range(rows)):
            for col_index, col in enumerate(range(columns)):
                x = col_index * x_distance + x_offset
                y = row_index * y_distance + y_offset

                if row_index == 0:
                    alien_sprite = Alien("blue_alien", x, y)
                elif 1 <= row_index <= 2:
                    alien_sprite = Alien("red_alien", x, y)
                else:
                    alien_sprite = Alien("yellow_alien", x, y)
                self.aliens.add(alien_sprite)

    def alien_position_checker(self):
        all_aliens = self.aliens.sprites()
        for alien in all_aliens:
            if alien.rect.right >= screen_width:
                self.alien_direction = -1
                self.alien_move_down(2)
            elif alien.rect.left <= 0:
                self.alien_direction = 1
                self.alien_move_down(2)

    def alien_move_down(self, distance):
        if self.aliens:
            for alien in self.aliens.sprites():
                alien.rect.y += distance

    def alien_shoot(self):
        if self.aliens.sprites():
            random_alien = choice(self.aliens.sprites())
            laser_sprite = Laser(random_alien.rect.center, 6, screen_height)
            self.alien_lasers.add(laser_sprite)

    def ufo_alien_timer(self):
        self.ufo_spawn_time -= 1
        if self.ufo_spawn_time <= 0:
            self.ufo.add(Ufo(choice(["right", "left"]), screen_width))
            self.ufo_spawn_time = randint(400, 800)

    def collision_checks(self):
        #  Player lasers
        if self.player.sprite.lasers:
            for laser in self.player.sprite.lasers:
                # obstacle collisions
                if pygame.sprite.spritecollide(laser, self.blocks, True):
                    laser.kill()

                # alien collisions
                aliens_hit = pygame.sprite.spritecollide(laser, self.aliens, True)
                if aliens_hit:
                    for alien in aliens_hit:
                        self.score += alien.value
                    laser.kill()

                # ufo collision
                if pygame.sprite.spritecollide(laser, self.ufo, True):
                    self.score += 50
                    laser.kill()

        # Alien lasers
        if self.alien_lasers:
            for laser in self.alien_lasers:
                # obstacle collisions
                if pygame.sprite.spritecollide(laser, self.blocks, True):
                    laser.kill()

                if pygame.sprite.spritecollide(laser, self.player, False):
                    laser.kill()
                    self.lives -= 1
                    if self.lives <= 0:
                        pygame.quit()
                        sys.exit()

        # Aliens
        if self.aliens:
            for alien in self.aliens:
                pygame.sprite.spritecollide(alien, self.blocks, True)

                if pygame.sprite.spritecollide(alien, self.player, False):
                    pygame.quit()
                    sys.exit()

    def display_lives(self):
        for live in reversed(range(self.lives)):
            x = self.live_x_start_pos + (
                (2 - live) * (self.live_surf.get_size()[0] + 10)
            )
            screen.blit(self.live_surf, (x, 8))

    def display_score(self):
        score_surf = self.font.render(f"score: {self.score}", False, "white")
        score_rect = score_surf.get_rect(topleft=(10, -10))
        screen.blit(score_surf, score_rect)

    def display_victory_message(self):
        if not self.aliens.sprites():
            victory_surf = self.font.render("You won", False, "white")
            victory_rect = victory_surf.get_rect(
                center=(screen_width / 2, screen_height / 2)
            )
            screen.blit(victory_surf, victory_rect)

    def show_menu(self):
        # Show title
        title_text = pygame.font.Font("graphics/Pixeled.ttf", 40).render(
            "SPACE INVADERS", True, (255, 255, 255)
        )
        title_rect = title_text.get_rect(center=(screen_width // 2, 100))
        screen.blit(title_text, title_rect)

        # Show instruction text
        instruction_text = pygame.font.Font("graphics/Pixeled.ttf", 20).render(
            "PRESS ANY KEY TO CONTINUE", True, (255, 255, 255)
        )
        instruction_rect = instruction_text.get_rect(center=(screen_width // 2, 150))
        screen.blit(instruction_text, instruction_rect)

        # Show enemy images and point values
        enemy_images = [
            pygame.image.load("graphics/yellow_alien.png").convert_alpha(),
            pygame.image.load("graphics/red_alien.png").convert_alpha(),
            pygame.image.load("graphics/blue_alien.png").convert_alpha(),
            pygame.image.load("graphics/ufo.png").convert_alpha(),
        ]

        enemy_texts = [
            ("= 10 PTS", (217, 255, 0)),
            ("= 20 PTS", (255, 0, 106)),
            ("= 30 PTS", (0, 183, 239)),
            ("= ??? PTS", (38, 211, 239)),
        ]

        for i, (image, (text, color)) in enumerate(zip(enemy_images, enemy_texts)):
            image_rect = image.get_rect(topleft=(200, 215 + i * 75))
            screen.blit(image, image_rect)

            enemy_text = pygame.font.Font("graphics/Pixeled.ttf", 20).render(
                text, True, color
            )
            enemy_rect = enemy_text.get_rect(topleft=(255, 200 + i * 75))
            screen.blit(enemy_text, enemy_rect)

    def run(self):
        # update all sprite groups
        # draw all sprite groups
        self.player.update()
        self.aliens.update(self.alien_direction)
        self.alien_lasers.update()
        self.ufo.update()

        self.alien_position_checker()
        self.ufo_alien_timer()
        self.collision_checks()
        self.display_lives()
        self.display_score()
        self.display_victory_message()

        self.player.sprite.lasers.draw(screen)
        self.player.draw(screen)
        self.blocks.draw(screen)
        self.aliens.draw(screen)
        self.alien_lasers.draw(screen)
        self.ufo.draw(screen)


if __name__ == "__main__":
    pygame.init()
    screen_width = 600
    screen_height = 600
    pygame.display.set_caption("Space Invader")
    screen = pygame.display.set_mode((screen_width, screen_height))
    clock = pygame.time.Clock()
    game = Game()

    ALIEN_LASER_EVENT = pygame.USEREVENT + 1
    pygame.time.set_timer(ALIEN_LASER_EVENT, 800)

    in_menu = True
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYDOWN and in_menu:
                in_menu = False
            elif event.type == ALIEN_LASER_EVENT and not in_menu:
                game.alien_shoot()

        screen.fill((30, 30, 30))

        if in_menu:
            game.show_menu()
        else:
            game.run()

        pygame.display.flip()
        clock.tick(60)
