import asyncio

from colorama import Back, Fore, Style, init
from TikTokLive import TikTokLiveClient
from TikTokLive.events import CommentEvent, ConnectEvent

# Initialize colorama
init()

# Create the client
client: TikTokLiveClient = TikTokLiveClient(unique_id="@mightysigmaoverload")

# Initialize vote counts
votes = {"!up": 0, "!down": 0, "!left": 0, "!right": 0}
command_order = []

# Flag to track if client is already started
client_started = False

# Listen to the connect event
@client.on(ConnectEvent)
async def on_connect(event: ConnectEvent):
    global client_started
    print(f"{Style.BRIGHT}{Fore.CYAN}Connected to @{event.unique_id}"+
          f"\n(Room ID: {client.room_id}){Style.RESET_ALL}")
    if not client_started:
        client_started = True
        # Start the voting process when connected
        asyncio.create_task(start_voting())

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
            chosen_command = next(
                cmd for cmd in command_order if cmd in top_commands
            )
        else:
            chosen_command = None

        # Execute the chosen command if any votes were cast
        if chosen_command:
            execute_command(chosen_command)
        else:
            print(f"{Style.BRIGHT}{Fore.RED}No votes were cast.{Style.RESET_ALL}")

def execute_command(command: str):
    # Example of different styled output based on the command
    if command == "!up":
        print(f"{Style.BRIGHT}{Back.GREEN}{Fore.WHITE}Moving up{Style.RESET_ALL}")
    elif command == "!down":
        print(f"{Style.BRIGHT}{Back.RED}{Fore.WHITE}Moving down{Style.RESET_ALL}")
    elif command == "!left":
        print(f"{Style.BRIGHT}{Back.YELLOW}{Fore.BLACK}Moving left{Style.RESET_ALL}")
    elif command == "!right":
        print(f"{Style.BRIGHT}{Back.BLUE}{Fore.WHITE}Moving right{Style.RESET_ALL}")

# if __name__ == '__main__':
#     asyncio.run(client.run())

if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    client.run()