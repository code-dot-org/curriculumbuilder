# -*- coding: utf-8 -*-

from __future__ import print_function
import glob
import json
import os
import re
import subprocess
import tempfile

from ddt import ddt, idata, unpack
from unittest2 import TestCase

from i18n.utils import I18nFileWrapper

# Of the top twenty words in the initial curriculumbuilder data set, take out
# all those like "r" that represent control characters and all the things like
# "csf" that don't actually have translations, and put together a super-basic
# english-to-french translation scheme for them.
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
    """
    Given a source file, redact, translate, and restore all data in that file
    and return a tuple containing the original data from the file as well as the
    generated result
    """
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
            "node_modules/.bin/restore",
            "-s", source_path,
            "-r", translated.name,
            "-p", ",".join(glob.glob(os.path.join(I18nFileWrapper.i18n_dir(), "config", "plugins", "*.js")))
        ], stdout=subprocess.PIPE)
        restored_json, err = restore.communicate()
        return restored_json

def _redact(source_path):
    redact = subprocess.Popen([
        "node_modules/.bin/redact", source_path,
        "-p", ",".join(glob.glob(os.path.join(I18nFileWrapper.i18n_dir(), "config", "plugins", "*.js")))
    ], stdout=subprocess.PIPE)
    redacted_json, err = redact.communicate()
    return json.loads(redacted_json)

def _parse(source_path=None, source_json=None):
    if source_path:
        parse = subprocess.Popen([
            "node_modules/.bin/parse", source_path,
            "-p", ",".join(glob.glob(os.path.join(I18nFileWrapper.i18n_dir(), "config", "plugins", "*.js")))
        ], stdout=subprocess.PIPE)
        parsed_json, err = parse.communicate()
    elif source_json:
        parse = subprocess.Popen([
            "node_modules/.bin/parse",
            "-p", ",".join(glob.glob(os.path.join(I18nFileWrapper.i18n_dir(), "config", "plugins", "*.js")))
        ], stdin=subprocess.PIPE, stdout=subprocess.PIPE)
        parsed_json, err = parse.communicate(input=source_json)

    return json.loads(parsed_json)


def _map_mdast(node):
    """
    Walk a MDAST and return a "map" that includes just the hierarchy and types
    of nodes, but none of the inner content of those nodes. Can be used to
    easily compare, for example, two trees which represent the same basic
    content in two different languages, and verify that they produce the same
    basic HTML structure.

    See https://github.com/syntax-tree/mdast for MDAST specification
    """
    result = {
        "type": node["type"]
    }

    if "children" in node:
        result["children"] = [_map_mdast(child) for child in node["children"]] 

    return result

def _annotate(left, right):
    """
    This is kinda dumb. The data-driven test library we're using will only give
    the generated tests useful names if `data.__name__` exists. But since our
    data is a primitive type (specifically, a list) we can't actually set
    arbitrary attributes on it (which raises the question of why the authors of
    the library picked that as the metric in the first place).

    To get around that, we create a simple subclass of list that allows us to
    set the __name__ attribute and annontate our data with something useful.

    See http://ddt.readthedocs.io/en/latest/api.html#ddt.ddt
    """
    return [NamedList(key, [left[key], right[key]]) for key in left.keys()]

class NamedList(list):
    def __init__(self, name, *args):
        self.__name__ = name
        return super(NamedList, self).__init__(*args)


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
        # Each entry represents a single piece of content, which can have
        # several individual fields. Verify that the source and redacted
        # versions have the same fields, and check each field pairwise against
        # both source and redacted.
        self.assertEqual(set(source.keys()), set(restored.keys()))
        for key in source.keys():
            with self.subTest(key=key):
                # no matter the changes made in the redaction, translation, and
                # restoration process, the restored data should still produce
                # the same HTML structure (but not necessarily the same text
                # content) as the original markdown
                self.assertEqual(_map_mdast(source[key]), _map_mdast(restored[key]))
