# Ainm

*Ainm* is the Irish word for "name".

It's a small Python tool that **predicts and generates baby names** using a
character-level Markov chain. It learns which letters tend to follow which
letter-sequences in a list of real names, then uses that to suggest the next
letter or invent brand-new names that sound plausible.


## Example

```
$ python baby_names.py --count 6
Learned from 208 names (order 2).

New name ideas: Aoimhe, Cala, Harra, Mastie, Matiel, Nualeb

$ python baby_names.py --next Ni
Next-letter predictions after 'Ni':
  a: 50%
  c: 25%
  e: 25%
```

(Output is random, so yours will differ.)

## Quick start

```bash
git clone https://github.com/<your-username>/ainm.git
cd ainm
python baby_names.py
```

Requires Python 3.8+.

## Usage

| Option | What it does | Default |
| --- | --- | --- |
| `--count N` | How many names to generate | 10 |
| `--prefix Ma` | Start every name with these letters | none |
| `--order N` | Context length. 2 is more creative, 3 sticks closer to real names | 2 |
| `--min-len N` / `--max-len N` | Bounds on name length | 3 / 9 |
| `--next Ni` | Show next-letter probabilities for a prefix, then exit | off |
| `--file path.txt` | Use a different names file | `names.txt` |

You can also use it as a library:

```python
from baby_names import NamePredictor, load_names

predictor = NamePredictor(load_names("names.txt"), order=3)
predictor.suggest(5, prefix="Ai")
predictor.predict_next("Ni")
```

## How it works

1. Every training name is padded with a start marker (`^`) and an end marker
   (`$`), then sliced into (context, next letter) pairs. For `anna` with
   order 2 that gives `^^ -> a`, `^a -> n`, `an -> n`, `nn -> a`, `na -> $`.
2. Counting those pairs gives a probability distribution over the next letter
   for each context.
3. To generate a name, the program starts from the prefix (or the start marker)
   and repeatedly samples the next letter from the distribution until it
   samples the end marker or hits the maximum length.
4. If a long context has never been seen, it **backs off** to a shorter one so
   generation doesn't dead-end.
5. Generated names that already exist in the training list are filtered out,
   so every suggestion is new.

## Training data

`names.txt` has about 200 Irish and international names to get started. One
name per line, `#` for comments. Results improve a lot with a bigger list, so
try the baby name datasets published by Ireland's CSO or the US Social
Security Administration.

## Tests

```bash
pip install pytest
pytest
```

## Limitations and ideas

- It only knows spelling patterns, not meaning, origin or popularity.
- Some outputs are nonsense. A filter using a pronounceability score would help.
- Possible extensions: a small web interface, popularity trends from real
  registry data, or scoring how realistic the generated names are against a
  held-out set of real names.

## Licence

MIT, see [LICENSE](LICENSE).
