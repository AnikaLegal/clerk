def drf_isoformat(datetime):
    iso_str = datetime.isoformat()
    if iso_str.endswith("+00:00"):
        iso_str = iso_str[:-6] + "Z"

    return iso_str
