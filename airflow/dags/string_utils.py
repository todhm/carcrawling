import re 

def parse_number(target_string):
    numexp = re.compile(r'[-]?\d[\d,]*[\.]?[\d{2}]*') #optional - in front
    numbers = numexp.findall(target_string)    
    if numbers:
        number = numbers[0]
        number = float(number.replace(',',''))
        return number
    return None 