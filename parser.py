def parse_response(text):
    """
    Parse AI response into structured dictionary.
    """

    result = {
        "Waste Item": "-",
        "Waste Category": "-",
        "Recyclable": "-",
        "Sri Lanka Disposal Guide": "-",
        "Environmental Impact": "-",
        "Reuse Idea": "-",
        "Eco Tip": "-",
        "Confidence": "-"
    }

    try:
        lines = text.split("\n")

        for line in lines:
            if ":" in line:
                key, value = line.split(":", 1)
                key = key.strip()
                value = value.strip()

                
                if key in result:
                    result[key] = value

    except Exception as e:
        print("Parsing error:", e)

    return result