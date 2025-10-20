import random
import string

def generate_password(length=12):
    # Define the character sets
    lowercase = string.ascii_lowercase
    uppercase = string.ascii_uppercase
    digits = string.digits

    # Combine all characters
    all_characters = lowercase + uppercase + digits

    # Randomly select characters for the password
    password = ''.join(random.choice(all_characters) for _ in range(length))

    return password

