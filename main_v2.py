import pygame
import pygame_gui
import socket

CURRENT_LOGIN = ''
CURRENT_MANAGER = None
WINS = 0
LOSE = 0
REG_DATE = 0
WIN_OR_LOSE = ''


class Connect_to_server:
    def __init__(self):
        self.server_ip = '192.168.43.131'
        self.server_port = 5002
        self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            self.client_socket.connect((self.server_ip, self.server_port))
            print('Success connect!')
        except Exception:
            print('Bad connect!')

    def recv_data(self):
        global CURRENT_LOGIN, CURRENT_MANAGER, WINS, LOSE, REG_DATE, Play, WIN_OR_LOSE, count
        data = self.client_socket.recv(4092)
        if data:
            data_key = data.decode().split()[0]  # key служит для распределения пакетов
            data_text = data.decode().split()[1:]  # информация, которая зависит от ключа
            if data_key == 'coords':  # координаты врага и шайбы для получения синхронного изображения
                new_enemy_coord, new_shaiba_coord, blue_count, red_count = data_text[:2], data_text[2:4], \
                                                                           data_text[-2], data_text[-1]
                enemy_sprite.update(new_enemy_coord)
                for sprite in shaiba_sprite:
                    sprite.new_coords(new_shaiba_coord)
                Count.update_count(blue_count, red_count)
                if int(blue_count) == 7:  # если один из счетчиков достигает 7, то на сервет отправляется событие остановки
                    self.client_socket.send('stop WIN'.encode())
                elif int(red_count) == 7:
                    self.client_socket.send('stop LOSE'.encode())
            elif data_key == 'end':  # клиент получает этот пакет в ответ на пустой запрос,
                # который отправляется серверу, после получения результатов от сервера
                self.client_socket.send(
                    f'game_log {CURRENT_LOGIN} {data_text[0]} {A_result_label.text.split()[1][:-1]}'.encode())
            elif data_key == 'stop':  # ответ от сервера на конец игры, нужно для синхронной остановки игры на обоих клиентах
                if data_text[0][:3] == 'WIN':
                    count = 0
                    Play = False  # прекражение цикла игры
                    A_result_label.set_text('You LOSE!')
                    CURRENT_MANAGER = after_game_manager
                elif data_text[0][:4] == 'LOSE':
                    count = 0
                    Play = False
                    A_result_label.set_text('You WIN!')
                    CURRENT_MANAGER = after_game_manager
                self.client_socket.send('add_log'.encode())
                Server.recv_data()

            elif data_key == 'Error':
                C_status_error.show()

            elif data_key == 'auth':  # отправка данных для попытки авторизации
                if data_text[0] == B_login_enter.get_text():
                    B_status_error.hide()
                    CURRENT_LOGIN = data_text[0]
                    REG_DATE = data_text[-3]
                    WINS = data_text[-2]
                    LOSE = data_text[-1]
                    P_reg_date.set_text(f'Дата регистрации: {REG_DATE}')
                    P_statistics_lose.set_text(f'Поражения: {LOSE}')
                    P_statistics_win.set_text(f'Победы: {WINS}')
                    P_login_label.set_text(f'Имя пользователя: {CURRENT_LOGIN}')
                    CURRENT_MANAGER = menu_manager
                else:
                    B_status_error.show()

            elif data_key == 'create':  # создание нового аккаунта
                if len(data_text) == 1:
                    C_status_succes.show()
                    C_status_passwords.hide()
                else:
                    C_status_error.show()
            elif data_key == 'rl':  # получение ответа от сервера на валидность логина
                if data_text[0] != 'Error':
                    R_secret_question_label.set_text(' '.join(data_text))
                    R_login_enter.disable()
                    R_login_button.disable()
                    R_secret_question_label.show()
                    R_secret_answer_label.show()
                    R_secret_answer_enter.show()
                    R_secret_answer_button.show()
                    R_status_login.hide()
                    R_status_password.hide()
                    R_status_answer.hide()
                else:
                    R_status_login.show()

            elif data_key == 'ra':  # получение ответа от сервера на правильность ответа на секретный вопрос
                if data_text[0] == 'True':
                    R_password_label.show()
                    R_password_enter.show()
                    R_repeat_password_label.show()
                    R_repeat_password_enter.show()
                    R_passwords_button.show()
                    R_status_answer.hide()
                else:
                    R_status_answer.show()
                    R_secret_answer_enter.clear()

            elif data_key == 'rp':
                R_status_password_replace.show()
                R_login_enter.enable()
                R_login_button.enable()
                R_secret_question_label.hide()
                R_secret_answer_enter.clear()
                R_secret_answer_enter.hide()
                R_secret_answer_label.hide()
                R_secret_answer_button.hide()
                R_password_label.hide()
                R_password_enter.clear()
                R_password_enter.hide()
                R_repeat_password_label.hide()
                R_repeat_password_enter.clear()
                R_repeat_password_enter.hide()
                R_passwords_button.hide()
            elif data_key == 'info':  # информация для профиля
                REG_DATE = data_text[0]
                WINS = data_text[1]
                LOSE = data_text[2]
                P_reg_date.set_text(f'Дата регистрации: {REG_DATE}')
                P_statistics_lose.set_text(f'Поражения: {LOSE}')
                P_statistics_win.set_text(f'Победы: {WINS}')

    def send_data(self, ex, ey, sx, sy):  # отправка координат
        ex1, ey1, sx1, sy1 = width - (ex + 45), height - (ey + 45), width - (sx + 33), height - (sy + 33)
        data = f'{ex1} {ey1} {sx1} {sy1}'.encode()
        self.client_socket.send(data)

    def send_gol(self, gol=True):
        if gol:
            self.client_socket.send('gol'.encode())
        else:
            self.client_socket.send('autogol'.encode())

    def send_sql(self, text: str):
        self.client_socket.send(text.encode())

    def send_get_info(self):
        self.client_socket.send(f'get_info {CURRENT_LOGIN}'.encode())


class Borders_wall(pygame.sprite.Sprite):
    def __init__(self, x1, y1, x2, y2):
        super().__init__()
        if x1 == x2 - 5:  # вертикальная стенка
            self.add(wall_sprites_ver)
            self.image = pygame.Surface((5, y2 - y1))
            pygame.draw.rect(self.image, 'red', (0, 0, 5, y2 - y1))
            self.rect = pygame.Rect(x1, y1, 5, y2 - y1)
        else:  # горизонтальная стенка
            self.add(wall_sprites_hor)
            self.image = pygame.Surface((200, 5))
            pygame.draw.rect(self.image, 'red', (0, 0, x2, y2))
            self.rect = pygame.Rect(x1, y1, 200, 5)
        self.mask = pygame.mask.from_surface(self.image)


class Line(pygame.sprite.Sprite):
    def __init__(self):
        super(Line, self).__init__(line_sprite)
        self.add(line_sprite)
        self.image = pygame.Surface((500, 5))
        pygame.draw.rect(self.image, 'green', (0, 0, 500, 5))
        self.rect = pygame.Rect(5, 305, 500, 5)
        self.mask = pygame.mask.from_surface(self.image)
        self.mask = pygame.mask.from_surface(self.image)


class Player(pygame.sprite.Sprite):
    player_image = pygame.image.load('data/bluepad.png')

    def __init__(self):
        super(Player, self).__init__(player_sprites)
        self.add(player_sprites)
        self.image = Player.player_image
        self.rect = self.image.get_rect()
        self.rect.x = width // 2
        self.rect.y = 400
        self.mask = pygame.mask.from_surface(self.image)

    def update(self, keys):
        left_flag, right_flag, up_flag, down_flag = True, True, True, True
        if any([pygame.sprite.collide_mask(self, border) for border in wall_sprites_ver]):
            if self.rect.x <= 5:
                left_flag = False
            else:
                right_flag = False
        if any([pygame.sprite.collide_mask(self, border) for border in wall_sprites_hor]):
            if self.rect.y <= 0:
                up_flag = False
            elif self.rect.y >= 550:
                down_flag = False
        if any([pygame.sprite.collide_mask(self, line) for line in line_sprite]):
            if self.rect.y <= 300:
                up_flag = False
        if any([pygame.sprite.collide_mask(self, gate) for gate in gate_sprite_blue]):
            down_flag = False
        if keys[pygame.K_UP] and up_flag:
            self.rect.y -= 5
        if keys[pygame.K_DOWN] and down_flag:
            self.rect.y += 5
        if keys[pygame.K_LEFT] and left_flag:
            self.rect.x -= 5
        if keys[pygame.K_RIGHT] and right_flag:
            self.rect.x += 5
        left_flag, right_flag, up_flag, down_flag = True, True, True, True


class Enemy(pygame.sprite.Sprite):
    enemy_image = pygame.image.load('data/redpad.png')

    def __init__(self):
        super(Enemy, self).__init__(enemy_sprite)
        self.add(enemy_sprite)
        self.image = Enemy.enemy_image
        self.rect = self.image.get_rect()
        self.rect.x = width // 2
        self.rect.y = 200
        self.mask = pygame.mask.from_surface(self.image)

    def update(self, new_enemy_coords):
        self.rect.x = int(new_enemy_coords[0])
        self.rect.y = int(new_enemy_coords[1])


class Gate(pygame.sprite.Sprite):
    def __init__(self, x, y, num):
        super(Gate, self).__init__()
        if num == 1:
            self.add(gate_sprite_red)
        else:
            self.add(gate_sprite_blue)
        self.image = pygame.Surface((105, 5))
        pygame.draw.rect(self.image, 'violet', (0, 0, 105, 5))
        self.rect = pygame.Rect(x - 5, y, 105, 5)
        self.mask = pygame.mask.from_surface(self.image)


class Shaiba(pygame.sprite.Sprite):
    shaiba_image = pygame.image.load('data/disc.png')

    def __init__(self):
        super(Shaiba, self).__init__()
        self.add(shaiba_sprite)
        self.image = Shaiba.shaiba_image
        self.rect = self.image.get_rect()
        self.rect.x = 255 - self.image.get_rect()[2] // 2
        self.rect.y = 307 - self.image.get_rect()[2] // 2
        self.mask = pygame.mask.from_surface(self.image)
        self.vx = 0
        self.vy = 0
        self.count = 0

    def gol(self):
        self.rect.x = 255 - self.image.get_rect()[2] // 2
        self.rect.y = 307 - self.image.get_rect()[2] // 2
        self.count = 0
        self.vx = 0
        self.vy = 0

    def update(self):
        for player in player_sprites:
            if pygame.sprite.collide_mask(self, player):
                self.vx = 2
                self.vy = 2
                self.count = 1
                if self.rect.x < player.rect.x and self.rect.y < player.rect.y:
                    self.vx *= -1
                    self.vy *= -1
                if self.rect.x > player.rect.x and self.rect.y < player.rect.y:
                    self.vx *= 1
                    self.vy *= -1
        for enemy in enemy_sprite:
            if pygame.sprite.collide_mask(self, enemy):
                self.vx = 2
                self.vy = 2
                self.count = 1
                if self.rect.x < enemy.rect.x and self.rect.y < enemy.rect.y:
                    self.vx *= -1
                    self.vy *= -1
                if self.rect.x > enemy.rect.x and self.rect.y < enemy.rect.y:
                    self.vx *= 1
                    self.vy *= -1
        if pygame.sprite.spritecollideany(self, wall_sprites_hor):
            self.vy = -self.vy
            self.count = 0
        if pygame.sprite.spritecollideany(self, wall_sprites_ver):
            self.vx = -self.vx
            self.count = 0
        self.rect = self.rect.move(self.vx, self.vy)
        if pygame.sprite.spritecollideany(self, gate_sprite_red):
            Server.send_gol(True)
            self.gol()
        if pygame.sprite.spritecollideany(self, gate_sprite_blue):
            Server.send_gol(False)
            self.gol()

    def new_coords(self, new_shaiba_coords):
        self.rect.x = int(new_shaiba_coords[0])
        self.rect.y = int(new_shaiba_coords[1])


class Counter:
    def __init__(self):
        self.count_blue = 0
        self.count_red = 0

    def update_count(self, blue_count, red_count):
        self.count_blue = red_count
        self.count_red = blue_count

    def show_count(self, screen):
        font = pygame.font.Font(None, 50)
        text1 = font.render(f"{self.count_red}", True, 'blue')
        text_x1 = 5
        text_y1 = 5
        screen.blit(text1, (text_x1, text_y1))

        text2 = font.render(f"{self.count_blue}", True, 'blue')
        text_x2 = 5
        text_y2 = 610 - text2.get_height()
        screen.blit(text2, (text_x2, text_y2))


class Background:
    wallpapers = [pygame.image.load('data/wallpaper1.jpg'),
                  pygame.image.load('data/wallpaper2.jpg'),
                  pygame.image.load('data/wallpaper3.jpg'),
                  pygame.image.load('data/wallpaper4.jpg'),
                  pygame.image.load('data/wallpaper5.jpg')]

    def __init__(self, width, height):
        self.count = 0
        self.image = Background.wallpapers[self.count]
        self.rect = (width, height)

    def change_wallpaper(self):
        if self.count < 4:
            self.count += 1
        else:
            self.count = 0
        self.image = Background.wallpapers[self.count]


if __name__ == '__main__':
    Server = Connect_to_server()  # соединение с сервером

    Count = Counter()  # инициализация счетчика

    pygame.init()
    pygame.display.set_caption('Аэрохоккей')
    size = width, height = 510, 615
    screen = pygame.display.set_mode(size)

    wall_sprites_ver = pygame.sprite.Group()
    wall_sprites_hor = pygame.sprite.Group()
    line_sprite = pygame.sprite.Group()
    shaiba_sprite = pygame.sprite.Group()
    player_sprites = pygame.sprite.Group()
    enemy_sprite = pygame.sprite.Group()
    gate_sprite_blue = pygame.sprite.Group()
    gate_sprite_red = pygame.sprite.Group()

    Borders_wall(0, 0, 5, 615)  # вертикальные стенки
    Borders_wall(505, 0, 510, 615)
    Borders_wall(0, 0, 205, 5)  # горизонтальные стенки
    Borders_wall(305, 0, 510, 5)
    Borders_wall(0, 610, 205, 615)
    Borders_wall(305, 610, 510, 615)
    Gate(205, 0, 1)  # спрайты ворот
    Gate(205, 610, 2)
    Line()  # спрайт линии раздела поля
    Player()  # спрайт игрока
    Enemy()  # спрайт соперника
    Shaiba()  # спрайт шайбы

    background = Background(510, 615)

    clock = pygame.time.Clock()
    count = 0
    running = True
    Play = False

    ############################################################################################################
    # стартовое окно
    begin_manager = pygame_gui.UIManager((510, 615), 'theme.json')

    B_authorization_button = pygame_gui.elements.UIButton(relative_rect=pygame.Rect(350, 45, 150, 50),
                                                          text='Войти',
                                                          manager=begin_manager)
    B_forgot_pass_button = pygame_gui.elements.UIButton(relative_rect=pygame.Rect(15, 150, 150, 50),
                                                        text='Забыли пароль',
                                                        manager=begin_manager)
    B_create_new_account_button = pygame_gui.elements.UIButton(relative_rect=pygame.Rect(180, 150, 150, 50),
                                                               text='Новый аккаунт',
                                                               manager=begin_manager)
    B_login_enter = pygame_gui.elements.UITextEntryLine(relative_rect=pygame.Rect(180, 10, 150, 50),
                                                        manager=begin_manager)
    B_pass_enter = pygame_gui.elements.UITextEntryLine(relative_rect=pygame.Rect(180, 80, 150, 50),
                                                       manager=begin_manager)
    B_login_label = pygame_gui.elements.UILabel(relative_rect=pygame.Rect(15, 10, 150, 50),
                                                text='Введите логин:',
                                                manager=begin_manager)
    B_pass_label = pygame_gui.elements.UILabel(relative_rect=pygame.Rect(15, 80, 150, 50),
                                               text='Введите пароль:',
                                               manager=begin_manager)
    B_status_error = pygame_gui.elements.UILabel(relative_rect=pygame.Rect(180, 560, 150, 50),
                                                 text='Ошибка',
                                                 manager=begin_manager)
    B_status_error.hide()

    ############################################################################################################
    # окно после игры
    after_game_manager = pygame_gui.UIManager((510, 615), 'theme.json')
    A_result_label = pygame_gui.elements.UILabel(relative_rect=pygame.Rect(180, 100, 150, 50),
                                                 text=f'YOU {WIN_OR_LOSE}!',
                                                 manager=after_game_manager)
    A_return_menu_button = pygame_gui.elements.UIButton(relative_rect=pygame.Rect(180, 300, 200, 50),
                                                        text='Вернуться в меню',
                                                        manager=after_game_manager)

    ############################################################################################################
    # восстановление пароля
    rescue_manager = pygame_gui.UIManager((510, 615), 'theme.json')

    R_login_label = pygame_gui.elements.UILabel(relative_rect=pygame.Rect(15, 10, 150, 50),
                                                text='Введите логин:',
                                                manager=rescue_manager)
    R_login_enter = pygame_gui.elements.UITextEntryLine(relative_rect=pygame.Rect(180, 10, 150, 50),
                                                        manager=rescue_manager)
    R_login_button = pygame_gui.elements.UIButton(relative_rect=pygame.Rect(345, 10, 100, 50),
                                                  text='Отправить',
                                                  manager=rescue_manager)
    R_secret_question_label = pygame_gui.elements.UILabel(relative_rect=pygame.Rect(15, 80, 395, 50),
                                                          text='',
                                                          manager=rescue_manager)
    R_secret_question_label.hide()

    R_secret_answer_label = pygame_gui.elements.UILabel(relative_rect=pygame.Rect(15, 150, 150, 50),
                                                        text='Секретный ответ:',
                                                        manager=rescue_manager)
    R_secret_answer_enter = pygame_gui.elements.UITextEntryLine(relative_rect=pygame.Rect(180, 150, 150, 50),
                                                                manager=rescue_manager)
    R_secret_answer_button = pygame_gui.elements.UIButton(relative_rect=pygame.Rect(345, 150, 100, 50),
                                                          text='Отправить',
                                                          manager=rescue_manager)
    R_secret_answer_label.hide()
    R_secret_answer_enter.hide()
    R_secret_answer_button.hide()

    R_password_label = pygame_gui.elements.UILabel(relative_rect=pygame.Rect(15, 220, 150, 50),
                                                   text='Введите пароль:',
                                                   manager=rescue_manager)
    R_password_enter = pygame_gui.elements.UITextEntryLine(relative_rect=pygame.Rect(180, 220, 150, 50),
                                                           manager=rescue_manager)
    R_password_label.hide()
    R_password_enter.hide()

    R_repeat_password_label = pygame_gui.elements.UILabel(relative_rect=pygame.Rect(15, 290, 150, 50),
                                                          text='Повторите пароль:',
                                                          manager=rescue_manager)
    R_repeat_password_enter = pygame_gui.elements.UITextEntryLine(relative_rect=pygame.Rect(180, 290, 150, 50),
                                                                  manager=rescue_manager)

    R_repeat_password_label.hide()
    R_repeat_password_enter.hide()

    R_passwords_button = pygame_gui.elements.UIButton(relative_rect=pygame.Rect(345, 255, 100, 50),
                                                      text='Отправить',
                                                      manager=rescue_manager)
    R_passwords_button.hide()

    R_return_begin_manager_button = pygame_gui.elements.UIButton(relative_rect=pygame.Rect(15, 360, 150, 50),
                                                                 text='Вернуться',
                                                                 manager=rescue_manager)
    R_status_login = pygame_gui.elements.UILabel(relative_rect=pygame.Rect(180, 560, 300, 50),
                                                 text='Неверный логин',
                                                 manager=rescue_manager)
    R_status_answer = pygame_gui.elements.UILabel(relative_rect=pygame.Rect(180, 560, 300, 50),
                                                  text='Неверный ответ',
                                                  manager=rescue_manager)
    R_status_password = pygame_gui.elements.UILabel(relative_rect=pygame.Rect(180, 560, 300, 50),
                                                    text='Некорректное заполнение',
                                                    manager=rescue_manager)
    R_status_password_replace = pygame_gui.elements.UILabel(relative_rect=pygame.Rect(180, 560, 300, 50),
                                                            text='Успешная смена пароля',
                                                            manager=rescue_manager)
    R_status_password.hide()
    R_status_login.hide()
    R_status_answer.hide()
    R_status_password_replace.hide()

    ############################################################################################################
    # регистрация аккаунта
    create_account_manager = pygame_gui.UIManager((510, 615), 'theme.json')

    C_login_label = pygame_gui.elements.UILabel(relative_rect=pygame.Rect(15, 10, 150, 50),
                                                text='Введите логин:',
                                                manager=create_account_manager)
    C_login_enter = pygame_gui.elements.UITextEntryLine(relative_rect=pygame.Rect(180, 10, 150, 50),
                                                        manager=create_account_manager)
    C_password_label = pygame_gui.elements.UILabel(relative_rect=pygame.Rect(15, 80, 150, 50),
                                                   text='Введите пароль:',
                                                   manager=create_account_manager)
    C_password_enter = pygame_gui.elements.UITextEntryLine(relative_rect=pygame.Rect(180, 80, 150, 50),
                                                           manager=create_account_manager)
    C_repeat_password_label = pygame_gui.elements.UILabel(relative_rect=pygame.Rect(15, 150, 150, 50),
                                                          text='Повторите пароль:',
                                                          manager=create_account_manager)
    C_repeat_password_enter = pygame_gui.elements.UITextEntryLine(relative_rect=pygame.Rect(180, 150, 150, 50),
                                                                  manager=create_account_manager)
    C_secret_question_label = pygame_gui.elements.UILabel(relative_rect=pygame.Rect(15, 220, 150, 50),
                                                          text='Секретный вопрос:',
                                                          manager=create_account_manager)
    C_secret_question_enter = pygame_gui.elements.UITextEntryLine(relative_rect=pygame.Rect(180, 220, 150, 50),
                                                                  manager=create_account_manager)
    C_secret_answer_label = pygame_gui.elements.UILabel(relative_rect=pygame.Rect(15, 290, 150, 50),
                                                        text='Секретный ответ:',
                                                        manager=create_account_manager)
    C_secret_answer_enter = pygame_gui.elements.UITextEntryLine(relative_rect=pygame.Rect(180, 290, 150, 50),
                                                                manager=create_account_manager)
    C_return_begin_manager_button = pygame_gui.elements.UIButton(relative_rect=pygame.Rect(15, 360, 150, 50),
                                                                 text='Вернуться',
                                                                 manager=create_account_manager)
    C_reg_account_button = pygame_gui.elements.UIButton(relative_rect=pygame.Rect(180, 360, 150, 50),
                                                        text='Зарегистрировать',
                                                        manager=create_account_manager)
    C_status_passwords = pygame_gui.elements.UILabel(relative_rect=pygame.Rect(180, 560, 150, 50),
                                                     text='Некорректный ввод',
                                                     manager=create_account_manager)
    C_status_succes = pygame_gui.elements.UILabel(relative_rect=pygame.Rect(180, 560, 150, 50),
                                                  text='Успешно',
                                                  manager=create_account_manager)
    C_status_error = pygame_gui.elements.UILabel(relative_rect=pygame.Rect(180, 560, 150, 50),
                                                 text='Ошибка',
                                                 manager=create_account_manager)
    C_status_succes.hide()
    C_status_passwords.hide()
    C_status_error.hide()
    ############################################################################################################
    # меню
    menu_manager = pygame_gui.UIManager((510, 615), 'theme.json')

    M_start_game_button = pygame_gui.elements.UIButton(relative_rect=pygame.Rect(180, 200, 150, 50),
                                                       text='Начать игру',
                                                       manager=menu_manager)
    M_profile_button = pygame_gui.elements.UIButton(relative_rect=pygame.Rect(180, 270, 150, 50),
                                                    text='Профиль',
                                                    manager=menu_manager)
    M_settings_button = pygame_gui.elements.UIButton(relative_rect=pygame.Rect(180, 340, 150, 50),
                                                     text='Настройки',
                                                     manager=menu_manager)
    M_exit_button = pygame_gui.elements.UIButton(relative_rect=pygame.Rect(180, 410, 150, 50),
                                                 text='Выход',
                                                 manager=menu_manager)
    ############################################################################################################
    # профиль
    profile_manager = pygame_gui.UIManager((510, 615), 'theme.json')

    P_login_label = pygame_gui.elements.UILabel(relative_rect=pygame.Rect(155, 100, 200, 50),
                                                text=f'Имя игрока - {CURRENT_LOGIN}',
                                                manager=profile_manager)
    P_statistics_win = pygame_gui.elements.UILabel(relative_rect=pygame.Rect(10, 250, 150, 50),
                                                   text=f'Побед: {WINS} {CURRENT_LOGIN}',
                                                   manager=profile_manager)
    P_statistics_lose = pygame_gui.elements.UILabel(relative_rect=pygame.Rect(10, 320, 150, 50),
                                                    text=f'Поражений: {LOSE}',
                                                    manager=profile_manager)
    P_reg_date = pygame_gui.elements.UILabel(relative_rect=pygame.Rect(10, 390, 300, 50),
                                             text=f'Дата регистрации {REG_DATE}',
                                             manager=profile_manager)
    P_return_menu_button = pygame_gui.elements.UIButton(relative_rect=pygame.Rect(10, 460, 200, 50),
                                                        text='Вернуться в меню',
                                                        manager=profile_manager)
    ############################################################################################################
    # настройки
    settings_manager = pygame_gui.UIManager((510, 615), 'theme.json')
    S_change_wallpaper = pygame_gui.elements.UIButton(relative_rect=pygame.Rect(155, 247, 200, 50),
                                                      text='Сменить обои',
                                                      manager=settings_manager)
    S_return_menu = pygame_gui.elements.UIButton(relative_rect=pygame.Rect(155, 317, 200, 50),
                                                 text='Вернуться в меню',
                                                 manager=settings_manager)
    ############################################################################################################
    CURRENT_MANAGER = begin_manager

    while running:
        time_delta = clock.tick(60) / 1000
        if count != 0:
            Server.recv_data()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                conformation_dialog_exit = pygame_gui.windows.UIConfirmationDialog(rect=pygame.Rect(130, 207, 250, 200),
                                                                                   manager=CURRENT_MANAGER,
                                                                                   window_title='Подтверждение выхода',
                                                                                   action_long_desc='Вы уверены, что хотите выйти?',
                                                                                   action_short_name='OK',
                                                                                   blocking=True)
            if event.type == pygame_gui.UI_CONFIRMATION_DIALOG_CONFIRMED:
                if event.ui_element == conformation_dialog_exit:
                    running = False
            if event.type == pygame_gui.UI_BUTTON_PRESSED:
                if event.ui_element == B_authorization_button:
                    if not B_login_enter.get_text() or not B_pass_enter.get_text():
                        B_status_error.show()
                    else:
                        Server.send_sql(f'auth {B_login_enter.get_text()} {B_pass_enter.get_text()}')
                        Server.recv_data()
                elif event.ui_element == B_create_new_account_button:
                    CURRENT_MANAGER = create_account_manager
                elif event.ui_element == B_forgot_pass_button:
                    CURRENT_MANAGER = rescue_manager
                elif event.ui_element == C_return_begin_manager_button:
                    CURRENT_MANAGER = begin_manager
                    C_status_error.hide()
                    C_status_passwords.hide()
                    C_status_succes.hide()
                    C_login_enter.clear()
                    C_password_enter.clear()
                    C_repeat_password_enter.clear()
                    C_secret_answer_enter.clear()
                    C_secret_question_enter.clear()
                elif event.ui_element == C_reg_account_button:
                    C_status_succes.hide()
                    C_status_passwords.hide()
                    C_status_error.hide()
                    if C_password_enter.get_text() == C_repeat_password_enter.get_text():
                        Server.send_sql(
                            f'create {C_login_enter.get_text()} {C_password_enter.get_text()} '
                            f'{C_secret_question_enter.get_text()} {C_secret_answer_enter.get_text()}')
                        Server.recv_data()
                    else:
                        C_status_passwords.show()
                elif event.ui_element == R_login_button:
                    Server.send_sql(f'rl {R_login_enter.get_text()}')
                    Server.recv_data()
                elif event.ui_element == R_secret_answer_button:
                    if len(R_secret_answer_enter.get_text()) != 0:
                        Server.send_sql(f'ra {R_login_enter.get_text()} {R_secret_answer_enter.get_text()}')
                        Server.recv_data()
                elif event.ui_element == R_passwords_button:
                    R_status_password.hide()
                    if R_password_enter.get_text() == R_repeat_password_enter.get_text() and len(
                            R_password_enter.get_text()) != 0:
                        Server.send_sql(f'rp {R_login_enter.get_text()} {R_password_enter.get_text()}')
                        Server.recv_data()
                    else:
                        R_status_password.show()
                elif event.ui_element == R_return_begin_manager_button:
                    CURRENT_MANAGER = begin_manager
                    R_status_password_replace.hide()
                    R_status_password.hide()
                    R_status_answer.hide()
                    R_status_login.hide()
                    R_login_enter.enable()
                    R_login_enter.clear()
                    R_login_button.enable()
                    R_secret_question_label.hide()
                    R_secret_answer_enter.clear()
                    R_secret_answer_enter.hide()
                    R_secret_answer_label.hide()
                    R_secret_answer_button.hide()
                    R_password_label.hide()
                    R_password_enter.clear()
                    R_password_enter.hide()
                    R_repeat_password_label.hide()
                    R_repeat_password_enter.clear()
                    R_repeat_password_enter.hide()
                    R_passwords_button.hide()
                elif event.ui_element == R_secret_answer_button:
                    Server.send_sql(f'ra {R_secret_answer_enter.get_text()}')
                    Server.recv_data()
                elif event.ui_element == R_passwords_button:
                    Server.send_sql(f'rp {R_password_enter.get_text()} {R_repeat_password_enter.get_text()}')
                    Server.recv_data()
                elif event.ui_element == M_exit_button:
                    CURRENT_MANAGER = begin_manager
                    Server.send_sql(f'exit {CURRENT_LOGIN} exit')
                elif event.ui_element == M_profile_button:
                    CURRENT_MANAGER = profile_manager
                    Server.send_get_info()
                    Server.recv_data()
                elif event.ui_element == M_settings_button:
                    CURRENT_MANAGER = settings_manager
                elif event.ui_element == S_return_menu:
                    CURRENT_MANAGER = menu_manager
                elif event.ui_element == S_change_wallpaper:
                    background.change_wallpaper()
                elif event.ui_element == P_return_menu_button:
                    CURRENT_MANAGER = menu_manager
                elif event.ui_element == A_return_menu_button:
                    CURRENT_MANAGER = menu_manager
                elif event.ui_element == M_start_game_button:
                    Play = True

            CURRENT_MANAGER.process_events(event)
        CURRENT_MANAGER.update(time_delta)

        if Play:
            keys = pygame.key.get_pressed()
            player_sprites.update(keys)
            pygame.mouse.set_visible(False)
            screen.fill('yellow')
            pygame.draw.circle(screen, 'green', (255, 307), 50, 5)
            wall_sprites_hor.draw(screen)
            wall_sprites_ver.draw(screen)
            line_sprite.draw(screen)
            player_sprites.draw(screen)
            shaiba_sprite.update()
            shaiba_sprite.draw(screen)
            for shaiba in shaiba_sprite:
                for enemy in player_sprites:
                    Server.send_data(enemy.rect.x, enemy.rect.y, shaiba.rect.x, shaiba.rect.y)
            enemy_sprite.draw(screen)
            Count.show_count(screen)
            gate_sprite_blue.draw(screen)
            gate_sprite_red.draw(screen)
            count += 1
            if not Play:
                CURRENT_MANAGER = after_game_manager
        else:
            pygame.mouse.set_visible(True)
            screen.blit(background.image, (0, 0))
            CURRENT_MANAGER.draw_ui(screen)
        pygame.display.flip()
        clock.tick(60)
