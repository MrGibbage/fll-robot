"""Paths and constants. Override any path with an environment variable."""
import os
REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LDRAW_LIB  = os.environ.get('LDRAW_LIB',  os.path.join(REPO, 'lib', 'ldraw'))          # official library (setup.sh downloads it)
STUDIO_LIB = os.environ.get('STUDIO_LIB', os.path.join(REPO, 'lib', 'studio-ldraw'))   # your own Stud.io library (optional)
_inv = os.path.join(REPO, 'profile', 'inventory.csv')
INVENTORY  = os.environ.get('FLL_INVENTORY', _inv if os.path.exists(_inv) else os.path.join(REPO, 'profile', 'inventory.example.csv'))
DESIGNS    = os.environ.get('FLL_DESIGNS', os.path.join(REPO, 'designs'))               # your models (git-ignored); used for usage counts
CATALOG_OUT= os.environ.get('FLL_CATALOG_OUT', os.path.join(REPO, 'PARTS_CATALOG.md'))   # point elsewhere for a private catalog
# SPIKE Prime kit electronics + common kit wheels: always "owned"
KIT = {'bb1142c01','55422c01','54675','54696','37308c01','39367pb01','41896','41897','15038p01','44771','73090b'}
