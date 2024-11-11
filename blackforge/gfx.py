import blackforge.object

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
            if self.frame >= self.frameDuration * len(self.frames) - 1:
                self.done = 1

class Particle(blackforge.object.GameObject):
    def __init__(self, app, size: list[int], location: list[float], assetID:str="particle") -> None:
        super().__init__(app, size, location, assetID)
        self.newState("dynamic", 0)

    def kill(self) -> None:
        del self

    def toggleDynamics(self) -> None:
        self.setState("dynamic", not self.getState("dynamic"))

    def update(self, tilemap) -> None:
        if self.getState("dynamic"): 
            super().update(tilemap)

        kill = 0
        if self.animation.done: kill = 1
        self.animation.update()

        return kill

class ParticleSystem:
    def __init__(self, app, location, maximum) -> None:
        self.app = app
        self.particles = []
        self.maximum = maximum
        self.location = location

    def addParticle(self, size, location, lifetime:int, assetID:str, dynamic:bool=0, velocity:list[float]=[0, 0], loop:bool=0) -> None:
        if len(self.particles)+1 > self.maximum: return None
        particle = Particle(self.app, size, [
            location[0] + self.location[0],
            location[1] + self.location[1]
        ], assetID)
        particle.addAnimation(assetID, assetID, loop, lifetime)
        particle.setAction(assetID)
        particle.setState("dynamic", dynamic)
        particle.velocity = velocity
        self.particles.append(particle)

    def update(self, tilemap) -> None:
        for particle in self.particles:
            if particle.update(tilemap):
                self.particles.remove(particle)
                particle.kill()

    def render(self, showRects:bool=0) -> None:
        for particle in self.particles:
            particle.render(showRect=showRects)
