import struct
import wave
from chunk import Chunk
from StringIO import StringIO


# Sample Loop Format
# Offset    Size    Description    Value
# 0x00    4    Cue Point ID    0 - 0xFFFFFFFF
# 0x04    4    Type    0 - 0xFFFFFFFF
# 0x08    4    Start    0 - 0xFFFFFFFF
# 0x0C    4    End    0 - 0xFFFFFFFF
# 0x10    4    Fraction    0 - 0xFFFFFFFF
# 0x14    4    Play Count    0 - 0xFFFFFFFF
def create_sample_loop(nframes):
    sample_loop = struct.pack('<LLLLLL', 0, 0, 0, nframes-1, 0, 0)
    return sample_loop   


# Sampler Chunk Format
# Offset    Size    Description    Value
# 0x00    4    Chunk ID    "smpl" (0x736D706C)
# 0x04    4    Chunk Data Size    36 + (Num Sample Loops * 24) + Sampler Data
# 0x08    4    Manufacturer    0 - 0xFFFFFFFF
# 0x0C    4    Product    0 - 0xFFFFFFFF
# 0x10    4    Sample Period    0 - 0xFFFFFFFF
# 0x14    4    MIDI Unity Note    0 - 127 (Here goes root note)
# 0x18    4    MIDI Pitch Fraction    0 - 0xFFFFFFFF
# 0x1C    4    SMPTE Format    0, 24, 25, 29, 30
# 0x20    4    SMPTE Offset    0 - 0xFFFFFFFF
# 0x24    4    Num Sample Loops    0 - 0xFFFFFFFF
# 0x28    4    Sampler Data    0 - 0xFFFFFFFF
# 0x2C    
# List of Sample Loops
def create_sampler_chunk(note, samples_per_second, nframes, add_loop=False):
    num_sample_loops = 1 if add_loop else 0
    sampler_chunk = struct.pack('<4sLLLLLLLLLL', 'smpl', 60,
                                0, 0,
                                samples_per_second,
                                note,
                                0, 0, 0,
                                num_sample_loops,
                                0)
    if add_loop:
        sampler_chunk += create_sample_loop(nframes)
    return sampler_chunk


def get_core_wave_info(buf):
    chf = Chunk(buf, bigendian = 0)
    datasize = chf.getsize()
    chf.read(4)
    root_note_position = None
    sampler_position = None
    sampler_size = None
    root_note = None
    _nframes = None
    
    while 1:
        try:
            chunk = Chunk(buf, bigendian=False)
        except EOFError:
            break
        chunkname = chunk.getname()
        
        if chunkname == 'fmt ':
            wFormatTag, _nchannels, _framerate, dwAvgBytesPerSec, wBlockAlign = struct.unpack('<HHLLH', chunk.read(14))
            if wFormatTag == wave.WAVE_FORMAT_PCM:
                sampwidth = struct.unpack('<H', chunk.read(2))[0]
                _sampwidth = (sampwidth + 7) // 8
            else:
                raise Exception, 'unknown format: %r' % (wFormatTag,)
            _framesize = _nchannels * _sampwidth
            samples_per_second = int(round(1. / _framerate * 1000000000))
        elif chunkname == 'data':
            _nframes = chunk.chunksize // _framesize
        elif chunkname == 'smpl':
            sampler_position = buf.tell() - 8
            sampler_size = chunk.getsize() + 8
            chunk.read(12)
            root_note_position = buf.tell()
            root_note, = struct.unpack('<L', chunk.read(4))
            break
        
        chunk.skip()

    word_aligned = is_word_aligned(buf, chunk)
    return {'word_aligned': word_aligned,
            'sampler_position': sampler_position,
            'sampler_size': sampler_size,
            'datasize': datasize,
            'nframes': _nframes,
            'samples_per_second': samples_per_second,
            'root_note': root_note,
            'root_note_position': root_note_position}


def is_word_aligned(buf, chunk):
    if (chunk.chunksize & 1) == 0:
        return True
    
    pos = buf.tell()
    buf.seek(-1, 2)
    last_byte = buf.read(1)
    buf.seek(pos)
    return last_byte == '\x00'

def write_data_size(buf, wave_info):
    sz = wave_info['datasize']
    buf.seek(4)
    buf.write(struct.pack('<L', sz))


def write_sampler_chunk(buf, note, wave_info, add_loop=True):
    sampler_chunk = create_sampler_chunk(note, wave_info['samples_per_second'] , wave_info['nframes'], add_loop=True)
    sampler_chunk_len = len(sampler_chunk) 
    buf.seek(0, 2)
    if not wave_info['word_aligned']:
        buf.write('\x00')
        sampler_chunk_len += 1
    buf.write(sampler_chunk)
    wave_info['datasize'] += sampler_chunk_len
    write_data_size(buf, wave_info)


def remove_sampler_chunk(buf, wave_info):
    sampler_position = wave_info['sampler_position']
    sampler_size = wave_info['sampler_size']
    if sampler_position is not None:
        data = buf.read()
        data = data[:sampler_position] + data[sampler_position+sampler_size:]
        buf.truncate(0)
        buf.seek(0)
        buf.write(data)
        wave_info['datasize'] -= sampler_size
        write_data_size(buf, wave_info)

def write_root_note(buf, note, wave_info):
    buf.seek(wave_info['root_note_position'])
    buf.write(struct.pack('<H', note))


def insert_root_note(f, wave_info, note):
    buf = StringIO(f.read())
    if wave_info['root_note_position'] is not None:
        write_root_note(buf, note, wave_info)
    else:
        write_sampler_chunk(buf, note, wave_info, add_loop=True)
    buf.seek(0)
    return buf.read()


def get_wave_info(f):
    data = f.read()
    buf = StringIO(data)
    buflen = len(data)
    wave_info = get_core_wave_info(buf)
    wave_info['filesize'] = buflen
    return wave_info


def modify_wav(fn, note):
    f = open(fn, 'rb')
    wave_info = get_wave_info()
    f.seek(0)
    new_data = insert_root_note(f, wave_info, note)
    with open(fn, 'wb') as f:
        f.write(new_data)


if __name__ == '__main__':
    fn = 'B.wav'
    note = 59   
    modify_wav(fn, note)

