import cPickle
from ConfigParser import ConfigParser
import imp
import os, sys
import string, template

###################
# Plugin handling #
###################

plugins = None
def get_active_plugins(tree=None):
  """ Return all plugins that are used by the tree.
      If tree is None, then all usable plugins are returned. """
  global plugins
  if plugins is None:
    plugins = load_plugins()
  # XXX: filter out the tree
  return plugins

def load_plugins():
  # XXX: discover and iterate over available plugins
  basedir = os.path.realpath(os.path.dirname(sys.argv[0]))
  m = imp.find_module('indexer', [os.path.join(basedir, 'xref-tools/cxx-clang')])
  module = imp.load_module('dxr.cxx-clang', m[0], m[1], m[2])
  plugins = [module]
  return plugins

def store_big_blob(tree, blob):
  htmlroot = os.path.join(tree.wwwdir, tree.tree + '-current')
  dbdir = os.path.join(htmlroot, '.dxr_xref')
  f = open(os.path.join(dbdir, 'index_blob.dat'), 'wb')
  try:
    cPickle.dump(blob, f, 2)
  finally:
    f.close()

def load_big_blob(tree):
  htmlroot = os.path.join(tree.wwwdir, tree.tree + '-current')
  dbdir = os.path.join(htmlroot, '.dxr_xref')
  f = open(os.path.join(dbdir, 'index_blob.dat'), 'rb')
  try:
    return cPickle.load(f)
  finally:
    f.close()

class DxrConfig(object):
  def __init__(self, config, tree=None):
    self._tree = tree
    self.xrefscripts = os.path.abspath(config.get('DXR', 'xrefscripts'))
    self.templates = os.path.abspath(config.get('DXR', 'templates'))
    self.wwwdir = os.path.abspath(config.get('Web', 'wwwdir'))
    self.virtroot = os.path.abspath(config.get('Web', 'virtroot'))
    self.hosturl = config.get('Web', 'hosturl')
    if self.hosturl.endswith('/'):
      self.hosturl = self.hosturl[:-1]
    self.glimpse = os.path.abspath(config.get('DXR', 'glimpse'))
    self.glimpseindex = os.path.abspath(config.get('DXR', 'glimpseindex'))

    if tree is None:
      self.trees = []
      for section in config.sections():
        if section == 'DXR' or section == 'Web':
          continue
        self.trees.append(DxrConfig(config, section))
    else:
      self.tree = self._tree
      for opt in config.options(tree):
        self.__dict__[opt] = config.get(tree, opt)
        if opt.endswith('dir'):
          self.__dict__[opt] = os.path.abspath(self.__dict__[opt])

  def getTemplateFile(self, name):
    tmpl = template.readFile(os.path.join(self.templates, name))
    tmpl = string.Template(tmpl).safe_substitute(**self.__dict__)
    return tmpl


def load_config(path):
  config = ConfigParser()
  config.read(path)

  return DxrConfig(config)

__all__ = ['get_active_plugins', 'store_big_blob', 'load_big_blob',
  'load_config']