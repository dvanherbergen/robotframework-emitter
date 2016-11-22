# robotframework-emitter

robotframework-emitter is a listener for robotframework that emits all test execution events to a websocket server.

## Usage

To use this listener, you need to install the python requests library:

```
pip install requests
```

Start robotframework with the a robot framework listener argument:

```
--listener ${PATH_TO_EMITTER};${TARGET_URL};${IDENTIFIER}
```

Example using command line option:

```
robot --listener /tmp/RFEmitter.py;ws://localhost:8080/upload;Test_Set_1 tests.robot
```

Example using ROBOT_OPTIONS:

```
export ROBOT_OPTIONS="--listener /tmp/RFEmitter.py;ws://localhost:8080/upload;Test_Set_1"
robot tests.robot
```

## TODO

- Send events asynchronously
- Error handling
