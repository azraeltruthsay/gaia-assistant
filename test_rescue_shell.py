from subprocess import run, PIPE

def _run(cmd: str, text=""):
    r = run(cmd.split(), input=text.encode(), stdout=PIPE, stderr=PIPE, timeout=40)
    return r.stdout.decode() + r.stderr.decode(), r.returncode

def test_boot_ok():
    out, code = _run("python gaia_rescue.py --cmd ping")
    assert code == 0
    assert "GAIA" in out

def test_self_reflect_once():
    # minimal prompt; avoids huge context
    out, code = _run('python gaia_rescue.py --cmd "Reflect"')
    assert code == 0