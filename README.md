# Unity Client

This repository contains a Unity client that interacts with a Unity simulation through a WebSocket server. It also includes a Flask server to receive goal coordinates.

## Prerequisites

Ensure you have Python 3.8 or later installed. It's recommended to use a virtual environment to manage dependencies.

## Setting up the Environment

1. Clone this repository:

    ```sh
    git clone https://github.com/Woshyy/smlr-ss24-communication-dummy.git
    cd smlr-ss24-communication-dummy

    ```

2. Create and activate a virtual environment:

    ```sh
    python -m venv venv
    source venv/bin/activate  # On Windows use `venv\Scripts\activate`
    ```

3. Install the required packages:

    ```sh
    pip install -r requirements.txt
    ```

## Running the Unity Client

To run the Unity client, execute the following command:

```sh
python unity_client.py
```

## How to Run the Website

To serve the website using Python 3's built-in HTTP server, follow these steps:

1. Ensure you have Python 3 installed.
2. Navigate to the `website` directory within the project directory:

    ```sh
    cd website
    ```

3. Start the HTTP server by running the following command:

    ```sh
    python3 -m http.server 8000
    ```

4. The website will be accessible at `http://localhost:8000`. Open this URL in your web browser to view the website.

## Triggering Movement Sequence on the Robot

To start the connection between the Python backend and the Unity client, follow these steps:

1. Send a POST request to the Flask server on port 3000. This request does not need to contain any specific data, as it is currently ignored. The only requirement is to trigger the start of the movement sequence of the robot.

    Here is an example using `curl`:

    ```sh
    curl -X POST http://localhost:3000/start
    ```

    Alternatively, you can use Python to send the request:

    ```python
    import requests

    response = requests.post('http://localhost:3000/start')
    print(response.status_code)
    ```

    Once the Flask server receives this packet, it will trigger the start of the movement sequence of the robot.

## Description

- `unity_client.py`: This script contains the main code for the Unity client. It includes classes for WebSocket communication, handling robot commands, and managing the environment.
- `website/`: This folder contains the build files from the Unity WebGL build. It includes all the necessary files to run the Unity simulation in a web browser.

## Ports

- **Port 3000**: This port is used by the Flask server to receive goal coordinates from Stefan's code. You can send POST requests with the goal positions to this port.
- **Port 5000**: This port is used for the WebSocket connection between the backend and the WebGL client. The Unity simulation communicates with this backend through the WebSocket server running on this port.
