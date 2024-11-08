from .__globs__ import _logger, pg, time, _sprite_count_, _blackforge_dir_

class Clock:
    FPS:int=0
    maxFPS:int=60
    last:float=0.0
    delta:float=0.0
    current:float=0.0

    def tick(self) -> None:
        self.current = time.time()

        if self.last == 0.0:
            self.delta = 0.0
        else: self.delta = self.current - self.last

        self.last = self.current

        if self.delta > 0: self.FPS = 1 / self.delta

    def rest(self) -> None:
        time.sleep(max(1 / self.maxFPS - self.delta, 0))

class Window:
    def __init__(self, width:int=800, height:int=600, title:str="GFrame: Game Window", color:list[int]=[140, 130, 160]) -> None:
        self.zoom:int = 2
        self.title:str=title
        self.color:list[int]=color
        self.size:list[int]=[width, height]
        self.display:pg.Surface=pg.display.set_mode(self.size)
        self.canvas:pg.Surface=pg.Surface([int(self.size[0]/self.zoom), int(self.size[1]/self.zoom)])
        pg.display.set_caption(self.title)
        pg.display.set_icon(pg.image.load(f"{_blackforge_dir_}assets\\logo.png"))

    def modZoom(self, delta:int) -> None:
        if self.zoom + delta < 1 or self.zoom + delta > 6:
            return
        self.zoom += delta

    def setIcon(self, image:pg.Surface) -> None:
        try:
            pg.display.set_icon(image)
        except (TypeError) as err: return None
    
    def setTitle(self, title:str) -> None:
        try:
            pg.display.set_caption(title)
        except (TypeError) as err: return None

    def clear(self) -> None:
        self.display.fill(self.color)
        self.canvas.fill(self.color)

    def blit(self, src:pg.Surface, dest:list[float]) -> None:
        self.canvas.blit(src, dest)
        
    def render(self):
        self.display.blit(pg.transform.scale(self.canvas, self.size), [0, 0])
        pg.display.flip()
        self.canvas = pg.Surface([int(self.size[0]/self.zoom), int(self.size[1]/self.zoom)])

class Camera:
    def __init__(self, window) -> None:
        self.window = window
        self.bounds = [
            window.size[0] * 2,
            window.size[1] * 2
        ]
        self.target = None
        self.scroll = [0, 0]
        self.rawScroll = [0, 0]
        self.subPixelCount = 120
        self.box = [100, 100, 100, 100]
    
    def setBox(self, box: list[int]) -> None:
        self.box = [*map(int, box)]

    def setBounds(self, bounds: list[int]) -> None:
        self.bounds = [*map(int, bounds)]

    def setTarget(self, entity) -> None:
        self.target = entity

    def centerTarget(self) -> None:
        centerX = self.target.rect().centerx
        centerY = self.target.rect().centery
        halfWidth = self.window.canvas.size[0] / 2
        halfHeight = self.window.canvas.size[1] / 2

        self.rawScroll[0] += (centerX - halfWidth - self.rawScroll[0]) / self.subPixelCount * self.window.zoom
        self.rawScroll[1] += (centerY - halfHeight - self.rawScroll[1]) / self.subPixelCount * self.window.zoom
    
        max_scroll_x = self.bounds[0] - self.window.canvas.size[0]
        max_scroll_y = self.bounds[1] - self.window.canvas.size[1]

        self.rawScroll[0] = max(0, min(self.rawScroll[0], max_scroll_x))
        self.rawScroll[1] = max(0, min(self.rawScroll[1], max_scroll_y))

        self.scroll = [int(self.rawScroll[0]), int(self.rawScroll[1])]

    def boxMode(self) -> None:
        centerX = self.target.rect().centerx
        centerY = self.target.rect().centery
        halfWidth = self.window.canvas.size[0] / 2
        halfHeight = self.window.canvas.size[1] / 2

        boxLeft = halfWidth - self.box[0]
        boxTop = halfHeight - self.box[1]
        boxRight = halfWidth + self.box[2]
        boxBottom = halfHeight + self.box[3]

        if centerX < boxLeft:
            self.rawScroll[0] += (centerX - boxLeft - self.rawScroll[0]) / self.subPixelCount
        elif centerX > boxRight:
            self.rawScroll[0] += (centerX - boxRight - self.rawScroll[0]) / self.subPixelCount

        if centerY < boxTop:
            self.rawScroll[1] += (centerY - boxTop - self.rawScroll[1]) / self.subPixelCount
        elif centerY > boxBottom:
            self.rawScroll[1] += (centerY - boxBottom - self.rawScroll[1]) / self.subPixelCount

        if self.bounds:
            max_scroll_x = self.bounds[0] - self.window.canvas.size[0]
            max_scroll_y = self.bounds[1] - self.window.canvas.size[1]

            self.rawScroll[0] = max(0, min(self.rawScroll[0], max_scroll_x))
            self.rawScroll[1] = max(0, min(self.rawScroll[1], max_scroll_y))

        self.scroll = [int(self.rawScroll[0]), int(self.rawScroll[1])]
