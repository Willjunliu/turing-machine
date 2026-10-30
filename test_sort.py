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
        c = ref.run(machine,tape)
        words = tape.strip("[]").split(",") if tape != "[]" else []
        want = "[" + ",".join(sorted(words)) + "]"
        self.assertTrue(c.halted)
        self.assertEqual(c.state, ref.ACCEPT)
        self.assertEqual(ref.tape_string(c), want)
        self.assertEqual(c.head, 0)

    def test_empty(self):
        self.assertSort("[]")

    def test_single_word(self):
        self.assertSort("[0123456789ABCDEF]")

    def test_duplicate_words(self):
        self.assertSort("[0123456789ABCDEF,0123456789ABCDEF]")

if __name__ == "__main__":
    unittest.main(argv=[sys.argv[0]])