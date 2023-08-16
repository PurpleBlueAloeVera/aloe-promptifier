Aloe's Promptifier
=======
A powerful and dynamic tool to enhance your workflow by assigning extra networks, entire prompts, negative prompts, or any string of your choice to trigger words !
-----------
![Screenshot](https://media.discordapp.net/attachments/1112805199233425458/1141343491788644353/PromtifierCapture.JPG)

## Install

Simply go in your extensions folder, open a CMD to that directory, and do the following command:
git clone https://github.com/PurpleBlueAloeVera/aloe-promptifier

OR

Go in extensions tab, and manually copy paste the link of the repo, and press install. Then restart.

## Features
- Anything you type in additions, will be appended to your prompt after a trigger word is detected
- Multiple detections = multiple additions
- No need for symbols, or anything. The trigger words will add whatever you assign to them automatically. (LoRAs, prompts, anything)


## Work in progress. . .

This is my first public extension, and a very experimental one. I hope anyone can find something useful to it. I know that I personally find it very usefull and practical since I use it all the time.
Any feedback would be greatly appreciated !

## Examples

Addition:

``<lora:some_subject_you_simp_over:0.55>, simp subject, ``

Trigger words (as many as you want, they won't duplicate the additions):

``simpsu``

How the prompt will change if you type "simpsu":

Positive prompt:
``simpsu, <lora:some_subject_you_simp_over:0.55>, simp subject, ``

Then select if you want it to be a [POS] addition, a [NEG] or a neutral [None] addition. 

POS : No matter WHERE the word is detected, it'll always append the addition to the positive prompt
NEG : No matter WHERE the word is detected, it'll always append the addition to the negative prompt
NONE : It'll always append the addition WHERE the trigger word has been detected.

And that's it ! It's highly customizable and allows for great control.
