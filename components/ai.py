from __future__ import annotations

from typing import TYPE_CHECKING

import numpy as np # type: ignore
import tcod

from actions import Action, MeleeAction, MovementAction, WaitAction
from components.base_component import BaseComponent

if TYPE_CHECKING:
    from entity import Actor

class BaseAI(Action, BaseComponent):
    entity: Actor
    
    def perform(self) -> None:
        return NotImplementedError()
    
    def get_path_to(self, dest_x: int, dest_y: int) -> list[tuple[int,int]]:
        """
        Compute and return a path to the target position.
        
        If there's no valid path then returns an empty list.
        """
        
        # Copy the walkable array
        cost = np.array(self.entity.gamemap.tiles["walkable"], dtype=np.int8)
        
        for entity in self.entity.gamemap.entities:
            # Check that an entity blocks movement and the cost isn't zero (blocking.)
            if entity.blocks_movement and cost[entity.x, entity.y]:
                # Add the cost of a blocked position.
                # A lower number means more enemies will crowd behind each other in
                # hallways. A higher number means enemies will take loner paths in
                # order to surround the player.
                cost[entity.x, entity.y] += 10
            
            # Create a graph from the cost array and pass that graph to a new pathfinder.
            graph = tcod.path.SimpleGraph(cost=cost, cardinal=2, diagonal=3)
            pathfinder = tcod.path.Pathfinder(graph)
            
            pathfinder.add_root((self.entity.x, self.entity.y)) #Start possition
            
            # Compute the path to the destination and remove the starting point.
            path: list[list[int]] = pathfinder.path_to((dest_x,dest_y))[1:].tolist()
            
            # Convert from list[list[int]] to list[tuple[int, int]]
            return [(index[0], index[1]) for index in path]

class HostileEnemy(BaseAI):
    def __init__(self, entity: Actor) -> None:
        super().__init__(entity)
        self.path: list[tuple[int,int]] = []
        
    def perform(self) -> None:
        target = self.engine.player
        dx = target.x - self.entity.x
        dy = target.y - self.entity.y
        distance = max(abs(dx), abs(dy))
        
        if self.engine.game_map.visible[self.entity.x, self.entity.y]:
            if distance <= 1:
                return MeleeAction(self.entity, dx, dy).perform()
            
            self.path = self.get_path_to(target.x, target.y)
        
        if self.path:
            dest_x, dest_y = self.path.pop(0)
            return MovementAction(
                self.entity, dest_x - self.entity.x, dest_y - self.entity.y,
            ).perform()
        
        return WaitAction(self.entity).perform()