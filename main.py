# take the input, read in each word (16 hex digits), store in memory, check if next word is higher or lower, flag if swapped, move to next word, repeat until end "]"
# if flagged, go back to "[", repeat ^, else end

HEX = "0123456789ABCDEF"
MARK = "abcdefghijklmnop"
OPEN, CLOSE, COMMA = "[", "]", ","
INIT, ACCEPT = "⎆", "✔"
RIGHT, LEFT, HALT = "→", "←", "⏹"
import sys

def mark(hex):
    return MARK[HEX.index(hex)]
def unmark(mark):
    return HEX[MARK.index(mark)]

class Machine:
    def __init__(self, text):
        self.tape = list(text)
        self.head = 0
        self.steps = 0

    def read(self):
        return self.tape[self.head]

    def write(self, symbol):
        self.tape[self.head] = symbol

    def right(self):
        self.head += 1
        self.steps += 1
 
    def left(self):
        assert self.head > 0, "moved off the left edge"   # '[' at cell 0 stops us
        self.head -= 1
        self.steps += 1

    def show(self):
        return "".join(self.tape) + "\n" + " " * self.head + "^"

def has_next_word(m: Machine) -> bool:
    while m.read() in HEX: # move to comma or [
        m.right()

    if m.read() == ",": found = True # "," if has next word, "]" is no
    else: found = False
    
    m.left()

    while m.read() in HEX: # move back to start of word
        m.left()
    
    m.right()
    
    return found

def erase_marks(m : Machine):
    while m.read() != ",": # going left from B, to "," between A and B
        if m.read() in MARK:
            m.write(unmark(m.read()))
        m.left()
    m.left() # past comma into A

    while m.read() not in "[,": # unmark A
        if m.read() in MARK:
            m.write(unmark(m.read()))
        m.left()
    m.right() # past "[," to A digit

    while m.read() in HEX: # go past A
        m.right()
    m.right() # past comma into B digit

def compare_and_swap(m : Machine) -> bool: # returns bool cus checks if its been swapped
    while True: # word A and word B
        a = m.read()
        m.write(mark(a)) # mark current

        m.right()

        while m.read() in HEX: # move to comma
            m.right()

        m.right() # in word b

        while m.read() in MARK: # move to non marked
            m.right()

        b = m.read()

        # compare
        if a == b:
            m.write(mark(b)) # mark b

            # check if end of word
            m.right() 
            if m.read() not in HEX: # B has no more hex, identical words
                m.left()
                erase_marks(m)
                return False

            # moving back to A's next unmarked digit
            m.left() # move back to B marked
            while m.read() in MARK: # move to comma between A and B
                m.left()
            m.left() # into A
            while m.read() in HEX: # move through HEX to first marked digit
                m.left()
            m.right() # A's next unmarked digit
            continue

        if HEX.index(a) < HEX.index(b):
            erase_marks(m) # A < B: already in order, tidy up
            return False 

        swap(m, a, b) # A > B: swap from here on (currently at b)
        return True

def swap(m: Machine, a, b):
    while True:
        m.write(mark(a)) # replace b with a
        m.left() # move back to B marked
        while m.read() in MARK: # move to comma between A and B
            m.left()
        m.left() # into A
        while m.read() in HEX: # move through HEX to first marked digit
            m.left()
        m.write(mark(b)) # replace a with b

        m.right()
        if m.read() == ",": # A is finished, all swapped
            break

        a = m.read()
        m.write(mark(a)) # mark a
        m.right()
        while m.read() in HEX: # move to comma
            m.right()

        m.right() # in word b

        while m.read() in MARK: # move to non marked
            m.right()

        b = m.read()
    # all words are swapped but marked (currently at "," between A and B)
    m.right() # into B's first digit
    while m.read() not in ",]": # unmark B going right
        m.write(unmark(m.read()))
        m.right()
    m.left()  # back onto B's last digit
    erase_marks(m) # now unmark A and finish

def sort_tape(text):
    m = Machine(text)
    m.right() # skip "["
    while True: # loop through the tape
        swapped = False
        while has_next_word(m):
            did_swap = compare_and_swap(m) # true or false
            swapped = swapped or did_swap # if swapped, stay true
        while m.read() != "[": # go back to beginning
            m.left()
        if not swapped: # no swap, accept
            return m
        m.right() # something swapped, do it again

import random
def tests():
    rng = random.Random(1)
    cases = [[], ["0123456789ABCDEF"], ["F" * 16, "0" * 16], ["0" * 15 + "B", "0" * 15 + "A"]]
    for _ in range(300):
        n = rng.randint(0, 7)
        words = []
        for _ in range(n):
            if words and rng.random() < 0.6:       # share a prefix with an earlier word
                w = list(rng.choice(words))
                p = rng.randrange(16)
                w[p:] = rng.choices(HEX, k=16 - p)
                words.append("".join(w))
            else:
                words.append("".join(rng.choices(HEX, k=16)))
        cases.append(words)
    for words in cases:
        m = sort_tape("[" + ",".join(words) + "]")
        got = "".join(m.tape)
        want = "[" + ",".join(sorted(words)) + "]"
        assert got == want and m.head == 0, (words, got)
    print(f"{len(cases)} cases passed: sorted, no marks left, head back at cell 0")
 
 
if __name__ == "__main__":
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    if args:
        m = sort_tape(args[0])
        print("result:", "".join(m.tape), f"(head={m.head}, steps={m.steps})")
    else:
        tests()