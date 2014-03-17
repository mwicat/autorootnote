=============
AutoRootNote
=============

A tool to automap the sample root key basing on its filename.

.. image:: https://github.com/mwicat/autorootnote/releases/download/v0.0.1/screenshot1.png

Installation
------------

Windows
~~~~~~~~~

Just download and launch the latest released `autorootnote.exe`
from https://github.com/mwicat/autorootnote/releases.

From source
~~~~~~~~~~~~~

To install using `pip`::

	pip install -e git+https://github.com/mwicat/autorootnote.git#egg=autorootnote

Ensure you have PyQt4 installed on your system, for Debian::

	sudo apt-get install python-qt4

Getting started
---------------

When the main `AutoRootNote` window appears, you can drag and drop to it sample files
and even whole directories. 

If root note can be guessed from the filename,
it will be shown in the `Guessed note` column. Otherwise, you should ensure
that sample filename is recognizable by the application.

When you are ready, hit the `Process` button.

Files can be deleted from the process queue by selecting them on the list and
hitting `delete` key.

Filename patterns
~~~~~~~~~~~~~~~~~~

The general rule for root key extraction is to seek for something that looks
like a note letter with optional sharp sign and octave number and is not
preceded nor followed by any other letter. Valid examples:

* K04Organ-D#1.wav
* HK002_d4.wav
* Arp E C4.wav

Warning
---------------

This is a free software and is delivered to you without any warranty. Use at your
own risk. As with any data tampering software, `AutoRootNote` can occasionaly damage 
files if a bug occurs, so please be sure to backup your precious samples first.
