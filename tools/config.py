"""Paths and constants. Override any path with an environment variable."""
import os
REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LDRAW_LIB  = os.environ.get('LDRAW_LIB',  os.path.join(REPO, 'lib', 'ldraw'))          # official library (setup.sh downloads it)
STUDIO_LIB = os.environ.get('STUDIO_LIB', os.path.join(REPO, 'lib', 'studio-ldraw'))   # your own Stud.io library (optional)
_own = os.path.join(REPO, 'profile', 'parts.csv')                                     # a team's own list (git-ignored)
PARTS      = os.environ.get('FLL_PARTS', _own if os.path.exists(_own) else os.path.join(REPO, 'PARTS_AVAILABLE.csv'))
DESIGNS    = os.environ.get('FLL_DESIGNS', os.path.join(REPO, 'designs'))               # your models (git-ignored); used for usage counts
CATALOG_OUT= os.environ.get('FLL_CATALOG_OUT', os.path.join(REPO, 'PARTS_CATALOG.md'))   # point elsewhere for a private catalog
