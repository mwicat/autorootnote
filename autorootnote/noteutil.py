NOTE_POS = 'C C# D D# E F F# G G# A A# B'.split()

def name_to_pitch(name):
    octave = int(name[-1])
    short_name = name[:-1]
    pos = NOTE_POS.index(short_name.upper())
    pitch = octave * 12 + pos
    return pitch

def pitch_to_name(pitch):
    octave = pitch / 12
    short_name = NOTE_POS[pitch % 12]
    name = '%s%s' % (short_name, octave)
    return name