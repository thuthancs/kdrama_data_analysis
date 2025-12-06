import re

def preprocess_title(title):
    # Use regex to extract all the text after the pattern '. ' which is the dot followed by a space
    match = re.search(r'\.\s+(.*)', title)
    if match:
        return match.group(1).strip()
    return title.strip()

def preprocess_episodes(episodes):
    # Remove 'eps' and space between the number and eps and convert it to an integer
    return int(episodes.replace('eps', '').strip())