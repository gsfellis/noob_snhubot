# Noob SNHUbot

A simple Slack bot written in Python for the [snhu_coders](https://snhu_coders.slack.com) Slack workgroup. It's a simple and fun side project for me, and anyone else is welcome to participate. Contact me on Slack or open an issue if you'd like to see an enhancement to the bot.

## Current State

Noob SNHUbot is very basic. It will only respond to a select few queries currently configured within a Python List (needs to be updated). It also only utilizes the Slack Client [RTM API](https://api.slack.com/rtm). The [Events](https://api.slack.com/events) and [Web](https://api.slack.com/web) APIs have not been utilized, but likely will be implemented later.

## Functionality

Noob SNHUbot will respond to the following direct messages. To begin a conversation, start a message in the channel with `@Noob SNHUbot`:

* do
   - Basic command from tutorial.
   - Responds with: _"Sure...write some more code then I can do that!"_
* what's my name?
   - Simple call and response.
   - Resonds with: _"Your name is `<@{name}>`! Did you forget or something?"_
* what is the airspeed velocity of an unladen swallow?
   - A clever joke.
   - Responds with a Youtube video to a Monty Python and the Holy Grail clip.
* roll `XdY[±Z]`
    - Rolls X number of Y-Sided dice with a + or - Z modifier!
    - Invalid rolls will respond with _"That roll is not valid. Try `@Noob SNHUbot roll help`"_
    - `roll help` will respond with a help message that explains the syntax with examples.
    - Valid rolls respond with a Slack [Attachment](https://api.slack.com/docs/message-attachments) message indicated the total value of the roll, what roll is operated on, individual roll values, and the modifier applied.

## Contributing

If you'd like to contribute, join us on the Slack workspace mentioned above. All SNHU students are welcome.