import sys

from src.game import set_up, run
import src.hitbox_visualizer as vis

HITBOX_EDIT = "-e" in sys.argv

if __name__ == "__main__":
    G = set_up(vis=HITBOX_EDIT)
    if HITBOX_EDIT:
        vis.run(G, migrations="-m" in sys.argv)
    else:
        run(G)

