'''
MediaLister
'''

import os, logging

from mutagen.mp3 import MP3
from mutagen.flac import FLAC

import Track, Album

class Lister():
    '''Class for printing track lists'''

    def __init__(self, debug=False, type=None, path=None, outputfile=None):
        '''Initialize stuff we need'''
        self.albums = []
        self.upaths = []
        self.fpath = None
        self.type = None
        self.debug = debug
        self.opath = outputfile
        self.format = ""
        self.types = {
            'mp3' : '.mp3',
            'FLAC' : '.flac',
        }
        if not path:
            self.fpath = os.getcwd()
        else:
            self.fpath = path
        if type:
            self.type = (type, self.types[type])
        if self.debug:
            '''Log everything, and send it to stderr.'''
            logging.basicConfig(level=logging.DEBUG)

    def walktree(self, fpath):
        '''Walk the directory tree recursively'''
        ''' Go through the directorie '''
        for (wpath, dirs, files) in os.walk(self.fpath):
            totalnumfiles = len(files)
            if totalnumfiles > 0:
                '''Prune all files that are not of the type we want'''
                if self.type:
                    files = self.prune(files)
                '''go through the remaining files'''
                for file in files:
                    #if self.debug: print file
                    fpath = os.path.join(wpath,file)
                    fpath = os.path.normpath(fpath)
                    '''determine the file type'''
                    if os.path.isfile(fpath):
                        #if self.debug: print "%s is a file" % file
                        size = os.path.getsize(fpath)
                        track = self.chooseprocessor(fpath, size)
                        #print track.info.preset
                        if track != None:
                            '''get the album'''
                            album = self.getalbum(track)
                            '''add the track to the album'''
                            album.tracks.append(track)
                        else:
                            continue
                            #return False

    def prune(self, files):
        '''remove files that dont mat te specified type'''
        for file in files:
            #if self.type != None: -- uneeded, method only entered if true in the first place
            test = os.path.splitext(file)[1].lower() == self.type[1]
            if not test:
                files.remove(file)
            else:
                #break # -- should be continue?
                continue
        return files

    def getalbum(self, track):
        '''obtain the album'''
        for album in self.albums:
            if album.title == track.album:
                return album
        '''create the album'''
        album = Album.Album(track.album, track.artist, track.date, self.format)
        '''add the track to the album'''
        self.albums.append(album)
        '''obtain the album'''
        for album in self.albums:
            if album.title == track.album:
                return album
        pass

    def addalbum(self, album):
        try:
            i = self.albums.index(album.title)
            return True
        except ValueError:
            self.albums.append(album)
            return False
        except:
            return False

    def validate(self,fpath):
        ''' Check if file is an mp3 or a flac file '''
        if os.path.splitext(fpath)[1].lower() == '.mp3':
            return "MP3"
        if os.path.splitext(fpath)[1].lower() == '.flac':
            return "FLAC"
        else:
            return None

    def chooseprocessor(self, fpath, size):
        '''choose the class to use'''
        self.format = self.validate(fpath)
        if not self.format:
            return None
        if self.format == "MP3":
            audioproc = MP3(fpath)
        else:
            audioproc = FLAC(fpath)
        otrack = Track.Track(audioproc, size)
        return otrack

    def getsize(self, fpath):
        '''get file size'''
        return os.path.getsize(fpath)

    def printtemplate(self, albums):
        from TemplateHandler import TemplateHandler
        t = TemplateHandler()
        t.loadtemplate()
        
        vd = {
            'albums' : self.albums,
            }
        logging.debug('! vd: %s' % str(vd))
        return t.printfilledtemplate(vd)
