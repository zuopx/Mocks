import os
from unittest import mock
from unittest.mock import patch

import pytest


class MyObject:
    """该类的方法的消息类型为（outgoing，command）。"""

    def __init__(self, repo):
        self._repo = repo
        self._repo.connect()

    def setup(self):
        self._repo.setup(cache=True, max_connections=256)


class TestMyObject:
    def test_init(self):
        external_obj = mock.Mock()
        myobj = MyObject(external_obj)
        external_obj.connect.assert_called_with()

    def test_setup(self):
        external_obj = mock.Mock()
        myobj = MyObject(external_obj)
        myobj.setup()
        external_obj.setup.assert_called_with(cache=True, max_connections=256)


class TestMeteoriteStats:
    def test_average_mass(self):
        stats = MeteoriteStats()
        stats.get_data = mock.Mock()
        stats.get_data.return_value = [1, 2, 3, 4, 5]
        data = stats.get_data()
        assert stats.average_mass(data) == 3


class MeteoriteStats:
    """该类的方法的消息类型为（outgoing，query）。"""

    def get_data(self):
        pass

    def average_mass(self, data):
        return sum(data) / len(data)


class Player:
    def __init__(self, name, password):
        self.name = name
        self._password = password

    def __eq__(self, other):
        return self.name == other.name and self._password == other._password


class TestPlayer:
    def test_eq(self):
        assert Player('test1', '163') == Player('test1', '163')


class LoginHanler:
    """该类的方法的消息类型有（outgoing, query）、（outgoing, command），还涉及到（outgoing, query）的多种返回情况（包括异常）。"""

    def __init__(self, repo, client):
        self._repo = repo
        self._client = client

    def login(self, name, password):
        try:
            player = self._repo.select(name, password)
        except NameException:
            self._client.NameWrong()
        except PasswordException:
            self._client.PasswordWrong()
        else:
            self._client.LoginSucc()
            return player


class NameException(Exception):
    pass


class PasswordException(Exception):
    pass


class TestLogin:
    def test_login_succ(self):
        repo = mock.Mock()
        client = mock.Mock()
        hanler = LoginHanler(repo, client)
        repo.select.side_effect = Player
        player = hanler.login('test1', '163')
        assert player == Player('test1', '163')
        client.LoginSucc.assert_called_with()

    def test_login_name_error(self):
        repo = mock.Mock()
        client = mock.Mock()
        hanler = LoginHanler(repo, client)
        repo.select.side_effect = NameException()
        player = hanler.login('test', '163')
        client.NameWrong.assert_called_with()

    def test_login_password_error(self):
        repo = mock.Mock()
        client = mock.Mock()
        hanler = LoginHanler(repo, client)
        repo.select.side_effect = PasswordException()
        player = hanler.login('test1', '123')
        client.PasswordWrong.assert_called_with()


class FileInfo:
    """该类的方法的消息为（outgoing, query），但是这个外部对象是内置的，不是传递进去的。"""
    def __init__(self, path):
        self.original_path = path
        self.filename = os.path.basename(path)

    def get_info(self):
        return [
            self.filename,
            self.original_path,
            os.path.abspath(self.filename)
        ]

class TestFileInfo:
    def test_get_info(self):
        filename = 'somefile.txt'
        original_path = f'../{filename}'
        with patch('os.path.abspath') as abspath_mock:
            test_abspath = 'some/abs/path'
            abspath_mock.return_value = test_abspath
            fi = FileInfo(original_path)
            assert fi.get_info() == [filename, original_path, test_abspath]
        