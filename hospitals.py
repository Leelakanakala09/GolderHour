def get_maps_link(severity):
    if severity == "Severe":
        query = "trauma hospital near me"
    else:
        query = "hospital near me"

    return f"https://www.google.com/maps/search/{query.replace(' ', '+')}"
