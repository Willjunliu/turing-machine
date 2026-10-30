import unittest
import importlib.util
import random
import sys

HEX = "0123456789ABCDEF"

spec = importlib.util.spec_from_file_location("ref", "tm.py")
ref = importlib.util.module_from_spec(spec)
spec.loader.exec_module(ref)

try:
    machine, problems = ref.load("sort.tsv")
except ref.InvalidMachine as e:
    print("INVALID:\n" + str(e))
    sys.exit(1)
for p in problems:
    print(p)
print(f"valid, {len(machine)} transitions")

class TestSort(unittest.TestCase):
    def assertSort(self, tape):
        c = ref.run(machine, tape)
        words = tape.strip("[]").split(",") if tape != "[]" else []
        want = "[" + ",".join(sorted(words)) + "]"
        self.assertTrue(c.halted)
        # self.assertEqual(c.state, ref.ACCEPT)
        self.assertEqual(ref.tape_string(c), want)
        self.assertEqual(c.head, 0)

    def test_empty(self):
        self.assertSort("[]")

    def test_single_word(self):
        self.assertSort("[0123456789ABCDEF]")

    def test_duplicate_words(self):
        self.assertSort("[0123456789ABCDEF,0123456789ABCDEF]")

    def test_identical_values(self): 
        self.assertSort("[0000000000000000,0000000000000000]")

    def test_ordered_two_words(self):
        self.assertSort("[1111111111111111,2222222222222222]")

    def test_1st_hex_digit(self):
        self.assertSort("[2000000000000000,1000000000000000]")

    def test_2nd_hex_digit(self):
        self.assertSort("[0200000000000000,0100000000000000]")

    def test_3rd_hex_digit(self):
        self.assertSort("[0020000000000000,0010000000000000]")

    def test_4th_hex_digit(self):
        self.assertSort("[0002000000000000,0001000000000000]")

    def test_5th_hex_digit(self):
        self.assertSort("[0000200000000000,0000100000000000]")

    def test_6th_hex_digit(self):
        self.assertSort("[0000020000000000,0000010000000000]")

    def test_7th_hex_digit(self):
        self.assertSort("[0000002000000000,0000001000000000]") 

    def test_8th_hex_digit(self):
        self.assertSort("[0000000200000000,0000000100000000]")

    def test_9th_hex_digit(self):
        self.assertSort("[0000000020000000,0000000010000000]")

    def test_10th_hex_digit(self):
        self.assertSort("[0000000002000000,0000000001000000]")

    def test_11th_hex_digit(self):
        self.assertSort("[0000000000200000,0000000000100000]")

    def test_12th_hex_digit(self):
        self.assertSort("[0000000000020000,0000000000010000]")

    def test_13th_hex_digit(self):
        self.assertSort("[0000000000002000,0000000000001000]")

    def test_14th_hex_digit(self):
        self.assertSort("[0000000000000200,0000000000000100]")

    def test_15th_hex_digit(self):
        self.assertSort("[0000000000000020,0000000000000010]")

    def test_16th_hex_digit(self):
        self.assertSort("[0000000000000002,0000000000000001]")

    def test_different_positions(self):
        self.assertSort("[0001000000000000,0000000100000000]")

    def test_multiple_positions(self):
        self.assertSort("[0000F0000A000000,0000E0000B000000]")

    def test_ordered_three_words(self):
        self.assertSort("[1111111111111111,2222222222222222,3333333333333333]")

    def test_reversed_order_three_words(self):
        self.assertSort("[3333333333333333,2222222222222222,1111111111111111]")

    def test_1_2_three_word_swap(self):
        self.assertSort("[2222222222222222,1111111111111111,3333333333333333]")

    def test_2_3_three_word_swap(self):
        self.assertSort("[1111111111111111,3333333333333333,2222222222222222]")

    def test_0_to_F_reversed(self):
        self.assertSort("[FFFFFFFFFFFFFFFF,EEEEEEEEEEEEEEEE,DDDDDDDDDDDDDDDD,CCCCCCCCCCCCCCCC,BBBBBBBBBBBBBBBB,AAAAAAAAAAAAAAAA,9999999999999999,8888888888888888,7777777777777777,6666666666666666,5555555555555555,4444444444444444,3333333333333333,2222222222222222,1111111111111111,0000000000000000]")

    def test_random(self):
        HEX = "0123456789ABCDEF"

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

        for words in cases:
            tape = "[" + ",".join(words) + "]"
            self.assertSort(tape)

if __name__ == "__main__":
    unittest.main()