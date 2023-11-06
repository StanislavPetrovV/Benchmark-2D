from settings import *
import os
import sys
from sdl2 import *
from sdl2.sdlimage import *
from sdl2.sdlttf import *


class SpriteUnit:
    def __init__(self, handler, x, y):
        self.handler = handler
        self.image_ind = randrange(len(handler.images))
        self.image = handler.images[self.image_ind]
        self.rect = SDL_Rect(x - 32, y - 35, 64, 70)
        self.x, self.y = x, y
        self.angle = 0.0
        self.rot_vel = randrange(-SPEED, SPEED)
        self.vel_x, self.vel_y = randrange(-SPEED, SPEED), randrange(-SPEED, SPEED)

    def translate(self):
        self.x += self.vel_x * self.handler.app.dt
        self.y += self.vel_y * self.handler.app.dt
        if self.x < 0 or self.x > WIN_W:
            self.vel_x *= -1
        if self.y < 0 or self.y > WIN_H:
            self.vel_y *= -1
        self.rect.x, self.rect.y = int(self.x) - 32, int(self.y) - 35

    def rotate(self):
        self.angle += self.rot_vel * self.handler.app.dt

    def update(self):
        self.rotate()
        self.translate()

    def kill(self):
        pass


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
                sprite = self.sprites.pop()
                sprite.kill()

    def load_images(self):
        paths = [item for item in pathlib.Path(SPRITE_DIR_PATH).rglob('*.png') if item.is_file()]
        return [IMG_LoadTexture(self.app.renderer, str(path).encode('utf-8')) for path in paths]

    def update(self):
        for sprite in self.sprites:
            sprite.update()

    def draw(self):
        for sprite in self.sprites:
            SDL_RenderCopyEx(
                self.app.renderer,
                sprite.image,
                None,
                sprite.rect,
                sprite.angle,
                None,
                SDL_FLIP_NONE
            )

    def on_mouse_press(self, x, y, is_create):
        if is_create:
            self.add_sprite(x, y)
        else:
            self.del_sprite()


class App:
    def __init__(self):
        SDL_Init(SDL_INIT_VIDEO | SDL_INIT_EVENTS | SDL_INIT_TIMER)
        IMG_Init(IMG_INIT_PNG)
        TTF_Init()
        self.window = SDL_CreateWindow(
            b'PySDL2 test',
            SDL_WINDOWPOS_CENTERED, SDL_WINDOWPOS_CENTERED,
            WIN_W, WIN_H,
            SDL_WINDOW_ALLOW_HIGHDPI
        )
        self.renderer = SDL_CreateRenderer(
            self.window,
            self.get_renderer(),
            SDL_RENDERER_ACCELERATED
        )
        self.renderer.draw_color = (0, 0, 0, 255)
        self.fps_bg = SDL_Color(0, 0, 0, 255)
        self.fps_fg = SDL_Color(0, 255, 0, 255)
        self.clock_freq = SDL_GetPerformanceFrequency()
        self.sprite_handler = SpriteHandler(self)
        self.dt = 0.0
        self.font = TTF_OpenFont(os.path.join(pathlib.Path(FONTS_DIR_PATH), 'verdana.ttf').encode('utf-8'), FONT_SIZE)
        self.fps_size = [FONT_SIZE * 13, FONT_SIZE * 1.5]
        SDL_SetRenderDrawColor(self.renderer, 0, 0, 0, 255)
        self.clock = SDL_GetPerformanceCounter()

    def get_renderer(self):
        prefer_order = ['direct3d11', 'direct3d', 'opengl', 'opengles2', 'opengles', 'software']
        if '--allow-d3d12' in sys.argv:
            prefer_order.insert(0, 'direct3d12')
        if '--use-renderer' in sys.argv:
            prefer_order.insert(0, sys.argv[sys.argv.index('--use-renderer') + 1])
        renderers = []
        for i in range(SDL_GetNumRenderDrivers()):
            info = SDL_RendererInfo()
            SDL_GetRenderDriverInfo(i, info)
            renderers.append(info.name.decode('utf-8'))
        for prefer_name in prefer_order:
            if prefer_name in renderers:
                SDL_SetWindowTitle(self.window, f'PySDL2 test ({prefer_name})'.encode('utf-8'))
                return renderers.index(prefer_name)
        return -1

    def update(self):
        now = SDL_GetPerformanceCounter()
        self.dt = (now - self.clock) / self.clock_freq
        self.clock = now
        self.sprite_handler.update()

    def draw_fps(self):
        fps = f'{(1 / self.dt) :.0f} FPS | {len(self.sprite_handler.sprites)} SPRITES'
        fps_surf = TTF_RenderText_Shaded(self.font, fps.encode(), self.fps_fg, self.fps_bg)
        fps_tex = SDL_CreateTextureFromSurface(self.renderer, fps_surf)
        SDL_RenderCopy(self.renderer, fps_tex, None, SDL_Rect(0, 0, fps_surf.contents.w, fps_surf.contents.h))
        SDL_DestroyTexture(fps_tex)
        SDL_FreeSurface(fps_surf)

    def draw(self):
        SDL_RenderClear(self.renderer)
        self.sprite_handler.draw()
        self.draw_fps()
        SDL_RenderPresent(self.renderer)

    def check_events(self):
        e = SDL_Event()
        while SDL_PollEvent(e):
            if e.type == SDL_QUIT or (e.type == SDL_KEYDOWN and e.key.keysym.sym == SDLK_ESCAPE):
                self.quit()
            elif e.type == SDL_MOUSEBUTTONDOWN:
                self.sprite_handler.on_mouse_press(e.button.x, e.button.y, e.button.button == SDL_BUTTON_LEFT)

    def quit(self):
        self.sprite_handler.sprites.clear()
        for image in self.sprite_handler.images:
            SDL_DestroyTexture(image)
        TTF_CloseFont(self.font)
        TTF_Quit()
        IMG_Quit()
        SDL_Quit()
        sys.exit()

    def run(self):
        while True:
            self.check_events()
            self.update()
            self.draw()


if __name__ == '__main__':
    app = App()
    app.run()
