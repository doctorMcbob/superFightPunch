"""
~~~ Stages ~~~
A stage will be a dict
  PLAT  : list of rects
  WIDTH : int

there will be an assumed floor at Y: 0 - SCREEN.get_height()

Stages will go infiniately in both directions
  but if you are outside the 0 to WIDTH you bleed damage (offscreen)
"""

STAGE_PATH = "src/bin/"
def load_stage(name):
    with open(STAGE_PATH + name) as f:
        stage = eval(f.read())

def get_stage(G, name):
    G["STAGE"] = load_stage(name)