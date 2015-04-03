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

  ends = collections.deque()

  ##This function is called once, before your first turn
  def init(self):
    pass

  ##This function is called once, after your last turn
  def end(self):
    pass

  def mySide(self, x):
    if self.playerID == 0:
      return x <= self.mapWidth/2
    return x > self.mapWidth/2
  
  def path(self, x, y, startx, starty):
    if x >= 0 and x < self.mapWidth and y >= 0 and y < self.mapHeight:
      return ((startx <= self.mapWidth/2) != (x <= self.mapWidth/2)) and self.tiles[x * self.mapHeight + y] != 2 
  
  def setStarts(self): # just 1 for now
    starts = collections.deque()
    for thief in self.thiefs:
      starts.appendleft((thief.x, thief.y))
    return starts

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

  def pathFind(self, start, end):
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
    return entryPoints

  def spawn(self, entryPoints):
    for entryPoint in entryPoints:
      self.players[self.playerID].purchaseThief(entryPoint[0], entryPoint[1], 4)
      pass

  def move(self):
    s = self.setStarts()
    for thief in self.thiefs:
      #thief.move(thief.x+random.randrange(-1,1,1), thief.y+random.randrange(-1,1,1))
      if thief.owner is self.playerID:
        s.clear()
        s.append((thief.x, thief.y))
        if s and self.ends:
          path = self.pathFind(s, self.ends)
          for i in range(thief.maxMovement - 1):
            if not path:
              break
            new = path.pop()
            thief.move(path[0], path[1])

  ##This function is called each time it is your turn
  ##Return true to end your turn, return false to ask the server for updated information
  def run(self):
    ends = collections.deque
    for trap in self.traps:
      if trap.owner != self.playerID and trap.trapType == 0:
        self.ends.append(trap)
    self.spawn(self.findEntryPoints())
    self.move()
    return 1

  def __init__(self, conn):
    BaseAI.__init__(self, conn)