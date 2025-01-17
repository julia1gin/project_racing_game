import sys
import pygame
from pygame.locals import *
import random
import json

score = 0
# Draw text function
def draw_text(text, font, color, surface, x, y):
    text_surface = font.render(text, True, color)
    text_rect = text_surface.get_rect(center=(x, y))
    surface.blit(text_surface, text_rect)

class Settings:
    def __init__(self):
        self.screen_width = 500
        self.screen_height = 600


        # Road and marker sizes
        self.road_width = 300
        self.marker_width = 10
        self.marker_height = 50

        #Lane
        self.left_lane = 150
        self.center_lane = 250
        self.right_lane = 350

        # Hud
        self.hud_height = 50  # Height of the HUD

        # Road
        self.road_height = self.screen_height - self.hud_height

        # for animating movement of the lane markers
        self.lane_marker_move_y = 0

        # Road and edge markers
        self.road = (100, self.hud_height, self.road_width, self.road_height)
        self.left_edge_marker = (95, self.hud_height, self.marker_width, self.road_height)
        self.right_edge_marker = (395, self.hud_height, self.marker_width, self.road_height)

        #Game settings
        self.gameover = False
        self.speed = 2
        self.level = 1


class Scoreboard:
    def __init__(self):
        self.data_file = 'scoreboard.json'
        self.width = 500
        global score


    def load_scoreboard(self):
        try:
            with open(self.data_file, 'r') as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            return []

    # Save scoreboard to file
    def save_scoreboard(self, scoreboard):
        with open(self.data_file, 'w') as f:
            json.dump(scoreboard, f)

    # Update scoreboard with top 3 logic
    def update_scoreboard(self, name, score):
        scoreboard = self.load_scoreboard()
        scoreboard.append({"name": name, "score": score})
        scoreboard = sorted(scoreboard, key=lambda x: x['score'], reverse=True)[:3]
        self.save_scoreboard(scoreboard)

    # Display top 3 records during name entry
    def display_top_scores(self):
        font = pygame.font.SysFont("Bookman Old Style", 24)
        scoreboard = self.load_scoreboard()

        draw_text("Top Scores:", font, white, screen, self.width / 2, 50)
        for i, entry in enumerate(scoreboard[:3]):
            draw_text(f"{i + 1}. {entry['name']}: {entry['score']}", font, white, screen, self.width / 2, 100 + i * 30)

    def get_player_name(self):
        font = pygame.font.SysFont("Bookman Old Style", 36)
        input_active = True
        name = ""
        winner_image = pygame.image.load("images/winner.jpg")

        while input_active:
            screen.blit(winner_image, (0, 0))
            self.display_top_scores()
            draw_text(f"{languages[current_language]["your_score"]}: {score}", font, white, screen, self.width / 2, 250)
            draw_text(languages[current_language]["your_name"], font, white, screen, self.width / 2, 300)
            draw_text(name, font, white, screen, self.width / 2, 350)

            for event in pygame.event.get():
                if event.type == QUIT:
                    pygame.quit()
                    sys.exit()

                if event.type == KEYDOWN:
                    if event.key == K_RETURN:
                        return name[:10]
                    elif event.key == K_BACKSPACE:
                        name = name[:-1]
                    else:
                        if len(name) < 10 and event.unicode.isprintable():
                            name += event.unicode

            pygame.display.update()

class Vehicle(pygame.sprite.Sprite):
    def __init__(self, image, x, y):
        pygame.sprite.Sprite.__init__(self)

        # scale the image down so it's not wider than the lane
        image_scale = 45 / image.get_rect().width
        new_width = image.get_rect().width * image_scale
        new_height = image.get_rect().height * image_scale
        self.image = pygame.transform.scale(image, (new_width, new_height))

        self.rect = self.image.get_rect()
        self.rect.center = [x, y]

class PlayerVehicle(Vehicle):
    def __init__(self, x, y):
        image = pygame.image.load('images/car.png')
        super().__init__(image, x, y)

languages = {
        "en":
            {"start": "Start", "settings": "Settings",
             "exit": "Exit", "score": "Score", "level": "Level",
             "game_over": "Game Over.", "developer": "Developer",
             "menu_music": "Menu Music", "game_music": "Game Music",
             "collision_sounds": "Collision sounds", "language": "Language",
             "back": "Back", "your_score": "Your score", "your_name": "Enter your name:"},

        "ru": {"start": "Начать", "settings": "Настройки",
               "exit": "Выход", "score": "Очки", "level": "Уровень",
               "game_over": "Игра окончена.", "developer": "Разработчик",
               "menu_music": "Громкость музыки в меню",
               "game_music": "Громкость музыки в игре",
               "collision_sounds": "Громкость звуков", "language": "Язык",
               "back": "Назад", "your_score": "Ваш счет", "your_name": "Введите свое имя:"}
    }

current_language = "en"



pygame.init()

# Initialize mixer for sound
pygame.mixer.init()
menu_music = pygame.mixer.Sound('sounds/background_menu.mp3')
game_music = pygame.mixer.Sound('sounds/main.mp3')
collision_sound = pygame.mixer.Sound('sounds/collision.mp3')

menu_volume = 0.5
game_volume = 0.5
collision_volume = 0.5


st = Settings()
menu_music.set_volume(menu_volume)
game_music.set_volume(game_volume)
collision_sound.set_volume(collision_volume)


screen_size = (st.screen_width, st.screen_height)
screen = pygame.display.set_mode(screen_size)
pygame.display.set_caption('Car Game')

# Background image
background_image = pygame.image.load('images/background.jpg')

# Colors
gray = (100, 100, 100)
green = (76, 208, 56)
red = (200, 0, 0)
white = (255, 255, 255)
black = (0, 0, 0)
cornsilk4 = (139, 136, 120, 255)
navajowhite = (139, 121, 94, 255)
magenta3 = (139, 0, 139, 255)
steelblue1 = (79, 148, 205, 255)


lanes = [st.left_lane, st.center_lane, st.right_lane]

# player's starting coordinates
player_x = 250
player_y = st.screen_height - 120  # Positioned above the bottom edge

# frame settings
clock = pygame.time.Clock()
fps = 120


# system to calculate level based on score
def get_level(score):
    return (score // 5) + 1

# sprite groups
player_group = pygame.sprite.Group()
vehicle_group = pygame.sprite.Group()

# create the player's car
player = PlayerVehicle(player_x, player_y)
player_group.add(player)

# load the vehicle images
image_filenames = ['police_car.png', 'long_car.png', 'big_car.png', 'ambulance.png']
vehicle_images = []
for image_filename in image_filenames:
    image = pygame.image.load('images/' + image_filename)
    vehicle_images.append(image)

# load the crash image
crash = pygame.image.load('images/crash.png')
crash_rect = crash.get_rect()

class Menu:
    # Main menu screen with animation
    def main_menu(self):
        st = Settings()
        global menu_volume, menu_music
        running_menu = True
        # Play the background menu music
        menu_music.set_volume(menu_volume)
        if (menu_music.get_num_channels() < 1):
            menu_music.play(loops=-1)
        font = pygame.font.SysFont("Bookman Old Style", 36)
        button_texts = [languages[current_language]["start"], languages[current_language]["settings"],
                        languages[current_language]["developer"], languages[current_language]["exit"]]
        button_widths = [font.size(text)[0] + 40 for text in button_texts]  # Add padding
        max_button_width = max(button_widths)
        button_height = 50
        button_y_positions = [200, 275, 350, 425]

        while running_menu:
            screen.blit(background_image, (0, 0))

            font = pygame.font.SysFont("Bookman Old Style", 36)

            # Draw title
            draw_text("Racing v0.0.1", font, white, screen, st.screen_width / 2, st.screen_height / 4)

            # Draw buttons
            buttons = []
            for i, text in enumerate(button_texts):
                button_rect = pygame.Rect((st.screen_width - max_button_width) / 2, button_y_positions[i],
                                          max_button_width,
                                          button_height)
                pygame.draw.rect(screen, magenta3, button_rect, border_radius=15)  # Rounded corners
                draw_text(text, font, white, screen, st.screen_width / 2, button_y_positions[i] + button_height / 2)
                buttons.append((button_rect, text))

            for event in pygame.event.get():
                if event.type == QUIT:
                    running_menu = False
                    pygame.quit()
                    sys.exit()

                if event.type == MOUSEBUTTONDOWN:
                    for button_rect, text in buttons:
                        if button_rect.collidepoint(event.pos):
                            if text == languages[current_language]["start"]:
                                menu_music.stop()
                                return 'start'
                            elif text == languages[current_language]["settings"]:
                                return 'settings'
                            elif text == languages[current_language]["developer"]:
                                return 'developer'
                            elif text == languages[current_language]["exit"]:
                                running_menu = False
                                pygame.quit()
                                sys.exit()

            pygame.display.update()

    # Settings screen
    def settings_screen(self):
        st = Settings()
        global current_language, menu_volume, game_volume, collision_volume
        running_settings = True
        font = pygame.font.SysFont("Bookman Old Style", 24)
        settings_font = pygame.font.SysFont("Bookman Old Style", 42)
        buttons_font = pygame.font.SysFont("Bookman Old Style", 28)
        adjusting_slider = None

        while running_settings:
            screen.fill(cornsilk4)

            draw_text(languages[current_language]["settings"], settings_font, white, screen, st.screen_width / 2,
                      st.screen_height / 8)

            # Menu music volume slider
            pygame.draw.rect(screen, navajowhite, (100, 150, 300, 10))
            pygame.draw.rect(screen, white, (100 + int(menu_volume * 300), 135, 10, 40))
            draw_text(languages[current_language]["menu_music"], font, white, screen, 250, 185)

            # Game music volume slider
            pygame.draw.rect(screen, navajowhite, (100, 220, 300, 10))
            pygame.draw.rect(screen, white, (100 + int(game_volume * 300), 205, 10, 40))
            draw_text(languages[current_language]["game_music"], font, white, screen, 250, 255)

            # Collision sound volume slider
            pygame.draw.rect(screen, navajowhite, (100, 290, 300, 10))
            pygame.draw.rect(screen, white, (100 + int(collision_volume * 300), 275, 10, 40))
            draw_text(languages[current_language]["collision_sounds"], font, white, screen, 250, 325)

            # Language selection dropdown
            pygame.draw.rect(screen, navajowhite, (100, 380, 300, 40))
            draw_text(f"{languages[current_language]["language"]}: {current_language.upper()}", buttons_font, white,
                      screen, st.screen_width / 2, 400)

            # Back button
            back_button = pygame.draw.rect(screen, navajowhite, (150, 450, 200, 50))
            draw_text(languages[current_language]["back"], buttons_font, white, screen, st.screen_width / 2, 475)

            for event in pygame.event.get():
                if event.type == QUIT:
                    running_settings = False
                    pygame.quit()
                    sys.exit()

                if event.type == MOUSEBUTTONDOWN:
                    if 100 <= event.pos[0] <= 400:
                        if 140 <= event.pos[1] <= 180:
                            menu_volume = (event.pos[0] - 100) / 300
                            menu_music.set_volume(menu_volume)
                        elif 210 <= event.pos[1] <= 250:
                            game_volume = (event.pos[0] - 100) / 300
                            game_music.set_volume(game_volume)
                        elif 280 <= event.pos[1] <= 320:
                            collision_volume = (event.pos[0] - 100) / 300
                            collision_sound.set_volume(collision_volume)
                        elif 380 <= event.pos[1] <= 420:
                            # Switch language
                            if current_language == "en":
                                current_language = "ru"
                            else:
                                current_language = "en"
                    if back_button.collidepoint(event.pos):
                        return 'menu'

            pygame.display.update()

    # Developer screen
    def developer_screen(self):
        font = pygame.font.SysFont("Bookman Old Style", 24)
        button_font = pygame.font.SysFont("Bookman Old Style", 28)
        global current_language
        running_developer = True
        dev_image = pygame.image.load("images/dev_image.png")
        # Calculate center position for text
        text_lines = [
            "Информация о разработчике:",
            "",
            "Автор: Гиниятуллина Юлия Сергеевна,",
            "студентка ИВТ 3 курс, группа 2.2",
            "Этот проект создан в рамках дисциплин",
            '"Математические основы компьютерной',
            'графики" и "Системы и технологии',
            'подготовки технической и издательской',
            'документации"'
        ]

        line_height = 30

        while running_developer:
            screen.blit(dev_image, (0, 0))
            st = Settings()

            # Display title and info text
            for idx, line in enumerate(text_lines):
                draw_text(line, font, white, screen, st.screen_width / 2, st.screen_height / 4 + idx * line_height)

            # Back button
            back_button = pygame.draw.rect(screen, steelblue1, (150, 450, 200, 50))
            draw_text(languages[current_language]["back"], button_font, white, screen, st.screen_width / 2, 475)

            for event in pygame.event.get():
                if event.type == QUIT:
                    running_developer = False
                    pygame.quit()
                    sys.exit()

                if event.type == MOUSEBUTTONDOWN:
                    if back_button.collidepoint(event.pos):
                        return 'menu'

            pygame.display.update()

# Game loop
def game_loop():
    st = Settings()
    board = Scoreboard()
    lane_marker_move_y = st.lane_marker_move_y

    global score
    gameover = st.gameover
    speed = st.speed
    level = st.level

    player_group.empty()
    vehicle_group.empty()

    player = PlayerVehicle(player_x, player_y)
    player_group.add(player)

    game_music.set_volume(game_volume)
    game_music.play(loops=-1)

    running = True
    while running:
        clock.tick(fps)

        for event in pygame.event.get():
            if event.type == QUIT:
                running = False

            if event.type == KEYDOWN:
                if event.key == K_ESCAPE:  # Pause the game
                    game_music.stop()
                    return 'menu'

                if event.key == K_LEFT and player.rect.center[0] > st.left_lane:
                    player.rect.x -= 100
                elif event.key == K_RIGHT and player.rect.center[0] < st.right_lane:
                    player.rect.x += 100

            for vehicle in vehicle_group:
                if pygame.sprite.collide_rect(player, vehicle):
                    gameover = True
                    collision_sound.set_volume(collision_volume)
                    collision_sound.play()
                    crash_rect.center = player.rect.center


        # Draw the background
        screen.fill(green)

        # Draw HUD panel
        pygame.draw.rect(screen, black, (0, 0, st.screen_width, st.hud_height))  # Top HUD background
        font = pygame.font.SysFont("Bookman Old Style", 20)
        draw_text(f'{languages[current_language]["score"]}: {score}', font, white, screen, 70, 25)
        draw_text(f'{languages[current_language]["level"]}: {level}', font, white, screen, st.screen_width - 70, 25)

        # Draw the road
        pygame.draw.rect(screen, gray, st.road)
        pygame.draw.rect(screen, white, st.left_edge_marker)
        pygame.draw.rect(screen, white, st.right_edge_marker)

        # Animate lane markers
        lane_marker_move_y += speed * 1.5
        if lane_marker_move_y >= st.marker_height * 2:
            lane_marker_move_y = 0
        for y in range(st.marker_height * -2, st.screen_height, st.marker_height * 2):
            pygame.draw.rect(screen, white, (st.left_lane + 45, y + lane_marker_move_y, st.marker_width, st.marker_height))
            pygame.draw.rect(screen, white, (st.center_lane + 45, y + lane_marker_move_y, st.marker_width, st.marker_height))

        # Draw player and vehicles
        player_group.draw(screen)

        if len(vehicle_group) < 2:
            add_vehicle = True
            for vehicle in vehicle_group:
                if vehicle.rect.top < vehicle.rect.height * 1.5:
                    add_vehicle = False

            if add_vehicle:
                lane = random.choice(lanes)
                image = random.choice(vehicle_images)
                vehicle = Vehicle(image, lane, st.hud_height - 50)
                vehicle_group.add(vehicle)

        for vehicle in vehicle_group:
            vehicle.rect.y += speed
            if vehicle.rect.top >= st.screen_height:
                vehicle.kill()
                score += 1
                if score % 5 == 0 and speed < 10:
                    speed += 0.5

        vehicle_group.draw(screen)

        # Update level
        level = get_level(score)

        # Head collision
        if pygame.sprite.spritecollide(player, vehicle_group, True):
            gameover = True
            collision_sound.set_volume(collision_volume)
            collision_sound.play()
            crash_rect.center = player.rect.center

        # Display crash image on collision
        if gameover:
            game_music.stop()
            screen.blit(crash, crash_rect)
            pygame.draw.rect(screen, red, (0, 50, st.screen_width, 100))
            draw_text(languages[current_language]["game_over"], font, white, screen, st.screen_width / 2, 100)
            pygame.display.update()

            while gameover:
                for event in pygame.event.get():
                    if event.type == QUIT:
                        running = False
                        gameover = False
                    if event.type == KEYDOWN:
                        name = board.get_player_name()
                        if name:
                            board.update_scoreboard(name, score)
                        return 'menu'

        pygame.display.update()

    game_music.stop()

# Start the game
while True:
    menu = Menu()
    result = menu.main_menu()

    if result == 'start':
        result = game_loop()
        if result == 'menu':
            continue
    elif result == 'settings':
        menu.settings_screen()
    elif result == 'developer':
        menu.developer_screen()
    else:
        break