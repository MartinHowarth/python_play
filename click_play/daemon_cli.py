import sys

import Pyro4
# from click.testing import CliRunner
# from naval.main import naval as cli

# runner = CliRunner()
# result = runner.invoke(cli, input="--help")
Pyro4.config.REQUIRE_EXPOSE = False


class RemoteIOManager:
    """The Pyro object that provides the remote in/out stream proxies"""

    def __init__(self, stdin_uri, stdout_uri):
        self.stdin_uri = stdin_uri
        self.stdout_uri = stdout_uri
        print("here")

    def getInputOutput(self):
        return Pyro4.Proxy(self.stdout_uri), Pyro4.Proxy(self.stdin_uri)


class SimpleProxy:
    """simple proxy to another object.
    Needed to be able to use built-in types as a remote Pyro object"""

    def __init__(self, open_file):
        # self._obj=open_file
        object.__setattr__(self, "_obj", open_file)

    def __getattribute__(self, name):
        if name == "fileno":
            # hack to make it work on Python 3.x
            raise AttributeError(name)
        elif name.startswith("_pyro"):
            # little hack to get Pyro's attributes from this object itself
            return object.__getattribute__(self, name)
        else:
            # all other attributes and methods are passed to the proxied _obj
            return getattr(object.__getattribute__(self, "_obj"), name)


d = Pyro4.Daemon(port=50000)
stdin_uri = d.register(SimpleProxy(sys.stdin), "inputoutput.stdin")  # remote stdin
stdout_uri = d.register(SimpleProxy(sys.stdout), "inputoutput.stdout")  # remote stdout
uri = d.register(RemoteIOManager(stdin_uri, stdout_uri), "example.inputoutput.manager")
print("object uri=", uri)
print("server running.")
d.requestLoop()
