from settings import *
import pygame as pg
import pygame.freetype as ft
import sys


class SpriteUnit(pg.sprite.Sprite):
    def __init__(self, handler, x, y):
        self.handler = handler
        self.x, self.y = x, y
        super().__init__(handler.group)
        self.image_ind = randrange(len(handler.images))
        self.image = handler.images[self.image_ind]
        self.rect = self.image.get_rect()
        self.vel_x, self.vel_y = self.get_vel(), self.get_vel()
        self.angle = 0
        self.rot_vel = self.get_vel()

    def rotate(self):
        self.angle += self.rot_vel * self.handler.app.dt
        self.image = self.handler.rot_cache[self.image_ind][
            int(NUM_ANGLES * (self.angle % 360) / 360)]
        self.rect = self.image.get_rect()

    def translate(self):
        self.x += self.vel_x * self.handler.app.dt
        self.y += self.vel_y * self.handler.app.dt
        if self.x < 0 or self.x > WIN_W:
            self.vel_x *= -1
        if self.y < 0 or self.y > WIN_H:
            self.vel_y *= -1

    def get_vel(self):
        return randrange(-SPEED, SPEED)

    def update(self):
        self.translate()
        self.rotate()
        self.rect.center = self.x, self.y


class SpriteHandler:
    def __init__(self, app):
        self.app = app
        self.images = self.load_images()
        self.rot_cache = self.get_rot_cache()
        self.group = pg.sprite.Group()
        self.sprites = [SpriteUnit(self, WIN_W // 2, WIN_H // 2)]

    def get_rot_cache(self):
        rot_cache = {}
        for i, image in enumerate(self.images):
            rot_cache[i] = []
            for angle in range(NUM_ANGLES):
                rot_img = pg.transform.rotate(image, angle * 360 / NUM_ANGLES)
                rot_cache[i].append(rot_img)
        return rot_cache

    def on_mouse_press(self):
        mouse_button = pg.mouse.get_pressed()
        if mouse_button[0]:
            x, y = pg.mouse.get_pos()
            self.add_sprite(x, y)
        elif mouse_button[2]:
            self.del_sprite()

    def add_sprite(self, x, y):
        for i in range(NUM_SPRITES_PER_CLICK):
            self.sprites.append(SpriteUnit(self, x, y))

    def del_sprite(self):
        for i in range(NUM_SPRITES_PER_CLICK):
            if len(self.sprites):
                sprite = self.sprites.pop()
                sprite.kill()

    def load_images(self):
        paths = [item for item in pathlib.Path(SPRITE_DIR_PATH).rglob('*.png') if item.is_file()]
        return [pg.image.load(str(path)).convert_alpha() for path in paths]

    def update(self):
        self.group.update()

    def draw(self):
        self.group.draw(self.app.screen)


class App:
    def __init__(self):
        pg.init()
        self.screen = pg.display.set_mode(WIN_SIZE)
        self.clock = pg.time.Clock()
        self.font = ft.SysFont('Verdana', FONT_SIZE)
        self.dt = 0.0
        self.sprite_handler = SpriteHandler(self)

    def update(self):
        pg.display.flip()
        self.sprite_handler.update()
        self.dt = self.clock.tick() * 0.001

    def draw(self):
        self.screen.fill('black')
        self.sprite_handler.draw()
        self.draw_fps()

    def draw_fps(self):
        fps = f'{self.clock.get_fps() :.0f} FPS | {len(self.sprite_handler.sprites)} SPRITES'
        self.font.render_to(self.screen, (0, 0), text=fps, fgcolor='green', bgcolor='black')

    def check_events(self):
        for e in pg.event.get():
            if e.type == pg.QUIT or (e.type == pg.KEYDOWN and e.key == pg.K_ESCAPE):
                pg.quit()
                sys.exit()
            elif e.type == pg.MOUSEBUTTONDOWN:
                self.sprite_handler.on_mouse_press()

    def run(self):
        while True:
            self.check_events()
            self.update()
            self.draw()


if __name__ == '__main__':
    app = App()
    app.run()






















