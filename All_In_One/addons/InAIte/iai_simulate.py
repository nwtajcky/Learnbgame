import bpy
from collections import OrderedDict

import sys
import time
from .iai_debuggingMode import debugMode

from . import iai_channels as chan
wr = chan.Wrapper

from .iai_agent import Agent
from .iai_actions import getmotions


class Simulation():
    """The object that contains everything once the simulation starts"""
    def __init__(self):
        self.agents = {}
        self.framelast = 1
        self.compbrains = {}
        Noise = chan.Noise(self)
        Sound = chan.Sound(self)
        State = chan.State(self)
        World = chan.World(self)
        Crowd = chan.Crowd(self)
        Ground = chan.Ground(self)
        Formation = chan.Formation(self)
        self.lvars = {"Noise": wr(Noise),
                      "Sound": wr(Sound),
                      "State": wr(State),
                      "World": wr(World),
                      "Crowd": wr(Crowd),
                      "Ground": wr(Ground),
                      "Formation": wr(Formation)}
        if debugMode:
            self.totalTime = 0
            self.totalFrames = 0

    def actions(self):
        """Set up the actions"""
        self.actions = getmotions()

    def newagent(self, name):
        """Set up an agent"""
        group = bpy.context.scene.iai_agents.coll[name].group
        groupEntry = bpy.context.scene.iai_groups.coll[group-1]
        ty = bpy.context.scene.iai_groups.coll[group-1].type
        if ty in bpy.data.node_groups:
            ag = Agent(name, bpy.data.node_groups[ty], self)
            self.agents[name] = ag
        else:
            print("No such brain type:" + ty)

    def createAgents(self, agents):
        """Set up all the agents at the beginning of the simulation"""
        for ag in agents:
            self.newagent(ag.name)

    def step(self, scene):
        """Called when the next frame is moved to"""
        if debugMode:
            t = time.time()
        print("NEWFRAME", bpy.context.scene.frame_current)
        for agent in self.agents.values():
            for tag in agent.access["tags"]:
                for channel in self.lvars:
                    if tag[:len(channel)] == channel:
                        self.lvars[channel].register(agent, tag[len(channel):],
                                                     agent.access["tags"][tag])
        # TODO registering channels would be much more efficient if done
        # straight after the agent is evaluated.
        for a in self.agents.values():
            a.step()
        for a in self.agents.values():
            a.apply()
        for chan in self.lvars.values():
            chan.newframe()
        if debugMode:
            newT = time.time()
            print("time", newT - t)
            self.totalTime += newT - t
            self.totalFrames += 1
            print("spf", self.totalTime/self.totalFrames)  # seconds per frame

    def frameChangeHandler(self, scene):
        """Given to Blender to call whenever the scene moves to a new frame"""
        if self.framelast+1 == bpy.context.scene.frame_current:
            self.framelast = bpy.context.scene.frame_current
            self.step(scene)
        if self.framelast >= bpy.context.scene.frame_current:
            active = bpy.context.active_object
            if active and active in self.agents:
                self.agents[bpy.context.active_object.name].highLight()

    def startFrameHandler(self):
        """Add self.frameChangeHandler to the Blender event handlers"""
        if debugMode:
            self.totalTime = 0
            self.totalFrames = 0
        print("Registering frame change handler")
        if self.frameChangeHandler in bpy.app.handlers.frame_change_pre:
            bpy.app.handlers.frame_change_pre.remove(self.frameChangeHandler)
        bpy.app.handlers.frame_change_pre.append(self.frameChangeHandler)

    def stopFrameHandler(self):
        """Remove self.frameChangeHandler from Blenders event handlers"""
        if self.frameChangeHandler in bpy.app.handlers.frame_change_pre:
            print("Unregistering frame change handler")
            bpy.app.handlers.frame_change_pre.remove(self.frameChangeHandler)
