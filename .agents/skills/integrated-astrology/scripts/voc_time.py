"""
VOC time calculator — shared engine between integrated-astrology and horary-astrology.
Canonical source: horary-astrology/scripts/voc_time.py
Usage: python voc_time.py <YYYY-MM-DD> <HH:MM> <lat> <lon>
"""
import sys, os
# Point to the canonical script in horary-astrology
CANONICAL = os.path.join(os.path.dirname(__file__),
    '..', '..', 'horary-astrology', 'scripts', 'voc_time.py')
CANONICAL = os.path.normpath(CANONICAL)

if __name__ == '__main__':
    # Redirect to the canonical implementation
    sys.argv[0] = CANONICAL
    with open(CANONICAL) as f:
        code = f.read()
    exec(code)
