"""
Baby name predictor: a character-level Markov chain.

It learns which letters tend to follow which letter-sequences in a list of
real names, then (1) predicts the next letter for a partial name and
(2) generates brand-new names that "sound right".

Names are loaded from names.txt (one per line) sitting next to this script.

Examples:
    python baby_names.py
    python baby_names.py --count 20 --order 3
    python baby_names.py --prefix Ma --min-len 4 --max-len 7
    python baby_names.py --next Ni
    python baby_names.py --file my_other_names.txt
"""

import argparse
import random
from collections import defaultdict, Counter
from pathlib import Path

DEFAULT_FILE = Path(__file__).with_name("names.txt")

# Used only if names.txt can't be found.
FALLBACK_NAMES = (
    "Aoife Saoirse Niamh Ciara Roisin Orla Maeve Cian Oisin Conor Darragh "
    "Fionn Emma Olivia Amelia Sophie Grace Hannah Lily Liam Noah Jack Daniel"
).split()


def load_names(path):
    """Read one name per line; skip blanks, #comments and non-letter junk."""
    path = Path(path)
    if not path.exists():
        print(f"(Couldn't find {path.name}, using a tiny built-in list.)\n")
        return FALLBACK_NAMES
    names = []
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if line and not line.startswith("#") and line.isalpha():
            names.append(line)
    return names


class NamePredictor:
    def __init__(self, names, order=2):
        self.order = order
        self.names = {n.lower() for n in names}
        # One model per context length (1..order) so we can back off to a
        # shorter context when a long one has never been seen.
        self.models = {k: defaultdict(Counter) for k in range(1, order + 1)}
        for name in self.names:
            for k, model in self.models.items():
                padded = "^" * k + name + "$"  # ^ = start, $ = end
                for i in range(len(padded) - k):
                    model[padded[i:i + k]][padded[i + k]] += 1

    def _counts(self, prefix):
        """Letter counts for the longest context we've actually seen."""
        for k in range(self.order, 0, -1):
            context = ("^" * k + prefix.lower())[-k:]
            counts = self.models[k].get(context)
            if counts:
                return counts
        return None

    def predict_next(self, prefix="", top=5):
        """Most likely next letters ('$' = name ends) with probabilities."""
        counts = self._counts(prefix)
        if not counts:
            return []
        total = sum(counts.values())
        return [(c, n / total) for c, n in counts.most_common(top)]

    def generate(self, prefix="", min_len=3, max_len=9):
        """Generate one name, optionally starting with a prefix."""
        name = prefix.lower()
        while len(name) < max_len:
            counts = dict(self._counts(name) or {})
            if len(name) < min_len:
                counts.pop("$", None)  # too short to stop yet
            if not counts:
                break
            letters, weights = zip(*counts.items())
            nxt = random.choices(letters, weights)[0]
            if nxt == "$":
                break
            name += nxt
        return name.capitalize()

    def suggest(self, count=10, prefix="", min_len=3, max_len=9):
        """Generate unique, genuinely new names (not already in the list)."""
        found = set()
        for _ in range(count * 200):
            if len(found) >= count:
                break
            name = self.generate(prefix, min_len, max_len)
            if len(name) >= min_len and name.lower() not in self.names:
                found.add(name)
        return sorted(found)


def main():
    parser = argparse.ArgumentParser(description="Baby name predictor")
    parser.add_argument("--file", default=DEFAULT_FILE, help="names file (one per line)")
    parser.add_argument("--order", type=int, default=2, help="context length: 2 = creative, 3 = closer to real names")
    parser.add_argument("--count", type=int, default=10, help="how many names to generate")
    parser.add_argument("--prefix", default="", help="start generated names with these letters")
    parser.add_argument("--min-len", type=int, default=3)
    parser.add_argument("--max-len", type=int, default=9)
    parser.add_argument("--next", metavar="PREFIX", help="show next-letter predictions for PREFIX and exit")
    args = parser.parse_args()

    names = load_names(args.file)
    predictor = NamePredictor(names, order=args.order)
    print(f"Learned from {len(predictor.names)} names (order {args.order}).\n")

    if args.next is not None:
        print(f"Next-letter predictions after '{args.next}':")
        for letter, p in predictor.predict_next(args.next):
            label = "(end of name)" if letter == "$" else letter
            print(f"  {label}: {p:.0%}")
        return

    ideas = predictor.suggest(args.count, args.prefix, args.min_len, args.max_len)
    print("New name ideas:", ", ".join(ideas) if ideas else "none found, try a different prefix or order")


if __name__ == "__main__":
    main()
