import json


command = "weather"
public = True

def execute(command, user):
    from noob_snhubot import slack_client
    bot_id = slack_client.api_call("auth.test")["user_id"]

    response = "Provide your 5-digit Zip Code to check your local weather!\n - `<@{}> {} 90201`".format(bot_id, command)
    attachment = None

    weather = command.split()    
    
    if len(weather) > 1:        
        zip_code = weather[1]

        # TODO: Implement zip checking API call
        if zip_code.isdigit() and len(zip_code) == 5:
            response = None

            attachment = json.dumps([
                {
                    "fallback": f"https://wttr.in/{zip_code}.png",
                    "pretext": f"Here is your weather report for {zip_code}!",
                    "image_url": f"https://wttr.in/{zip_code}.png",           
                    "color": "#7CD197"
                }        
            ])

    return response, attachment