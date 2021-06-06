# RCPiCar: Radio-controlled Raspberry Pi Car - Library

## Development

### Set up

1. Create a venv directory by running `./make.py venv` and do not forget to activate it before the next step.
2. Install the project and its dependencies by running `pip install --editable .[tests]`.

### Static type checking

This project uses static type checking using [mypy](http://mypy-lang.org/).
You can run the static type checker by running `./make.py check_type`.
Only if the exit code is `0`, then the typing is okay.

### Code style

This project tries to enforce a uniform code style.
You can run the style checker by running `./make.py check_style`.
Only if the exit code is `0`, then the code style is okay.

### Tests

You can run the test suite by running `./make.py test`.
Only if the exit code is `0`, then all tests were passed.
This will also print the code and branch coverage and creates a coverage report in `./htmlcov`.

### Build

You can build the project for deployment by running `./make.py build`.
Only if the exit code is `0`, then the build was successful.

### Upload

You can upload the project to PyPI by running `./make.py upload`.
Only if the exit code is `0`, then the upload was successful.

### Set up PyCharm

1. At first set up the project as described above.
2. Run `./make.py build` successfully.
3. Open the project in PyCharm and configure it to use the interpreter of the venv.
4. You may mark the following directories as **Excluded**:
    - `./.mypy_cache`
    - `./.pytest_cache`
    - `./build`
    - `./dist`
    - `./htmlcov`
    - `./src/*.egg-info`
    - `./venv`
5. Mark the following directories as **Sources Root**:
    - `./stubs`
6. Run Configurations should automatically be imported from the `./.run` directory.

### Best practices

- Only specify the type if mypy and/or PyCharm cannot automatically infer the type.
    - For example PyCharm cannot infer the generic type of for example `self.socket = Placeholder[Socket]()`. Therefore, please write `self.socket: Placeholder[Socket] = Placeholder()` instead.
- Third-party libraries often do not provide type information, but you can create stub files (`*.pyi`) in the `./stubs` directory for it.
- Please use the type `Any` or type `Callable` with ellipsis `...` as argument types only if there is no other way or if it is actually correct.
- To decrease complexity, please consider:
    - Use composition over inheritance.
    - Separation of concerns: Each class has exactly one purpose.
    - Keep the line count of each file small.
    - Keep your dependencies small:
        - Try to avoid third-party libraries and use python's standard library instead.
        - Never use `import module`. Import everything explicitly using `from module import something` to keep the dependencies the smallest possible.
        - Use relative imports to import from other project files.
        - Please use those rules for import at the top of each file:
            - First, import python standard packages and third-party libraries ordered alphabetically by package name.
            - Afterwards, import other project files ordered by relative distance (from innermost e.g. `from .Lazy import Lazy` to outermost e.g. `from ..util.Lazy import Lazy`) and alphabetically by package name.
    - Please do not use method decorators except of course `@abstractmethod`, `@property` and `@staticmethod`.

## Links

[Here](https://github.com/franzmandl/rcpicar_example) is an example on how this library can be used.
