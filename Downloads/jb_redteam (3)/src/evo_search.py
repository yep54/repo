
import random
def evolve(seeds, mutate_fn, fitness_fn, pop_size=50, gens=10, cx_rate=0.3, mut_rate=0.7, elite=5):
    pop=random.sample(seeds, min(pop_size, len(seeds))); scores=[fitness_fn(x) for x in pop]
    for g in range(gens):
        pairs=list(zip(pop, scores)); pairs.sort(key=lambda x: x[1], reverse=True)
        next_pop=[x for x,_ in pairs[:elite]]
        while len(next_pop)<pop_size:
            if random.random()<cx_rate and len(pop)>=2:
                a,b=random.sample(pop,2); cut=random.randint(1, min(len(a),len(b))-1); child=a[:cut]+b[cut:]
            else:
                child=random.choice(pop)
            if random.random()<mut_rate: child=mutate_fn(child)
            next_pop.append(child)
        pop=next_pop[:]; scores=[fitness_fn(x) for x in pop]
    best=max(zip(pop, scores), key=lambda t:t[1]); return best, list(zip(pop, scores))
