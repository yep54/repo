
import math
class UCB1:
    def __init__(self, arms): self.arms=list(arms); self.n={a:0 for a in self.arms}; self.r={a:0.0 for a in self.arms}; self.t=0
    def select(self):
        self.t+=1
        for a in self.arms:
            if self.n[a]==0: return a
        ucb={a: self.r[a]/self.n[a] + math.sqrt(2*math.log(self.t)/self.n[a]) for a in self.arms}
        return max(self.arms, key=lambda a: ucb[a])
    def update(self, arm, reward): self.n[arm]+=1; self.r[arm]+=reward
