import datetime
import json
import os
import re
import sched
import sys
import threading
import time

import websocket._exceptions as ws_exceptions
from slackclient import SlackClient

# Import bot cmds
import cmds

# create env variable with client_id in it
client_id = os.environ["SLACK_CLIENT"]

# create new Slack Client object
slack_client = SlackClient(client_id)

# noob_snhubot's user ID in Slack:
bot_id = None

# constants
RTM_READ_DELAY = 1
MENTION_REGEX = "^<@(|[WU].+?)>(.*)"

# Dictionary of scheduled events
SCHED = {}

commands = list(cmds.COMMANDS.values())
commands.sort()

def sched_has_task(task) -> bool:
    """
    Returns true or false if the a task is currently scheduled
    """
    return any([task in v['arguments'] for v in SCHED.values()])
    
    # for v in SCHED.values():
    #     if task in v['arguments']:
    #         return True
    
    # return False

def cleanup_sched():
    """
    Removes expired events when their threds become inactive
    """
    sched = list(SCHED.items())

    for k, v in sched:
        if not v['thread'].is_alive():
            SCHED.pop(k, None)


def schedule_cmd(command, channel, sched_time, user_id = bot_id, event_type = 'message'):
    """
    Scheduled a bot command for execution at a specific time
    """
    s = sched.scheduler(time.time, datetime.timedelta)

    now_time = datetime.datetime.now().time()
    sched_date = datetime.date.today()

    if now_time > sched_time:
        sched_date += datetime.timedelta(days=1)

    sched_combine = datetime.datetime.combine(sched_date, sched_time)

    # Add the task to the scheduler
    task = s.enterabs(
        sched_combine.timestamp(), 
        1, 
        handle_command,
        (command, channel, bot_id, event_type)
    )

    # Spawn a thread daemon to handle the task
    t = threading.Thread(target=s.run)
    t.daemon = True
    t.start()

    # Add task to SCHED
    SCHED[t.ident] = {
        'thread': t,
        'time': task.time, 
        'function': task.action.__name__, 
        'arguments': task.argument
    }

    print(task) 

def parse_bot_commands(slack_events):
    """
        Parses a list of events coming from the Slack RTM API to find bot commands.
        If a bot command is found, this function returns a tuple of command and channel.
        If it's not found, then this function returns None, None.
    """
    for event in slack_events:
        if event["type"] == "message" and not "subtype" in event:
            user_id, message = parse_direct_mention(event["text"])
            if user_id == bot_id:
                return message, event["channel"], event["user"], event["type"]
        elif event["type"] == "team_join":
            return "greet user", None, event["user"].get("id"), event["type"]
    
    return None, None, None, None

def parse_direct_mention(message_text):
    """
        Finds a direct mention in message text and returns the user ID which 
        was mentioned. If there is no direct mentions, returns None
    """
    matches = re.search(MENTION_REGEX, message_text)
    # the first group contains the username, the second groups contains the remaining message
    return (matches.group(1), matches.group(2).strip()) if matches else (None, None)

def execute_command(command, commands, user):
    """
    Executes the command and returns responses received from command output

    Respones can be response, attachment, or channels, depending on command executed
    """
    response1 = None
    response2 = None
    
    for k, v in commands:     
        if command.lower().startswith(v):
            cmd = getattr(getattr(cmds, k), 'execute')
            
            response1, response2 = cmd(command, user)

    return response1, response2

def handle_command(command, channel, user, msg_type):
    """
        Executes bot command if the command is known
    """
    # Default response is help text for the user    
    default_response = "Does not compute. Try `<@{}> help` for command information.".format(bot_id)

    response = None
    attachment = None

    print("Recieved command '{}' from user: {} on channel: {}".format(command, user, channel))

    if msg_type == "message":
        response, attachment = execute_command(command, cmds.COMMANDS.items(), user)
    else:
        response, channel = execute_command(command, cmds.COMMANDS_HIDDEN.items(), user)
    
    # Sends the response back to the channel
    if attachment:
        print("Sending attachment: {}".format(attachment))
        slack_client.api_call(
            "chat.postMessage",
            channel=channel,
            attachments=attachment
        )
    else:
        print("Sending response: {}".format(response or default_response))
        slack_client.api_call(
            "chat.postMessage",
            channel=channel,
            text=response or default_response
        )

def main():
    # main loop to reconnect bot if necessary
    while True:
        #if slack_client.rtm_connect(with_team_state=False):
        if slack_client.rtm_connect(with_team_state=False, auto_reconnect=True):
            print("Noob SNHUbot connected and running!")
            
            # Read bot's user id by calling Web API method 'auth.test'
            bot_id = slack_client.api_call("auth.test")["user_id"]        

            print("Bot ID: " + bot_id)
            
            
            # replace with slack_client.server.connected
            #while slack_client.server.connected:

            
            while True:
                #cleanup_sched()
                
                # Exceptions: TimeoutError, ConnectionResetError, WebSocketConnectionClosedException
                try:
                    command, channel, user, msg_type = parse_bot_commands(slack_client.rtm_read())

                    if command:
                        handle_command(command, channel, user, msg_type)
                    time.sleep(RTM_READ_DELAY)                
                except TimeoutError as err:
                    print("Timeout Error occurred.\n{}".format(err))
                except ws_exceptions.WebSocketConnectionClosedException as err:
                    print("Connection is closed.\n{}\n{}".format(err, *sys.exc_info()[0:]))                    
                    break
                except ConnectionResetError as err:
                    print("Connection has been reset.\n{}\n{}".format(err, *sys.exc_info()[0:]))
                    break
                except:
                    print("Something awful happened!\n{}\n{}".format(*sys.exc_info()[0:]))
                    sys.exit()

                # Keep scheduling the task
                #if not sched_has_task('packtbook'):
                #    schedule_cmd('packtbook', 'CB8B913T2', datetime.time(21, 30))
                    #datetime.time.now() + datetime.timedelta(mins=5)
                    #d = datetime.datetime.now() + datetime.timedelta(seconds=15)
                    #schedule_cmd('packtbook', 'C93JZKLLA', d.time())

                # Execute clean up only when tasks have been scheduled
                #if SCHED:
                #    cleanup_sched()
                    
        else:
            print("Connection failed. Exception traceback printed above.")
            break

        print("Reconnecting...")    

if __name__ == "__main__":
    main()