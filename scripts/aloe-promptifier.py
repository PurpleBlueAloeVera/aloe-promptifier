import os
import re
import json
import gradio as gr
import modules.scripts as scripts

current_dir = os.path.dirname(os.path.abspath(__file__))
repo_dir = os.path.join(current_dir, '..')

class Script(scripts.Script):

    def title(self):
        return "Prompt Appender"

    def show(self, is_img2img):
        return scripts.AlwaysVisible

    def save_to_file(self, addition, triggers, type_flag):
        additions_file = os.path.join(repo_dir, "additions_prompt.json")

        if os.path.exists(additions_file):
            with open(additions_file, encoding="utf8") as f:
                data = json.load(f)
        else:
            data = {}

        trigger_list = triggers.split(',')
        
        # Add comma and space before the user's addition
        formatted_addition = ", " + addition

        data[formatted_addition] = {"type": type_flag, "triggers": [t.strip() for t in trigger_list]}

        with open(additions_file, 'w', encoding="utf8") as f:
            json.dump(data, f, indent=4)



    def ui(self, is_img2img):
        help_value = (
            "In addition, you're gonna want to type whatever LoRAs or embeddings you want the triggers words to add to the prompt. In the triggers you'll want to put whatever keyword(s) you want to be the triggers that'll append the addition you chose to your prompt. Then, by selecting POS or NEG, you decide to lock its place. Meaning if you picked POS, where ever you type the trigger, will only append the addition to the positive prompt. And vice-vera. You may also choose NONE, if you want it to behave based on where your keyword is detected. If detected in positive prompt, addition will be appended to positive prompt."
        )

        main_accordion = gr.Accordion("Aloe's Promptifier", open=False)

        with main_accordion:
            addition_input = gr.Textbox(label="Addition", placeholder="Type whatever LoRAs, embeddings.. or plain text that you want the triggers words to add to the prompt")
            triggers_input = gr.Textbox(label="Trigger Words", placeholder="Type your trigger words for that specific addition. Write them separated by commas.")
            type_selector = gr.Radio(label="Type of Trigger", choices=["[pos]", "[neg]", "None"], default="None")  # Adding the type selector
            save_button = gr.Button(value="Save")
            help_text = gr.Textbox(label="Scroll down to see the full text", value=(help_value), editable=False, height=100, lines=8)
                
            save_button.click(self.output_func, inputs=[addition_input, triggers_input, type_selector], outputs=[addition_input, triggers_input])  # Add type_selector to inputs

            # Return components as a list
            return [addition_input, triggers_input, type_selector, save_button, help_text]

    def output_func(self, addition, triggers, type_flag):
        self.save_to_file(addition, triggers, type_flag)
        return "", "", "Saved successfully!"  # Clearing the text boxes and updating the message box


    def process(self, p, *args, **kwargs):
        additions_file = os.path.join(repo_dir, "additions_prompt.json")
        if os.path.exists(additions_file):
            with open(additions_file, encoding="utf8") as f:
                additions_data = json.load(f)

            original_prompt = p.all_prompts[0]
            detected_additions_main = set()
            detected_additions_pos = set()
            detected_additions_neg = set()
            used_triggers = set()  # Track which triggers have been used

            # Function to detect triggers and add to detected additions set
            def detect_and_add(prompt, detected_additions_main, detected_additions_pos, detected_additions_neg):
                for addition, info in additions_data.items():
                    for trigger in info["triggers"]:
                        if trigger not in used_triggers and re.search(r'\b' + re.escape(trigger) + r'\b', prompt):  # Check if the trigger has been used before
                            if info["type"] == "[pos]":
                                detected_additions_pos.add(addition)
                            elif info["type"] == "[neg]":
                                detected_additions_neg.add(addition)
                            else:
                                detected_additions_main.add(addition)
                            used_triggers.add(trigger)  # Mark the trigger as used

            for prompt in p.all_prompts:
            detect_and_add(prompt, detected_additions_main, detected_additions_pos, detected_additions_neg)

            # Appending the detected additions

            # First, append additions for detected triggers of type None
            for addition in detected_additions_main:
                p.all_prompts = [prompt + addition for prompt in p.all_prompts]
                if getattr(p, 'all_hr_prompts', None) is not None:
                    p.all_hr_prompts = [prompt + addition for prompt in p.all_hr_prompts]
                p.all_negative_prompts = [prompt + addition for prompt in p.all_negative_prompts]

            # Next, ensure all [pos] additions are added to all_prompts and all_hr_prompts
            for addition in detected_additions_pos:
                p.all_prompts = [prompt + addition for prompt in p.all_prompts]
                if getattr(p, 'all_hr_prompts', None) is not None:
                    p.all_hr_prompts = [prompt + addition for prompt in p.all_hr_prompts]

            # Lastly, ensure all [neg] additions are added to all_negative_prompts
            for addition in detected_additions_neg:
                p.all_negative_prompts = [prompt + addition for prompt in p.all_negative_prompts]



            if original_prompt != p.all_prompts[0]:
                p.extra_generation_params["Trigger words prompt"] = original_prompt
        else:
            print(f"File {additions_file} not found.", file=sys.stderr)



    def append_text(self, p, addition):
        p.all_prompts = [prompt + addition for prompt in p.all_prompts]
        if getattr(p, 'all_hr_prompts', None) is not None:
            p.all_hr_prompts = [prompt + addition for prompt in p.all_hr_prompts]
        p.all_negative_prompts = [prompt + addition for prompt in p.all_negative_prompts]
