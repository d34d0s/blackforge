import blackforge.resource, blackforge.events, blackforge.assets, blackforge.world
from .globs import _logger

class Application:
    assets = blackforge.assets.AssetManager()
    
    def __init__(
            self,
            name:str,
            windowSize:list[int],
            config:callable=None
        ):
        self.name = name
        self.tilemaps:dict[str] = {}
        self.clock = blackforge.resource.Clock()
        self.events = blackforge.events.EventHandler()
        self.window = blackforge.resource.Window(windowSize[0], windowSize[1], name)
        self.camera = blackforge.resource.Camera(self.window)
        config() if config else _logger.log(_logger.LOG_WARNING, "Application `config()` Method Not Passed To Constructor | Make Sure To Configure Your App!")

    def getTilemap(self, mapName:str) -> blackforge.world.TileMap|None:
        try:
            return self.tilemaps.get(mapName, None)
        except (KeyError) as err: ...

    def newTilemap(self, mapName:str, mapPath:str) -> blackforge.world.TileMap|None:
        if not self.tilemaps.get(mapName, 0):
            self.tilemaps[mapName] = blackforge.world.TileMap(self, mapPath)
            return self.tilemaps[mapName]
        return None

    def setMethods(
            self,
            preProcess:callable=None,
            process:callable=None,
            postProcess:callable=None
        ):
        self.preProcess = preProcess if preProcess is not None else self.preProcess
        self.process = process if process is not None else self.process
        self.postProcess = postProcess if postProcess is not None else self.postProcess

    def preProcess(self, *args, **kwargs) -> None:
        _logger.log(_logger.LOG_ERROR, "Application Pre-Processing Method Not Implemented")
    
    def process(self, *args, **kwargs) -> None:
        _logger.log(_logger.LOG_ERROR, "Application Main Process Method Not Implemented")
    
    def postProcess(self, *args, **kwargs) -> None:
        _logger.log(_logger.LOG_ERROR, "Application Post-Processing Method Not Implemented")

    def run(self, *args, **kwargs) -> None:
        while not self.events.quit:
            self.preProcess(*args, **kwargs)
            self.process(*args, **kwargs)
            self.postProcess(*args, **kwargs)
