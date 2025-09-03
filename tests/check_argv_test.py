import sys
from main import check_argv

def test_check_argv_no_arg(monkeypatch):
    # Simulate sys.argv only having the script name
    monkeypatch.setattr(sys, "argv", ["script.py"])

    # Simulate user typing "yay"
    monkeypatch.setattr("builtins.input", lambda _: "yay")

    result = check_argv()
    assert result == "yay"

def test_check_argv_one_arg(monkeypatch):
    # Simulate sys.argv having the script name and one argument
    monkeypatch.setattr(sys, "argv", ["script.py", "paru"])

    result = check_argv()
    assert result == "paru"
    
def test_check_argv_extra_args(monkeypatch):
    # Simulate sys.argv having the script name and extra arguments
    monkeypatch.setattr(sys, "argv", ["script.py", "spotify", "extra_arg"])

    result = check_argv()
    assert result == "spotify"
