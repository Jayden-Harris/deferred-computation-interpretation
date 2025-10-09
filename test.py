import random
import matplotlib.pyplot as plt

class GlobalState:
    def __init__(self):
        self.ledger = {}

    def commit(self, name, value):
        self.ledger[name] = value

def random_choice(prob_dict):
    """Pick a key based on probabilities in prob_dict"""
    items = list(prob_dict.items())
    keys, probs = zip(*items)
    cumulative = [sum(probs[:i+1]) for i in range(len(probs))]
    r = random.random()
    for k, c in zip(keys, cumulative):
        if r < c:
            return k
    return keys[-1]  # fallback

class DeferredQuantumState:
    def __init__(self, name, outcomes, dependencies=None):
        self.name = name
        self.outcomes = outcomes
        self.dependencies = dependencies or []

    def measure(self, global_state, context, coherence):
        weights = {}
        for outcome, func in self.outcomes.items():
            w = func(global_state, context, coherence)
            w = self.adjust_for_coherence(w, global_state)
            weights[outcome] = w

        # Normalize
        total = sum(weights.values())
        probabilities = {k: v / total for k, v in weights.items()}

        result = random_choice(probabilities)
        global_state.commit(self.name, result)
        return result

    def adjust_for_coherence(self, weight, global_state):
        committed_dependencies = sum(1 for dep in self.dependencies if dep in global_state.ledger)
        return weight / (1 + 0.1 * committed_dependencies)

global_state = GlobalState()
num_detectors = 5
coherence_budget = 1.0

def interference_factor(pos):
    center = num_detectors // 2
    return 1 / (1 + abs(pos - center))

num_pairs = 200
hit_counts_A = {i: 0 for i in range(num_detectors)}
hit_counts_B = {i: 0 for i in range(num_detectors)}

for n in range(num_pairs):
    photon_A = DeferredQuantumState(f"PhotonA_{n}", {
        i: lambda g, c, h, pos=i: 0.2 * interference_factor(pos) for i in range(num_detectors)
    })

    photon_B = DeferredQuantumState(f"PhotonB_{n}", {
        i: lambda g, c, h, pos=i: 0.2 * interference_factor(pos) * (
            1.5 if g.ledger.get(f"PhotonA_{n}") in ["2","3"] else 1.0
        ) for i in range(num_detectors)
    }, dependencies=[f"PhotonA_{n}"])

    result_A = photon_A.measure(global_state, {}, coherence_budget)
    result_B = photon_B.measure(global_state, {}, coherence_budget)

    hit_counts_A[result_A] += 1
    hit_counts_B[result_B] += 1

plt.figure(figsize=(10,4))
plt.bar(hit_counts_A.keys(), hit_counts_A.values(), alpha=0.6, label="Photon A")
plt.bar(hit_counts_B.keys(), hit_counts_B.values(), alpha=0.6, label="Photon B")
plt.xlabel("Detector Position")
plt.ylabel("Hit Count")
plt.title("DCI Simulation: Deferred Quantum States with Conditional Dependencies")
plt.legend()
plt.show()
