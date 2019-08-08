# pylint: disable=missing-docstring,invalid-name,line-too-long
from django.test import TestCase

import markdown

class TestDetails(TestCase):
    """ Test details extension. """

    def setUp(self):
        self.markdown = markdown.Markdown(extensions=['curriculumBuilder.details:DetailsExtension'])

    def test_details_can_render(self):
        source = '::: details [summary-content]\n' + \
        'contents, which are sometimes further block elements\n' + \
        ':::'
        expected = '<details><summary><p>summary-content</p></summary><p>contents, which are sometimes further block elements</p></details>'

        rendered = self.markdown.convert(source)
        self.assertEqual(rendered, expected)

    def test_details_can_span_multiple_blocks(self):
        source = '::: details [summary-content]\n' + \
        '\n' + \
        'contents, which are sometimes further block elements\n' + \
        '\n' + \
        ':::'
        expected = '<details><summary><p>summary-content</p></summary><p>contents, which are sometimes further block elements</p></details>'

        rendered = self.markdown.convert(source)
        self.assertEqual(rendered, expected)

    def test_details_can_have_a_variable_number_of_opening_colons(self):
        source = ':::::::: details [summary-content]\n' + \
        'contents, which are sometimes further block elements\n' + \
        ':::::::::::::'
        expected = '<details><summary><p>summary-content</p></summary><p>contents, which are sometimes further block elements</p></details>'

        rendered = self.markdown.convert(source)
        self.assertEqual(rendered, expected)

    def test_details_can_render_markdown_syntax_in_the_summary(self):
        source = '::: details [**summary** _content_]\n' + \
        'contents, which are sometimes further block elements\n' + \
        ':::'
        expected = '<details><summary><p><strong>summary</strong> <em>content</em></p></summary><p>contents, which are sometimes further block elements</p></details>'

        rendered = self.markdown.convert(source)
        self.assertEqual(rendered, expected)

    def test_details_can_render_markdown_syntax_in_the_body(self):
        source = '::: details [summary-content]\n' + \
        '\n' + \
        '# Contents\n' + \
        '- can\n' + \
        '- be\n' + \
        '- markdown\n' + \
        '\n' + \
        ':::'
        expected = '<details><summary><p>summary-content</p></summary><h1>Contents</h1><ul>' + \
        '<li>can</li>' + \
        '<li>be</li>' + \
        '<li>markdown</li>' + \
        '</ul></details>'

        rendered = self.markdown.convert(source)
        self.assertEqual(rendered, expected)

    def test_details_ignores_trailing_colons(self):
        # Look how pretty this can be!
        source = '::::::::::::: details [summary-content] :::::::::::::\n' + \
        'contents, which are sometimes further block elements\n' + \
        ':::::::::::::::::::::::::::::::::::::::::::::::::::::'
        expected = '<details><summary><p>summary-content</p></summary><p>contents, which are sometimes further block elements</p></details>'

        rendered = self.markdown.convert(source)
        self.assertEqual(rendered, expected)

    def test_details_ignores_excess_whitespace(self):
        source = ':::      details       [summary-content]          \n' + \
        '\n' + \
        'contents, which are sometimes further block elements\n' + \
        '\n' + \
        ':::'
        expected = '<details><summary><p>summary-content</p></summary><p>contents, which are sometimes further block elements</p></details>'

        rendered = self.markdown.convert(source)
        self.assertEqual(rendered, expected)

    def test_details_can_nest(self):
        source = ':::: details [outer]\n' + \
        '::: details [inner]\n' + \
        'innermost content\n' + \
        ':::\n' + \
        '::::'
        expected = '<details><summary><p>outer</p></summary><details><summary><p>inner</p></summary><p>innermost content</p></details></details>'

        rendered = self.markdown.convert(source)
        self.assertEqual(rendered, expected)

    def test_details_requires_a_summary_block(self):
        source = '::: details\n' + \
        'contents, which are sometimes further block elements\n' + \
        ':::'
        expected = '<p>::: details\n' + \
        'contents, which are sometimes further block elements\n' + \
        ':::</p>'

        rendered = self.markdown.convert(source)
        self.assertEqual(rendered, expected)

    def test_details_requires_at_least_three_opening_colons(self):
        source = ':: details [summary-content]\n' + \
        'contents, which are sometimes further block elements\n' + \
        ':::'
        expected = '<p>:: details [summary-content]\n' + \
        'contents, which are sometimes further block elements\n' + \
        ':::</p>'

        rendered = self.markdown.convert(source)
        self.assertEqual(rendered, expected)
