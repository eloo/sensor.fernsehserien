from unittest.mock import patch

import pytest
import socket
import pytest_socket

pytest_plugins = "pytest_homeassistant_custom_component"

@pytest.fixture
def socket_enabled(pytestconfig):
    """Enable socket.socket for duration of this test function.
    This incorporates changes from https://github.com/miketheman/pytest-socket/pull/76
    and hardcodes allow_unix_socket to True because it's not passed on the command line.
    """
    socket_was_disabled = socket.socket != pytest_socket._true_socket
    pytest_socket.enable_socket()
    fernsehSerienIps = socket.gethostbyname_ex('www.fernsehserien.de')[2]
    fernsehSerienBilderIps = socket.gethostbyname_ex('bilder.fernsehserien.de')[2]
    fernsehSerienIps.extend(fernsehSerienBilderIps)
    pytest_socket.socket_allow_hosts(fernsehSerienIps, True)
    yield
    if socket_was_disabled:
        disable_socket(allow_unix_socket=True)
