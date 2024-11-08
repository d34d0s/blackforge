import blackforge.app as app
import blackforge.assets as assets
import blackforge.input as input
import blackforge.events as events
import blackforge.entity as entity
import blackforge.object as object
import blackforge.gameworld as world
import blackforge.resource as resource

import os, platform, blackforge.version as ver
if "BLACKFORGE_NO_PROMT" not in os.environ:
    print(
        f"BlackForge {ver.BLACKFORGE_MAJOR}.{ver.BLACKFORGE_MINOR}.{ver.BLACKFORGE_PATCH} | Random Quote..."
    )