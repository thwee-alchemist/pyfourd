#!/usr/bin/env python
# coding: utf-8

# # PyFourD
# 
# In this noteboo, I set out to recreate the dynamic multilevel graph visualization described in the paper of the same name. You can find it on [arxiv.org](https://arxiv.org/abs/0712.1549).

# The library imports are kind of scattered throughout the notebook. In this format, it seemed more appropriate to keep the imports roughly where they'll be used. Of course, that quickly gets out of hand, so I might go back to putting them back to the top. 

# In[1]:


from pythreejs import *
from IPython.display import display
from math import pi

import matplotlib.pyplot as plt
from random import random

import threading
import time
from random import random
import numpy as np

# Reduce repo churn for examples with embedded state:
from pythreejs._example_helper import use_example_model_ids
use_example_model_ids()


class Cube(object): 
    def __init__(self, color, position, size):
        self.color = color
        self.position = position
        self.size = size
        self.object = self.draw(self.size)
        
    def draw(self, size=1.0):
        self.cube = Mesh(
            BoxGeometry(
                width=size,
                height=size,
                depth=size
            ), 
            MeshPhysicalMaterial(color=self.color),
            position=self.position
        )
        return self.cube
    
    def move(self, velocity):
        self.object.position = list(np.add(self.position, velocity))


class Connection(object):
    def __init__(self, start, end, color):
        self.start = start
        self.end = end
        self.color = color
        self.object = self.draw()
        
    def draw(self):
        self.geometry = Geometry(vertices=[self.start, self.end], colors=[self.color])
        self.material = LineBasicMaterial(lineWidth=1, color=self.color)
        self.line = Line(geometry=self.geometry, material=self.material, type="LinePieces")
        
        return Object3D(children=[
            self.line
        ])
    
    def update(self, source, target):
        self.geometry = Geometry(vertices=[source, target])

class Settings:
    def __init__(self):
        self.repulsion = 1e-2
        self.epsilon = 1e-6
        self.attraction = 1e-2
        self.inner_distance = 1e1


settings = Settings()




class Vertex(Cube):
    def __init__(self, id, color="cornflowerblue", size=0.1):
        super().__init__(color, [random(), random(), random()], size)
        self.id = id
        self.velocity = list([0.0, 0.0, 0.0])
        self.edges = set([])
        
    def add_edge(self, edge):
        self.edges.add(edge)
        edge.source.add_edge(edge)
        edge.target.add_edge(edge)
        
    def move(self, velocity):
        super().move(velocity)
        for edge in self.edges:
            if edge.source == self:
                edge.geometry.vertices[0] = self.object.position         
                
            if edge.target == self:
                edge.geometry.vertices[1] = self.object.position
        
    def accelerate(self, force):
        self.velocity = np.add(self.velocity, force)
        self.move(self.velocity)
    
    def repel(self, other):
        diff = np.subtract(self.object.position, other.object.position)
        abs_diff = np.linalg.norm(diff)
        
        force = list(np.multiply(
            np.multiply(diff, abs_diff),
            np.divide(
                settings.repulsion, 
                (np.multiply((settings.epsilon + abs_diff), (settings.epsilon + abs_diff)))
            )
        ))
        
        self.accelerate(force)
        other.accelerate(np.negative(force))
        
        return force
    
    

class Edge(Connection):
    def __init__(self, id, source, target, options={'strength': 1.0, 'color': 'darkorange', 'lineWidth': 1.0}):
        
        super().__init__(
            source.object.position, 
            target.object.position, 
            options['color']
        )
        
        self.id = id
        self.source = source
        self.target = target
        
        self.options = options
    
    def attract(self):
        diff = np.subtract(self.source.object.position, self.target.object.position)
        force = np.multiply(diff, np.negative(settings.attraction))
        force = np.multiply(force, self.options['strength'])
        
        self.source.accelerate(force)
        self.target.accelerate(np.negative(force))
        
        self.geometry.vertices = [self.source.object.position, self.target.object.position]
        
        self.line.geometry.verticesNeedUpdate = True
        self.line.matrixWorldNeedsUpdate = True
        
        return force


class BarnesHutTree(object):
    def __init__(self, settings):
        self.inners = []
        self.outers = {}
        self.settings = settings
        self.size = 0.0
        
        
    def insert(self, vertex):
        if not len(self.inners):
            self.place_inner(vertex)
        else:
            c = self.center()
            p = vertex.position
            distance = np.linalg.norm(p - c)
            
            if distance < self.settings.inner_distance:
                self.place_inner(vertex)
            else:
                self.place_outer(vertex)
        
        self.size += 1.0
        
    def center(self):
        if self.size == 0.0:
            return [0.0, 0.0, 0.0]
        else:
            return np.mean([v.object.position for v in self.inners], axis=0)
        
    def place_inner(self, vertex):
        self.inners.append(vertex)
        
    def place_outer(self, vertex):
        octant = self.get_octant(vertex.object.position)
        self.outers[octant] = BarnesHutTree(self.settings)
        self.outers[octant].insert(vertex)
    
    def get_octant(self, position):
        c = self.center()
        
        if c[0] < position[0]:
            x = 'l'
        else:
            x = 'r'
            
        if c[1] < position[1]:
            y = 'u'
        else:
            y = 'd'
            
        if c[2] < position[2]:
            z = 'i'
        else:
            z = 'o'
            
        return x + y + z
    
    def estimate(self, vertex):
        if vertex in self.inners:
            for v in self.inners:
                if v is not vertex:
                    f = vertex.repel(v)
        else:
            for tree in self.outers.values():
                tree.estimate(vertex)


class Graph(object):
    def __init__(self, scene, options={'width': 970, 'height': 600, 'background': 'black'}):
        self.scene = scene
        
        self.V = {}
        self.E = {}
        
        self.options = options
        
        self.l = threading.Thread(target=self._layout, args=())
        self.lock = threading.Lock()
    
    # rename to vertex(id, **options): create if not exists, update otherwise
    def add_vertex(self, id, options={'color': 'darkblue', 'size': 10}):
        self.lock.acquire() # these are a candidate for decorators
        self.V[id] = Vertex(id, **options)
        self.lock.release()
        
        self.scene.add(self.V[id].object)
        return id
        
    # same for this one
    def add_edge(self, id, source_id, target_id, options={'strength': 1.0}):
        self.lock.acquire()
        
        self.E[id] = Edge(id, self.V[source_id], self.V[target_id], options=options)
        self.scene.add(self.E[id].object)
        
        self.lock.release()
        return id
        
    def remove_vertex(self, id):
        self.lock.acquire()
        for e in self.E.values():
            if e.source.id == id or e.target.id == id:
                self.remove(e)
                
        self.scene.remove(self.V[id].line)
        del self.V[id]
        self.lock.release()
        
    def remove_edge(self, id):
        self.lock.acquire()
        self.scene.remove(self.E[id].object)
        del self.E[id]
        self.lock.release()
        
    def layout(self):
        self.l.start()
    
    def _layout(self):
        while True:
            self.lock.acquire()
            
            tree = BarnesHutTree(settings) # todo: settings
            for vertex in self.V.values():
                tree.insert(vertex)
                
            for vertex in self.V.values():
                tree.estimate(vertex)
            
            for e in self.E.values():
                e.attract()
                
            self.lock.release()
            time.sleep(0.0125)
            

class FourD(object):
    def __init__(self):
        self.scene = self.createScene()
        self.graph = Graph(scene)
        self.graph.layout()
    
    def createScene(self, width=960, height=600, background='white'):

        camera = PerspectiveCamera( position=[10, 6, 10], aspect=width/height )
        key_light = DirectionalLight(position=[0, 10, 10])
        ambient_light = AmbientLight()

        scene = Scene(children=[camera, key_light, ambient_light], background='white')
        controller = OrbitControls(controlling=camera)
        renderer = Renderer(camera=camera, scene=scene, controls=[controller], width=width, height=height)

        self.scene = scene
