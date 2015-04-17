#-*-python-*-
from BaseAI import BaseAI
from GameObject import *
import random
import copy
import collections
from sets import Set

class AI(BaseAI):
  """The class implementing gameplay logic."""
  @staticmethod
  def username():
    return "FreakBot"

  @staticmethod
  def password():
    return "password"

  sarcophagi = {}
  scarabs = 500
  ends = collections.deque()
  total = dict()
  explored = {}
  entryPoints = []
  EMPTY, SPAWN, WALL = range(3)
  BOMBER, DIGGER, NINJA, GUIDE, SLAVE = range(5)
  SARCOPHAGUS, SPIKEPIT, SWINGINGBLADE, BOULDER, SPIDERWEB, QUICKSAND, OILVASE, ARROWWALL, HEADWIRE, MERCURYPIT, MUMMY, FAKEROTATINGWALL = range(12)
  ##This function is called once, before your first turn
  def init(self):
    self.findEntryPoints()
    pass

  ##This function is called once, after your last turn
  def end(self):
    pass

  def mySide(self, x):
    if self.playerID == 0:
      return x < self.mapWidth/2
    return x >= self.mapWidth/2

  def tileAt(self, coords):
    return self.tiles[coords[0] * self.mapHeight + coords[1]]

  def path(self, x, y, startx, starty):
    if x >= 0 and x < self.mapWidth and y >= 0 and y < self.mapHeight:
      return ((self.mySide(startx)) == (self.mySide(x))) and self.tiles[x * self.mapHeight + y].type != self.WALL

  def setEnds(self):
    ends = collections.deque()
    for trap in self.traps:
      if trap.owner != self.playerID and trap.trapType == 0:
        ends.appendleft((trap.x, trap.y))
    return ends

  def neighbors(self, tile):
    n = []
    if tile[1] - 1 >= 0 and self.path(tile[0], tile[1] - 1, tile[0], tile[1]):
      n.append((tile[0], tile[1] - 1))
    if tile[1] + 1 < self.mapHeight and self.path(tile[0], tile[1] + 1, tile[0], tile[1]):
      n.append((tile[0], tile[1] + 1))
    if tile[0] - 1 >= 0 and self.path(tile[0] - 1, tile[1], tile[0], tile[1]):
      n.append((tile[0] - 1, tile[1]))
    if tile[0] + 1 < self.mapWidth and self.path(tile[0] + 1, tile[1], tile[0], tile[1]):
      n.append((tile[0] + 1, tile[1]))
    return n

  def allNeighbors(self, tile):
    n = []
    if tile[1] - 1 >= 0:
      n.append((tile[0], tile[1] - 1))
    if tile[1] + 1 < self.mapHeight:
      n.append((tile[0], tile[1] + 1))
    if tile[0] - 1 >= 0:
      n.append((tile[0] - 1, tile[1]))
    if tile[0] + 1 < self.mapWidth:
      n.append((tile[0] + 1, tile[1]))
    return n

  def pathFind(self, start, end, thiefType):
    Open = collections.deque(start)
    Closed = Set(start)
    parentMap = dict()
    path = []
    while Open:
      current = Open.pop()
      if current in end:
        while current not in start:
          path.append(current)
          current = parentMap[current]
        return path
      for neighbor in self.neighbors(current): 
        if neighbor not in Closed:
          parentMap[neighbor] = current
          Closed.add((neighbor))
          Open.appendleft((neighbor))
    pass

  def findEntryPoints(self):
    entryPoints = []
    for tile in self.tiles:
      if tile.type == 1 and not self.mySide(tile.x):
        entryPoints.append((tile.x, tile.y))
    self.entryPoints = entryPoints

  def spawn(self, entryPoints):
    #first, spawn guides
    if self.roundTurnNumber < 4:
      for entryPoint in entryPoints:
        self.spawnThief(entryPoint, self.GUIDE)
    else:
      thiefType = self.NINJA
      self.count(thiefType)
      for entryPoint in entryPoints:
        self.spawnThief(entryPoint, thiefType)
    pass

  def spawnThief(self, entryPoint, thiefType):
    if thiefType not in self.total:
      self.total[thiefType] = 0
    if self.total[thiefType] < self.thiefTypes[thiefType].maxInstances and self.scarabs > self.thiefTypes[thiefType].cost:
      self.scarabs = self.scarabs - self.thiefTypes[thiefType].cost
      self.total[thiefType] = self.total[thiefType] + 1
      self.players[self.playerID].purchaseThief(entryPoint[0], entryPoint[1], thiefType)

  def count(self, thiefType):
    self.total = dict()
    for thief in self.thieves:
      if thief.owner == self.playerID and thief.thiefType == thiefType and thief.alive:
        if thiefType not in self.total:
            self.total[thiefType] = 0
        self.total[thiefType] = self.total[thiefType] + 1
    return self.total

  def move(self):
    s = collections.deque()
    for thief in self.thieves:
      if thief.owner is self.playerID and thief.alive:
        s.clear()
        s.append((thief.x, thief.y))
        if s and self.ends:
          path = self.pathFind(s, self.ends, thief.thiefType)
          for i in range(thief.maxMovement):
            if path:
              new = path.pop()
              #if (new[0], new[1]) in self.explored and self.explored[(new[0], new[1])] == self.EMPTY:
              thief.move(new[0], new[1])

  def placeTraps(self):
    s = collections.deque()
    for neighbor in self.neighbors(self.sarcophagi[self.playerID]):
      self.players[self.playerID].placeTrap(neighbor[0], neighbor[1], self.SWINGINGBLADE)
      for neighbor2 in self.neighbors(neighbor):
        self.players[self.playerID].placeTrap(neighbor2[0], neighbor2[1], self.SWINGINGBLADE)
        for neighbor3 in self.neighbors(neighbor2):
          self.players[self.playerID].placeTrap(neighbor3[0], neighbor3[1], self.SWINGINGBLADE)

  def findTraps(self):
    for trap in self.traps:
      if trap.owner == self.playerID^1:
        self.explored[(trap.x, trap.y)] = trap
    for thief in self.thieves:
      if thief.owner == self.playerID and thief.thiefType == self.GUIDE:
        for neighbor in self.allNeighbors((thief.x, thief.y)):
          if (neighbor[0], neighbor[1]) not in self.explored:
            self.explored[neighbor[0], neighbor[1]] = self.tiles[neighbor[0] * self.mapHeight + neighbor[1]].type

  ##This function is called each time it is your turn
  ##Return true to end your turn, return false to ask the server for updated information
  def run(self):
    self.ends = self.setEnds()
    if self.roundTurnNumber > 1:
      self.findTraps()
      self.spawn(self.entryPoints)
      self.move()


    if self.roundTurnNumber < 2:
      self.explored = {}
      for entryPoint in self.entryPoints:
        self.explored[entryPoint] = self.SPAWN

      self.scarabs = self.scarabsForThieves
      for trap in self.traps:
        if trap.trapType == self.SARCOPHAGUS:
          self.sarcophagi[trap.owner] = (trap.x, trap.y)
      self.placeTraps()

    return 1

  def __init__(self, conn):
    BaseAI.__init__(self, conn)