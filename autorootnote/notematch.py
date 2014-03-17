import re

NOTE_RE = re.compile(r'.*[^a-zA-Z0-9]([BCDEFGA][#]?[0-9])[^a-zA-Z0-9].*', re.I)

def extract_root_name(name):
    res = NOTE_RE.search(name)
    return res.group(1).upper() if res is not None else None


if __name__ == '__main__':
    test_names = ['K04Organ-D#1.wav',
                  'K04Organ-B1.wav',
                  './synth/ARP Odyssey/Arp E Multi/Arp E C4.wav',
                  'BassK02-C4.wav', './floorfilling/Drum_Hits/Nu-Disco_PERC40.wav', 'HK002_d4.wav']
    for name in test_names:
        print name, extract_root_name(name)