from django.test import SimpleTestCase

from mezzanine.core.templatetags.mezzanine_tags import richtext_filters


class TipsTestCase(SimpleTestCase):
    """
    Test our custom "tips" markdown plugin
    """

    def test_rendering_basic_tip(self):
        markdown = (
            "!!!content <content-0>\n"
            "\n"
            "    ### Teaching this course as a class?\n"
            "    Our grade-aligned CS Fundamentals courses use unplugged lessons to build community and introduce tricky computer science concepts, including **events**. Check out the lesson [The Big Event Jr.](https://curriculum.code.org/csf-19/coursea/11/) from [Course A](https://curriculum.code.org/csf-19/coursea/)!\n"
        )
        expected = (
            '<div class="admonition content">\n'
                '<p class="admonition-title" id="content_content-0"><i class="fa fa-mortar-board"></i>Content Corner</p>\n'
                '<div></div>\n'
                '<div>\n'
                    '<h3 id="teaching-this-course-as-a-class">Teaching this course as a class?</h3>\n'
                    '<p>Our grade-aligned CS Fundamentals courses use unplugged lessons to build community and introduce tricky computer science concepts, including <strong>events</strong>. Check out the lesson <a href="https://curriculum.code.org/csf-19/coursea/11/" target="_blank">The Big Event Jr.</a> from <a href="https://curriculum.code.org/csf-19/coursea/" target="_blank">Course A</a>!</p>\n'
                '</div>\n'
            '</div>'
        )
        self.assertEqual(expected, richtext_filters(markdown))

    def test_rendering_tip_with_complex_content(self):
        markdown = (
            "!!!discussion <discussion-0>\n"
            "\n"
            "	**Goal:** Aim to hear a few different students share reasons that instructions are \"bad\". The point here is just to get students thinking and there's no specific answer you're driving towards. Some possible ideas, however, might include:\n"
            "    \n"
            "    * Instructions are not clear on what to do\n"
            "    * Instructions use confusing words\n"
            "    * Instructions don't actually accomplish what they're supposed to\n"
        )
        expected = (
            '<div class="admonition discussion">\n'
                '<p class="admonition-title" id="discussion_discussion-0"><i class="fa fa-comments"></i>Discussion Goal</p>\n'
                '<div></div>\n'
                '<div>\n'
                    '<p><strong>Goal:</strong> Aim to hear a few different students share reasons that instructions are "bad". The point here is just to get students thinking and there\'s no specific answer you\'re driving towards. Some possible ideas, however, might include:</p>\n'
                '</div>\n'
                '<div>\n'
                    '<ul>\n'
                        '<li>Instructions are not clear on what to do</li>\n'
                        '<li>Instructions use confusing words</li>\n'
                        '<li>Instructions don\'t actually accomplish what they\'re supposed to</li>\n'
                    '</ul>\n'
                '</div>\n'
            '</div>'
        )
        self.assertEqual(expected, richtext_filters(markdown))

    def test_rendering_guide_without_title(self):
        # Guides have no default title, and the current logic will only render
        # the paragraph containing both the icon and the title text if there is
        # a title, so a guide without a title will render without an icon.
        #
        # This test is meant to document current behavior, not to comment on
        # desired behavior; we do in fact probably want to fix this behavior in
        # the long term.
        markdown = (
            "!!!guide <content-0>\n"
            "\n"
            "	inner content"
        )
        expected = (
            '<div class="admonition guide">\n'
              '<div></div>\n'
              '<div>\n'
                '<p>inner content</p>\n'
              '</div>\n'
            '</div>'
        )
        self.assertEqual(expected, richtext_filters(markdown))

    def test_rendering_div_wrapping(self):
        # If there a new line between 2 elements, they will be wrapped in separate divs.
        markdown_with_newline = (
            "!!!guide <content-0>\n"
            "\n"
            "    # A header\n"
            "    \n"
            "    A paragraph\n"
        )
        expected_with_newline = (
            '<div class="admonition guide">\n'
                '<div></div>\n'
                '<div>\n'
                    '<h1 id="a-header">A header</h1>\n'
                '</div>\n'
                '<div>\n'
                    '<p>A paragraph</p>\n'
                '</div>\n'
            '</div>'
        )
        self.assertEqual(expected_with_newline, richtext_filters(markdown_with_newline))

        # Otherwise, if there is no newline between 2 elements, they will be wrapped in a same div.
        markdown_without_newline = (
            "!!!guide <content-0>\n"
            "\n"
            "    # A header\n"
            "    A paragraph\n"
        )
        expected_without_newline = (
            '<div class="admonition guide">\n'
                '<div></div>\n'
                '<div>\n'
                    '<h1 id="a-header">A header</h1>\n'
                    '<p>A paragraph</p>\n'
                '</div>\n'
            '</div>'
        )
        self.assertEqual(expected_without_newline, richtext_filters(markdown_without_newline))


    def test_rendering_without_newline(self):
        # If there is no newline between a title and a paragraph,
        # there won't be any empty div in the output.
        markdown_without_newline = (
            "!!!guide <content-0>\n"
            "    This is the only paragraph\n"
        )
        expected_without_empty_div = (
          '<div class="admonition guide">\n'
              '<div>\n'
                  '<p>This is the only paragraph</p>\n'
              '</div>\n'
          '</div>'
        )
        self.assertEqual(expected_without_empty_div, richtext_filters(markdown_without_newline))

        # Otherwise, there will be an empty div in the output.
        markdown_with_newline = (
            "!!!guide <content-0>\n"
            "\n"
            "    This is the only paragraph\n"
        )
        expected_with_empty_div = (
          '<div class="admonition guide">\n'
              '<div></div>\n'
              '<div>\n'
                  '<p>This is the only paragraph</p>\n'
              '</div>\n'
          '</div>'
        )
        self.assertEqual(expected_with_empty_div, richtext_filters(markdown_with_newline))