import asyncio
import websockets
import json
import gym
from gym import spaces
import numpy as np
from flask import Flask, request
import threading


class RobotCommand:
    def __init__(self, type, axes, gripper, speed):
        self.type = type
        self.axes = axes
        self.gripper = gripper
        self.speed = speed

    def to_json(self):
        return json.dumps({
            "type": self.type,
            "axes": self.axes,
            "gripper": self.gripper,
            "speed": self.speed
        })


class EnvObservation:
    def __init__(self, obj=None, end_effector=None, axes=None):
        self.obj = obj if obj is not None else []
        self.end_effector = end_effector if end_effector is not None else []
        self.axes = axes if axes is not None else []

    @staticmethod
    def from_json(observation_json):
        observation_dict = json.loads(observation_json)
        observation = EnvObservation()
        observation.obj = observation_dict["Obj"]
        observation.end_effector = observation_dict["EndEffector"]
        observation.axes = observation_dict["Axes"]
        return observation


class WebSocketServer:
    def __init__(self, host='0.0.0.0', port=5000):
        self.host = host
        self.port = port
        self.clients = set()

    async def handle_connection(self, websocket, path):
        print("Connection received")
        self.clients.add(websocket)
        try:
            await websocket.wait_closed()
        finally:
            self.clients.remove(websocket)

    async def send_robot_command(self, command):
        for client in self.clients:
            await client.send(command.to_json())
            observation_json = await client.recv()
            print(f"Received observation: {observation_json}")
            return EnvObservation.from_json(observation_json)

    async def start_server(self):
        async with websockets.serve(self.handle_connection, self.host, self.port):
            print(f"WebSocket server is running on ws://{self.host}:{self.port}")
            await asyncio.Future()

    async def run_server(self):
        await self.start_server()


class GoalReceiver:
    def __init__(self):
        self.app = Flask(__name__)
        self.goal = None

        @self.app.route('/', methods=['POST'])
        def post():
            data_json = request.json
            self.goal = data_json  # Store the received goal
            return 'Data received: ' + str(data_json) + '\n'

    def run(self, debug=False):
        def run_app():
            self.app.run(port=3000, debug=debug)

        thread = threading.Thread(target=run_app)
        thread.daemon = True  # This ensures that the thread will close when the main program exits
        thread.start()

    def get_goal(self):
        while self.goal is None:
            print("Waiting for goal")
            asyncio.sleep(1)  # Adding a small delay to avoid busy-waiting
        return self.goal
    
    def is_goal_received(self):
        return self.goal is not None

    def reset_goal(self):
        self.goal = None


class UnityEnv(gym.Env):
    def __init__(self):
        super(UnityEnv, self).__init__()

        self.server = WebSocketServer()

        # Start the server within the same event loop
        asyncio.create_task(self.server.run_server())

        self.action_space = spaces.Box(
            low=-180, high=180, shape=(7,), dtype=np.float32)
        self.observation_space = spaces.Box(
            low=-np.inf, high=np.inf, shape=(18,), dtype=np.float32)

    async def reset(self):
        axes = [-180, -50, 10, 5, 3, 2, 1]
        command = RobotCommand(1, axes, False, 1.5)
        return await self.server.send_robot_command(command)

    async def step(self, action):
        axes = action.tolist()
        command = RobotCommand(1, axes, False, 1.5)
        observation = await self.server.send_robot_command(command)

        reward = self.get_reward(observation)
        done = self.is_termination_condition(observation)
        info = {}

        return observation, reward, done, info

    def get_reward(self, observation):
        # Put reward function here
        return 0

    def is_termination_condition(self, observation):
        # Put termination condition here
        return False

    async def wait_for_connection(self):
        while (len(self.server.clients) == 0):
            print("There are no clients connected. Waiting for clients to connect...")
            await asyncio.sleep(1)


async def main():
    goal_receiver = GoalReceiver()
    goal_receiver.run()

    env = UnityEnv()
    await env.wait_for_connection()
    await env.reset()
    c = 0
    _goal = goal_receiver.get_goal()
    while True:
        if goal_receiver.is_goal_received():
            c = 0
            env.reset()
            goal_receiver.reset_goal()
        
        if c < 120:
            obs = await env.step(np.array([c, c, c, c, c, c, c]))
            c += 1



asyncio.run(main())
