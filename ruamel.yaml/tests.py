#!/usr/bin/env python3
import mmap
import os
import sys
import unittest
from collections import OrderedDict
from pathlib import Path
import typing

from fileTestSuite.unittest import FileTestSuiteTestCaseMixin

dict = OrderedDict

thisDir = Path(__file__).resolve().absolute().parent
repoRootDir = thisDir.parent

sys.path.insert(0, str(repoRootDir))

import cbor2
from icecream import ic

thisDir = Path(__file__).resolve().absolute().parent

def object_hook(decoder, value):
	if isinstance(value, dict):
		return value

	return Point(value['x'], value['y'])

class YAMLTestClassMixin(FileTestSuiteTestCaseMixin):
	maxDiff = None

	@property
	def fileTestSuiteDir(self) -> Path:
		return thisDir

	def loadYAML(self, t: bytes):
		raise NotImplementedError("Implement the loadYAML method")

	def _testProcessorImpl(self, challFile: Path, respFile: Path, paramsDict=None) -> None:
		self._testChallengeResponsePair(challFile.read_bytes(), respFile.read_bytes())

	def _testChallengeResponsePair(self, chall: bytes, resp: bytes):
		y = self.loadYAML(chall)
		c = cbor2.loads(resp)
		self.assertEqual(c, y)

"""
from ruamel.yaml import YAML
class RuamelYAMLTestClass(unittest.TestCase, YAMLTestClassMixin):
	def loadYAML(self, t: bytes):
		y = YAML(typ="safe")
		return y.load(t)
"""

"""
import yaml
class PyYAMLTestClass(unittest.TestCase, YAMLTestClassMixin):
	def loadYAML(self, t: bytes):
		return yaml.load(t, Loader=yaml.SafeLoader)
"""

from ryml import parse_to_python
class RapidYAMLTestClass(unittest.TestCase, YAMLTestClassMixin):
	def loadYAML(self, t: bytes):
		return parse_to_python(t)

if __name__ == "__main__":
	unittest.main()
