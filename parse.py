import re
from assistant import send_timer_update, send_temp_update
import pi

# Parses LLM Instructions for recipe
def parser(text):
    sentences = re.split(r'[%%%\n]', text)
    sentences = [sentence.strip() for sentence in sentences if sentence]
    return sentences

# "Give me a pasta recipe where each instruction is separated by %%%, and only give me instructions, no ingredients, etc. Indent each new instruction without the instruction number"

# Parse type of instruction
def parse_type(text):
    if re.search(r'\bIngredients: \[', text) and re.search(r'\bInstructions: \[', text):
        return "recipe"
    if re.search(r'\bdone\b', text.lower()):
        return "done"
    return None

#Parse actual instruction
def parse_instruction(text):
    # Search for the Instructions section using a regular expression
    match = re.search(r'Instructions:\s*\[(.*?)\]', text)
    if match:
        # Extract the instructions text from the match
        instructions_text = match.group(1)
        
        # Use re.findall to capture all the instructions inside the quotes and return them as a list
        instructions = re.findall(r'"(.*?)"', instructions_text)
        
        return instructions

def parse_conversation(response):
    # Use a regular expression to match the response after '### Response:'
    match = re.search(r'### Response:\s*(.*)', response)
    if match:
        # Return the captured response text
        return match.group(1).strip()
    else:
        # Return an empty string if no response is found
        return ""

    
# Handles fractional values
def convert_to_decimal(value):
    if value is None: return 0.0
    if '/' in value:
        numerator, denominator = value.split('/')
        return float(numerator) / float(denominator)
    return float(value)

def parse_time(sentence):
    match = re.search(r'(\d+/\d+|\d+\.\d+|\d+)\s*(hour|hours?)', sentence)
    match2 = re.search(r'(\d+/\d+|\d+\.\d+|\d+)\s*(minute|minutes?)', sentence)
    match3 = re.search(r'(\d+/\d+|\d+\.\d+|\d+)\s*(second|seconds?)', sentence)
    
    if match or match2 or match3:
        if match: hours = match.group(1)
        else: hours = '0'
        if match2: minutes = match2.group(1)
        else: minutes = '0'
        if match3: seconds = int(match3.group(1))
        else: seconds = 0

        hours = convert_to_decimal(hours)
        minutes = convert_to_decimal(minutes)

        total_time = 3600 * hours + 60 * minutes + seconds
        return total_time
    return None

def checktime(sentence):
    sentence = sentence.lower()
    time = parse_time(sentence)
    if time:
        print(f"Checking sentence:{sentence}")
        return time
    return None

def checktemp(sentence):
    # Convert sentence to lowercase for case-insensitive matching
    sentence = sentence.lower()
    
    # Print the sentence being checked
    print(f"Checking sentence: {sentence}")
    
    # Check for temperature patterns in Celsius or Fahrenheit
    matchC = re.search(r'(\d+\.\d+)\s*°?C', sentence) or re.search(r'(\d+)\s*°?C', sentence)
    matchF = re.search(r'(\d+\.\d+)\s*F', sentence) or re.search(r'(\d+)\s*F', sentence)
    
    # Define keywords and their associated temperatures in Celsius
    keyword_temperatures = {
        'boil': 100,  # Boiling point of water in Celsius
        'simmer': 85,  # Simmering temperature range in Celsius
        'freeze': 0,  # Freezing point of water in Celsius
        'chill': 4,  # Chilling temperature range in Celsius
        'heat': 60,  # General heating temperature in Celsius
        'cook': 75,  # General cooking temperature in Celsius
        'roast': 200,  # Roasting temperature in Celsius (for baking)
        'bake': 180,  # Baking temperature in Celsius
        'grill': 180  # Grilling temperature in Celsius
    }

    # If no cooking-related keyword is found, check for explicit temperature values
    if matchC:
        temperature = matchC.group(1)
        print(f"Temperature detected: {temperature} °C")
        return temperature
    elif matchF:
        temperature = matchF.group(1)
        temperature =  int((temperature - 32) / (9/5))
        print(f"Temperature detected: {temperature} °C")
        return temperature
    
    # Check if any cooking-related keyword exists in the sentence  
    else:
        for keyword, temp in keyword_temperatures.items():
            if keyword in sentence:
                print(f"Cooking-related keyword detected: {keyword} at {temp}°C")
                return temp  # Return the temperature for the detected cooking action



def scale(sentence):
    sentence.lower()
    match_grams = re.search(r'(\d+/\d+|\d+\.\d+|\d+)\s*(gram|grams|g)', sentence)
    match_kgs = re.search(r'(\d+/\d+|\d+\.\d+|\d+)\s*(kg|kgs)', sentence)
    match_lb = re.search(r'(\d+/\d+|\d+\.\d+|\d+)\s*(lb|lbs)', sentence)
    amount_in_grams = 0

    if match_grams:
        amount = match_grams.group(1)
        amount_in_grams = convert_to_decimal(amount)
        return amount_in_grams
        
    
    elif match_kgs:
        amount = match_kgs.group(1)
        amount_in_kgs = convert_to_decimal(amount)
        amount_in_grams = amount_in_kgs * 1000
        return amount_in_grams
    
    elif match_lb:
        amount = match_lb.group(1)
        amount_in_lb = convert_to_decimal(amount)   
        amount_in_grams = amount_in_lb * 453.592
        return amount_in_grams
            
    return None


def main():
    # Sample output from ChatGPT
    # Input: Give me a pasta recipe where each instruction is separated by %%%, and only give me instructions, no ingredients, etc. Indent each new instruction without the instruction number. Specify temperature and weights needed
    text = """Bring 4 liters of salted water to a boil over high heat (about 212°F/100°C). %%%
    Cook 200g of pasta until al dente, following the package instructions (usually about 8-10 minutes). %%%
    Drain the pasta and reserve 120ml of pasta water. %%%
    Heat 30ml of olive oil in a skillet over medium heat (around 300°F/150°C). %%%
    Add 4 minced garlic cloves and sauté for 1-2 minutes until fragrant. %%%
    Add 1/4 teaspoon of chili flakes and stir for 30 seconds. %%%
    Toss the cooked pasta into the skillet and mix well for 1-2 minutes. %%%
    Stir in the reserved 120ml of pasta water to loosen the sauce. %%%
    Season with salt and pepper to taste. %%%
    Garnish with 30g of grated Parmesan and fresh parsley before serving."""
    texts = parser(text)
    print(texts)
    print("\n")
    for cur in texts:
        print(scale(cur))
        checktemp(cur)
        print(parse_time(cur))
        checktime(cur)
        print(checktime(cur))
    # print("\n")
    # print(checktime(texts))
    # print("\n")
    # print(parse_time(texts))
    # print("\n")
    # print(checktemp(texts))
    # print("\n")
    # print(scale(texts))
    

#main()
