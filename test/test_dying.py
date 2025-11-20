import time
from unittest import TestCase
from unittest.mock import Mock, patch

from src.status.dying import DEAD, DYING, add_dying, is_dead, is_dying
from src.users import BotUser, FakeUser


class TestDying(TestCase):
    @classmethod
    def setUpClass(cls):
        from src import users

        users.Bot = BotUser(None, "bot", "bot", "bot.user", "bot")

    def setUp(self):
        DYING.clear()
        DEAD.clear()

    @patch("src.status.dying.locks.reaper")
    def test_add_dying_success(self, mock_reaper):
        var = Mock()
        var.game_id = time.time()
        player = FakeUser.from_nick("testplayer")

        result = add_dying(var, player, "wolf", "night kill")

        self.assertTrue(result)
        self.assertTrue(is_dying(var, player))
        self.assertIn(player, DYING)
        killer_role, reason, _, _ = DYING[player]
        self.assertEqual(killer_role, "wolf")
        self.assertEqual(reason, "night kill")

    @patch("src.status.dying.locks.reaper")
    def test_add_dying_already_dying(self, mock_reaper):
        var = Mock()
        var.game_id = time.time()
        player = FakeUser.from_nick("testplayer")

        result1 = add_dying(var, player, "wolf", "night kill")
        result2 = add_dying(var, player, "villager", "lynch")

        self.assertTrue(result1)
        self.assertFalse(result2)
        self.assertEqual(DYING[player][0], "wolf")

    @patch("src.status.dying.locks.reaper")
    def test_add_dying_game_ended(self, mock_reaper):
        var = Mock()
        var.game_id = time.time() + 100
        player = FakeUser.from_nick("testplayer")

        result = add_dying(var, player, "wolf", "night kill")

        self.assertFalse(result)
        self.assertNotIn(player, DYING)

    @patch("src.status.dying.locks.reaper")
    def test_add_dying_already_dead(self, mock_reaper):
        var = Mock()
        var.game_id = time.time()
        player = FakeUser.from_nick("testplayer")
        DEAD.add(player)

        result = add_dying(var, player, "wolf", "night kill")

        self.assertFalse(result)
        self.assertNotIn(player, DYING)

    @patch("src.status.dying.locks.reaper")
    def test_is_dead(self, mock_reaper):
        var = Mock()
        var.game_id = time.time()
        player = FakeUser.from_nick("testplayer")

        self.assertFalse(is_dead(var, player))
        DEAD.add(player)
        self.assertTrue(is_dead(var, player))
