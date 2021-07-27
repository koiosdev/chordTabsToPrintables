#!/usr/bin/env python3
##
# @file main.py
#
# @brief This program converts supported tablature source files to a printable format
#
# @section description Description
# Creates Song objects of all tablatures it can find in a given directory or its subdirectories
# Supported inputs currently: Any .txt file, as long as each section has a corresponding [<sectionName>] delimiter
# Supported outputs currently: PNG format
# Song objects are then parsed into separate metadata information and sections
# Sections contain lines of lyric and corresponding tablature data
# The program then tries to fit these sections within the chosen output dimensions (currently A4)
#   as best as it can, shrinking or growing sections to fit the remaining space
#
# @section notes Notes
# - Splitting raw text into lyric and tablature info is very basic at the moment.
#   We need a better way to classify & split the various channels (raw tab, lyrics, chords, more?) that can be expected in tablature
#
# @section todo TODO
# - Various prints should be printed at specific log levels, to easily switch between debug, info or warnings only

import lib.chordFinder
import lib.dataStructures
import lib.initSongs
import lib.transpose
import lib.config
import output2img
import output2txt

def main():
  # Init config file
  lib.config.initConfig()
  # Init Song objects for all songs with compatible inputs
  songs = lib.initSongs.getSongObjects()
  # Get what programs we are going to run
  configObj = lib.config.config['options']
  exportToImg = configObj['exporttoimg'] == '1'
  exportToTxt = configObj['exporttotxt'] == '1'
  exportToRaw = configObj['exporttoraw'] == '1'

  # Convert all songs into sections
  for song in songs:
    print("Start parsing of file '{}'...".format(song.inputFile)) 
    # Initialise internal data structures
    print("song file extension {}".format(song.fileExtension))
    if song.fileExtension == 'txt':
      song.initSections()
    elif song.fileExtension == 'rawtxt':
      song.initPreprocessed()
    else:
      print("File extension '{}' not supported. Skipping...".format(song.fileExtension))
      continue
    # If input is .raw output. If output to raw is set, overwrite itself
    # ready quickly using rules
    if not song.isParsed:
      print("Song was not initialized correctly. Skipping...")
      continue

    if exportToTxt:
      # Create subdirectory where we will output our images
      targetDirectory = song.outputLocation + "-txt"
      print("Successfully parsed file. Writing output to '{}'\n".format(targetDirectory)) 
      # Write out metadata and sections, as many as can fit on one page
      output2txt.outputToTxt(targetDirectory, False, song)
    if exportToRaw:
      # Create subdirectory where we will output our images
      targetDirectory = song.outputLocation + "-txt"
      print("Successfully parsed file. Writing output to '{}'\n".format(targetDirectory)) 
      # Write out metadata and sections, as many as can fit on one page
      output2txt.outputToTxt(targetDirectory, True, song)
    if exportToImg:
      # Fit all sections on each page, resizes down if it does not fit on width
      song.fitSectionsByWidth()
      # Prerender: calculate Pages, and move sections into Pages
      song.sectionsToPages()
      # Optimalisation: try to fill whitespace
      while len(song.pages) > song.maxPages:
        print("Resizing down since we have {} pages and want {} pages".format(len(song.pages), song.maxPages))
        song.resizeAllSections(-1)
        song.sectionsToPages()
      while song.canFillWhitespace():
        print("Resizing down to fill remaining vertical whitespace")
        song.resizeAllSections(-1)
        song.sectionsToPages()
      # Optimalisation: increase font size to fit target page amount
      song.increaseToMinPages()
      # Parse as PNG a4
      # Create subdirectory where we will output our images
      targetDirectory = song.outputLocation + "-a4-png"
      print("Successfully parsed file. Writing output to '{}'\n".format(targetDirectory)) 
      # Write out metadata and sections, as many as can fit on one page
      output2img.outputToImage(targetDirectory, song)

if __name__ == "__main__":
  main()
