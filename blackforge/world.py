import os, random, json
import blackforge.resource, blackforge.asset, blackforge.entity

class StaticTile(blackforge.entity.StaticEntity):
    def __init__(self, app, asset:str, size:int, location:list[int], physical:bool=0, variant:int=0, layer:str="background") -> None:
        super().__init__(0, app, [size, size], location, assetID=asset)
        self.asset:str = asset
        self.layer:str = layer
        self.variant:int = variant
        self.physical:bool = physical

    def renderRect(self, window:blackforge.resource.Window, offset:list[float]=[0, 0]) -> None:
        blackforge.asset.drawRect(window.canvas, self.size, ((self.location[0] * self.size[0]) - offset[0], (self.location[1] * self.size[1]) - offset[1]), [0, 255, 0], width=1)

    def render(self, window:blackforge.resource.Window, offset:list[float]=[0, 0], showRect:bool=0) -> None:
        try:
            asset = self.app.assets.getImage(self.assetID)
            if isinstance(asset, list): asset = asset[self.variant]
            window.blit(asset, ((self.location[0] * self.size[0]) - offset[0], (self.location[1] * self.size[1]) - offset[1]))
            if showRect: self.renderRect(window, offset)
        except (TypeError, AttributeError) as err: ...

class DynamicTile(blackforge.entity.DynamicEntity):
    def __init__(self, app, asset:str, size:int, location:list[int], physical:bool=0, variant:int=0, layer:str="background") -> None:
        super().__init__(0, app, [size, size], location, assetID=asset)
        self.asset:str = asset
        self.layer:str = layer
        self.variant:int = variant
        self.physical:bool = physical

    def renderRect(self, window:blackforge.resource.Window, offset:list[float]=[0, 0]) -> None:
        blackforge.asset.drawRect(window.canvas, self.size, ((self.location[0] * self.size[0]) - offset[0], (self.location[1] * self.size[1]) - offset[1]), [0, 255, 0], width=1)

    def render(self, window:blackforge.resource.Window, offset:list[float]=[0, 0], showRect:bool=0) -> None:
        try:
            asset = self.app.assets.getImage(self.assetID)
            if isinstance(asset, list): asset = asset[self.variant]
            window.blit(asset, ((self.location[0] * self.size[0]) - offset[0], (self.location[1] * self.size[1]) - offset[1]))
            if showRect: self.renderRect(window, offset)
        except (TypeError, AttributeError) as err: ...

class CloudEntity(blackforge.entity.DynamicEntity):
    def __init__(self, app, speed:int, depth:int, size:list[int], location:list[float]) -> None:
        super().__init__(0, app, size, location, "clouds")
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
            asset = data[tileLayer][gridLocation]["asset"].replace("/", "\\")
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

    def getMouseMapLocation(self) -> list[int]:
        canvasLocation = self.app.window.getMouseLocation()
        return [
            int(canvasLocation[0] + self.app.camera.scroll[0]),
            int(canvasLocation[1] + self.app.camera.scroll[1])
        ]
    
    def getMouseGridLocation(self) -> list[int]:
        canvasLocation = self.app.window.getMouseLocation()
        return [
            int(canvasLocation[0] + self.app.camera.scroll[0] // self.tileSize),
            int(canvasLocation[1] + self.app.camera.scroll[1] // self.tileSize)
        ]

    def getTile(self, location:list[int], layer:str="background", remove:bool=0) -> StaticTile | DynamicTile | None:
        strLocation = f"{int(location[0] // self.tileSize)};{int(location[1] // self.tileSize)}"
        if not remove: return self.data["tiles"][layer].get(strLocation, None)
        else:
            tile = self.data["tiles"][layer].get(strLocation, None)
            if tile: del self.data["tiles"][layer][strLocation]
            return tile

    def _genLookupRegion(self, size:list[int], location:list[int]) -> list[list]:
        region = []
        right = int((location[0] + size[0]) // self.tileSize)
        bottom = int((location[1] + size[1]) // self.tileSize)
        top = int((location[1] - size[1] / 2) // self.tileSize)
        left = int((location[0] - size[0] / 2) // self.tileSize)

        for x in range(left, right + 1):
            for y in range(top, bottom + 1):
                region.append((x, y))
        return region

    def getTileRegion(self, size:list[int], location:list[int], layer:str="background") -> list[set]:
        tiles = []
        for gridLocation in self._genLookupRegion(size, location):
            strLocation = f"{gridLocation[0]};{gridLocation[1]}"
            if strLocation in self.data["tiles"][layer]:
                tiles.append(self.data["tiles"][layer][strLocation])
        return tiles

    def getTileRegionRects(self, size:list[int], location:list[int], layer:str="background"):
        rects = []
        for tile in self.getTileRegion(size=size, location=location, layer=layer):
            if tile.physical:
                rects.append(blackforge.asset.createRect(
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

