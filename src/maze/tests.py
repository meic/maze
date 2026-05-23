from django.test import TestCase
from django.contrib.auth.models import User
from maze.forms import MazeCreateForm, Select2Multiple


class Select2MultipleTest(TestCase):
    def test_widget_attributes_and_media(self):
        # Instantiate the form
        form = MazeCreateForm()

        # Check that 'users' field uses Select2Multiple widget
        widget = form.fields["users"].widget
        self.assertIsInstance(widget, Select2Multiple)

        # Check that it renders with the class 'select2'
        html = form["users"].as_widget()
        self.assertIn('class="', html)
        self.assertIn("select2", html)

        # Check media JS and CSS files are correctly configured on the widget
        media_js = list(widget.media.render_js())
        media_css = list(widget.media.render_css())

        self.assertTrue(any("select2.min" in tag and ".js" in tag for tag in media_js))
        self.assertTrue(any("select2-init" in tag and ".js" in tag for tag in media_js))
        self.assertTrue(any("select2.min" in tag and ".css" in tag for tag in media_css))
        self.assertTrue(
            any("select2-bootstrap-5-theme.min" in tag and ".css" in tag for tag in media_css)
        )
