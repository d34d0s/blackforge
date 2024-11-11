import blackforge.asset, blackforge.entity, blackforge.gfx

class GameObject(blackforge.entity.DynamicEntity):
    def __init__(self, app, size:list[int], location:list[float], assetID:str="player") -> None:
        super().__init__(0, app, size, location, assetID)
        self.action = "idle"
        self.actions:dict[bool] = {
            "run": 0,
            "idle": 0,
            "jump": 0,
        }
        self.state = {
            "flip-x": 0,
            "flip-y": 0,
            "grounded": 0,
            "air-time": 0,
        }
        self.image = None
        self.animation:blackforge.gfx.Animation = None
        self.animations:dict[blackforge.gfx.Animation] = {}

    def newState(self, flag:str, value) -> None:
        if flag not in self.state:
            self.state[flag] = value

    def getState(self, flag:str) -> None:
        if flag in self.state:
            return self.state[flag]

    def setState(self, flag:str, value=1) -> None:
        if flag in self.state:
            self.state[flag] = value
    
    def remState(self, flag:str) -> None:
        if flag in self.state:
            self.state.pop(flag)

    def addAnimation(self, animName:str, assetName:str, loop:bool, frameDuration:float=5, frameOffset:list[int]=[0, 0]) -> None:
        self.animations[animName] = blackforge.gfx.Animation(self.app, assetName, loop=loop, frameDuration=frameDuration, frameOffset=frameOffset)

    def setAction(self, action:str) -> None:
        try:
            self.actions[self.action] = 0
            self.action = action
            self.actions[self.action] = 1
            self.animation = self.animations[self.action]
        except (KeyError) as err: ...
        

    def update(self, tilemap) -> None:
        super().update(tilemap)
        try:
            self.animation.update()
            self.image = self.animation.getFrame()
        except (AttributeError, TypeError) as err: ...
        
        self.state["air-time"] += 1
        if self.collisions["down"]:
            self.state["air-time"] = 0

        if self.movement["right"]:
            self.setState("flip-x", 0)
        elif self.movement["left"]:
            self.setState("flip-x", 1)
        
        if self.state["air-time"] <= 4:
            self.setState("grounded", 1)
        else: self.setState("grounded", 0)

    def render(self, showRect:bool = 0) -> None:
        try:
            image = blackforge.asset.flipSurface(
                x=self.state.get("flip-x", False),
                y=False,
                surface=self.animation.getFrame()
            )
            renderLocation = [
                (self.location[0] - self.animation.frameOffset[0]) - self.app.camera.scroll[0],
                (self.location[1] - self.animation.frameOffset[1]) - self.app.camera.scroll[1]
            ]
            self.app.window.blit(image, renderLocation)
        except (TypeError, AttributeError) as err:
            try:
                image = self.app.assets.getImage(self.assetID)
                image = blackforge.asset.flipSurface(
                    x=self.state.get("flip-x", False),
                    y=False,
                    surface=image
                )
                renderLocation = [
                    self.location[0] - self.app.camera.scroll[0],
                    self.location[1] - self.app.camera.scroll[1]
                ]

                self.app.window.blit(image, renderLocation)
            except (TypeError, KeyError): ...
        if showRect: self.renderRect()

