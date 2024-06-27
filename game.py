# you will need to install a web driver of your choice
# the code is yours and it is free to use and edit
# the tiktok user must be live online  before running the code
# 
# if you need any help contact with me:
# Discord: @zampx 
# Telegram: @zampx
# YouTube: @exatube
# TikTOk: @exatube
#

import asyncio
import signal
import sys
import time

from colorama import Back, Fore, Style, init
from TikTokLive import TikTokLiveClient
from TikTokLive.events import CommentEvent, ConnectEvent
from selenium import webdriver
from selenium.webdriver.edge.service import Service
from selenium.webdriver.edge.options import Options
from selenium.webdriver.common.keys import Keys  # Import Keys for keyboard actions
from selenium.webdriver.common.action_chains import ActionChains  # Import ActionChains
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By

# Initialize colorama
init()

# Create the TikTokLiveClient
client: TikTokLiveClient = TikTokLiveClient(unique_id="@exatube")

# Initialize vote counts
votes = {"!up": 0, "!down": 0, "!left": 0, "!right": 0}
command_order = []

# Flag to track if client is already started
client_started = False

# Initialize the Edge WebDriver
exec = "./msedgedriver.exe"
service = Service(executable_path=exec)
options = Options()
options.add_argument("--log-level=3")  # Suppress WebDriver logs
driver = webdriver.Edge(service=service, options=options)


# Function to simulate pressing arrow keys
def simulate_arrow_keys(command):
    # Create an ActionChains object
    actions = ActionChains(driver)

    # Simulate pressing the arrow keys based on the command
    if command == "!up":
        actions.send_keys(Keys.ARROW_UP).perform()
    elif command == "!down":
        actions.send_keys(Keys.ARROW_DOWN).perform()
    elif command == "!left":
        actions.send_keys(Keys.ARROW_LEFT).perform()
    elif command == "!right":
        actions.send_keys(Keys.ARROW_RIGHT).perform()


# Listen to the connect event
@client.on(ConnectEvent)
async def on_connect(event: ConnectEvent):
    global client_started
    print(f"{Style.BRIGHT}{Fore.CYAN}Connected to @{event.unique_id}" +
          f"\n(Room ID: {client.room_id}){Style.RESET_ALL}")
    if not client_started:
        client_started = True
        # Start the voting process when connected
        asyncio.create_task(start_voting())
        driver.get("https://www.2048.org")


# Listen to the comment event
async def on_comment(event: CommentEvent) -> None:
    global votes, command_order
    comment = event.comment.lower()
    command = comment.split()[0]  # Get the first word of the comment
    if command in votes:
        votes[command] += 1
        command_order.append(command)


client.add_listener(CommentEvent, on_comment)


async def start_voting():
    global votes, command_order
    while True:
        # Clear previous votes
        votes = {k: 0 for k in votes}
        command_order = []

        # Start a 10-second voting period
        await asyncio.sleep(10)

        # Determine the command with the highest votes
        max_votes = max(votes.values())
        top_commands = [
            cmd for cmd, count in votes.items() if count == max_votes
        ]

        # If there's a tie, use the first command in the order
        if len(top_commands) == 1:
            chosen_command = top_commands[0]
        elif command_order:
            chosen_command = next(cmd for cmd in command_order
                                  if cmd in top_commands)
        else:
            chosen_command =  None

        # just enable if a tie causes a problem
        #chosen_command =  top_commands[0]
        
        # Execute the chosen command if any votes were cast
        if chosen_command:
            await execute_command(chosen_command)
        else:
            print(
                f"{Style.BRIGHT}{Fore.RED}No votes were cast.{Style.RESET_ALL}"
            )


async def execute_command(command: str):
    # Example of different styled output based on the command
    if command in ["!up", "!down", "!left", "!right"]:
        simulate_arrow_keys(command)
        # Example of different styled output based on the command
        if command == "!up":
            print(
                f"{Style.BRIGHT}{Back.GREEN}{Fore.WHITE}Moving up{Style.RESET_ALL}"
            )
        elif command == "!down":
            print(
                f"{Style.BRIGHT}{Back.RED}{Fore.WHITE}Moving down{Style.RESET_ALL}"
            )
        elif command == "!left":
            print(
                f"{Style.BRIGHT}{Back.YELLOW}{Fore.BLACK}Moving left{Style.RESET_ALL}"
            )
        elif command == "!right":
            print(
                f"{Style.BRIGHT}{Back.BLUE}{Fore.WHITE}Moving right{Style.RESET_ALL}"
            )


async def shutdown(loop):
    tasks = [t for t in asyncio.all_tasks() if t is not asyncio.current_task()]
    [task.cancel() for task in tasks]
    await client.disconnect()
    print(f"{Style.BRIGHT}{Fore.YELLOW}Cancelling " +
          f"{len(tasks)} outstanding tasks{Style.RESET_ALL}")
    await asyncio.gather(*tasks, return_exceptions=True)
    loop.stop()


def main():
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)

    async def handle_shutdown():
        await shutdown(loop)

    try:
        # Handle SIGINT (Ctrl+C) on Windows
        signal.signal(signal.SIGINT,
                      lambda sig, frame: asyncio.create_task(handle_shutdown()))
        client.run()
    except (KeyboardInterrupt, SystemExit):
        print(f"{Style.BRIGHT}{Fore.YELLOW}Received exit signal," +
              f" shutting down...{Style.RESET_ALL}")
    finally:
        loop.close()
        driver.quit()


if __name__ == '__main__':
    main()

    # Keep the script running until interrupted
    while True:
        time.sleep(10)  # Keep script alive