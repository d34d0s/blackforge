import blackforge.assets, blackforge.entity

class GameObject(blackforge.entity.DynamicEntity):
    def __init__(self, app, size:list[int], location:list[float], assetID:str="player") -> None:
        super().__init__(0, app, assetID, size, location, assetID)
        self.action = "idle"
        self.actions:dict[bool] = {
            "run": 0,
            "idle": 0,
            "jump": 0,
        }
        self.state = {
            "flip-x": 0,
            "flip-y": 0,
            "air-time": 0,
        }
        self.image = None
        self.animation = None
        self.animations:dict[blackforge.assets.Animation] = {}

    def setState(self, flag:int) -> None:
        if not self.state[flag]:
            self.state[flag] = 1
    
    def remState(self, flag:int) -> None:
        if self.state[flag]:
            self.state[flag] = 0

    def addAnimation(self, animName:str, assetName:str, loop:bool, frameDuration:float=5, frameOffset:list[int]=[0, 0]) -> None:
        self.animations[animName] = blackforge.assets.Animation(self.app, assetName, loop=loop, frameDuration=frameDuration, frameOffset=frameOffset)

    def setAction(self, action:str) -> None:
        if self.actions.get(action, False): return None
        self.actions[self.action] = 0
        self.action = action
        self.actions[self.action] = 1
        self.animation = self.animations[self.action]

    def update(self, tilemap) -> None:
        super().update(tilemap)
        try:
            self.animation.update()
            self.image = self.animation.getFrame()
            
            self.state["air-time"] += 1
            if self.collisions["down"]:
                self.state["air-time"] = 0

            if self.movement["right"]:
                self.remState("flip-x")
                self.setAction("run")
            elif self.movement["left"]:
                self.setAction("run")
                self.setState("flip-x")
            else: self.setAction("idle")
            
            if self.state["air-time"] > 4:
                self.setAction("jump")

        except (AttributeError, TypeError) as err:
            self.state["air-time"] += 1
            if self.collisions["down"]:
                self.state["air-time"] = 0

            if self.movement["right"]:
                self.remState("flip-x")
            elif self.movement["left"]:
                self.setState("flip-x")

    def render(self, showRect:bool = 0) -> None:
        try:
            image = blackforge.assets.flipSurface(
                x=self.state.get("flip-x", False),
                y=False,
                surface=self.animation.getFrame()
            )
            renderLocation = [
                (self.location[0] - self.animation.frameOffset[0]) - self.app.camera.scroll[0],
                (self.location[1] - self.animation.frameOffset[1]) - self.app.camera.scroll[1]
            ]
        except (TypeError, AttributeError) as err:
            image = blackforge.assets.flipSurface(
                x=self.state.get("flip-x", False),
                y=False,
                surface=self.app.assets.getImage(self.assetID)
            )
            renderLocation = [
                self.location[0] - self.app.camera.scroll[0],
                self.location[1] - self.app.camera.scroll[1]
            ]

        self.app.window.blit(image, renderLocation)
        if showRect: self.renderRect()

