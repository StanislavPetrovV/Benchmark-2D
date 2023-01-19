from settings import *
import pygame as pg
import pygame.freetype as ft
import sys
from pygame._sdl2.video import Window, Renderer, Texture, Image


class SpriteUnit(pg.sprite.Sprite):
    def __init__(self, handler, x, y):
        self.handler = handler
        super().__init__(handler.group)
        self.image_ind = randrange(len(handler.images))
        self.image = Image(handler.images[self.image_ind])
        self.rect = self.image.get_rect()
        self.orig_rect = self.rect.copy()
        self.x, self.y = x, y
        self.angle = 0
        self.rot_vel = randrange(-SPEED, SPEED)
        self.vel_x, self.vel_y = randrange(-SPEED, SPEED), randrange(-SPEED, SPEED)

    def translate(self):
        self.x += self.vel_x * self.handler.app.dt
        self.y += self.vel_y * self.handler.app.dt
        if self.x < 0 or self.x > WIN_W:
            self.vel_x *= -1
        if self.y < 0 or self.y > WIN_H:
            self.vel_y *= -1
        self.rect.center = self.x, self.y

    def rotate(self):
        self.angle += self.rot_vel * self.handler.app.dt
        self.image.angle = self.angle
        self.rect.center = self.x, self.y

    def update(self):
        self.rotate()
        self.translate()


class SpriteHandler:
    def __init__(self, app):
        self.app = app
        self.images = self.load_images()
        self.group = pg.sprite.Group()
        self.sprites = [SpriteUnit(self, WIN_W // 2, WIN_H // 2)]

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
        images = [pg.image.load(str(path)) for path in paths]
        return [Texture.from_surface(self.app.renderer, image) for image in images]

    def update(self):
        self.group.update()

    def draw(self):
        self.group.draw(self.app.renderer)

    def on_mouse_press(self):
        mouse_button = pg.mouse.get_pressed()
        if mouse_button[0]:
            x, y = pg.mouse.get_pos()
            self.add_sprite(x, y)
        elif mouse_button[2]:
            self.del_sprite()


class App:
    def __init__(self):
        pg.init()
        self.window = Window(size=WIN_SIZE)
        self.renderer = Renderer(self.window)
        self.renderer.draw_color = (0, 0, 0, 255)
        self.clock = pg.time.Clock()
        self.sprite_handler = SpriteHandler(self)
        self.dt = 0.0
        self.font = ft.SysFont('Verdana', FONT_SIZE)
        self.fps_size = [FONT_SIZE * 13, FONT_SIZE * 1.5]
        self.fps_surf = pg.Surface(self.fps_size)

    def update(self):
        self.sprite_handler.update()
        self.dt = self.clock.tick(0) * 0.001

    def draw_fps(self):
        self.fps_surf.fill('black')
        fps = f'{self.clock.get_fps() :.0f} FPS | {len(self.sprite_handler.sprites)} SPRITES'
        self.font.render_to(self.fps_surf, (10, 10), text=fps, fgcolor='green', bgcolor='black')
        tex = Texture.from_surface(self.renderer, self.fps_surf)
        tex.draw((0, 0, *self.fps_size), (0, 0, *self.fps_size))

    def draw(self):
        self.renderer.clear()
        self.sprite_handler.draw()
        self.draw_fps()
        self.renderer.present()

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