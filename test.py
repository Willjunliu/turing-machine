# Tests a sorter machine file using the course's reference parser/simulator.
# Usage:  python test.py tm.py sort.tsv

import importlib.util
import random
import sys

HEX = "0123456789ABCDEF"

spec = importlib.util.spec_from_file_location("ref", sys.argv[1])
ref = importlib.util.module_from_spec(spec)
spec.loader.exec_module(ref)

try:
    machine, problems = ref.load(sys.argv[2])
except ref.InvalidMachine as e:
    print("INVALID:\n" + str(e))
    sys.exit(1)
for p in problems:
    print(p)
print(f"valid, {len(machine)} transitions")

rng = random.Random(1)
cases = [[], ["0123456789ABCDEF"], ["F" * 16, "0" * 16], ["0" * 15 + "B", "0" * 15 + "A"], ["F" * 16] * 3]
for _ in range(300):
    n = rng.randint(0, 7)
    words = []
    for _ in range(n):
        if words and rng.random() < 0.6:  # share a prefix with an earlier word
            w = list(rng.choice(words))
            p = rng.randrange(16)
            w[p:] = rng.choices(HEX, k=16 - p)
            words.append("".join(w))
        else:
            words.append("".join(rng.choices(HEX, k=16)))
    cases.append(words)

bad, most = 0, 0
for words in cases:
    c = ref.run(machine, "[" + ",".join(words) + "]")
    want = "[" + ",".join(sorted(words)) + "]"
    most = max(most, c.steps)
    if not (c.halted and c.state == ref.ACCEPT and ref.tape_string(c) == want and c.head == 0):
        bad += 1
        if bad <= 3:
            print("FAIL:", words, "->", c.state, ref.tape_string(c), "head", c.head)
print(f"{len(cases) - bad}/{len(cases)} cases passed (longest run: {most:,} steps)")