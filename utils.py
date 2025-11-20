import re


def validate_txt(path):
    with open(path, "r") as f:
        content = f.readlines()
        cards = []
        pattern = re.compile(r"^(\d+) (.+)$")
        errors = []
        for line in content:
            line = line.strip()
            if line.startswith("//"):
                continue
            if not line:
                continue
            match = pattern.match(line)
            if not match:
                errors.append(line)
                continue
            cards.append(match.groups())
        return cards, errors
