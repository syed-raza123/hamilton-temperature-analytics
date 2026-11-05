temperatures = [18.5, 32.4, 25.1, 35.6, 29.8]

weather = {
    "city": "Hamilton",
    "year": 2025,
    "unit": "Celsius"
}

##Combined Challenge — 2 marks Write a for loop that goes through the temperatures list, calls your is_hot function, and prints only temperatures above 30°C. Hint: Use if is_hot(temp): inside your loop.
def is_hot(temp):
    if temp > 30:
        return True
    else:
        return False
    