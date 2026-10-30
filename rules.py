# Your rules, completed and fixed. Same syntax as yours: write_rule(...), HEXSYM, MARKSYM,
# grouped symbols, "" for "leave the cell unchanged".
# Run:  python sort_rules_fixed.py   -> writes sort_user.tsv

HEX = "0123456789ABCDEF"
MARK = "abcdefghijklmnop"
OPEN, CLOSE, COMMA = "[", "]", ","
INIT, ACCEPT = "⎆", "✔"
RIGHT, LEFT, HALT = "→", "←", "⏹"

HEXSYM = " ".join(HEX)
MARKSYM = " ".join(MARK)


def mark(hex):
    return MARK[HEX.index(hex)]


def unmark(m):
    return HEX[MARK.index(m)]


seen = set()  # catches duplicate (state, symbol) rows while generating


def write_rule(current_state, current_symbol, move, next_symbol, next_state):
    for s in current_symbol.split(" "):
        assert (current_state, s) not in seen, f"duplicate rule for {(current_state, s)}"
        seen.add((current_state, s))
    f.write(f"{current_state}\t{current_symbol}\t{move}\t{next_symbol}\t{next_state}\n")


def build():
    write_rule(INIT, "[", RIGHT, "", "start_0")

    # fl = the swap flag, the last character of every main-loop state name
    # (0 = nothing swapped yet this pass, 1 = something has)
    for fl in "01":
        # start: head on A's first digit (or "]" if the list is empty)
        write_rule(f"start_{fl}", HEXSYM, RIGHT, "", f"peek_{fl}")
        write_rule(f"start_{fl}", "]", LEFT, "", f"rewind_{fl}")

        # peek: is there a word B after A?
        write_rule(f"peek_{fl}", HEXSYM, RIGHT, "", f"peek_{fl}")
        write_rule(f"peek_{fl}", ",", LEFT, "", f"go_back_{fl}")
        write_rule(f"peek_{fl}", "]", LEFT, "", f"rewind_{fl}")

        # go_back: return to the first digit of A
        write_rule(f"go_back_{fl}", HEXSYM, LEFT, "", f"go_back_{fl}")
        write_rule(f"go_back_{fl}", ", [", RIGHT, "", f"compare_{fl}")

        # compare: load A's next unmarked digit into the state
        for a in HEX:
            write_rule(f"compare_{fl}", a, RIGHT, mark(a), f"carry_{fl}_{a}")
        # all digits equal: no swap. Head is now on B's first digit (all of B is marked),
        # so walk to the end of B first, then come back un-marking.
        write_rule(f"compare_{fl}", ",", RIGHT, "", f"move_to_end_b_{fl}")

        for a in HEX:
            write_rule(f"carry_{fl}_{a}", HEXSYM, RIGHT, "", f"carry_{fl}_{a}")
            write_rule(f"carry_{fl}_{a}", ",", RIGHT, "", f"find_{fl}_{a}")  # go to B
            write_rule(f"find_{fl}_{a}", MARKSYM, RIGHT, "", f"find_{fl}_{a}")
            for b in HEX:
                if b == a:
                    write_rule(f"find_{fl}_{a}", b, LEFT, mark(b), f"back_b_{fl}")
                elif HEX.index(a) < HEX.index(b):
                    write_rule(f"find_{fl}_{a}", b, LEFT, "", f"erase_b_{fl}")
                else:  # drop a into B, pick up b. The swap path is always flag 1.
                    write_rule(f"find_{fl}_{a}", b, LEFT, mark(a), f"swap_back_{b}")

        # back_b / back_a: after an equal digit, return to A's next unmarked digit
        write_rule(f"back_b_{fl}", MARKSYM, LEFT, "", f"back_b_{fl}")
        write_rule(f"back_b_{fl}", ",", LEFT, "", f"back_a_{fl}")
        write_rule(f"back_a_{fl}", HEXSYM, LEFT, "", f"back_a_{fl}")
        write_rule(f"back_a_{fl}", MARKSYM, RIGHT, "", f"compare_{fl}")

        # move_to_end_b: walk right across B (all marked), turn left on "," or "]"
        write_rule(f"move_to_end_b_{fl}", MARKSYM, RIGHT, "", f"move_to_end_b_{fl}")
        write_rule(f"move_to_end_b_{fl}", ", ]", LEFT, "", f"erase_b_{fl}")

        # erase_b: walk left through B un-marking, cross the comma
        for mk in MARK:  # (not "mark": that would overwrite the mark() function!)
            write_rule(f"erase_b_{fl}", mk, LEFT, unmark(mk), f"erase_b_{fl}")
        write_rule(f"erase_b_{fl}", HEXSYM, LEFT, "", f"erase_b_{fl}")
        write_rule(f"erase_b_{fl}", ",", LEFT, "", f"erase_a_{fl}")

        # erase_a: walk left through A un-marking, stop at "[" or ","
        for mk in MARK:
            write_rule(f"erase_a_{fl}", mk, LEFT, unmark(mk), f"erase_a_{fl}")
        write_rule(f"erase_a_{fl}", HEXSYM, LEFT, "", f"erase_a_{fl}")
        write_rule(f"erase_a_{fl}", ", [", RIGHT, "", f"to_b_{fl}")

        # to_b: walk right across A into B. B becomes the new A.
        write_rule(f"to_b_{fl}", HEXSYM, RIGHT, "", f"to_b_{fl}")
        write_rule(f"to_b_{fl}", ",", RIGHT, "", f"start_{fl}")

        # rewind: end of pass, walk left to "["
        write_rule(f"rewind_{fl}", HEXSYM + " ,", LEFT, "", f"rewind_{fl}")
        if fl == "0":
            write_rule("rewind_0", "[", HALT, "", ACCEPT)  # no swap this pass: sorted
        else:
            write_rule("rewind_1", "[", RIGHT, "", "start_0")  # swapped: another pass

    # ---- swap path (always flag 1, so no flag in these names) ----
    for b in HEX:
        # swap_back_b: carrying b left through B's marks to the comma
        write_rule(f"swap_back_{b}", MARKSYM, LEFT, "", f"swap_back_{b}")
        write_rule(f"swap_back_{b}", ",", LEFT, "", f"swap_put_{b}")
        # swap_put_b: left through A's plain digits to its last mark, overwrite with b
        write_rule(f"swap_put_{b}", HEXSYM, LEFT, "", f"swap_put_{b}")
        write_rule(f"swap_put_{b}", MARKSYM, RIGHT, mark(b), "swap_next")

    # swap_next: A's next digit, or "," if A is finished
    for h in HEX:
        write_rule("swap_next", h, RIGHT, mark(h), f"swap_carry_{h}")
    write_rule("swap_next", ",", RIGHT, "", "move_to_end_b_1")  # done: tidy up, flag 1

    for h in HEX:
        write_rule(f"swap_carry_{h}", HEXSYM, RIGHT, "", f"swap_carry_{h}")
        write_rule(f"swap_carry_{h}", ",", RIGHT, "", f"swap_find_{h}")
        write_rule(f"swap_find_{h}", MARKSYM, RIGHT, "", f"swap_find_{h}")
        for y in HEX:
            write_rule(f"swap_find_{h}", y, LEFT, mark(h), f"swap_back_{y}")


if __name__ == "__main__":
    with open("sort.tsv", "w", encoding="utf-8", newline="") as f:
        build()
    print(f"wrote sort.tsv: {len(seen)} (state, symbol) pairs")