from unittest.mock import patch

from django.core.management import call_command
from django.db.utils import OperationalError
from django.test import TestCase


class CommandTests(TestCase):

    def test_wait_for_db_ready(self):
        # test waiting for db when db is available
        # the function to retrieve db is __getitem__
        with patch('django.db.utils.ConnectionHandler.__getitem__') as gi:
            # mock
            gi.return_value = True
            # wait for db is the name of management command
            call_command('wait_for_db')
            # call_count from unittest
            self.assertEqual(gi.call_count, 1)

    @patch('time.sleep', return_value=True)
    def test_wait_for_db(self, ts):
        # test waiting for db
        # check if ConnectionHandler raises OperationalError
        with patch('django.db.utils.ConnectionHandler.__getitem__') as gi:
            # the first 5 times raises error
            # 6th time raises ok
            gi.side_effect = [OperationalError] * 5 + [True]
            call_command('wait_for_db')
            self.assertEqual(gi.call_count, 6)
