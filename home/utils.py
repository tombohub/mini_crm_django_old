import urllib.parse


def parse_website_url(redirect_link: str | None) -> str | None:
    """
    Parse the website URL from the yellow page canada redirect link.

    Args:
        redirect_link (str): The redirect link that contains the website URL.

    Returns:
        str: The website URL if found, otherwise "not found".
    """
    if redirect_link is None:
        return None

    decoded_link = urllib.parse.unquote(redirect_link)
    split_link = decoded_link.split("redirect=")
    website_url = split_link[1]

    return website_url
