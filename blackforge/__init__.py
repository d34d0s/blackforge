import blackforge.app as app

import blackforge.input as input
import blackforge.events as events

import blackforge.gfx as gfx
import blackforge.asset as asset
import blackforge.resource as resource

import blackforge.world as world
import blackforge.entity as entity
import blackforge.object as object

import os, platform, blackforge.version as ver
if "BLACKFORGE_NO_PROMT" not in os.environ:
    print(
        f"BlackForge {ver.BLACKFORGE_MAJOR}.{ver.BLACKFORGE_MINOR}.{ver.BLACKFORGE_PATCH}.{ver.BLACKFORGE_YEAR} | Random Quote Here..."
    )