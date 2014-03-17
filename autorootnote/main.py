import sys

from PyQt4 import QtGui

import noteutil
import notematch
import rootnote

import batchui.fileutil as fileutil
import batchui.batchui as batchui

import waveutil

COLUMNS = [('short_fn', 'Filename'),
           ('guessed_root', 'Guessed note'),
           ('guessed_midi', 'Guessed MIDI'),
           ('current_root', 'Current note'),
           ('current_midi', 'Current MIDI'),
           ('status_text', 'Status')]


def parse_file(fn, preferences, parameters):
    wave_info = waveutil.get_file_info(fn)
    short_fn = fileutil.shorten_fn(fn) 
    current_midi = ''
    current_root = ''
    guessed_root = ''
    guessed_midi =  ''
    note = None
    exception = None
    
    if wave_info is None:
        raise Exception('Not a valid wave file.')
    
    if wave_info['root_note'] is not None:
        current_midi = '%s' % wave_info['root_note']
        current_root = noteutil.pitch_to_name(wave_info['root_note'])

    guessed_root_maybe = notematch.extract_root_name(fn)
    if guessed_root_maybe is not None:
        note = noteutil.name_to_pitch(guessed_root_maybe)
        guessed_midi = '%s' % note
        guessed_root = guessed_root_maybe
    else:
        raise Exception('Cannot guess root note.')
        
    item = {'fn': fn,
            'short_fn': short_fn,
            'guessed_root': guessed_root,
            'guessed_midi': guessed_midi,
            'current_root': current_root,
            'current_midi': current_midi,
            'wave_info': wave_info,
            'note': note,
            'exception': exception}
    
    return item


def process_item(item, should_backup, preferences, parameters):
    if item.data['note'] is None or item.data['status'] == 'processed':
        return
    waveutil.modify_root_note(item.data['fn'],
                              item.data['wave_info'],
                              item.data['note'],
                              backup=should_backup)
    item.data['current_midi'] = item.data['guessed_midi']
    item.data['current_root'] = item.data['guessed_root']
    print item.data


def on_remove_loop_info(items):
    for item in items:
        wave_info = waveutil.get_file_info(item.data['fn'])
        with open(item.data['fn'], 'rb+') as f:
            rootnote.remove_sampler_chunk(f, wave_info)
        wave_info = waveutil.get_file_info(item.data['fn'])

        item.data['current_midi'] = None
        item.data['current_root'] = None
        item.data['wave_info'] = wave_info
        item.data['status'] = 'pending'


def main():
    argv = sys.argv[1:]
    app = QtGui.QApplication(argv)
    actions = [('Remove loop info', on_remove_loop_info)]
    window = batchui.BatchWindow('AutoRootNote',
                                 parse_file,
                                 process_item,
                                 columns=COLUMNS,
                                 actions=actions,
                                 is_valid_file=waveutil.is_valid_wave)
    sys.exit(app.exec_())    

if __name__ == '__main__':
    main()
