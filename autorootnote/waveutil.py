import os
import rootnote
import batchui.fileutil as fileutil

def is_valid_wave(fn):
    ext = os.path.splitext(fn)[1]
    return ext == '.wav'

def get_file_info(fn):
    if not is_valid_wave(fn):
        return None    
    f = open(fn, 'rb')
    wave_info = rootnote.get_wave_info(f)
    return wave_info


def modify_root_note(fn, wave_info, note, backup=False):
    with open(fn, 'rb') as f:
        new_data = rootnote.insert_root_note(f, wave_info, note)
    if backup:
        fileutil.make_backup(fn)
    with open(fn, 'wb') as f:
        f.write(new_data)

