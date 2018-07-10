#!/usr/bin/env python
# -*- coding: utf-8 -*-

import glob
import json
import os
import re
import subprocess
import tempfile

from unittest2 import TestCase

from i18n.utils import I18nFileWrapper

from ddt import ddt, idata, unpack

EN_FR = {
  'to': u'à',
  'the': u'la',
  'a': u'une',
  'of': u'de',
  'students': u'élèves',
  'and': u'et',
  'in': u'dans',
  'will': u'volonté',
  'this': u'ce',
  'for': u'pour',
  'lesson': u'leçon',
  'that': u'cette',
  'loops': u'boucles',
  'is': u'est',
  'be': u'être',
  'with': u'avec',
  'debugging': u'débogage',
  'class': u'classe',
  'your': u'votre',
  'programming': u'la programmation',
  'on': u'sur',
  'their': u'leur',
  'an': u'un',
  'as': u'comme',
  'each': u'chaque',
  'student': u'étudiant',
  'we': u'nous',
  'have': u'avoir',
  'how': u'comment',
  'group': u'groupe',
  'they': u'ils',
  'are': u'sont',
  'make': u'faire',
  'or': u'ou',
  'using': u'en utilisant',
  'think': u'pense',
  'out': u'en dehors'
}

def _translate(data):
    if isinstance(data, dict):
        return {key: _translate(data[key]) for key in data.keys()}
    elif isinstance(data, list):
        return [_translate(datum) for datum in data]
    elif isinstance(data, basestring):
        for en, fr in EN_FR.iteritems():
            data = re.sub(r"\b{}\b".format(en), fr, data)
        return data
    else:
        print("don't know how to translate {}".format(data))
        return data

def _get_source_and_translated_data_from_file(source_path):
    redacted_data = _redact(source_path)
    translated_data = _translate(redacted_data)
    restored_json = _restore(source_path, translated_data)
    parsed_source_data = _parse(source_path=source_path)
    parsed_restored_data = _parse(source_json=restored_json)
    return (parsed_source_data, parsed_restored_data)

def _restore(source_path, translated_data):
    with tempfile.NamedTemporaryFile() as translated:
        json.dump(translated_data, translated)
        translated.flush()
        restore = subprocess.Popen([
            "restore",
            "-s", source_path,
            "-r", translated.name,
            "-p", ",".join(glob.glob(os.path.join(I18nFileWrapper.i18n_dir(), "config", "plugins", "*.js")))
        ], stdout=subprocess.PIPE)
        restored_json, err = restore.communicate()
        return restored_json

def _redact(source_path):
    redact = subprocess.Popen([
        "redact", source_path,
        "-p", ",".join(glob.glob(os.path.join(I18nFileWrapper.i18n_dir(), "config", "plugins", "*.js")))
    ], stdout=subprocess.PIPE)
    redacted_json, err = redact.communicate()
    return json.loads(redacted_json)

def _parse(source_path=None, source_json=None):
    if source_path:
        parse = subprocess.Popen([
            "parse", source_path,
            "-p", ",".join(glob.glob(os.path.join(I18nFileWrapper.i18n_dir(), "config", "plugins", "*.js")))
        ], stdout=subprocess.PIPE)
        parsed_json, err = parse.communicate()
    elif source_json:
        parse = subprocess.Popen([
            "parse",
            "-p", ",".join(glob.glob(os.path.join(I18nFileWrapper.i18n_dir(), "config", "plugins", "*.js")))
        ], stdin=subprocess.PIPE, stdout=subprocess.PIPE)
        parsed_json, err = parse.communicate(input=source_json)

    return json.loads(parsed_json)

def _map_mdast(node):
    result = {
        "type": node["type"]
    }

    if "children" in node:
        result["children"] = [_map_mdast(child) for child in node["children"]] 

    return result


class NamedList(list):
    def __init__(self, name, *args):
        self.__name__ = name
        return super(NamedList, self).__init__(*args)

def _annotate(left, right):
    return [NamedList(key, [left[key], right[key]]) for key in left.keys()]

curriculum_file = os.path.join(I18nFileWrapper.i18n_dir(), 'tests', 'data', "curriculum" + '.json')
lesson_file = os.path.join(I18nFileWrapper.i18n_dir(), 'tests', 'data', "lesson" + '.json')
unit_file = os.path.join(I18nFileWrapper.i18n_dir(), 'tests', 'data', "unit" + '.json')

@ddt
class RedactRestoreTestCase(TestCase):

    @idata(_annotate(*_get_source_and_translated_data_from_file(curriculum_file)))
    @unpack
    def test_curriculum_data(self, *args):
        self._run_tests(*args)

    @idata(_annotate(*_get_source_and_translated_data_from_file(lesson_file)))
    @unpack
    def test_lesson_data(self, *args):
        self._run_tests(*args)

    @idata(_annotate(*_get_source_and_translated_data_from_file(unit_file)))
    @unpack
    def test_unit_data(self, *args):
        self._run_tests(*args)

    def _run_tests(self, source, restored):
        self.assertEqual(set(source.keys()), set(restored.keys()))
        for key in source.keys():
            with self.subTest(key=key):
                self.assertEqual(_map_mdast(source[key]), _map_mdast(restored[key]))
