import random
import itertools

def _AStar(start, goal):
    def heuristic(a, b):
        ax, ay = a
        bx, by = b
        return abs(ax - bx) + abs(ay - by)

    def reconstructPath(n):
        if n == start:
            return [n]
        return reconstructPath(cameFrom[n]) + [n]

    def neighbors(n):
        x, y = n
        return (x - 1, y), (x + 1, y), (x, y - 1), (x, y + 1)

    closed = set()
    open = set()
    open.add(start)
    cameFrom = {}
    gScore = {start: 0}
    fScore = {start: heuristic(start, goal)}

    while open:
        current = None
        for i in open:
            if current is None or fScore[i] < fScore[current]:
                current = i

        if current == goal:
            return reconstructPath(goal)

        open.remove(current)
        closed.add(current)

        for neighbor in neighbors(current):
            if neighbor in closed:
                continue
            g = gScore[current] + 1

            if neighbor not in open or g < gScore[neighbor]:
                cameFrom[neighbor] = current
                gScore[neighbor] = g
                fScore[neighbor] = gScore[neighbor] + heuristic(neighbor, goal)
                if neighbor not in open:
                    open.add(neighbor)
    return ()


def generate(cells_x: int, cells_y: int, cell_size: int = 5) -> list[list[str]]:
    class Cell(object):
        def __init__(self, x, y, id):
            self.x = x
            self.y = y
            self.id = id
            self.connected = False
            self.connectedTo = []
            self.room = None

        def connect(self, other):
            self.connectedTo.append(other)
            other.connectedTo.append(self)
            self.connected = True
            other.connected = True

        def __str__(self):
            return "(%i,%i)" % (self.x, self.y)

    cells = {}
    for y in range(cells_y):
        for x in range(cells_x):
            c = Cell(x, y, len(cells))
            cells[(c.x, c.y)] = c

    current = lastCell = firstCell = random.choice(list(cells.values()))
    current.connected = True

    def getNeighborCells(cell):
        for x, y in ((-1, 0), (0, -1), (1, 0), (0, 1)):
            try:
                yield cells[(cell.x + x, cell.y + y)]
            except KeyError:
                continue

    while True:
        unconnected = list(filter(lambda x: not x.connected, getNeighborCells(current)))
        if not unconnected:
            break

        neighbor = random.choice(unconnected)
        current.connect(neighbor)

        current = lastCell = neighbor

    while True:
        unconnected = list(filter(lambda x: not x.connected, cells.values()))
        if not unconnected:
            break

        candidates = []
        for cell in filter(lambda x: x.connected, cells.values()):
            neighbors = list(filter(lambda x: not x.connected, getNeighborCells(cell)))
            if not neighbors:
                continue
            candidates.append((cell, neighbors))
        if candidates:
            cell, neighbors = random.choice(candidates)
            cell.connect(random.choice(neighbors))

    extraConnections = random.randint(int((cells_x + cells_y) / 4), int((cells_x + cells_y) / 1.2))
    maxRetries = 10
    while extraConnections > 0 and maxRetries > 0:
        cell = random.choice(list(cells.values()))
        neighbor = random.choice(list(getNeighborCells(cell)))
        if cell in neighbor.connectedTo:
            maxRetries -= 1
            continue
        cell.connect(neighbor)
        extraConnections -= 1

    rooms = []
    for cell in cells.values():
        width = random.randint(3, cell_size - 2)
        height = random.randint(3, cell_size - 2)
        x = (cell.x * cell_size) + random.randint(1, cell_size - width - 1)
        y = (cell.y * cell_size) + random.randint(1, cell_size - height - 1)
        floorTiles = []
        for i in range(width):
            for j in range(height):
                floorTiles.append((x + i, y + j))
        cell.room = floorTiles
        rooms.append(floorTiles)

    connections = {}
    for c in cells.values():
        for other in c.connectedTo:
            connections[tuple(sorted((c.id, other.id)))] = (c.room, other.room)
    for a, b in connections.values():
        start = random.choice(a)
        end = random.choice(b)

        corridor = []
        for tile in _AStar(start, end):
            if tile not in a and tile not in b:
                corridor.append(tile)
        rooms.append(corridor)

    stairsUp = random.choice(firstCell.room)
    stairsDown = random.choice(lastCell.room)

    tiles = {}
    tilesX = cells_x * cell_size
    tilesY = cells_y * cell_size
    for x in range(tilesX):
        for y in range(tilesY):
            tiles[(x, y)] = "0"
    for xy in itertools.chain.from_iterable(rooms):
        tiles[xy] = "."

    def get_neighbor_tiles(xy):
        tx, ty = xy
        for x, y in ((-1, -1), (0, -1), (1, -1),
                     (-1, 0), (1, 0),
                     (-1, 1), (0, 1), (1, 1)):
            try:
                yield tiles[(tx + x, ty + y)]
            except KeyError:
                continue

    for xy, tile in tiles.items():
        if not tile == "." and "." in get_neighbor_tiles(xy):
            tiles[xy] = "#"
    tiles[stairsUp] = "<"
    tiles[stairsDown] = ">"

    matrix = []
    for y in range(tilesY):
        aux_list = []
        for x in range(tilesX):
            aux_list.append(tiles[(x, y)])
        matrix.append(aux_list)

    return matrix