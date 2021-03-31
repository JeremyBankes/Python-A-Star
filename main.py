import turtle, time, random

def clamp(val, minimum=0, maximum=255):
    if val < minimum:
        return minimum
    if val > maximum:
        return maximum
    return val

def adj_color(hex_color: str, amount: float):
    hex_color = hex_color.strip('#')
    r, g, b = int(hex_color[:2], 16), int(hex_color[2:4], 16), int(hex_color[4:], 16)
    r = int(clamp(r * amount))
    g = int(clamp(g * amount))
    b = int(clamp(b * amount))
    return "#%02x%02x%02x" % (r, g, b)

def manhattan_dist(x1: int, y1: int, x2: int, y2: int):
    return abs(x1 - x2) + abs(y1 - y2)

class Window:
    def __init__(self, title: str, width: int, height: int):
        self.window = turtle.Screen()
        self.window.title(title)
        self.window.tracer(0, 0)
        self.canvas = self.window.cv._canvas
        self.root = self.window._root
        self.canvas["highlightthickness"] = 0
        self.canvas["borderwidth"] = 0
        self.window.setup(width, height)
        self.window.bgcolor("#5b5b5b")
        self.window.listen()
        self.on_key_press(self.window.bye, "Escape")
        self.root.resizable(False, False)
        return

    def on_key_once(self, event, key: str):
        self.window.onkey(event, key)
        return

    def on_key_press(self, event, key: str):
        self.window.onkeypress(event, key)
        return

    def on_key_release(self, event, key: str):
        self.window.onkeyrelease(event, key)
        return

    def update(self):
        self.window.update()
        return

class World:
    def __init__(self, path: str, width: int, height: int, tile_size: int,
                 screen_width: int, screen_height: int, color_scheme: list):
        self.map = {}
        self.path = path
        self.width = width
        self.height = height
        self.tile_size = tile_size
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.color_scheme = color_scheme

        self.painter = Entity(self, "#000000")
        return

    def load(self):
        file = open(self.path, "r")
        for y in range(0, self.height):
            line = file.readline()
            while line.startswith("#"):
                line = file.readline()
            for x in range(0, self.width):
                self.set_tile(x, y, int(line[x]))
        return

    def draw(self):
        for ty in range(0, self.height):
            for tx in range(0, self.width):
                map_value = self.map[tx, ty]
                self.painter.set_size(self.tile_size - 2)
                if type(map_value) == int:
                    self.painter.set_color(self.tile_type(map_value))
                else:
                    self.painter.set_color(map_value)
                self.painter.goto(tx, ty)
                self.painter.stamp()
        return

    def set_tile(self, tx: int, ty: int, type: int):
        self.map[tx, ty] = type
        return

    def get_tile(self, tx: int, ty: int):
        if (tx, ty) in self.map.keys():
            return self.map[tx, ty]
        return 0, 0

    def tile_type(self, type: int):
        cs = self.color_scheme
        if len(cs) > type:
            # 1 + random.randint(-self.tile_size / 2, self.tile_size / 2) / 1000
            return adj_color(cs[type], random.randint(100, 110) / 100)
        return "#FF00FF"

    @staticmethod
    def is_solid(type: int):
        return type in [1]

class Node:

    def __init__(self, x: int, y: int, parent):
        self.x = x
        self.y = y

        if parent is None:
            self.g = 0
        else:
            self.g = parent.g + 1
        self.h = -1
        self.f = -1

        self.parent = parent
        return

    def coords(self):
        return self.x, self.y

    def calc_scores(self, target):
        x1, y1 = self.coords()
        x2, y2 = target.coords()
        self.h = manhattan_dist(x1, y1, x2, y2)
        self.f = self.g + self.h
        return

    def __str__(self):
        return "x: " + str(self.x) + ", y: " + str(self.y) + ", g: " \
               + str(self.g) + ", h: " + str(self.h) + ", f: " + str(self.f)

class Entity:
    def __init__(self, world: World, color: str):
        self.world = world
        self.entity = turtle.Turtle()
        self.entity.speed(0)
        self.entity.shape("square")
        self.entity.shapesize((world.tile_size - 2) / 20)
        self.entity.penup()
        self.set_color(color)
        self.goto(1, 1)
        return

    def goto(self, tx: int, ty: int):
        px = -self.world.screen_width / 2 + self.world.tile_size / 2 + tx * self.world.tile_size
        py = self.world.screen_height / 2 - self.world.tile_size / 2 - ty * self.world.tile_size
        self.entity.goto(px, py)
        return

    def set_size(self, pixels):
        self.entity.shapesize(pixels / 20)

    def get_x(self):
        return (self.entity.xcor() + self.world.screen_width // 2) // self.world.tile_size

    def get_y(self):
        return (self.entity.ycor() - self.world.screen_height // 2) // -self.world.tile_size

    def set_color(self, color: str):
        self.entity.color(color)
        return

    def stamp(self):
        self.entity.stamp()
        return

class Player(Entity):
    MOVE_DELAY = 0.08

    def __init__(self, world: World, window: Window, color: str, tps: int):
        Entity.__init__(self, world, color)
        self.set_color(color)
        self.pressed = []
        self.move_timer = 0
        self.tps = tps
        window.on_key_press(lambda: self.pressed.append("w") if "w" not in self.pressed else None, "w")
        window.on_key_press(lambda: self.pressed.append("a") if "a" not in self.pressed else None, "a")
        window.on_key_press(lambda: self.pressed.append("s") if "s" not in self.pressed else None, "s")
        window.on_key_press(lambda: self.pressed.append("d") if "d" not in self.pressed else None, "d")
        window.on_key_release(lambda: self.pressed.remove("w"), "w")
        window.on_key_release(lambda: self.pressed.remove("a"), "a")
        window.on_key_release(lambda: self.pressed.remove("s"), "s")
        window.on_key_release(lambda: self.pressed.remove("d"), "d")
        window.on_key_press(lambda: self.pressed.append("Up") if "Up" not in self.pressed else None, "Up")
        window.on_key_press(lambda: self.pressed.append("Left") if "Left" not in self.pressed else None, "Left")
        window.on_key_press(lambda: self.pressed.append("Down") if "Down" not in self.pressed else None, "Down")
        window.on_key_press(lambda: self.pressed.append("Right") if "Right" not in self.pressed else None, "Right")
        window.on_key_release(lambda: self.pressed.remove("Up"), "Up")
        window.on_key_release(lambda: self.pressed.remove("Left"), "Left")
        window.on_key_release(lambda: self.pressed.remove("Down"), "Down")
        window.on_key_release(lambda: self.pressed.remove("Right"), "Right")
        return

    def tick(self):
        if self.move_timer <= 0:
            if any(x in self.pressed for x in ["w", "a", "s", "d", "Up", "Down", "Left", "Right"]):
                tx = self.get_x()
                ty = self.get_y()
                if "w" in self.pressed or "Up" in self.pressed:
                    ty -= 1
                if "a" in self.pressed or "Left" in self.pressed:
                    tx -= 1
                if "s" in self.pressed or "Down" in self.pressed:
                    ty += 1
                if "d" in self.pressed or "Right" in self.pressed:
                    tx += 1
                if not self.world.is_solid(self.world.get_tile(self.get_x(), ty)):
                    self.goto(self.get_x(), ty)
                if not self.world.is_solid(self.world.get_tile(tx, self.get_y())):
                    self.goto(tx, self.get_y())
                self.move_timer = Player.MOVE_DELAY
        else:
            self.move_timer -= 1 / self.tps
        return

class Follower(Entity):
    MOVE_DELAY = 0.1

    def __init__(self, target: Entity, world: World, window: Window, color: str, tps: int):
        Entity.__init__(self, world, color)

        self.move_timer = 0
        self.target = target
        self.window = window
        self.path = []
        self.tps = tps
        return

    def tick(self):
        if self.move_timer <= 0:
            self.determine_path_to(self.target.get_x(), self.target.get_y())
            self.take_step()
            self.move_timer = Follower.MOVE_DELAY
        else:
            self.move_timer -= 1 / self.tps
        return

    def get_walkable(self, parent: Node):
        result = []
        for i in range(-1, 2):
            for j in range(-1, 2):
                if 0 in [i, j] and (i != 0 or j != 0):
                    tx, ty = parent.x + j, parent.y + i
                    solid = World.is_solid(self.world.get_tile(tx, ty))
                    if not solid:
                        result.append(Node(tx, ty, parent))
        return result

    @staticmethod
    def get_lowest_f(open_list: list):
        best = None
        for node in open_list:
            if best is None or node.f < best.f:
                best = node
        return best

    @staticmethod
    def node_list_contains(node_list: list, target_node: Node):
        target_coords = target_node.coords()
        for node in node_list:
            if target_coords == node.coords():
                return True
        return False

    @staticmethod
    def get_node_by_coords(node_list: list, x, y):
        for node in node_list:
            if node.coords() == (x, y):
                return node
        return None

    def determine_path_to(self, tx, ty):
        open_list = []
        closed_list = []

        current_node = Node(self.get_x(), self.get_y(), None)

        target_node = Node(tx, ty, None)

        open_list.append(current_node)

        while len(open_list) != 0:
            current_node = Follower.get_lowest_f(open_list)
            closed_list.append(current_node)
            open_list.remove(current_node)
            if Follower.node_list_contains(closed_list, target_node):
                self.backtrace_path(current_node)
                break
            walkables = self.get_walkable(current_node)
            for walkable in walkables:
                if Follower.node_list_contains(closed_list, walkable):
                    continue
                if not Follower.node_list_contains(open_list, walkable):
                    walkable.calc_scores(target_node)
                    open_list.append(walkable)
                else:
                    walkable.calc_scores(target_node)
                    coords = walkable.coords()
                    preexisting = Follower.get_node_by_coords(open_list, coords[0], coords[1])
                    if walkable.f < preexisting.f:
                        preexisting = walkable
        return

    def backtrace_path(self, node: Node):
        self.path.clear()
        while node.parent is not None:
            self.path.append(node.coords())
            node = node.parent
        return

    def take_step(self):
        if len(self.path) > 0:
            coords = self.path[-1]
            self.goto(coords[0], coords[1])
            self.path.pop(len(self.path) - 1)
        return


TITLE = "A* Pathfinding [Made with love by Jeremy Bankes]"
WIDTH = 900
HEIGHT = 600
TPS = 8
WORLD_TILE_WIDTH = 30
WORLD_TILE_HEIGHT = 20
SHOW_TIMINGS = True

COLOR_SCHEME = [
    "#b2b7b2",  # FLOOR
    "#707070",  # WALLS
]

window = Window(TITLE, 900, 600)

world = World("world.txt", WORLD_TILE_WIDTH, WORLD_TILE_HEIGHT, 30, WIDTH, HEIGHT, COLOR_SCHEME)
world.load()
world.draw()

player = Player(world, window, "#229900", TPS)
player.goto(1, 1)

follower = Follower(player, world, window, "#a32c47", TPS)
follower.goto(28, 18)

def toggle_keyset():
    if "w" in player.keyset:
        player.keyset = ["Up", "Left", "Down", "Right"]
    else:
        player.keyset = ["w", "a", "s", "d"]

def click(x, y):
    player.goto((x + WIDTH / 2) // world.tile_size, (HEIGHT / 2 - y) // world.tile_size)
    player.tick();
    window.update();

window.on_key_once(toggle_keyset, "r")
window.window.onclick(click)

try:
    tick_time = 1 / TPS
    last_time = time.time()
    while True:
        current_time = time.time()
        if current_time - last_time > tick_time:
            last_time = current_time
            player.tick()
            follower.tick()
            window.update()
except turtle.Terminator:
    exit()
