#-*-python-*-
from BaseAI import BaseAI
from GameObject import *
import random

class AI(BaseAI):
  """The class implementing gameplay logic."""
  @staticmethod
  def username():
    return "FreakBot"

  @staticmethod
  def password():
    return "password"

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
    for thief in self.thiefs:
      thief.move(thief.x+random.randrange(-1,1,1), thief.y+random.randrange(-1,1,1))
  ##This function is called each time it is your turn
  ##Return true to end your turn, return false to ask the server for updated information
  def run(self):
    self.spawn(self.findEntryPoints())
    self.move()
    return 1

  def __init__(self, conn):
    BaseAI.__init__(self, conn)