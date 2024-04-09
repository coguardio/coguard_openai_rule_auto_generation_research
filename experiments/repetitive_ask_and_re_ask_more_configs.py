#!/bin/python

import json
from openai import OpenAI

def main():
    """
    The main function. The goal here is to iterate 10 times and keep collecting answers
    to obtain as complete of a list of spark configuration parameters as possible.
    """
    client = OpenAI()

    system_message = "You are an assistant that is a cybersecurity expert and knows their configuration files. Your response here should be a JSON list of strings which are unique and sorted alphabetically."
    assistant_responses = []
    question = "Please list security relevant Apache spark configuration parameters that you have not found yet in previous prompt answers to me. Include in the output list all previously found configuration parameters."

    for counter in range(10):
        messages = [
            {"role": "system", "content": system_message},
        ]
        for response in assistant_responses:
            messages.append({"role": "user", "content": question})
            messages.append({"role": "assistant", "content": response})
        messages.append({"role": "user", "content": question})
        completion = client.chat.completions.create(
            model = "gpt-4",
            messages = messages
        )
        print(f"Intermediate result: {completion.choices[0].message.content}")
        #print(f"New size: {len(json.loads(completion.choices[0].message.content))}")
        assistant_responses.append(completion.choices[0].message.content)
    print(assistant_responses[-1])


if __name__ == '__main__':
    main()
