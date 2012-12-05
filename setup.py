import os
import glob
import sys

from setuptools import setup

def find_data_files(source, target, patterns):
  """Locates the specified data-files and returns the matches
  in a data_files compatible format.

  source is the root of the source data tree.
    Use '' or '.' for current directory.
  target is the root of the target data tree.
    Use '' or '.' for the distribution directory.
  patterns is a sequence of glob-patterns for the
    files you want to copy.

  From http://www.py2exe.org/index.cgi/data_files
  """
  if glob.has_magic(source) or glob.has_magic(target):
    raise ValueError("Magic not allowed in source, target")
  ret = {}
  for pattern in patterns:
    pattern = os.path.join(source, pattern)
    for filename in glob.glob(pattern):
      if os.path.isfile(filename):
        targetpath = os.path.join(target, os.path.relpath(filename, source))
        path = os.path.dirname(targetpath)
        ret.setdefault(path, []).append(filename)
  return sorted(ret.items())

# For locating source files
sys.path.append("src")

options = {
  "py2exe": {
    "bundle_files": 2, # Bundle everything but the Python interpreter
    "compressed": True,
    "optimize": 2,
    "ascii": True,
    "packages": ["OpenGL.arrays", "OpenGL.platform"],
    "dll_excludes": ["w9xpopen.exe"],
    "excludes": [
      # Built-in stuff
      "_ssl", "BaseHTTPServer", "bz2", "calendar", "curses", "distutils",
      "doctest", "email", "ftplib", "httplib", "inspect", "locale", "md5",
      "multiprocessing", "pdb", "pickle",

      # Tcl/Tk
      "Tkconstants", "Tkinter", "tcl",

      # PIL/Tk stuff
      "_imagingtk", "PIL._imagingtk", "ImageTk", "PIL.ImageTK", "FixTk",

      # Unused Pygame features
      "pygame.font", "pygame.mixer", "pygame.movie"
    ],
    "dist_dir": "dist/win32"
  },
  "py2app": {
    "app": ["src/main.py"],
    "argv_emulation": True,
    "dist_dir": "dist/mac"
  }
}

extraOpts = {}
if os.name == "nt":
  import py2exe
  setupRequires = ["py2exe"]
  extraOpts["windows"] = [
    {
      "script": "src/main.py",
      "dest_base": "mumei",
      "icon_resources": [(0, "assets/pickle.ico")]
    }
  ]
elif sys.platform == "darwin":
  setupRequires = ["py2app"]
else:
  setupRequires = []

setup(
  name="Mumei",
  version="0.1",
  url="https://github.com/aarmea/mumei",
  description="Mumei",
  data_files=find_data_files("assets", "assets", [
    "*.csv", "*.h", "*.png",
    "levels/*",
  ]),
  options=options,
  setup_requires=setupRequires,
  zipfile=None,
  **extraOpts
)
