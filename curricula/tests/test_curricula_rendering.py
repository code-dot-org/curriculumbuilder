from django.test import TestCase
from django.contrib.auth.models import Permission
from django.utils import translation

from curricula.factories import UserFactory, CurriculumFactory, UnitFactory
from lessons.factories import LessonFactory, ResourceFactory, ActivityFactory


class CurriculaRenderingTestCase(TestCase):
    def setUp(self):
        user = UserFactory()
        user.is_staff = True
        user.save()
        self.user = user
        self.client.login(username=user.username, password='password')

        self.test_curriculum = CurriculumFactory(slug="test-curriculum")
        self.csf_curriculum = CurriculumFactory(
            slug="csf-curriculum",
            unit_template_override='curricula/csf_unit.html')
        self.pl_curriculum = CurriculumFactory(
            slug="pl-curriculum",
            unit_template_override='curricula/pl_unit.html')
        self.test_unit = UnitFactory(parent=self.test_curriculum, slug="test-unit", unit_name="test-unit-name")
        self.hoc_unit = UnitFactory(
            parent=self.test_curriculum,
            slug="hoc-unit",
            lesson_template_override="curricula/hoc_lesson.html")
        self.csf_unit = UnitFactory(
            parent=self.csf_curriculum,
            slug="csf-unit",
            i18n_ready=True,
            lesson_template_override="curricula/csf_lesson.html")
        self.pl_unit = UnitFactory(
            parent=self.pl_curriculum,
            slug="pl-unit",
            i18n_ready=True,
            lesson_template_override="curricula/pl_lesson.html")
        resource = ResourceFactory()
        self.test_lesson = LessonFactory(parent=self.test_unit)
        self.test_lesson.resources.add(resource)
        self.test_activity = ActivityFactory(lesson=self.test_lesson, content='[code-studio]')
        self.hoc_lesson = LessonFactory(parent=self.hoc_unit)
        self.hoc_lesson.resources.add(resource)
        self.csf_lesson = LessonFactory(parent=self.csf_unit)
        self.csf_lesson.resources.add(resource)
        self.pl_lesson = LessonFactory(parent=self.pl_unit)
        self.pl_lesson.resources.add(resource)

    def test_homepage(self):
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)

    def test_render_curriculum(self):
        response = self.client.get('/test-curriculum/')
        self.assertEqual(response.status_code, 200)

    def test_render_unit(self):
        response = self.client.get('/test-curriculum/test-unit/')
        self.assertEqual(response.status_code, 200)
        response = self.client.get('/csf-curriculum/csf-unit/')
        self.assertEqual(response.status_code, 200)
        response = self.client.get('/test-curriculum/hoc-unit/')
        self.assertEqual(response.status_code, 200)
        response = self.client.get('/pl-curriculum/pl-unit/')
        self.assertEqual(response.status_code, 200)
        response = self.client.get('/test-curriculum/test-unit/glance/')
        self.assertEqual(response.status_code, 200)
        response = self.client.get('/test-curriculum/test-unit/vocab/')
        self.assertEqual(response.status_code, 200)
        response = self.client.get('/test-curriculum/test-unit/code/')
        self.assertEqual(response.status_code, 200)
        response = self.client.get('/test-curriculum/test-unit/resources/')
        self.assertEqual(response.status_code, 200)
        response = self.client.get('/test-curriculum/test-unit/objectives/')
        self.assertEqual(response.status_code, 200)
        response = self.client.get('/test-curriculum/test-unit/unit_feedback/')
        self.assertEqual(response.status_code, 200)
        response = self.client.get('/test-curriculum/test-unit/?pdf=1')
        self.assertEqual(response.status_code, 200)
        response = self.client.get('/pl-curriculum/pl-unit/?pdf=1')
        self.assertEqual(response.status_code, 200)

    def test_render_lesson(self):
        response = self.client.get('/test-curriculum/test-unit/1/')
        self.assertEqual(response.status_code, 200)
        response = self.client.get('/test-curriculum/hoc-unit/1/')
        self.assertEqual(response.status_code, 200)
        response = self.client.get('/csf-curriculum/csf-unit/1/')
        self.assertEqual(response.status_code, 200)
        response = self.client.get('/pl-curriculum/pl-unit/1/')
        self.assertEqual(response.status_code, 200)

    def test_render_curriculum_admin_menu(self):
        self.assert_admin_menu('/test-curriculum/', False)
        self.assert_admin_menu('/pl-curriculum/', False)

        # Supply one combination of permissions which give the user access
        # to the admin controls in this menu. Other combinations, such as
        # when a partner views a page they own, are not covered by this test.
        self.add_permission(self.user, 'change_curriculum')
        self.add_permission(self.user, 'access_all_curricula')

        # Copy button appears in admin menu for users with sufficient permissions
        self.assert_admin_menu('/test-curriculum/', True)
        self.assert_admin_menu('/pl-curriculum/', True)

    def test_render_unit_admin_menu(self):
        self.assert_admin_menu('/test-curriculum/test-unit/', False)
        self.assert_admin_menu('/pl-curriculum/pl-unit/', False)

        # Supply one combination of permissions which give the user access
        # to the admin controls in this menu. Other combinations, such as
        # when a partner views a page they own, are not covered by this test.
        self.add_permission(self.user, 'change_unit')
        self.add_permission(self.user, 'access_all_units')

        # Copy button appears in admin menu for users with sufficient permissions
        self.assert_admin_menu('/test-curriculum/test-unit/', True)
        self.assert_admin_menu('/pl-curriculum/pl-unit/', True)

    def test_render_lesson_admin_menu(self):
        self.assert_admin_menu('/test-curriculum/test-unit/1/', False)
        self.assert_admin_menu('/test-curriculum/hoc-unit/1/', False)
        self.assert_admin_menu('/pl-curriculum/pl-unit/1/', False)

        # Supply one combination of permissions which give the user access
        # to the admin controls in this menu. Other combinations, such as
        # when a partner views a page they own, are not covered by this test.
        self.add_permission(self.user, 'change_lesson')
        self.add_permission(self.user, 'access_all_lessons')

        # Copy button appears in admin menu for users with sufficient permissions
        self.assert_admin_menu('/test-curriculum/test-unit/1/', True)
        self.assert_admin_menu('/test-curriculum/hoc-unit/1/', True)
        self.assert_admin_menu('/pl-curriculum/pl-unit/1/', True)

    def assert_admin_menu(self, path, with_admin_controls):
        response = self.client.get(path)
        self.assertEqual(response.status_code, 200)
        self.assertIn('admin_edit', response.content)
        if with_admin_controls:
            self.assertIn('deepSpaceCopy', response.content)
            self.assertIn('Get Code Studio Stage Details', response.content)
        else:
            self.assertNotIn('deepSpaceCopy', response.content)
            self.assertNotIn('Get Code Studio Stage Details', response.content)

    def add_permission(self, user, codename):
        permission = Permission.objects.get(codename=codename)
        user.user_permissions.add(permission)

    def test_render_lesson_with_levels(self):
        stage = {
            "levels": [{
                "path": "/s/dance/stage/1/puzzle/1",
                "name": "Dance_Party_11",
                "mini_rubric": True
            },{
                "path": "/s/dance/stage/1/puzzle/2",
                "name": "Dance_Party_22",
                "teacher_markdown": "teacher markdown",
                "named_level": True
            }],
            "stageName": "test stage"
        }
        self.test_lesson.stage = stage
        self.test_lesson.save()
        response = self.client.get('/test-curriculum/test-unit/1/')
        self.assertEqual(response.status_code, 200)

    def test_render_lesson_with_code_studio_pull_through(self):
        stage = {
            "levels": [{
                "id": 21375,
                "position": 1,
                "named_level": False,
                "bonus_level": False,
                "assessment": "",
                "progression": "",
                "path": "/s/dance/stage/1/puzzle/1",
                "name": "Dance_Party_11",
                "display_name": "Bubble Choice: All the Choices",
                "description": "This is a BubbleChoice level. Choose one of the activities below to practice what you have learned!",
                "type": "BubbleChoice",
                "teacher_markdown": "A wonderful note to the teacher",
                "sublevels": [
                    {
                        "id": 13103,
                        "level_id": 13103,
                        "position": 1,
                        "letter": "a",
                        "icon": "fa-video-camera",
                        "type": "StandaloneVideo",
                        "name": "AllTheThings_StandaloneVideo",
                        "display_name": "AllTheThings_StandaloneVideo",
                        "video_youtube": "https://www.youtube-nocookie.com/embed/QvyTEx1wyOY/?autoplay=1\u0026enablejsapi=1\u0026iv_load_policy=3\u0026modestbranding=1\u0026rel=0\u0026showinfo=1\u0026v=QvyTEx1wyOY\u0026wmode=transparent",
                        "video_download": "https://videos.code.org/2015/csp/cs_is_changing_everything.mp4",
                        "description": "Want to watch a video instead of programming? This level is for you!",
                        "thumbnail_url": "",
                        "url": "http://localhost-studio.code.org:3000/levels/13103"
                    },
                    {
                        "id": 21394,
                        "level_id": 21394,
                        "position": 2,
                        "letter": "b",
                        "icon": "",
                        "mini_rubric": "false",
                        "type": "Weblab",
                        "name": "Web Lab 1",
                        "display_name": "MAKE A WEBPAGE",
                        "long_instructions": "Make an awesome web page!\r\n\r\n1. Look at the web page we gave you to start with. Look how lame it is. 1996 just called and wants its web page back. But don't get depressed - YOU can fix it!\r\n2. Add a background-color attribute in the body style in style.css to make the page background color 'darkcyan'\r\n3. Add a text-align attribute to the body style in style.css to center the image and text horizontally\r\n4. Change index.html to include an inspiring hashtag\r\n5. Add a color attribute to the p style in style.css to make the inspiring hashtag white\r\n6. Add a font-size attribute to the p style in style.css to make your inspiring hashtag REALLY BIG! (Try 24px and 3em and see what happens.)",
                        "description": "You can make a webpage on this one!",
                        "thumbnail_url": "",
                        "url": "http://localhost-studio.code.org:3000/levels/21394"
                    },
                    {
                        "id": 19060,
                        "level_id": 19060,
                        "position": 3,
                        "letter": "c",
                        "icon": "",
                        "type": "Craft",
                        "mini_rubric": "false",
                        "name": "Overworld Chop Tree - allthethings",
                        "display_name": "Overworld Chop Tree - allthethings",
                        "short_instructions": "Wood is a very important resource. Many things are made from it. Walk to the tree and use the destroy block command to chop it down.",
                        "description": "Minecraft is all the rag right now!",
                        "thumbnail_url": "https://images.code.org/78b6eb71df859b3e222c58458981f950-image-1567806072924.PNG",
                        "url": "http://localhost-studio.code.org:3000/levels/19060"
                    }
                ]
            }],
            "stageName": "test stage",
            "lockable": False
        }

        self.test_lesson.stage = stage
        self.test_lesson.save()
        response = self.client.get('/test-curriculum/test-unit/1/')
        self.assertEqual(response.status_code, 200)
        self.assertIn('Bubble Choice: All the Choices', response.content)
        self.assertIn('Choose from the following activities:', response.content)
        self.assertIn('This is a BubbleChoice level. Choose one of the activities below to practice what you have learned!', response.content)
        self.assertIn('A wonderful note to the teacher', response.content)
        self.assertIn('AllTheThings_StandaloneVideo', response.content)
        self.assertIn('MAKE A WEBPAGE', response.content)
        self.assertIn('Overworld Chop Tree - allthethings', response.content)
        self.assertIn('<img src="https://images.code.org/78b6eb71df859b3e222c58458981f950-image-1567806072924.PNG" width="150" class="sublevel-thumbnail"/>', response.content)

    def test_metadata_for_course(self):
        response = self.client.get('/metadata/course/test-curriculum.json')
        self.assertEqual(response.status_code, 200)

    def test_metadata_for_unit(self):
        response = self.client.get('/metadata/test-unit-name.json')
        self.assertEqual(response.status_code, 200)

    def test_get_pdf_url(self):
        en_url = self.csf_unit.get_pdf_url()
        with translation.override('es-mx'):
            es_url = self.csf_unit.get_pdf_url()
        with translation.override('hi-in'):
            hi_url = self.csf_unit.get_pdf_url()
        self.assertEqual('/csf-curriculum/csf-unit.pdf', en_url)
        self.assertEqual('/es-mx/csf-curriculum/csf-unit.pdf', es_url)
        self.assertEqual('/csf-curriculum/csf-unit.pdf', hi_url)
