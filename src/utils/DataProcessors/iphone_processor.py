import re

class IphoneProcessor:
    @staticmethod
    def extract_battery_health(text):
        if not isinstance(text, str):
            return None
        
        # KROK 1: Szukamy konkretnie frazy z baterią (tak jak wcześniej)
        pattern_bater = r'(?:bater.{0,20}?\b(\d{2,3})\s?(?:%|procent|proc)|(\d{2,3})\s?(?:%|procent|proc).{0,20}?bater)'
        match = re.search(pattern_bater, text, re.IGNORECASE | re.DOTALL)
        
        if match:
            val = match.group(1) if match.group(1) else match.group(2)
            return int(val)
        
        # KROK 2: Jeśli nie znaleziono baterii, szukamy jakiegokolwiek procentu
        # Szukamy liczby 80-99 (bo 100% to najczęściej "pewność" lub "sprawność")
        # iPhone 15 Pro raczej nie spadł jeszcze poniżej 80% kondycji
        fallback_pattern = r'\b([6-9][0-9])\s?%'
        fallback_match = re.search(fallback_pattern, text)
        
        if fallback_match:
            return int(fallback_match.group(1))
            
        return None
