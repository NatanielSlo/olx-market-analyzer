import re

class BaseProcessor:
    @staticmethod
    def clean_storage(value):
        if not value:
            return None
        
        match = re.search(r'(\d+)\s*(GB|TB)', str(value), re.IGNORECASE)
        if not match:
            return None
        
        number = float(match.group(1))
        unit = match.group(2).upper()
        
        if unit == 'TB':
            return int(number * 1024)
        return int(number)