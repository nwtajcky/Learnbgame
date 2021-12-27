from . import iai_channels as chan
import random
import functools

import bpy

import mathutils

from .iai_debuggingMode import debugMode


class Impulse():
    def __init__(self, tup):
        if debugMode:
            assert isinstance(tup[0], str), "Impulse key should be type str"
            assert isinstance(tup[1], int) or isinstance(tup[1], float), \
                "Impulse value should be type int or float"
        self.key = tup[0]
        self.val = tup[1]


class ImpulseContainer():
    # TODO Isn't this just a dictionary?!?!?!
    def __init__(self, cont):
        self.cont = cont

    def __getitem__(self, key):
        if key in self.cont:
            if isinstance(self.cont[key], Impulse):
                return self.cont[key]
            else:
                return Impulse((key, self.cont[key]))

    def __iter__(self):
        return iter([Impulse(x) for x in self.cont.items()])
        # This gets calculated every time the input is looked at
        # Better to calculate in __init__?
        # Do iter objects need making each time

    def __contains__(self, item):
        return item in self.cont

    def __len__(self):
        return len(self.cont)

    def values(self):
        return self.cont.values()

    def __repr__(self):
        return "Impusle container(" + str(self.cont) + ")"


class Neuron():
    """The representation of the nodes. Not to be used on own"""
    def __init__(self, brain, bpyNode):
        self.brain = brain  # type: Brain
        self.neurons = self.brain.neurons  # type: List[Neuron]
        self.inputs = []  # type: List[str] - strings are names of neurons
        self.result = None  # type: None | ImpulseContainer - Cache for current
        self.resultLog = [(0, 0, 0), (0, 0, 0)]  # type: List[(int, int, int)]
        self.fillOutput = bpy.props.BoolProperty(default=True)
        self.bpyNode = bpyNode  # type: iai_bpyNodes.LogicNode
        self.settings = {}  # type: Dict[str, bpy.props.*]
        self.dependantOn = []  # type: List[str] - strings are names of neurons

    def evaluate(self):
        """Called by any neurons that take this neuron as an input"""
        if self.result:
            # Return a cached version of the answer if possible
            return self.result
        noDeps = len(self.dependantOn) == 0
        dep = True in [self.neurons[x].isCurrent for x in self.dependantOn]
        # Only output something if the node isn't dependant on a state
        #  or if one of it's dependancies is the current state
        if noDeps or dep:
            inps = []
            for i in self.inputs:
                got = self.neurons[i].evaluate()
                """For each of the inputs the result is collected. If the
                input in not a dictionary then it is made into one"""
                if got is not None:
                    inps.append(got)
            im = self.core(inps, self.settings)
            if isinstance(im, dict):
                output = ImpulseContainer(im)
            elif isinstance(im, ImpulseContainer):
                if debugMode:
                    print("iai_brainClasses.py - This should not be allowed")
                output = im
            elif im is None:
                output = im
            else:
                output = ImpulseContainer({"None": im})
        else:
            output = None
        self.result = output

        # Calculate the colour that would be displayed in the agent is selected
        total = 0
        if output:
            val = 1
            av = sum(output.values()) / len(output)
            if av > 0:
                startHue = 0.333
            else:
                startHue = 0.5

            if av > 1:
                hueChange = -(-(abs(av)+1)/abs(av) + 2) * (1/3)
                hue = 0.333 + hueChange
                sat = 1
            elif av < -1:
                hueChange = (-(abs(av)+1)/abs(av) + 2) * (1/3)
                hue = 0.5 + hueChange
                sat = 1
            else:
                hue = startHue

            if abs(av) < 1:
                sat = abs(av)**(1/2)
            else:
                sat = 1
        else:
            hue = 0
            sat = 0
            val = 0.5
        self.resultLog[-1] = (hue, sat, val)

        return output

    def newFrame(self):
        self.result = None
        self.resultLog.append((0, 0, 0.5))

    def highLight(self, frame):
        """Colour the nodes in the interface to reflect the output"""
        hue, sat, val = self.resultLog[frame]
        self.bpyNode.use_custom_color = True
        c = mathutils.Color()
        c.hsv = hue, sat, val
        self.bpyNode.color = c
        self.bpyNode.keyframe_insert("color")
        # self.bpyNode.update()


class State():
    """The basic element of the state machine. Abstract class"""
    def __init__(self, brain, bpyNode, name):
        """A lot of the fields are modified by the compileBrain function"""
        self.name = name
        self.brain = brain
        self.neurons = self.brain.neurons
        self.outputs = []
        self.valueInputs = []  # Left empty by start state
        self.finalValue = 1.0
        self.finalValueCalcd = False
        self.settings = {}
        self.isCurrent = False

        self.length = 0
        self.cycleState = False
        self.currentFrame = 0

        self.bpyNode = bpyNode
        self.resultLog = {0:(0, 0, 0), 1:(0, 0, 0)}

    def query(self):
        """If this state is a valid next move return float > 0"""
        if not self.finalValueCalcd:
            self.evaluate()
        # print("query", self.name, self.finalValue)
        return self.finalValue

    def moveTo(self):
        """Called when the current state moves to this node"""
        # print("Moving to a new state:", self.name)
        self.currentFrame = 0
        self.isCurrent = True

    def evaluate(self):
        """Called while all the neurons are being evaluated"""
        if self.finalValueCalcd:
            return
        self.finalValueCalcd = True
        if len(self.valueInputs) == 0:
            self.finalValue = self.settings["ValueDefault"]
            return
        values = []
        for inp in self.valueInputs:
            values.append(self.neurons[inp].evaluate())

        total = 0
        num = 0
        vals = []

        for v in values:
            if v is not None:
                if self.settings["ValueFilter"] == "AVERAGE":
                    for i in v.values():
                        total += i
                        num += 1
                vals += v.values()
        if num == 0:
            num = 1
        if len(vals) == 0:
            result = 0
        elif self.settings["ValueFilter"] == "AVERAGE":
            result = total / num
        elif self.settings["ValueFilter"] == "MAX":
            result = max(vals)
        elif self.settings["ValueFilter"] == "MIN":
            result = min(vals)
        self.finalValue = result

    def evaluateState(self):
        """Return the state to move to (allowed to return itself)

        :returns: moving to new state, name of new state or None
        :rtype: bool, string | None
        """
        self.currentFrame += 1

        """Check to see if the current state is still playing an animation"""
        # print("currentFrame", self.currentFrame, "length", self.length)
        # print("Value compared", self.length - 2 - self.settings["Fade out"])

        # The proportion of the way through the state
        if self.length == 0:
            complete = 1
        else:
            complete = self.currentFrame/self.length
            complete = 0.5 + complete/2
        sceneFrame = bpy.context.scene.frame_current
        self.resultLog[sceneFrame] = ((0.15, 0.4, complete))

        if self.currentFrame < self.length - 1:
            return False, self.name

        # ==== Will stop here is this state hasn't reached its end ====

        options = []
        for con in self.outputs:
            val = self.neurons[con].query()
            # print(con, val)
            if val is not None:
                options.append((con, val))

        # If the cycleState button is checked then add a contection back to
        #    this state again.
        if self.cycleState and self.name not in self.outputs:
            val = self.neurons[self.name].query()
            # print(con, val)
            if val is not None:
                options.append((self.name, val))

        if len(options) > 0:
            if len(options) == 1:
                return True, options[0][0]
            else:
                return True, max(options, key=lambda v: v[1])[0]

        return False, None

    def newFrame(self):
        self.finalValueCalcd = False

    def highLight(self, frame):
        if frame in self.resultLog:
            hue, sat, val = self.resultLog[frame]
        else:
            hue = 0.0
            sat = 0.0
            val = 1.0
        self.bpyNode.use_custom_color = True
        c = mathutils.Color()
        c.hsv = hue, sat, val
        self.bpyNode.color = c
        self.bpyNode.keyframe_insert("color")


class Brain():
    """An executable brain object. One created per agent"""
    def __init__(self, sim, userid):
        self.userid = userid
        self.sim = sim
        self.agvars = {}
        self.lvars = self.sim.lvars
        self.outvars = {}
        self.tags = {}
        self.isActiveSelection = False

        self.currentState = None
        self.startState = None

        # set in compileBrian
        self.outputs = []
        self.neurons = {}
        self.states = []

    def setStartState(self, stateNode):
        """Used by compileBrian"""
        self.currentState = stateNode
        self.startState = stateNode

    def reset(self):
        self.outvars = {"rx": 0, "ry": 0, "rz": 0,
                        "px": 0, "py": 0, "pz": 0}
        self.tags = self.sim.agents[self.userid].access["tags"]
        # self.tags = {}
        self.agvars = self.sim.agents[self.userid].agvars

    def execute(self):
        """Called for each time the agents needs to evaluate"""
        actv = bpy.context.active_object
        self.isActiveSelection = actv is not None and actv.name == self.userid
        self.reset()
        for name, var in self.lvars.items():
            var.setuser(self.userid)
        for neur in self.neurons.values():
            neur.newFrame()
        for out in self.outputs:
            self.neurons[out].evaluate()
        if self.currentState:
            new, nextState = self.neurons[self.currentState].evaluateState()
            self.neurons[self.currentState].isCurrent = False
            if nextState is None:
                nextState = self.startState
            self.currentState = nextState
            self.neurons[self.currentState].isCurrent = True
            if new:
                self.neurons[nextState].moveTo()

    def hightLight(self, frame):
        """This will be called for the agent that is the active selection"""
        for n in self.neurons.values():
            n.highLight(frame)
