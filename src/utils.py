from datetime import datetime

def today_formatted_date() -> str:
    months = {
        1: "janeiro", 2: "fevereiro", 3: "março", 4: "abril",
        5: "maio", 6: "junho", 7: "julho", 8: "agosto",
        9: "setembro", 10: "outubro", 11: "novembro", 12: "dezembro"
    }
    today = datetime.now()
    return f"{today.day} de {months[today.month]} de {today.year}"


