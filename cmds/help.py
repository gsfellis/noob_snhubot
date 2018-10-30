import json

command = "help"
public = True

def execute(command, user):
    # import on execution
    from cmds import COMMANDS
    from noob_snhubot import slack_client
    bot_id = slack_client.api_call("auth.test")["user_id"]

    commands = list(COMMANDS.values())
    commands.sort()
    
    response = None
    #response = f'You can issue me a `command` using the format: `<@{bot_id}> <command> [options]`. Follow `command` prompts and help screens to determine `options`.\nHere are all the commands I know how to execute:\n'

    cmd_list = ""
    for command in commands:
        cmd_list += "  - `{}`\n".format(command)

    attachment = json.dumps([
        {
            "text": "So you need a little help? Below you can find examples and a list of commands I know how to execute.\n",            
            "thumb_url": "http://st.depositphotos.com/1431107/4033/v/950/depositphotos_40334707-stock-illustration-vector-help-sign.jpg",           
            "fields":[  
                {
                    "title":"Commands",
                    "value":f"{cmd_list}",
                    "short":"true"
                },
                {
                    "title":"Examples",
                    "value":f"<@{bot_id}> help\n<@{bot_id}> channels\n<@{bot_id}> catalog it140",
                    "short":"true"
                }
            ],
			"color": "warning"
        }
    ])


    return response, attachment