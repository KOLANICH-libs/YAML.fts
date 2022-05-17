#!/usr/bin/env python3

import datetime
import math
import shutil
import typing
from ast import literal_eval
from datetime import date, timezone
from pathlib import Path

import cbor2
import pytz
import ruamel.yaml
from ruamel.yaml import YAML
from fsutilz import copytree, movetree


def loadYAML(t: typing.Union[str, Path]):
	y = YAML(typ="safe")
	try:
		return False, y.load(t)
	except ruamel.yaml.composer.ComposerError as ex:
		return True, list(y.load_all(t))

def serializeYAML(res) -> str:
	from io import StringIO
	y = YAML(typ="unsafe")
	y.indent(mapping=2, sequence=4, offset=2)

	with StringIO() as f:
		y.dump(res, f)
		return f.getvalue()

def moveWithAux(targetDir, el, corrData):
	if corrData:
		for corrEl in corrData:
			shutil.move(corrEl, targetDir / el.name)
	el.rename(targetDir / el.name)

def convertAndMoveWithAuxDataAutodetectDir(el, dataDir):
	corrData = set(el.parent.glob(el.stem + ".*")) - {el}
	if len(corrData) == 1:
		validDir = dataDir / next(iter(corrData)).suffix[1:]
	else:
		validDir = dataDir / "valid"
	_convertAndMove(el, validDir, corrData)


def convertAndMoveWithAuxDataSameDir(el, validDir):
	corrData = set(el.parent.glob(el.stem + ".*")) - {el}
	_convertAndMove(el, el.parent, corrData)


def _convertAndMove(el, validDir, corrData):
	validMultiDir = validDir / "multi"
	unhashableDir = validDir / "unhashable"
	ctorErrorDir = validDir / "noCtor"
	invalidDir = validDir / "invalid"
	invalidCBORDir = validDir / "cborError"

	try:
		isMulti, d = loadYAML(el.read_bytes().strip())

		if isMulti:
			validMultiDir.mkdir(parents=True, exist_ok=True)

		cborRes = (validDir if not isMulti else validMultiDir) / (el.stem + ".cbor")
		try:
			cborRes.write_bytes(cbor2.dumps(d, timezone=timezone.utc))
		except:
			invalidCBORDir.mkdir(parents=True, exist_ok=True)
			moveWithAux(invalidCBORDir, el, corrData)
			return

	except Exception as ex:
		print(el)
		print(repr(ex))
		if "found unhashable key" in str(ex):
			unhashableDir.mkdir(parents=True, exist_ok=True)
			moveWithAux(unhashableDir, el, corrData)
			return

		if "could not determine a constructor for the tag" in str(ex):
			ctorErrorDir.mkdir(parents=True, exist_ok=True)
			moveWithAux(ctorErrorDir, el, corrData)
			return

		invalidDir.mkdir(parents=True, exist_ok=True)
		moveWithAux(invalidDir, el, corrData)
	else:
		if isMulti:
			moveWithAux(validMultiDir, el, corrData)
		else:
			moveWithAux(validDir, el, corrData)


RUAMEL_YAML_TESTS_DATA_DIR = Path("./ruamel.yaml/")
RUAMEL_YAML_DATA_DIR = Path("./ruamel.yaml.data/")

noDataNames = {"dumper-error", "emitter-error", "former-dumper-error", "former-loader-error", "loader-error", "loader-warning", "stream-error", "single-loader-error", "recursive"}

uselessFiles = {"structure", "unicode", "skip-ext", "roundtrip", "path", "events", "marks", "recursive"}


def convertRuamelTestsDirIntoFTS(dataDir):
	for ext in noDataNames:
		subDirName = dataDir / ext
		subDirName.mkdir(parents=True, exist_ok=True)
		for f in dataDir.glob("*." + ext):
			shutil.move(f, subDirName / f.name)

	for uselessExt in uselessFiles:
		for f in dataDir.glob("*." + uselessExt):
			f.unlink()

	for el in sorted(set(dataDir.glob("*.data"))):
		convertAndMoveWithAuxDataAutodetectDir(el, dataDir)

	errorsDir = dataDir / "errors"
	errorsDir.mkdir(parents=True, exist_ok=True)

	for el in noDataNames:
		if el.endswith("-error"):
			errKind = el[: -len("-error")]
			(dataDir / el).rename(errorsDir / errKind)

	(dataDir / "error").rename(errorsDir / "error")

	validDir = dataDir / "valid"

	for f in dataDir.glob("*.data"):
		convertAndMoveWithAuxDataSameDir(f, validDir)

	for ext in noDataNames:
		for f in (dataDir / ext).glob("*/*." + ext):
			newName = f.parent / (f.stem + ".yaml")
			f.rename(newName)
			f = newName
			convertAndMoveWithAuxDataSameDir(f, dataDir)

	#for f in (dataDir / "recursive").glob("*.recursive"):
	#	res = {}
	#	exec(f.read_text(), res)
	#	d = res["value"]
	#	(f.parent / (f.stem + ".cbor")).write_bytes(cbor2.dumps(d, timezone=timezone.utc, value_sharing=True))
	#	(f.parent / (f.stem + ".yaml")).write_text(serializeYAML(d))

	movetree(dataDir / "code", validDir)

	for f in dataDir.glob("**/*.data"):
		f.rename(f.parent / (f.stem + ".yaml"))

def convertRuamelYamlDataIntoFTS(dataDir):
	for f in dataDir.glob("*.yaml"):
		convertAndMoveWithAuxDataSameDir(f, f.parent)

if __name__ == "__main__":
	convertRuamelTestsDirIntoFTS(RUAMEL_YAML_TESTS_DATA_DIR)
	#convertRuamelYamlDataIntoFTS(RUAMEL_YAML_DATA_DIR)
