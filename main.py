# take the input, read in each word (16 hex digits), store in memory, check if next word is higher or lower, flag if swapped, move to next word, repeat until end "]"
# if flagged, go back to "[", repeat ^, else end

HEX = "0123456789ABCDEF"
MARK = "abcdefghijklmnop"
OPEN, CLOSE, COMMA = "[", "]", ","
INIT, ACCEPT = "⎆", "✔"
RIGHT, LEFT, HALT = "→", "←", "⏹"

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
        if m.read in MARK:
            m.write(unmark(m.read()))
        m.left()
    m.left() # past comma into A

    while m.read() not in "[,": # unmark A
        if m.read in MARK:
            m.write(unmark(m.read()))
        m.left()
    m.right() # past "[," to A digit

    while m.read() in HEX: # go past A
        m.right()
    m.right() # past comma into B digit

def compare(m : Machine):
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
                return

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
            return

        swap(m, a) # A > B: swap from here on
        return

def swap(m: Machine, a):
    pass

            



