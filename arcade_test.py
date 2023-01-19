from settings import *
import arcade


class SpriteUnit(arcade.Sprite):
    def __init__(self, handler, x, y):
        self.handler = handler
        self.x, self.y = x, y
        super().__init__()
        self.image_ind = randrange(len(handler.images))
        self.texture = handler.images[self.image_ind]
        self.angle = 0
        self.rot_vel = self.get_vel()
        self.vel_x, self.vel_y = self.get_vel(), self.get_vel()

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
        self.center_x, self.center_y = self.x, self.y


class SpriteHandler:
    def __init__(self, app):
        self.app = app
        self.images = self.get_images()
        self.sprites = arcade.SpriteList(use_spatial_hash=False)
        self.sprites.append(SpriteUnit(self, WIN_W // 2, WIN_H // 2))

    def add_sprite(self, x, y):
        for i in range(NUM_SPRITES_PER_CLICK):
            self.sprites.append(SpriteUnit(self, x, y))

    def del_sprite(self):
        for i in range(NUM_SPRITES_PER_CLICK):
            if len(self.sprites):
                self.sprites.pop()

    def get_images(self):
        paths = [item for item in pathlib.Path(SPRITE_DIR_PATH).rglob('*.png') if item.is_file()]
        return [arcade.load_texture(str(path)) for path in paths]

    def update(self):
        self.sprites.update()

    def draw(self):
        self.sprites.draw()


class App(arcade.Window):
    def __init__(self):
        super().__init__(*WIN_SIZE, center_window=True, antialiasing=False)
        self.dt = 0.0
        self.text = arcade.Text(text='text', start_x=0, start_y=WIN_H - FONT_SIZE,
                               font_size=FONT_SIZE, color=arcade.color.GREEN, bold=True)
        self.sprite_handler = SpriteHandler(self)

    def draw_fps(self):
        arcade.draw_xywh_rectangle_filled(self.text.x, self.text.y, *self.text.content_size,
                                          arcade.color.BLACK)
        self.text.text = f'{round(1 / self.dt, 1)} FPS | {len(self.sprite_handler.sprites)} SPRITES'
        self.text.draw()

    def on_mouse_press(self, x, y, button, modifiers):
        if button == arcade.MOUSE_BUTTON_LEFT:
            self.sprite_handler.add_sprite(x, y)
        elif button == arcade.MOUSE_BUTTON_RIGHT:
            self.sprite_handler.del_sprite()

    def on_update(self, delta_time):
        self.sprite_handler.update()
        self.dt = delta_time

    def on_draw(self):
        self.clear()
        self.sprite_handler.draw()
        self.draw_fps()


if __name__ == '__main__':
    app = App()
    app.run()
