import pyray as ray
from raylib import MOUSE_BUTTON_LEFT, MOUSE_BUTTON_RIGHT
from raylib.colors import *
from settings import *


class SpriteUnit:
    def __init__(self, handler, x, y):
        self.handler = handler
        self.image_ind = randrange(len(handler.images))
        self.image = handler.images[self.image_ind]
        self.x, self.y = x, y
        self.angle = 0
        self.rot_vel = self.get_vel()
        self.vel_x, self.vel_y = self.get_vel(), self.get_vel()
        self.center = self.image.width * 0.5, self.image.height * 0.5

    def get_vel(self):
        return randrange(-SPEED, SPEED)

    def translate(self):
        self.x += self.vel_x * self.handler.app.dt
        self.y += self.vel_y * self.handler.app.dt
        if self.x < 0 or self.x > WIN_W:
            self.vel_x *= -1
        if self.y < 0 or self.y > WIN_H:
            self.vel_y *= -1


    def rotate(self):
        self.angle += self.rot_vel * self.handler.app.dt

    def update(self):
        self.rotate()
        self.translate()

    def draw(self):
        ray.draw_texture_pro(self.image,
                            (0, 0, self.image.width, self.image.height),
                            (self.x, self.y, self.image.width, self.image.height),
                             self.center, self.angle, WHITE)


class SpriteHandler:
    def __init__(self, app):
        self.app = app
        self.images = self.load_images()
        self.sprites = [SpriteUnit(self, WIN_W // 2, WIN_H // 2)]

    def add_sprite(self, x, y):
        for i in range(NUM_SPRITES_PER_CLICK):
            self.sprites.append(SpriteUnit(self, x, y))

    def del_sprite(self):
        for i in range(NUM_SPRITES_PER_CLICK):
            if len(self.sprites):
                self.sprites.pop()

    def load_images(self):
        paths = [item for item in pathlib.Path(SPRITE_DIR_PATH).rglob('*.png') if item.is_file()]
        return [ray.load_texture(str(path)) for path in paths]

    def update(self):
        self.on_mouse_press()
        [sprite.update() for sprite in self.sprites]

    def draw(self):
        [sprite.draw() for sprite in self.sprites]

    def on_mouse_press(self):
        if ray.is_mouse_button_pressed(MOUSE_BUTTON_LEFT):
            pos = ray.get_mouse_position()
            self.add_sprite(pos.x, pos.y)
        elif ray.is_mouse_button_pressed(MOUSE_BUTTON_RIGHT):
            self.del_sprite()


class App:
    def __init__(self):
        ray.init_window(*WIN_SIZE, 'test')
        self.sprite_handler = SpriteHandler(self)
        self.dt = 0.0

    def draw_fps(self):
        text = f'{ray.get_fps() :.0f} FPS | {len(self.sprite_handler.sprites)} SPRITES'
        ray.draw_rectangle(0, 0, FONT_SIZE * int(len(text) * 0.6), FONT_SIZE, BLACK)
        ray.draw_text(text, 0, 0, FONT_SIZE, GREEN)

    def update(self):
        self.dt = ray.get_frame_time()
        self.sprite_handler.update()

    def draw(self):
        ray.begin_drawing()
        ray.clear_background(BLACK)
        self.sprite_handler.draw()
        self.draw_fps()
        ray.end_drawing()

    def run(self):
        while not ray.window_should_close():
            self.update()
            self.draw()
        self.destroy()

    def destroy(self):
        [ray.unload_texture(tex) for tex in self.sprite_handler.images]
        ray.close_window()


if __name__ == '__main__':
    app = App()
    app.run()