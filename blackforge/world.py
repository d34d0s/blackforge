import os, random, json
import blackforge.resource, blackforge.assets, blackforge.entity

class StaticTile(blackforge.entity.StaticEntity):
    def __init__(self, app, asset:str, size:int, location:list[int], physical:bool=0, variant:int=0, layer:str="background") -> None:
        super().__init__(0, app, "tile", [size, size], location, assetID=asset)
        self.asset:str = asset
        self.layer:str = layer
        self.variant:int = variant
        self.physical:bool = physical

    def renderRect(self, window:blackforge.resource.Window, offset:list[float]=[0, 0]) -> None:
        blackforge.assets.drawRect(window.canvas, self.size, ((self.location[0] * self.size[0]) - offset[0], (self.location[1] * self.size[1]) - offset[1]), [0, 255, 0], width=1)

    def render(self, window:blackforge.resource.Window, offset:list[float]=[0, 0], showRect:bool=0) -> None:
        try:
            asset = self.app.assets.getImage(self.assetID)
            if isinstance(asset, list): asset = asset[self.variant]
            window.blit(asset, ((self.location[0] * self.size[0]) - offset[0], (self.location[1] * self.size[1]) - offset[1]))
            if showRect: self.renderRect(window, offset)
        except (TypeError, AttributeError) as err: ...

class DynamicTile(blackforge.entity.DynamicEntity):
    def __init__(self, app, asset:str, size:int, location:list[int], physical:bool=0, variant:int=0, layer:str="background") -> None:
        super().__init__(0, app, "tile", [size, size], location, assetID=asset)
        self.asset:str = asset
        self.layer:str = layer
        self.variant:int = variant
        self.physical:bool = physical

    def renderRect(self, window:blackforge.resource.Window, offset:list[float]=[0, 0]) -> None:
        blackforge.assets.drawRect(window.canvas, self.size, ((self.location[0] * self.size[0]) - offset[0], (self.location[1] * self.size[1]) - offset[1]), [0, 255, 0], width=1)

    def render(self, window:blackforge.resource.Window, offset:list[float]=[0, 0], showRect:bool=0) -> None:
        try:
            asset = self.app.assets.getImage(self.assetID)
            if isinstance(asset, list): asset = asset[self.variant]
            window.blit(asset, ((self.location[0] * self.size[0]) - offset[0], (self.location[1] * self.size[1]) - offset[1]))
            if showRect: self.renderRect(window, offset)
        except (TypeError, AttributeError) as err: ...

class CloudEntity(blackforge.entity.DynamicEntity):
    def __init__(self, app, speed:int, depth:int, size:list[int], location:list[float]) -> None:
        super().__init__(0, app, "cloud", size, location, "clouds")
        self.speed = speed
        self.depth = depth

    def update(self, tilemap) -> None:
        self.location[0] += self.speed

    def render(self, window:blackforge.resource.Window, camera:blackforge.resource.Camera) -> None:
        image = self.app.assets.getImage(self.assetID)[0]
        renderLocation = [self.location[0] - camera.scroll[0] * self.depth, self.location[1] - camera.scroll[1] * self.depth]
        window.blit(image, [
            renderLocation[0] % (window.size[0] + self.size[0]) - self.size[0],
            renderLocation[1] % (window.size[1] + self.size[1]) - self.size[1],
        ])

def loadWorldForge2Data(app, mapPath:str) -> dict[str]:
    layers = ["background", "midground", "foreground"]
    
    if os.path.exists(mapPath):
        with open(mapPath, 'r') as mapSrc:
            data = json.load(mapSrc)
            mapSrc.close()

    tiles = []
    tileInfo = {"background":{}, "midground":{}, "foreground":{}}
    while layers:
        layer = layers.pop(0)
        for gridLocation in data[layer]:
            tileLayer = data[layer][gridLocation]["layer"]
            location = gridLocation.split(";")
            location[0] = int(location[0])
            location[1] = int(location[1])

            size = int(data["mapInfo"]["tilesize"])
            variant = data[tileLayer][gridLocation]["id"]
            asset = data[tileLayer][gridLocation]["asset"]
            physical = data[tileLayer][gridLocation]["properties"]["collisions"]
            tileInfo[tileLayer][gridLocation] = {
                "size": size,
                "layer": tileLayer,
                "location": location,
                "physical": physical,
                "asset": asset,
                "variant": variant,
            }
            tiles.append(StaticTile(app, asset, size, location, physical, variant, tileLayer))
    return {"tileInfo": tileInfo, "mapInfo": data["mapInfo"], "tiles": tiles}

class TileMap:
    def __init__(self, app, mapPath:str) -> None:
        self.app = app
        self.data = {
            "tiles": {"background":{}, "midground":{}, "foreground":{}},
            "mapInfo": {},
        }
        self.tileSize = 8
        self.configure(mapPath)
    
    def configure(self, mapPath:str) -> None:
        data = loadWorldForge2Data(self.app, mapPath)
        self.data["mapInfo"] = data["mapInfo"]
        self.tileSize = data["mapInfo"]["tilesize"]
        for tile in data["tiles"]:
            strLocation = f"{int(tile.location[0]//self.tileSize)};{int(tile.location[1]//self.tileSize)}"
            tile.location = [*map(int, strLocation.split(";"))]
            self.data["tiles"][tile.layer][strLocation] = tile

    def getLookupRegion(self, regionOffset:list[int]=[0, 0]) -> list[list]:
        return [
            ( 0, -1 )   , # up
            ( 0,  1 )   , # down
            (-1,  0 )   , # left
            ( 1,  0 )   , # right
            
            ( 0,  0 )   , # center
            
            (-1, -1 )   , # top-left
            ( 1, -1 )   , # top-right
            (-1,  1 )   , # bottom-left
            ( 1,  1 )   , # bottom-right
        ]

    def getTilesInRegion(self, location, layer:str="background", regionOffset:list[int]=[0, 0]) -> list[set]:
        tiles = []
        tileLocation = (int(location[0] // self.tileSize), int(location[1] // self.tileSize))
        for offset in self.getLookupRegion(regionOffset):
            strLocation = f"{tileLocation[0] + offset[0] + regionOffset[0]};{tileLocation[1] + offset[1] + regionOffset[1]}"
            if strLocation in self.data["tiles"][layer]:
                tiles.append(self.data["tiles"][layer][strLocation])
        return tiles

    def lookupTiles(self, location:list[int], layer:str="background", regionOffset:list[int]=[0, 0]):
        rects = []
        for tile in self.getTilesInRegion(location=location, layer=layer, regionOffset=regionOffset):
            if tile.physical:
                rects.append(blackforge.assets.createRect(
                    size=[self.tileSize, self.tileSize],
                    location=[ tile.location[0] * self.tileSize, tile.location[1] * self.tileSize ]
                ))
        return rects

    def render(self, showRects:bool=0) -> None:
        window = self.app.window
        scroll = self.app.camera.scroll

        for layer in self.data["tiles"]:
            for x in range(scroll[0] // self.tileSize, (scroll[0] + window.size[0]) // self.tileSize + 1):
                for y in range(scroll[1] // self.tileSize, (scroll[1] + window.size[1]) // self.tileSize + 1):
                    strLocation = f"{x};{y}"
                    if strLocation not in self.data["tiles"][layer]: continue
                    tile = self.data["tiles"][layer][strLocation]
                    tile.render(self.app.window, offset=self.app.camera.scroll, showRect=showRects)

class SkyBox:
    def __init__(self, app, tilemap, cloudSize:list[int], cloudCount:int=16) -> None:
        self.app = app
        self.tilemap = tilemap
        self.clouds:list[CloudEntity] = [CloudEntity(
            app,
            random.random() * 0.05 + 0.05,
            random.random() * 0.6 + 0.2,
            cloudSize,
            [random.random() * 99999, random.random() * 99999]
        ) for _ in range(cloudCount)]

        self.clouds.sort(key=lambda x: x.depth)

    def update(self):
        [ cloud.update(self.tilemap) for cloud in self.clouds ]
    
    def render(self) -> None:
        [ cloud.render(self.app.window, self.app.camera) for cloud in self.clouds ]
