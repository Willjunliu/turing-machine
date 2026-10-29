HEX = "0123456789ABCDEF"
MARK = "abcdefghijklmnop"
OPEN, CLOSE, COMMA = "[", "]", ","
INIT, ACCEPT = "⎆", "✔"
RIGHT, LEFT, HALT = "→", "←", "⏹"

HEXSYM = " ".join(HEX)
MARKSYM = " ".join(MARK)
def mark(hex):
    return MARK[HEX.index(hex)]
def unmark(mark):
    return HEX[MARK.index(mark)]

def write_rule(current_state, current_symbol, move, next_symbol, next_state):
    f.write(f"{current_state}\t{current_symbol}\t{move}\t{next_symbol}\t{next_state}\n")


write_rule("scan_word", HEXSYM, RIGHT, "", "scan_word")
write_rule("scan_word", ",", RIGHT, "", "next_word")
write_rule("scan_word", MARKSYM, LEFT, "", "scan_word")
write_rule("scan_word", ",", LEFT, "", "previous_word")
write_rule("peek", HEXSYM, RIGHT, "", "peek")
write_rule("peek", ",", LEFT, "", "go_back")
write_rule("peek", "]", LEFT, "", "rewind")
write_rule("go_back", HEXSYM, LEFT, "", "go_back")
write_rule("go_back", ", [", RIGHT, "", "compare")
for mark in MARK:
    write_rule("erase_b", mark, LEFT, unmark(mark), "erase_b")
write_rule("erase_b", HEXSYM, LEFT, "", "erase_b")
write_rule("erase_b", ",", LEFT, "", "erase_a")
write_rule("erase_marks", ",", LEFT, "", "erase_marks")
for mark in MARK:
    write_rule("erase_a", mark, LEFT, unmark(mark), "erase_a")
write_rule("erase_a", HEXSYM, LEFT, "", "erase_a")
write_rule("erase_a", ", [", RIGHT, "", "scan_word")
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