from .utils import bitmask
from .resource import Window, Camera
from .__globs__ import pg, os, re, _sprite_count_

# ------------------------------------------------------------ #
class AssetManager:
    def __init__(self) -> None:
        self.font:dict = {}
        self.image:dict = {}
        self.audio:dict = {}

    def getImage(self, key:str) -> pg.Surface|pg.Surface:
        return self.image.get(key, None)
    
    def setImage(self, key:str, image:pg.Surface) -> pg.Surface|None:
        try:
            self.image[key] = image
        except (KeyError) as err: print(err)

    def loadImage(self, key:str, path:str, scale:list=None, colorKey:list=None) -> pg.Surface:
        try:
            self.image[key] = loadImage(path, scale, colorKey)
        except (FileNotFoundError) as err: print(err)
    
    def loadImageDir(self, key:str, path:str, scale:list=None, colorKey:list=None) -> list:
        try:
            self.image[key] = loadImageDir(path, scale, colorKey)
        except (FileNotFoundError) as err: ...
    
    def loadImageSheet(self, key:str, path:str, frameSize:int, colorKey:list=None) -> list:
        try:
            self.image[key] = loadImageSheet(path, frameSize, colorKey)
        except (FileNotFoundError) as err: ...

class Animation:
    def __init__(self, app, assetName, loop:bool=1, frameDuration:float=5, frameOffset:list[int]=[0, 0]) -> None:
        self.app = app
        self.done = 0
        self.frame = 0
        self.loop = loop
        self.frames = []
        self.assetName = assetName
        self.frameOffset = frameOffset
        self.frameDuration = frameDuration

        self.loadFrames()

    def loadFrames(self):
        self.frames = self.app.assets.getImage(self.assetName)

    def copy(self):
        return Animation(self.app, self.assetName, self.assetPath, self.frameDuration)

    def getFrame(self):
        return self.frames[int(self.frame / self.frameDuration)]

    def update(self) -> None:
        if self.loop:
            self.frame = (self.frame + 1) % (self.frameDuration * len(self.frames))
        else:
            self.frame = min(self.frame + 1, self.frameDuration * len(self.frames) - 1)
            if self.frames >= self.frameDuration * len(self.frames) - 1:
                self.done = 1
# ------------------------------------------------------------ #

# ------------------------------------------------------------ #
def showMouse() -> None:
    pg.mouse.set_visible(True)

def hideMouse() -> None:
    pg.mouse.set_visible(False)

def createSurface(size:list[int], color:list[int]) -> pg.Surface :
    s:pg.Surface = pg.Surface(size)
    s.fill(color)
    return s

def createRect(location:list, size:list) -> pg.Rect :
    return pg.Rect(location, size)

def flipSurface(surface:pg.Surface, x:bool, y:bool) -> pg.Surface:
    return pg.transform.flip(surface, x, y)

def fillSurface(surface:pg.Surface, color:list[int]) -> None:
    surface.fill(color)

def naturalKey(string_) -> list[int] :
    return [int(s) if s.isdigit() else s for s in re.split(r'(\d+)', string_)]

def drawLine(display:pg.Surface, color:list[int], start:list[int|float], end:list[int|float], width:int=1) -> None :
    pg.draw.line(display, color, start, end, width=width)
    
def drawRect(display:pg.Surface, size:list[int], location:list[int|float], color:list[int]=[255,0,0], width:int=1) -> None :
    pg.draw.rect(display, color, pg.Rect(location, size), width=width)

def drawCircle(surface, color, center, radius, width=0):
    pg.draw.circle(surface, color, (int(center[0]), int(center[1])), radius, width)

def rotateSurface(surface:pg.Surface, angle:float) -> None :
    return pg.transform.rotate(surface, angle)

def scaleSurface(surface:pg.Surface, scale:list) -> pg.Surface :
    return pg.transform.scale(surface, scale)

def imageVisible(image:pg.Surface, threshold:int=1) -> bool:
    result = False
    pixels, noPixels = 0, 0
    for y in range(image.size[1]):
        for x in range(image.size[0]):
            pixel = image.get_at([x, y])
            if pixel[3] == 0:
                noPixels += 1
            pixels += 1
    if pixels-noPixels >= threshold:
        result = True
    return result

def loadImage(file_path:str, scale:list=None, colorKey:list=None) -> pg.Surface :
    image:pg.Surface = pg.image.load(file_path).convert_alpha()
    image.set_colorkey(colorKey)
    if scale: image = scaleSurface(image, scale)
    return image

def loadImageDir(dirPath:str, scale:list=None, colorKey:list=None) -> list[pg.Surface] :
    images:list = []
    for _, __, image in os.walk(dirPath):
        sorted_images = sorted(image, key=naturalKey)
        for image in sorted_images:
            full_path = dirPath + '/' + image
            image_surface = loadImage(full_path, scale, colorKey)
            if imageVisible(image_surface):
                images.append(image_surface)
    return images
            
def loadImageSheet(sheetPath:str, frameSize:list[int], colorKey:list=None) -> list[pg.Surface] :
    sheet = loadImage(sheetPath)
    frame_x = int(sheet.get_size()[0] / frameSize[0])
    frame_y = int(sheet.get_size()[1] / frameSize[1])
    
    frames = []
    for row in range(frame_y):
        for col in range(frame_x):
            x = col * frameSize[0]
            y = row * frameSize[1]
            frame = pg.Surface(frameSize, pg.SRCALPHA).convert_alpha()
            frame.set_colorkey(colorKey)
            frame.blit(sheet, (0,0), pg.Rect((x, y), frameSize))   # blit the sheet at the desired coords (texture mapping)
            if imageVisible(frame):
                frames.append(frame)
    return frames
# ------------------------------------------------------------ 
