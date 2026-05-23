from django.test import TestCase
from django.contrib.auth.models import User, Permission
from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import PermissionDenied, ValidationError
from django.urls import reverse
from django.utils import timezone
from maze.forms import MazeCreateForm, MyMazeCreateForm, StepForm, Select2Multiple
from maze.models import Directions, Category, Cell, Task, Maze, Step


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


class CategoryModelTest(TestCase):
    def test_category_string_representation(self):
        category = Category.objects.create(name="Science Fiction")
        self.assertEqual(str(category), "Science Fiction")

    def test_get_random_task(self):
        category = Category.objects.create(name="Science")
        task1 = Task.objects.create(category=category, difficulty=Task.EASY, description="Easy Task", archived=False)
        task2 = Task.objects.create(category=category, difficulty=Task.EASY, description="Archived Easy", archived=True)
        task3 = Task.objects.create(category=category, difficulty=Task.HARD, description="Hard Task", archived=False)
        
        # Test max difficulty EASY gets task1 only
        chosen = category.get_random_task(Task.EASY)
        self.assertEqual(chosen, task1)
        
        # Test max difficulty HARD gets either task1 or task3
        chosen = category.get_random_task(Task.HARD)
        self.assertIn(chosen, [task1, task3])
        
        # Test no matching tasks returns None
        empty_cat = Category.objects.create(name="Empty")
        self.assertIsNone(empty_cat.get_random_task(Task.EASY))


class CellModelTest(TestCase):
    def setUp(self):
        self.category = Category.objects.create(name="Default")
        self.maze = Maze.objects.create(title="Test Maze", height=5, width=5)

    def test_can_move_methods(self):
        cell = Cell.objects.create(
            x=0, y=0, maze=self.maze,
            path_north=True, path_east=False, path_south=True, path_west=False
        )
        self.assertTrue(cell.can_move(Directions.NORTH))
        self.assertFalse(cell.can_move(Directions.EAST))
        self.assertTrue(cell.can_move(Directions.SOUTH))
        self.assertFalse(cell.can_move(Directions.WEST))

    def test_get_direction_choices(self):
        cell = Cell.objects.create(
            x=0, y=0, maze=self.maze,
            path_north=True, path_east=False, path_south=False, path_west=False
        )
        choices = cell.get_direction_choices()
        self.assertEqual(len(choices), 1)
        self.assertEqual(choices[0][0], Directions.NORTH)
        self.assertIn("North (Title starts with A-M)", choices[0][1])


class MazeModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="testuser", password="password")
        self.category = Category.objects.create(name="Math")
        self.task = Task.objects.create(category=self.category, difficulty=Task.EASY, description="Solve 1+1")

    def test_maze_string_representation(self):
        maze = Maze.objects.create(title="My Maze", height=5, width=5)
        self.assertEqual(str(maze), f"{maze.id}: My Maze")

    def test_generate_cells(self):
        maze = Maze.objects.create(title="Cell Maze", height=5, width=5)
        maze.generate_cells()
        self.assertEqual(maze.cells.count(), 25)
        # End coordinates set
        self.assertEqual(maze.end_x, 4)
        self.assertEqual(maze.end_y, 4)
        # Starting cell must be marked seen
        start_cell = maze.cells.get(x=0, y=0)
        self.assertTrue(start_cell.seen)

    def test_set_next_task(self):
        maze = Maze.objects.create(
            title="Task Maze", height=5, width=5,
            task_difficulty=Task.EASY, category=self.category
        )
        maze.set_next_task()
        self.assertEqual(maze.next_task, self.task)

    def test_urls(self):
        maze = Maze.objects.create(title="URL Maze", height=5, width=5)
        self.assertEqual(maze.get_absolute_url(), reverse("maze:maze", kwargs={"maze_id": maze.id}))
        self.assertEqual(maze.get_ajax_url(), reverse("maze:ajax_maze", kwargs={"maze_id": maze.id}))
        self.assertEqual(maze.get_ajax_url(clear=True), reverse("maze:ajax_maze_clear", kwargs={"maze_id": maze.id}))

    def test_move_action(self):
        maze = Maze.objects.create(title="Move Maze", height=2, width=2, task_difficulty=Task.EASY, category=self.category)
        maze.users.add(self.user)
        # Manually create cells for testing movement
        # (0, 0) -> (1, 0) East is allowed
        # (1, 0) is the end at (1, 1)? Wait, width=2, height=2, so end is (1, 1).
        cell_0_0 = Cell.objects.create(x=0, y=0, maze=maze, path_east=True, seen=True)
        cell_1_0 = Cell.objects.create(x=1, y=0, maze=maze, path_south=True)
        cell_0_1 = Cell.objects.create(x=0, y=1, maze=maze)
        cell_1_1 = Cell.objects.create(x=1, y=1, maze=maze) # End cell
        maze.set_end()
        maze.set_next_task()

        self.assertTrue(maze.can_move(Directions.EAST))
        
        # Move East
        maze.move(Directions.EAST)
        self.assertEqual(maze.current_x, 1)
        self.assertEqual(maze.current_y, 0)
        self.assertTrue(maze.cells.get(x=1, y=0).seen)
        self.assertFalse(maze.finished)
        
        # Move South to end cell (1, 1)
        maze.move(Directions.SOUTH)
        self.assertEqual(maze.current_x, 1)
        self.assertEqual(maze.current_y, 1)
        self.assertTrue(maze.finished)

    def test_user_can_navigate(self):
        maze = Maze.objects.create(title="Nav Maze", height=5, width=5)
        maze.users.add(self.user)
        
        self.assertTrue(maze.user_can_navigate(self.user))
        
        # If maze is finished
        maze.finished = True
        maze.save()
        self.assertFalse(maze.user_can_navigate(self.user))


class MazeCreateFormTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="testuser", password="password")
        self.category = Category.objects.create(name="Science")
        self.task = Task.objects.create(category=self.category, difficulty=Task.EASY, description="Science task")

    def test_maze_create_form_valid(self):
        data = {
            "title": "Form Maze",
            "height": 6,
            "width": 6,
            "users": [self.user.id],
            "task_difficulty": Task.EASY,
            "category": self.category.id,
        }
        form = MazeCreateForm(data=data)
        self.assertTrue(form.is_valid(), form.errors.as_data())
        maze = form.save()
        self.assertEqual(maze.title, "Form Maze")
        self.assertEqual(maze.height, 6)
        self.assertEqual(maze.width, 6)
        self.assertEqual(maze.cells.count(), 36)
        self.assertEqual(maze.next_task, self.task)

    def test_maze_create_form_invalid(self):
        data = {
            "title": "", # Required
            "height": 5,
            "width": 5,
        }
        form = MazeCreateForm(data=data)
        self.assertFalse(form.is_valid())
        self.assertIn("title", form.errors)


class MyMazeCreateFormTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="myuser", password="password")
        self.category = Category.objects.create(name="Math")
        self.task = Task.objects.create(category=self.category, difficulty=Task.EASY, description="Math task")

    def test_my_maze_create_form_valid(self):
        data = {
            "size": 8,
            "task_difficulity": Task.EASY,
            "category": self.category.id,
        }
        form = MyMazeCreateForm(data=data)
        self.assertTrue(form.is_valid(), form.errors.as_data())
        maze = form.save(user=self.user)
        self.assertEqual(maze.title, "myuser")
        self.assertEqual(maze.height, 8)
        self.assertEqual(maze.width, 8)
        self.assertIn(self.user, maze.users.all())
        self.assertEqual(maze.cells.count(), 64)

    def test_my_maze_create_form_invalid_size(self):
        data = {
            "size": 4, # Less than min_value=5
            "task_difficulity": Task.EASY,
            "category": self.category.id,
        }
        form = MyMazeCreateForm(data=data)
        self.assertFalse(form.is_valid())
        self.assertIn("size", form.errors)


class StepFormTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="stepuser", password="password")
        self.category = Category.objects.create(name="Reading")
        self.task = Task.objects.create(category=self.category, difficulty=Task.EASY, description="Read Book")
        self.maze = Maze.objects.create(
            title="Step Maze", height=3, width=3,
            task_difficulty=Task.EASY, category=self.category, next_task=self.task
        )
        self.maze.users.add(self.user)
        # Create mock cells
        self.cell_0_0 = Cell.objects.create(x=0, y=0, maze=self.maze, path_east=True, path_south=True, seen=True)
        self.cell_1_0 = Cell.objects.create(x=1, y=0, maze=self.maze, path_west=True)
        self.cell_0_1 = Cell.objects.create(x=0, y=1, maze=self.maze, path_north=True)
        self.cell_1_1 = Cell.objects.create(x=1, y=1, maze=self.maze)
        self.maze.set_end()

    def test_step_form_initialization(self):
        form = StepForm(maze=self.maze, user=self.user)
        # Choices should limit to East and South for (0,0)
        direction_choices = [c[0] for c in form.fields["direction"].choices]
        self.assertIn(Directions.EAST, direction_choices)
        self.assertIn(Directions.SOUTH, direction_choices)
        self.assertNotIn(Directions.NORTH, direction_choices)
        self.assertNotIn(Directions.WEST, direction_choices)

    def test_step_form_direction_invalid(self):
        # Trying to move North when path_north is False
        data = {
            "title": "Apple Book",
            "author": "Author A",
            "reader": "Reader R",
            "pages": 100,
            "direction": Directions.NORTH,
        }
        form = StepForm(data=data, maze=self.maze, user=self.user)
        self.assertFalse(form.is_valid())
        self.assertIn("direction", form.errors)

    def test_validate_move_north_success(self):
        # North rule: Title starts with A-M
        self.cell_0_0.path_north = True
        self.cell_0_0.save()
        data = {
            "title": "Apple Book",
            "author": "Author A",
            "reader": "Reader R",
            "pages": 100,
            "direction": Directions.NORTH,
        }
        form = StepForm(data=data, maze=self.maze, user=self.user)
        self.assertTrue(form.is_valid(), form.errors.as_data())

    def test_validate_move_north_failure(self):
        # North rule: Title starts with A-M. Orange starts with O.
        self.cell_0_0.path_north = True
        self.cell_0_0.save()
        data = {
            "title": "Orange Book",
            "author": "Author A",
            "reader": "Reader R",
            "pages": 100,
            "direction": Directions.NORTH,
        }
        form = StepForm(data=data, maze=self.maze, user=self.user)
        self.assertFalse(form.is_valid())
        self.assertIn("__all__", form.errors)

    def test_validate_move_south_success(self):
        # South rule: Title starts with N-Z
        data = {
            "title": "Orange Book",
            "author": "Author A",
            "reader": "Reader R",
            "pages": 100,
            "direction": Directions.SOUTH,
        }
        form = StepForm(data=data, maze=self.maze, user=self.user)
        self.assertTrue(form.is_valid(), form.errors.as_data())

    def test_validate_move_south_failure(self):
        # South rule: Title starts with N-Z. Apple starts with A.
        data = {
            "title": "Apple Book",
            "author": "Author A",
            "reader": "Reader R",
            "pages": 100,
            "direction": Directions.SOUTH,
        }
        form = StepForm(data=data, maze=self.maze, user=self.user)
        self.assertFalse(form.is_valid())
        self.assertIn("__all__", form.errors)

    def test_validate_move_east_success(self):
        # East rule: Even number of pages
        data = {
            "title": "Any Book",
            "author": "Author A",
            "reader": "Reader R",
            "pages": 100,
            "direction": Directions.EAST,
        }
        form = StepForm(data=data, maze=self.maze, user=self.user)
        self.assertTrue(form.is_valid(), form.errors.as_data())

    def test_validate_move_east_failure(self):
        # East rule: Even number of pages. 101 is odd.
        data = {
            "title": "Any Book",
            "author": "Author A",
            "reader": "Reader R",
            "pages": 101,
            "direction": Directions.EAST,
        }
        form = StepForm(data=data, maze=self.maze, user=self.user)
        self.assertFalse(form.is_valid())
        self.assertIn("__all__", form.errors)

    def test_validate_move_west_success(self):
        # West rule: Odd number of pages
        self.cell_0_0.path_west = True
        self.cell_0_0.save()
        data = {
            "title": "Any Book",
            "author": "Author A",
            "reader": "Reader R",
            "pages": 101,
            "direction": Directions.WEST,
        }
        form = StepForm(data=data, maze=self.maze, user=self.user)
        self.assertTrue(form.is_valid(), form.errors.as_data())

    def test_validate_move_west_failure(self):
        # West rule: Odd number of pages. 100 is even.
        self.cell_0_0.path_west = True
        self.cell_0_0.save()
        data = {
            "title": "Any Book",
            "author": "Author A",
            "reader": "Reader R",
            "pages": 100,
            "direction": Directions.WEST,
        }
        form = StepForm(data=data, maze=self.maze, user=self.user)
        self.assertFalse(form.is_valid())
        self.assertIn("__all__", form.errors)

    def test_step_form_save(self):
        data = {
            "title": "Even Pages Book",
            "author": "Author A",
            "reader": "Reader R",
            "pages": 150,
            "direction": Directions.EAST,
        }
        form = StepForm(data=data, maze=self.maze, user=self.user)
        self.assertTrue(form.is_valid())
        step = form.save()
        
        # Step saved and references correct values
        self.assertEqual(step.title, "Even Pages Book")
        self.assertEqual(step.maze, self.maze)
        self.assertEqual(step.user, self.user)
        self.assertEqual(step.task, self.task)
        
        # Maze moved
        self.assertEqual(self.maze.current_x, 1)
        self.assertEqual(self.maze.current_y, 0)


class MazeViewsTest(TestCase):
    def setUp(self):
        self.password = "Secr3tP@ssword"
        self.user = User.objects.create_user(username="normaluser", password=self.password)
        self.category = Category.objects.create(name="Fiction")
        
        # Create user with maze add permission
        self.creator_user = User.objects.create_user(username="creator", password=self.password)
        content_type = ContentType.objects.get_for_model(Maze)
        add_perm = Permission.objects.get(codename="add_maze", content_type=content_type)
        self.creator_user.user_permissions.add(add_perm)

        # Superuser
        self.superuser = User.objects.create_superuser(username="superuser", password=self.password)

        # A default maze
        self.maze = Maze.objects.create(
            title="Main Maze", height=5, width=5,
            task_difficulty=Task.EASY, category=self.category
        )
        self.maze.users.add(self.user)
        self.maze.generate_cells()

    def test_maze_create_view_unauthorized(self):
        self.client.login(username="normaluser", password=self.password)
        response = self.client.get(reverse("maze:maze_create"))
        self.assertEqual(response.status_code, 403)

    def test_maze_create_view_authorized_get(self):
        self.client.login(username="creator", password=self.password)
        response = self.client.get(reverse("maze:maze_create"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "bookmaze/form_view.html")

    def test_maze_create_view_authorized_post_success(self):
        self.client.login(username="creator", password=self.password)
        post_data = {
            "title": "Created from View",
            "height": 5,
            "width": 5,
            "users": [self.user.id],
            "task_difficulty": Task.EASY,
            "category": self.category.id,
        }
        response = self.client.post(reverse("maze:maze_create"), data=post_data)
        self.assertRedirects(response, reverse("maze:index"))
        self.assertTrue(Maze.objects.filter(title="Created from View").exists())

    def test_my_maze_create_view_anonymous(self):
        response = self.client.get(reverse("maze:my_maze_create"))
        self.assertRedirects(response, f"{reverse('login')}?next={reverse('maze:my_maze_create')}")

    def test_my_maze_create_view_authorized_post(self):
        self.client.login(username="normaluser", password=self.password)
        post_data = {
            "size": 6,
            "task_difficulity": Task.EASY,
            "category": self.category.id,
        }
        response = self.client.post(reverse("maze:my_maze_create"), data=post_data)
        self.assertRedirects(response, reverse("maze:index"))
        self.assertTrue(Maze.objects.filter(title="normaluser").exists())

    def test_index_view_search(self):
        # Create another maze
        Maze.objects.create(title="Searchable Maze", height=5, width=5)
        
        response = self.client.get(reverse("maze:index"), {"search": "Searchable"})
        self.assertEqual(response.status_code, 200)
        
        # Check context
        mazes = response.context["all_maze_page"].object_list
        self.assertEqual(len(mazes), 1)
        self.assertEqual(mazes[0].title, "Searchable Maze")

    def test_index_view_empty_page(self):
        response = self.client.get(reverse("maze:index"), {"page": 999})
        self.assertEqual(response.status_code, 404)

    def test_maze_detail_view_anonymous(self):
        response = self.client.get(self.maze.get_absolute_url())
        self.assertEqual(response.status_code, 200)
        self.assertIsNone(response.context["form"])

    def test_maze_detail_view_authorized_user(self):
        self.client.login(username="normaluser", password=self.password)
        response = self.client.get(self.maze.get_absolute_url())
        self.assertEqual(response.status_code, 200)
        self.assertIsNotNone(response.context["form"])

    def test_maze_detail_view_unauthorized_user(self):
        # user2 is not in self.maze.users
        user2 = User.objects.create_user(username="otheruser", password=self.password)
        self.client.login(username="otheruser", password=self.password)
        response = self.client.get(self.maze.get_absolute_url())
        self.assertEqual(response.status_code, 200)
        self.assertIsNone(response.context["form"])

    def test_maze_detail_view_clear_superuser_only_success(self):
        self.client.login(username="superuser", password=self.password)
        response = self.client.get(f"/maze/{self.maze.id}/clear/")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context["ajax_url"], self.maze.get_ajax_url(clear=True))

    def test_maze_detail_view_clear_regular_user_failure(self):
        self.client.login(username="normaluser", password=self.password)
        response = self.client.get(f"/maze/{self.maze.id}/clear/")
        self.assertEqual(response.status_code, 403)

    def test_maze_detail_view_post_valid_step(self):
        # Set current cell mock to allow East move
        cell = self.maze.get_current_cell()
        cell.path_east = True
        cell.save()

        self.client.login(username="normaluser", password=self.password)
        post_data = {
            "title": "Valid East",
            "author": "Author E",
            "reader": "Reader E",
            "pages": 200, # even for East
            "direction": Directions.EAST,
        }
        response = self.client.post(self.maze.get_absolute_url(), data=post_data)
        # Should redirect back to the maze view
        self.assertEqual(response.status_code, 302)
        
        # Verify step is saved
        self.assertTrue(Step.objects.filter(title="Valid East").exists())
        # Verify maze position updated
        self.maze.refresh_from_db()
        self.assertEqual(self.maze.current_x, 1)

    def test_ajax_maze_view_data(self):
        response = self.client.get(self.maze.get_ajax_url())
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["width"], self.maze.width)
        self.assertEqual(data["height"], self.maze.height)
        self.assertEqual(len(data["cells"]), 25)
        
        # Cell (0,0) is seen, so it has path details
        start_cell_data = [c for c in data["cells"] if c["x"] == 0 and c["y"] == 0][0]
        self.assertTrue(start_cell_data["seen"])
        self.assertIn("path_north", start_cell_data)

        # Unseen cells (e.g. 1, 1) should not have path details if not cleared / finished
        unseen_cell = self.maze.cells.get(x=1, y=1)
        unseen_cell.seen = False
        unseen_cell.save()
        
        response = self.client.get(self.maze.get_ajax_url())
        data = response.json()
        unseen_cell_data = [c for c in data["cells"] if c["x"] == 1 and c["y"] == 1][0]
        self.assertFalse(unseen_cell_data["seen"])
        self.assertNotIn("path_north", unseen_cell_data)

    def test_ajax_maze_view_clear_superuser(self):
        self.client.login(username="superuser", password=self.password)
        
        unseen_cell = self.maze.cells.get(x=1, y=1)
        unseen_cell.seen = False
        unseen_cell.save()
        
        response = self.client.get(self.maze.get_ajax_url(clear=True))
        self.assertEqual(response.status_code, 200)
        data = response.json()
        
        # Unseen cells should have path details because clear is True
        unseen_cell_data = [c for c in data["cells"] if c["x"] == 1 and c["y"] == 1][0]
        self.assertFalse(unseen_cell_data["seen"])
        self.assertIn("path_north", unseen_cell_data)

    def test_ajax_maze_view_clear_regular_user_denied(self):
        self.client.login(username="normaluser", password=self.password)
        response = self.client.get(self.maze.get_ajax_url(clear=True))
        self.assertEqual(response.status_code, 403)
