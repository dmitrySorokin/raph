from Brain import *

class TestBrain(Brain):
    def __init__(self):
        Brain.__init__(self, "TestBrain")

        self.actions = [
                            [AttackMonster(),   4000],
                            [FixStatus(),       3000],
                            [RestoreHP(),       2500],
                            [SearchSpot(),      2000],
                            [OpenDoors(),       1750],
                            [DipForExcalibur(), 1600],
                            [GetPhatz(),        1500],
                            [Explore(),         1000],
                            [Descend(),          500],
                            [Search(),           400],
                            [RandomWalk(),         1],
                       ]

    def executeNext(self):
        for action in [x[0] for x in sorted(self.actions, cmp=lambda x,y:y[1]-x[1])]:
            Kernel.instance.log("### TestBrain -> "+str(action))
            if action.can():
                action.execute()
                break

    def s_isWeak(self):
        Kernel.instance.log("Praying because I'm weak")
        Kernel.instance.send("#pray\n")
