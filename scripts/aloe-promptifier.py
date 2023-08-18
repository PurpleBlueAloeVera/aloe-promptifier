import os
import re
import json
import gradio as gr
import modules.scripts as scripts
import sys

current_dir = os.path.dirname(os.path.abspath(__file__))
repo_dir = os.path.join(current_dir, '..')

class Script(scripts.Script):

    def title(self):
        return "Prompt Appender"

    def show(self, is_img2img):
        return scripts.AlwaysVisible

    def save_to_file(self, addition, triggers, type_flag):
        additions_file = os.path.join(repo_dir, "additions_prompt.json")
        
        trigger_list = triggers.split(',')
        
        # Add comma and space before the user's addition
        formatted_addition = ", " + addition

        # If the file doesn't exist, initialize data with the user's input
        if not os.path.exists(additions_file):
            data = {
                formatted_addition: {"type": type_flag, "triggers": [t.strip() for t in trigger_list]}
            }
        else:  # If the file exists, load its content and add the new entry
            with open(additions_file, encoding="utf8") as f:
                data = json.load(f)
                data[formatted_addition] = {"type": type_flag, "triggers": [t.strip() for t in trigger_list]}

        # Save the updated data back to the file
        with open(additions_file, 'w', encoding="utf8") as f:
            json.dump(data, f, indent=4)

    def ui(self, is_img2img):
        help_value = "..."  # Your help text here

        main_accordion = gr.Accordion("Aloe's Promptifier", open=False)

        with main_accordion:
            enable_checkbox = gr.Checkbox(label="Enable Prompt Appender", default=True)
            addition_input = gr.Textbox(label="Addition", placeholder="Type whatever LoRAs, embeddings.. or plain text that you want the triggers words to add to the prompt")
            triggers_input = gr.Textbox(label="Trigger Words", placeholder="Type your trigger words for that specific addition. Write them separated by commas.")
            type_selector = gr.Radio(label="Type of Trigger", choices=["[pos]", "[neg]", "None"], default="None")
            save_button = gr.Button(value="Save")
            help_text = gr.Textbox(label="Scroll down to see the full text", value=(help_value), editable=False, height=100, lines=8)

            save_button.click(self.output_func, inputs=[addition_input, triggers_input, type_selector], outputs=[addition_input, triggers_input])

            # Disable addition input components if checkbox is unchecked
            addition_input.disabled = not enable_checkbox.value
            triggers_input.disabled = not enable_checkbox.value
            type_selector.disabled = not enable_checkbox.value
            save_button.disabled = not enable_checkbox.value

            # Return components as a list
            return [enable_checkbox, addition_input, triggers_input, type_selector, save_button, help_text]

    def output_func(self, addition, triggers, type_flag):
        if type_flag is None:
            type_flag = "None"
        self.save_to_file(addition, triggers, type_flag)
        return "", "", "Saved successfully!"  # Clearing the text boxes and updating the message box


    def regulator(self, p):
        regulated_file = os.path.join(repo_dir, "regulated.json")
        if os.path.exists(regulated_file):
            with open(regulated_file, encoding="utf8") as f:
                regulated_data = json.load(f)

            for safe_words, banned_words in regulated_data.items():
                safe_words_list = safe_words.split('|')
                for safe_word in safe_words_list:
                    # If any safe word is detected in the prompts
                    if any(safe_word in prompt for prompt in p.all_prompts):
                        def remove_banned_words(prompt):
                            for word in banned_words:
                                # Removing the banned word from the prompt using regex
                                prompt = re.sub(r'\b' + re.escape(word) + r'\b', '', prompt)
                            return prompt.strip()  # Removing any extra spaces

                        # Apply the removal function to the prompts
                        p.all_prompts = [remove_banned_words(prompt) for prompt in p.all_prompts]
                        
                        # If 'all_hr_prompts' attribute exists, do the same for them
                        if getattr(p, 'all_hr_prompts', None) is not None:
                            p.all_hr_prompts = [remove_banned_words(prompt) for prompt in p.all_hr_prompts]

                        # Apply the removal function to negative prompts
                        p.all_negative_prompts = [remove_banned_words(prompt) for prompt in p.all_negative_prompts]
        else:
            print(f"File {regulated_file} not found.", file=sys.stderr)

    def process(self, p, enable_prompt_appender=True, *args, **kwargs):
        if enable_prompt_appender:
            # Processing with the additions
            additions_file = os.path.join(repo_dir, "additions_prompt.json")
            if os.path.exists(additions_file):
                with open(additions_file, encoding="utf8") as f:
                    additions_data = json.load(f)

                detected_additions_pos = set()
                detected_additions_neg = set()

                def detect_and_add(prompt, type_flag, detected_additions):
                    for addition, info in additions_data.items():
                        for trigger in info["triggers"]:
                            if re.search(r'\b' + re.escape(trigger) + r'\b', prompt):
                                if info["type"] == type_flag:
                                    detected_additions.add(addition)

                for prompt in p.all_prompts:
                    detect_and_add(prompt, "None", detected_additions_pos)
                    detect_and_add(prompt, "[pos]", detected_additions_pos)
                    detect_and_add(prompt, "[neg]", detected_additions_neg)

                for prompt in p.all_negative_prompts:
                    detect_and_add(prompt, "None", detected_additions_neg)
                    detect_and_add(prompt, "[neg]", detected_additions_neg)
                    detect_and_add(prompt, "[pos]", detected_additions_pos)

                for addition in detected_additions_pos:
                    p.all_prompts = [prompt + addition for prompt in p.all_prompts]
                    if getattr(p, 'all_hr_prompts', None) is not None:
                        p.all_hr_prompts = [prompt + addition for prompt in p.all_hr_prompts]
                
                for addition in detected_additions_neg:
                    p.all_negative_prompts = [prompt + addition for prompt in p.all_negative_prompts]
            else:
                print(f"File {additions_file} not found.", file=sys.stderr)

            # Call the regulator function after processing with the additions
            self.regulator(p)

    def append_text(self, p, addition):
        p.all_prompts = [prompt + addition for prompt in p.all_prompts]
        if getattr(p, 'all_hr_prompts', None) is not None:
            p.all_hr_prompts = [prompt + addition for prompt in p.all_hr_prompts]
        p.all_negative_prompts = [prompt + addition for prompt in p.all_negative_prompts]
