## Aloe's Promptifier

A powerful and dynamic tool designed to enhance your workflow. Assign extra networks, entire prompts, negative prompts, or any string of your choice to specific trigger words.
-----------
![Screenshot](https://media.discordapp.net/attachments/1147985470035337290/1152008127252803644/image.png)

## Latest Updates
    
    - added button to quickly edit the .json file if corrections are needed
    - added more clarity to the buttons
    - cleaned the code
    - help textbox updated which provides a quick guide

## Active example

![Screenshot](https://media.discordapp.net/attachments/1055299933051293716/1152016926386700298/image.png)

## Install

Option 1: Using CMD

    Navigate to your extensions folder.
    Open a command prompt in that directory.
    Run the following command: https://github.com/PurpleBlueAloeVera/aloe-promptifier

Option 2: Manual Installation

    Go to the Extensions tab.
    Copy and paste the repository link. https://github.com/PurpleBlueAloeVera/aloe-promptifier
    Click 'Install' and restart.

## Features

- Dynamic Additions: Anything you type in the 'additions' field will be appended to your prompt when a trigger word is detected.
- No Duplicates: Multiple trigger words can lead to multiple additions, but they won't duplicate.
- Automatic Appending: No need for special symbols. The trigger words will automatically append the assigned strings, including LoRAs, prompts, and more.
- Regulator feature to create a list of safe words which IF detected, won't allow the banned words to be used. (Great for people that want to regulate their public SD bots, or else.)
      Example of a regulator use case would be: if the word "child" is detected in the prompt, any banned words of your choosing WON'T make it to generation if the user types the banned words. Will be further enhanced with time.

## Functions

- `Positive` = Appends only to the `positive` prompt no matter where the trigger word is detected.
- `Negative` = Appends only to the `negative` prompt, no matter where the trigger word is detected.
- `Default` = Appends `wherever the trigger word is detected`.

