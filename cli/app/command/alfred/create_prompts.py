import os
import json
import uuid
import click
from openai import OpenAI

# Configuration
HOME = os.path.expanduser("~")

PROMPTS_DIR = os.path.join(
    HOME,
    "Documents",
    "Alfred.alfredpreferences",
    "snippets",
    "0110--coding-prompts",
)

REASONING_PROMPTS_DIR = os.path.join(
    HOME,
    "Documents",
    "Alfred.alfredpreferences",
    "snippets",
    "0120--reasoning-prompts",
)


@click.command()
@click.option("--topic", prompt="Enter the technology or topic", help="Technology or topic to create prompts for")
@click.option("--context", help="Additional context for the prompt generation")
@click.option("--no-reasoning", is_flag=True, help="Don't create reasoning prompts")
@click.option("--no-code-only", is_flag=True, help="Don't create code-only prompts")
def create_prompts(topic, context, no_reasoning, no_code_only):
    """Create specialist prompts for Alfred snippets."""
    # Ensure the prompts directories exist
    os.makedirs(PROMPTS_DIR, exist_ok=True)
    os.makedirs(REASONING_PROMPTS_DIR, exist_ok=True)

    # Normalize topic (lowercase, trim)
    topic = topic.strip().lower()

    # Generate the prompt names
    specialist_name = f"specialist-{topic}"
    code_only_name = f"specialist-{topic}-(code-only)"
    reasoning_name = f"reason-{specialist_name}"

    try:
        # Show a message that we're generating prompts
        click.echo(f"Generating AI prompts for '{topic}'...")

        # Generate prompts using OpenAI
        specialist_prompt, code_only_prompt, reasoning_prompt = _generate_prompts_with_openai(topic, context)

        # Create the snippet files
        specialist_file = _create_snippet_file(specialist_name, specialist_prompt)

        if not no_code_only:
            code_only_file = _create_snippet_file(code_only_name, code_only_prompt)
        if not no_reasoning:
            reasoning_file = _create_snippet_file(reasoning_name, f"{reasoning_prompt}\n\n", REASONING_PROMPTS_DIR)

        # Display success message
        click.echo(f"✅ Created {specialist_file}")
        click.echo(f"✅ Created {code_only_file}")
        click.echo(f"✅ Created {reasoning_file}")
        click.echo(f"\nPrompts created successfully for '{topic}'!")

    except Exception as e:
        click.echo(f"❌ Error creating prompts: {str(e)}")


def _generate_uid():
    """Generate a new uppercase UUID."""
    return str(uuid.uuid4()).upper()


def _create_snippet_file(name, prompt, directory=PROMPTS_DIR):
    """Create a snippet file with the given name and prompt."""
    uid = _generate_uid()
    filename = f"{name} [{uid}].json"
    filepath = os.path.join(directory, filename)

    # Create the snippet data
    data = {"alfredsnippet": {"snippet": prompt, "uid": uid, "name": name, "keyword": ""}}

    # Write the file
    with open(filepath, "w") as f:
        json.dump(data, f, indent=2)

    return filename


def _generate_reasoning_prompt(specialist_prompt, topic, add_context):
    """Generate a reasoning prompt based on specialist prompt."""
    try:
        client = OpenAI()

        # Define the system message and user prompt
        system_message = """
        You are an expert at transforming instructional prompts into reasoning prompts.
        A reasoning prompt should be concise, direct to the point, and avoid direct instructions or explicit reasoning steps.
        """

        user_prompt = REASONING_PROMPT_TEMPLATE.format(
            specialist_prompt=specialist_prompt,
            topic=topic,
            add_context=add_context,
        )

        # Make the API call
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[{"role": "system", "content": system_message}, {"role": "user", "content": user_prompt}],
            temperature=0,
        )

        transformed_prompt = response.choices[0].message.content.strip()
        return transformed_prompt

    except Exception as e:
        click.echo(f"❌ Error generating reasoning prompt with OpenAI: {str(e)}")
        raise


def _generate_prompts_with_openai(topic, add_context):
    """Use OpenAI to generate prompts for the given topic."""
    try:
        client = OpenAI()

        # Generate specialist prompt
        system_message = """
        You are an expert prompt engineer, specialized in creating prompts for LLMs to act as domain specialists.
        """

        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": system_message},
                {"role": "user", "content": GENERAL_PROMPT_TEMPLATE.format(topic=topic, add_context=add_context)},
            ],
            temperature=0.7,
            max_tokens=300,
        )

        specialist_prompt = response.choices[0].message.content.strip()

        # Generate code-only prompt
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": system_message},
                {"role": "user", "content": CODE_ONLY_PROMPT_TEMPLATE.format(topic=topic, add_context=add_context)},
            ],
            temperature=0.7,
            max_tokens=300,
        )

        code_only_prompt = response.choices[0].message.content.strip()

        # Generate reasoning prompt
        reasoning_prompt = _generate_reasoning_prompt(specialist_prompt, topic, add_context)

        return specialist_prompt, code_only_prompt, reasoning_prompt

    except Exception as e:
        click.echo(f"❌ Error generating prompts with OpenAI: {str(e)}")
        raise


GENERAL_PROMPT_TEMPLATE = f"""
I want you to act as a prompt generator. First I will give you a topic. You can find an example of how you should create the new prompt below. An example is surrounded by the prompt_example tag below.

<prompt_example>
I want you to act as an English pronunciation assistant for Turkish speaking people. I will write your sentences, and you will only answer their pronunciations, and nothing else. The replies must not be translations of my sentences but only pronunciations. Pronunciations should use Turkish Latin letters for phonetics. Do not write explanations on replies. My first sentence is:
</prompt_example>

Follow the rules below when creating the prompts. They are surrounded by the <rules> and </rules> tags.

<rules>
1. The prompt should be self-explanatory and appropriate to the title.
2. Don't refer to the provided example.
3. Always start the prompts with 'I want you to act as'.
4. Always finish the prompt with 'My first [task/question/goal] is:'.
5. Write only the prompt and nothing more.
6. It should be written in simple plain text, without any formatting.
7. The final prompt should instruct the answers to be concise and direct.
8. Added to the topic, more context information might be provided to be added to the prompt.
9. If the given topic is about a programming technology, the prompt should instruct to skip installation and set up instructions.
10. Bring as much details as possible to the prompt.
</rules>

Additional context: {{add_context}}
My title for the prompt is: {{topic}}

Return ONLY the prompt text, nothing else.
"""

CODE_ONLY_PROMPT_TEMPLATE = f"""
I want you to act as a prompt generator for programming languages. I will give you a language/framework/library/tool. Then you should write a prompt about that language/framework/library/tool. An example is surrounded by the prompt_example tag below.

<prompt_example>
I want you to act as a JavaScript code generator. I will describe specific programming tasks or problems, and your role is to respond with the appropriate JavaScript code to solve them. Your responses should be purely in code form, without explanations or annotations. Please ensure that the code is concise, functional, uses concise comments and directly addresses the task at hand. My first task for you is:
</prompt_example>

Follow the rules below when creating the prompts. They are surrounded by the <rules> and </rules> tags.

<rules>
1. The prompt should be appropriate to the given language/framework/library/tool.
2. Don't refer to the provided example.
3. Always start the prompts with 'I want you to act as'.
4. Always finish the prompt with 'My first [task/question/goal] is:'.
5. Write only the prompt and nothing more.
6. The prompt should instruct to assume I have a basic understanding of the topic, but don't assume I have any prior knowledge of the specific task or question.
7. The final prompt should instruct the answers to be concise and direct.
8. The prompt should instruct to provide answers with code only.
9. The prompt should instruct to use standard libraries or community defaults where possible instead of creating its own custom solutions.
10. Added to the topic, more context information might be provided to be added to the prompt.
11. The prompt should instruct to skip installation and set up instructions.
12. Bring as much details as possible to the prompt.
</rules>

Additional context: {{add_context}}
My title for the prompt is: {{topic}}

Return ONLY the prompt text, nothing else.
"""

REASONING_PROMPT_TEMPLATE = f"""
Please transform the following instructional prompt into a reasoning prompt:

Original prompt:
```
{{specialist_prompt}}
```

Guidelines for the transformation:
1. Make it concise and direct to the point
2. Remove any direct instructions or explicit reasoning steps
3. Focus on the core intent of the prompt
4. Maintain the same domain expertise but simplify the framing
5. The result should be cleaner and more focused
6. New prompts start with "You are a <domain expert>..."
7. The prompt should ask guidance on how to do something, not a question
8. The prompt should finish with ":"

Additional context: {{add_context}}
The topic is: {{topic}}

Return ONLY the transformed prompt text, nothing else.
"""


if __name__ == "__main__":
    create_prompts()
