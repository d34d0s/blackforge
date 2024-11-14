"""
BLACKFORGE [ sub-module ]

The AI sub-module provides functions that are intended to act as
method-overrides for the blackforge.object.GameObject `update()` method
"""

import random
import blackforge.asset
import blackforge.world
import blackforge.object

def roamStopWL(tilemap:blackforge.world.TileMap, object:blackforge.object.GameObject, minDist:int=30, maxDist:int=60, showChecks:bool=1) -> None:
    """
    the default patrol/roaming functionality with a stop condition of ledges and walls
    """
    if object.getState("walk-dist") is None:
        object.newState("walk-dist", random.randint(minDist, maxDist))

    if object.getState("walk-dist"):
        checkWall = [
            int((object.location[0] - tilemap.tileSize) if object.getState("flip-x") else ((object.location[0] + object.size[0]) + tilemap.tileSize)),
            int((object.location[1] + (object.size[1] / 2)))
        ]
        
        checkLedge = [
            checkWall[0],
            int((object.location[1] + object.size[1]))
        ]

        wall = tilemap.getTile(checkWall)
        ledge = tilemap.getTile(checkLedge)
        
        if wall:
            if (object.collisions["right"] or object.collisions["left"]):
                object.stop("left") if object.getState("flip-x") else object.stop("right")
                object.setState("flip-x", not bool(object.getState("flip-x")))
            
            if showChecks:
                blackforge.asset.drawRect(
                    object.app.window.canvas,
                    wall.size,
                    [
                        (wall.location[0] * wall.size[0]) - object.app.camera.scroll[0],
                        (wall.location[1] * wall.size[1]) - object.app.camera.scroll[1]
                    ]
                )
        else: ...

        if ledge:
            if showChecks:
                blackforge.asset.drawRect(
                    object.app.window.canvas,
                    ledge.size,
                    [
                        (ledge.location[0] * ledge.size[0]) - object.app.camera.scroll[0],
                        (ledge.location[1] * ledge.size[1]) - object.app.camera.scroll[1]
                    ]
                )
        else:
            object.stop("left") if object.getState("flip-x") else object.stop("right")
            object.setState("flip-x", not bool(object.getState("flip-x")))
    
        object.setState("walk-dist", max(0, object.getState("walk-dist") - 1))
        object.move("left") if object.getState("flip-x") else object.move("right")
    
    # 1/100 chance of random distance between min and max dist
    # 1frame/1.67sec at 60fps
    elif random.random() < 0.01:
        object.setState("walk-dist", random.randint(minDist, maxDist))
    else:
        object.stop("left") if object.getState("flip-x") else object.stop("right")

    object.update(tilemap)
