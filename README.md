# robotframework-emitter

robotframework-emitter is a listener for robotframework that emits all test execution events to a REST service.

## Usage


To use this listener, you need to install the python requests library:

```
sudo pip install requests

```

To run the tests:
```
sudo pip install HTTPretty

```




Start robotframework with the a robot framework listener argument:

```
--listener ${PATH_TO_EMITTER};${TARGET_HOST};${IDENTIFIER};${PERSIST}
```

PATH_TO_EMITTER:  fully qualified path to emitter.py
TARGET_HOST:      test framework host
IDENTIFIER:       test run name
PERSIST:          store run information



Example using command line option:

```
robot --listener /tmp/Emitter.py;Test_Set_1;https://localhost:8080/ tests.robot
```

Example using ROBOT_OPTIONS:

```
export ROBOT_OPTIONS="--listener /tmp/Emitter.py;http://localhost:8080/upload;Test_Set_1"
robot tests.robot
```

## TODO

- Send events asynchronously
- Error handling
