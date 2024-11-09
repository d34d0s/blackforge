import blackforge.assets
from .globs import pg

class Entity:
    def __init__(self, id:int, app, type:str, size:list[int], location:list[float], assetID:str=None) -> None:
        self.id = id
        self.app = app
        self.type = type
        self.size = size
        self.location = location
        self.assetID:str = assetID
    
    def scale(self, x:int=1, y:int=1) -> None:
        self.size = [
            self.size[0] * x,
            self.size[1] * y,
        ]

    def rect(self) -> pg.Rect:
        return blackforge.assets.createRect(self.location, self.size)
    
    def renderRect(self) -> None:
        blackforge.assets.drawRect(self.app.window.canvas, self.size, (self.location[0] - self.app.camera.scroll[0], self.location[1] - self.app.camera.scroll[1]), [0, 255, 0], width=1)

    def render(self, showRect:bool=0) -> None:
        try:
            image = self.app.assets.getImage(self.assetID)
            self.app.window.blit(image, (self.location[0] - self.app.camera.scroll[0], self.location[1] - self.app.camera.scroll[1]))
            if showRect: self.renderRect()
        except (TypeError, AttributeError) as err: ...

    def update(self, *args, **kwargs) -> None: raise NotImplementedError

class StaticEntity(Entity):
    def __init__(self, id:int, app, type:str, size:list[int], location:list[float], assetID:str=None) -> None:
        super().__init__(id, app, type, size, location, assetID=assetID)

    def update(self, *args, **kwargs) -> None:
        ...

class DynamicEntity(Entity):
    def __init__(self, id:int, app, type:str, size:list[int], location:list[float], assetID:str=None, regionOffset:list[int]=[1, 1]) -> None:
        super().__init__(id, app, type, size, location, assetID=assetID)
        self.regionOffset = regionOffset
        self.velocity:list[float] = [0.0, 0.0]
        self.movement:dict[str, bool] = {
            "up": 0,
            "down": 0,
            "left": 0,
            "right": 0,
        }
        self.collisions:dict[str, bool] = {
            "up": 0,
            "down": 0,
            "left": 0,
            "right": 0,
        }

    def stop(self, direction:str) -> None:
        self.movement[direction] = 0

    def move(self, direction:str) -> None:
        self.movement[direction] = 1

    def update(self, tilemap) -> None:
        self.collisions = {
            "up": 0,
            "down": 0,
            "left": 0,
            "right": 0,
        }
        
        transformation = [
            (self.movement["right"] - self.movement["left"]) + self.velocity[0],
            (self.movement["down"] - self.movement["up"]) + self.velocity[1],
        ]
        
        self.location[0] += transformation[0]
        rect = self.rect()
        for tile in tilemap.lookupTiles(self.location, regionOffset=self.regionOffset):
            if rect.colliderect(tile):
                if transformation[0] > 0:
                    rect.right = tile.left
                    self.collisions["right"] = 1
                if transformation[0] < 0:
                    rect.left = tile.right
                    self.collisions["left"] = 1
                self.location[0] = rect.x

        self.location[1] += transformation[1]
        rect = self.rect()
        for tile in tilemap.lookupTiles(self.location, regionOffset=self.regionOffset):
            if rect.colliderect(tile):
                if transformation[1] > 0:
                    rect.bottom = tile.top
                    self.collisions["down"] = 1
                if transformation[1] < 0:
                    rect.top = tile.bottom
                    self.collisions["up"] = 1
                self.location[1] = rect.y

        if self.velocity[0] > 0:
            self.velocity[0] = max(self.velocity[0] - 0.1, 0)
        else:
            self.velocity[0] = min(self.velocity[0] + 0.1, 0)
        
        self.velocity[1] = min(3, self.velocity[1] + 0.1)
        if self.collisions["up"] or self.collisions["down"]:
            self.velocity[1] = 0

