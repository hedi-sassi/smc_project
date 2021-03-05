"""
Utilities for client communication with the trusted server.
You should not need to change this file.
"""

import json
import time
from typing import Union, Tuple

import requests


class Communication:
    """
    Network communications with the server.

    Attributes:
        server_host: hostname of the server
        server_port: port of the server
        client_id: Identifier of this client
        poll_delay: delay between requests in seconds (default: 0.2 s)
        protocol: network protocol to use (default: "http")
    """

    def __init__(
            self,
            server_host: str,
            server_port: int,
            client_id: str,
            poll_delay: float = 0.2,
            protocol: str = "http"
    ):
        self.base_url = f"{protocol}://{server_host}:{server_port}"
        self.client_id = client_id
        self.poll_delay = poll_delay

    def send_private_message(
            self,
            receiver_id: str,
            label: str,
            message: Union[bytes, str]
    ) -> None:
        """
        Send a private message to the server.
        """

        url = f"{self.base_url}/private/{self.client_id}/{receiver_id}/{label}"
        requests.post(url, message)

    def retrieve_private_message(
            self,
            label: str
    ) -> bytes:
        """
        Retrieve a private message from the server.
        """

        url = f"{self.base_url}/private/{self.client_id}/{label}"
        # We can either use a websocket, or do some polling, but websockets would require asyncio.
        # So we are doing polling to avoid introducing a new programming paradigm.
        while True:
            res = requests.get(url)
            if res.status_code == 200:
                return res.content
            time.sleep(self.poll_delay)

    def publish_message(
            self,
            label: str,
            message: Union[bytes, str]
    ) -> None:
        """
        Publish a message on the server.
        """

        url = f"{self.base_url}/public/{self.client_id}/{label}"
        print(f"POST {url}")
        requests.post(url, message)

    def retrieve_public_message(
            self,
            sender_id: str,
            label: str
    ) -> bytes:
        """
        Retrieve a public message from the server.
        """

        url = f"{self.base_url}/public/{self.client_id}/{sender_id}/{label}"

        # We can either use a websocket, or do some polling, but websockets would require asyncio.
        # So we are doing polling to avoid introducing a new programming paradigm.
        while True:
            print(f"GET  {url}")
            res = requests.get(url)
            if res.status_code == 200:
                return res.content
            if res.status_code == 404:
                return None
            time.sleep(self.poll_delay)

    def retrieve_beaver_triplet_shares(
            self,
            op_id: str
    ) -> Tuple[int, int, int]:
        """
        Retrieve a triplet of shares generated by the trusted server.
        """

        url = f"{self.base_url}/shares/{self.client_id}/{op_id}"

        res = requests.get(url)
        print("#####", res)
        return tuple(json.loads(res.text))
