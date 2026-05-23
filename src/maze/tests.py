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


from django.urls import reverse
from maze.models import Maze, Step

class IndexStatsTest(TestCase):
    def setUp(self):
        # Create users
        self.user1 = User.objects.create_user(username="reader1", password="password")
        self.user2 = User.objects.create_user(username="reader2", password="password")

        # Create finished and active mazes
        self.maze1 = Maze.objects.create(title="Maze One", height=5, width=5, finished=True)
        self.maze1.users.add(self.user1)
        
        self.maze2 = Maze.objects.create(title="Maze Two", height=5, width=5, finished=False)
        self.maze2.users.add(self.user1)
        self.maze2.users.add(self.user2)

        self.maze3 = Maze.objects.create(title="Maze Three", height=5, width=5, finished=False)
        self.maze3.users.add(self.user2)

        # Create steps / books read
        Step.objects.create(
            direction=10,
            title="Book A",
            pages=150,
            maze=self.maze1,
            user=self.user1
        )
        Step.objects.create(
            direction=20,
            title="Book B",
            pages=250,
            maze=self.maze2,
            user=self.user1
        )
        Step.objects.create(
            direction=30,
            title="Book C",
            pages=300,
            maze=self.maze2,
            user=self.user2
        )

    def test_anonymous_user_sees_global_stats(self):
        response = self.client.get(reverse("maze:index"))
        self.assertEqual(response.status_code, 200)
        
        # Check context global stats
        self.assertEqual(response.context["total_books"], 3)
        self.assertEqual(response.context["total_pages"], 700)
        self.assertEqual(response.context["total_mazes_complete"], 1)
        self.assertEqual(response.context["total_active_mazes"], 2)

        # Personal stats should be 0/empty
        self.assertEqual(response.context["user_books"], 0)
        self.assertEqual(response.context["user_pages"], 0)
        self.assertEqual(response.context["user_mazes_complete"], 0)
        self.assertEqual(response.context["user_active_mazes"], 0)

        # Confirm numbers are rendered in response content
        self.assertContains(response, "3</span>")
        self.assertContains(response, "700</span>")
        self.assertContains(response, "1</span>")
        self.assertContains(response, "2</span>")
        
        # Personal labels ("by you") should NOT be visible
        self.assertNotContains(response, "by you")

    def test_authenticated_user_sees_personal_stats(self):
        # Log in as user1
        self.client.login(username="reader1", password="password")
        response = self.client.get(reverse("maze:index"))
        self.assertEqual(response.status_code, 200)

        # Global stats should still be correct
        self.assertEqual(response.context["total_books"], 3)
        self.assertEqual(response.context["total_pages"], 700)
        self.assertEqual(response.context["total_mazes_complete"], 1)
        self.assertEqual(response.context["total_active_mazes"], 2)

        # Personal stats for user1:
        # - Books read: Book A, Book B (2 books)
        # - Pages read: 150 + 250 = 400 pages
        # - Completed mazes: maze1 (1 completed)
        # - Active mazes: maze2 (1 active)
        self.assertEqual(response.context["user_books"], 2)
        self.assertEqual(response.context["user_pages"], 400)
        self.assertEqual(response.context["user_mazes_complete"], 1)
        self.assertEqual(response.context["user_active_mazes"], 1)

        # Check rendering of personal stats
        self.assertContains(response, "2 by you")
        self.assertContains(response, "400 by you")
        self.assertContains(response, "1 by you")
