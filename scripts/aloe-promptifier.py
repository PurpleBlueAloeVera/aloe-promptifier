import os
import re
import json
import gradio as gr
import modules.scripts as scripts

# Determine the path to the directory containing the currently executing script
current_dir = os.path.dirname(os.path.abspath(__file__))

# Go up one directory to reach the main folder of the extension
repo_dir = os.path.join(current_dir, '..')

class Script(scripts.Script):

    def title(self):
        return "Prompt Appender"

    def show(self, is_img2img):
        return scripts.AlwaysVisible

    def save_to_file(self, addition, triggers):
        additions_file = os.path.join(repo_dir, "additions_prompt.json")
        
        if os.path.exists(additions_file):
            with open(additions_file, encoding="utf8") as f:
                data = json.load(f)
        else:
            data = {}

        data[addition] = triggers

        with open(additions_file, 'w', encoding="utf8") as f:
            json.dump(data, f, indent=4)

    def ui(self, is_img2img):
        # Create a main accordion for all widgets
        help_value = (
            "In addition, you're gonna want to type whatever LoRAs or embeddings you want the triggers words to add to the prompt.\n\n"
            "2. Trigger Words:\n"
            "In trigger words, you type the words you want to be automatic triggers for the prompt addition. And they should be separated by commas. DO NOT PUT A COMMA AT THE END !! Example: something, trigger, yes\n\n"
            "3. Click 'Save' to save add this your configuration. You can add as many as you want.\n\n"
            "BEHAVIOUR:\n\n"
            "The detection script will detect multiple keywords and add multiple additions. So make sure to organize it well !\n\n"
            "Example:\n"
            "If you have a LoRA for clothes, that has \"wearing\" as a trigger and another LoRA for.. haircuts, that has \"hair\" in the triggers and that you type \"wearing and hair\" in the prompt. It'll load both LoRAs.\n\n"
            "If you wanna edit the file manually: Extensions/AloePromptifier/additions_prompt.json"
        )

        main_accordion = gr.Accordion("Aloe's Promptifier", open=True)

        with main_accordion:
            addition_input = gr.Textbox(label="Addition", placeholder="Type whatever LoRAs, embeddings.. or plain text that you want the triggers words to add to the prompt")
            triggers_input = gr.Textbox(label="Trigger Words", placeholder="Type your trigger words for that specific addition. Write them separated by commas.")
            save_button = gr.Button(value="Save")

            help_accordion = gr.Accordion("Aloe's Promptifier Guide", open=False)
            with help_accordion:
                gr.Textbox(label="Scroll down to see the full text", value=(help_value), editable=True, height=200, lines=8)

            # Set click behavior for the save button
        save_button.click(self.output_func, inputs=[addition_input, triggers_input], outputs=[addition_input, triggers_input])

        return [main_accordion] 

    def output_func(self, addition, triggers):
        self.save_to_file(addition, triggers.split(','))
        return "", "", "Saved successfully!"  # Clearing the text boxes and updating the message box

    def process(self, p):
        additions_file = os.path.join(repo_dir, "additions_prompt.json")
        if os.path.exists(additions_file):
            with open(additions_file, encoding="utf8") as f:
                additions_data = json.load(f)

            original_prompt = p.all_prompts[0]
            detected_additions_main = set()
            detected_additions_negative = set()

            for prompt in p.all_prompts:
                for addition, triggers in additions_data.items():
                    for trigger in triggers:
                        if re.search(r'\b' + re.escape(trigger) + r'\b', prompt):
                            detected_additions_main.add(addition)
                            break

            for negative_prompt in p.all_negative_prompts:
                for addition, triggers in additions_data.items():
                    for trigger in triggers:
                        if re.search(r'\b' + re.escape(trigger) + r'\b', negative_prompt):
                            detected_additions_negative.add(addition)
                            break

            for addition in detected_additions_main:
                p.all_prompts = [prompt + addition for prompt in p.all_prompts]
                if getattr(p, 'all_hr_prompts', None) is not None:
                    p.all_hr_prompts = [prompt + addition for prompt in p.all_hr_prompts]

            for addition in detected_additions_negative:
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
