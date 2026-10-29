# take the input, read in each word (16 hex digits), store in memory, check if next word is higher or lower, flag if swapped, move to next word, repeat until end "]"
# if flagged, go back to "[", repeat ^, else end

HEX = "0123456789ABCDEF"
MARK = "abcdefghijklmnop"
OPEN, CLOSE, COMMA = "[", "]", ","
INIT, ACCEPT = "⎆", "✔"
RIGHT, LEFT, HALT = "→", "←", "⏹"

HEXSYM = " ".join(HEX)
MARKSYM = " ".join(MARK)
import sys

def mark(hex):
    return MARK[HEX.index(hex)]
def unmark(mark):
    return HEX[MARK.index(mark)]

class Machine:
    def __init__(self, text):
        self.tape = list(text) # input
        self.head = 0 # current position
        self.steps = 0 # step counter

    def read(self): # read head
        return self.tape[self.head]

    def write(self, symbol): # overwrite symbol at head
        self.tape[self.head] = symbol

    def right(self): # head move right
        self.head += 1
        self.steps += 1
 
    def left(self): # head move left
        assert self.head > 0, "moved off the left edge"   # '[' at cell 0 stops us
        self.head -= 1
        self.steps += 1

    def show(self):
        return "".join(self.tape) + "\n" + " " * self.head + "^"

def write_rule(current_state, current_symbol, move, next_symbol, next_state):
    f.write(f"{current_state}\t{current_symbol}\t{move}\t{next_symbol}\t{next_state}\n")


states = "start"

def to_next_word(m: Machine):
    m.right()

    while m.read() in HEX: # move to comma between A and B
        m.right()
    m.right() # into B

    write_rule("scan_word", HEXSYM, RIGHT, "", "scan_word")

    write_rule("scan_word", ",", RIGHT, "", "next_word")

def to_previous_word(m: Machine):
    while m.read() in MARK: # move to comma between A and B
        m.left()
    m.left() # into A

    write_rule("scan_word", MARKSYM, LEFT, "", "scan_word")

    write_rule("scan_word", ",", LEFT, "", "previous_word")

def to_nonmarked(m: Machine):
    while m.read() in MARK: # move to non marked
        m.right()

def to_marked(m: Machine):
    while m.read() in HEX: # move through HEX to first marked digit
        m.left()

def unmark_left(m: Machine):
    while m.read() not in "[,": 
        if m.read() in MARK:
            m.write(unmark(m.read()))
        m.left()

def has_next_word(m: Machine) -> bool: 
    while m.read() in HEX: # move to comma or [
        m.right()

    if m.read() == ",": 
        found = True # "," if has next word, "]" is no
    else: 
        found = False
    
    m.left()

    while m.read() in HEX: # move back to start of word
        m.left()
    
    m.right()
    write_rule("peek", HEXSYM, RIGHT, "", "peek")
    write_rule("peek", ",", LEFT, "", "go_back")
    write_rule("peek", "]", LEFT, "", "rewind")
    write_rule("go_back", HEXSYM, LEFT, "", "go_back")
    write_rule("go_back", ", [", RIGHT, "", "compare")
    return found

def erase_marks(m : Machine):
    unmark_left(m) 
    m.left() # past comma into A

    for mark in MARK:
        write_rule("erase_b", mark, LEFT, unmark(mark), "erase_b")
    write_rule("erase_b", HEXSYM, LEFT, "", "erase_b")
    write_rule("erase_b", ",", LEFT, "", "erase_a")


    unmark_left(m) # unmark A
    m.right() # past "[," to A digit

    write_rule("erase_marks", ",", LEFT, "", "erase_marks")
    for mark in MARK:
        write_rule("erase_a", mark, LEFT, unmark(mark), "erase_a")
        

    to_next_word(m) # move to B

    write_rule("erase_a", HEXSYM, LEFT, "", "erase_a")
    write_rule("erase_a", ", [", RIGHT, "", "scan_word")

def compare_and_swap(m : Machine) -> bool: # returns bool cus checks if its been swapped
    # checks if A > B, if so swaps them
    while True: # word A and word B
        a = m.read()
        m.write(mark(a)) # mark current

        to_next_word(m) # move to word B

        to_nonmarked(m) # move to next nonmarked digit in B

        b = m.read()

        # compare
        if a == b:
            m.write(mark(b)) # mark b

            # check if end of word
            m.right() 
            if m.read() not in HEX: # B has no more hex, identical words
                m.left()
                erase_marks(m)
                return False # no swap

            # moving back to A's next unmarked digit
            m.left() # move back to B marked
            to_previous_word(m) # move to word A
            to_marked(m) # move to first marked digit in A
            m.right() # A's next unmarked digit
            continue # check rest of word

        if HEX.index(a) < HEX.index(b):
            erase_marks(m) # A < B: already in order, tidy up
            return False # no swap

        swap(m, a, b) # A > B: swap from here on (currently at b)
        return True

for a in HEX:
    write_rule("compare", a, RIGHT, mark(a), f"carry_{a}")
write_rule("compare", ",", RIGHT, "", "erase_b")      # all digits equal: no swap

for a in HEX:
    write_rule(f"carry_{a}", HEXSYM, RIGHT, "", f"carry_{a}")
    write_rule(f"carry_{a}", ",", RIGHT, "", f"find_{a}") # go to B
    write_rule(f"find_{a}",  MARKSYM, RIGHT, "", f"find_{a}")
    for b in HEX: 
        if b == a:
            write_rule(f"find_{a}", b, LEFT, mark(b), "back_b") # go back through B and A and compare the next word
        elif HEX.index(a) < HEX.index(b):
            write_rule(f"find_{a}", b, LEFT, "", "erase_b")
        else:
            write_rule(f"find_{a}", b, LEFT, mark(a), f"swap_back_{b}") # swapped b with marked a, pick up b

write_rule("back_b", MARKSYM, LEFT, "", "back_b")
write_rule("back_b", ",",      LEFT, "", "back_a")
write_rule("back_a", HEXSYM,  LEFT, "", "back_a")
write_rule("back_a", MARKSYM, RIGHT, "", "compare")


for b in HEX:
    # swap_back_b: carrying b left through B's marked digits to the comma
    write_rule(f"swap_back_{b}", MARKSYM, LEFT, "", f"swap_back_{b}") # go left through marks
    write_rule(f"swap_back_{b}", ",",     LEFT, "", f"swap_put_{b}") # until comma

    # swap_put_b: left through A's plain digits to its last marked digit,
    # overwrite it with b, step right
    write_rule(f"swap_put_{b}", HEXSYM,  LEFT,  "", f"swap_put_{b}") # go left through hexs
    write_rule(f"swap_put_{b}", MARKSYM, RIGHT, mark(b), "swap_next") # until mark and write marked b 

# swap_next: head on A's next digit, or on "," if A is finished
for h in HEX:
    write_rule("swap_next", h, RIGHT, mark(h), f"swap_carry_{h}")   # mark it, carry it
write_rule("swap_next", ",", RIGHT, "", "move_to_end_b") # A done: tidy up  
write_rule("move_to_end_b", MARKSYM, RIGHT, "", "move_to_end_b") 
write_rule("move_to_end_b", ",", LEFT, "", "erase_b")  


for h in HEX:
    # swap_carry_h: carry h right over the rest of A, across the comma
    write_rule(f"swap_carry_{h}", HEXSYM, RIGHT, "", f"swap_carry_{h}")
    write_rule(f"swap_carry_{h}", ",",    RIGHT, "", f"swap_find_{h}")

    # swap_find_h: skip B's marks, write h over B's next digit y, carry y back
    write_rule(f"swap_find_{h}", MARKSYM, RIGHT, "", f"swap_find_{h}")
    for y in HEX:
        write_rule(f"swap_find_{h}", y, LEFT, mark(h), f"swap_back_{y}")



def swap(m: Machine, a, b): # swaps words A and B
    while True:
        m.write(mark(a)) # replace b with a
        m.left() # move back to B marked
        to_previous_word(m) # move to word A
        to_marked(m) # move to first marked digit in A
        m.write(mark(b)) # replace a with b

        m.right()
        if m.read() == ",": # A is finished, all swapped
            break

        a = m.read()
        m.write(mark(a)) # mark a
        
        to_next_word(m) # move to word B
        to_nonmarked(m) # move to next nonmarked digit in B

        b = m.read()
    # all words are swapped but marked (currently at "," between A and B)
    m.right() # into B's first digit

    while m.read() in MARK: 
        m.right()
    write_rule("scan_word", HEXSYM, RIGHT, "", "scan_word")

    m.left() # move to last digit of B
    write_rule("scan_word", ",", LEFT, "", "")

    erase_marks(m) # now unmark A and B

def sort_tape(text):
    m = Machine(text)
    m.right() # skip "["
    while True: # loop through the tape
        swapped = False
        while has_next_word(m):
            did_swap = compare_and_swap(m) # true or false
            swapped = swapped or did_swap # if any swapped, stay true
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
    with open("sort.tsv", "w", encoding="utf-8") as f: # write to file
        if args:
            m = sort_tape(args[0])
            print("result:", "".join(m.tape), f"(head={m.head}, steps={m.steps})")
        else:
            # tests()
            m = sort_tape("[C53D17892A8D0F2D,8D251C8331387B1D,FBBD171C817C81E0,DFCF837BC6F0705F,1FEB07B141DEEC90]")