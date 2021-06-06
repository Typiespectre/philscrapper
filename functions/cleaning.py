import re


def clean_text(text):
    new_text = ""
    cleaned_text = re.sub(r"\\x..", "", str(text), flags=re.I)
    cleaned_text = re.sub(r"\\n..", "", cleaned_text, flags=re.I)
    cleaned_text = re.sub(
        "[\{\}\[\]\/?.,;:|\)*~`!^\-_+<>@\#$%&\\\=\('\"’”“–—]", "", cleaned_text
    )
    cleaned_text = re.sub(r"[0-9]", " ", cleaned_text)
    cleaned_text = re.sub(r"\s+", " ", cleaned_text, flags=re.I)
    cleaned_text = re.sub(r"^\s+", " ", cleaned_text)
    cleaned_text = re.sub(r"\s+$", " ", cleaned_text)
    cleaned_text = re.sub(r"\s+[a-zA-Z]\s+", " ", cleaned_text)
    return cleaned_text