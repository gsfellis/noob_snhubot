
command = "help"
public = True

def execute(command, user):
    # import on execution
    from cmds import COMMANDS
    from noob_snhubot import slack_client
    bot_id = slack_client.api_call("auth.test")["user_id"]

    commands = list(COMMANDS.values())
    commands.sort()

    attachment = None    
    response = f'You can issue me a `command` using the format: `<@{bot_id}> <command> [options]`. Follow `command` prompts and help screens to determine `options`.\nHere are all the commands I know how to execute:\n'

    for command in commands:
        response += "  - `{}`\n".format(command)

    return response, attachment