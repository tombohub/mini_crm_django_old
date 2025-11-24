from dataclasses import dataclass

from bs4 import BeautifulSoup

from home.utils import parse_website_url


@dataclass
class BusinessData:
    business_name: str
    phone_number: str
    website_url: str


def extract_data(html: str) -> list[BusinessData]:
    """
    Extract business data from the given yellow pages canada page HTML.

    Args:
        html (str): The HTML content to extract data from.

    Returns:
        list[BusinessData]: A list of BusinessData objects containing the extracted data.
    """
    soup = BeautifulSoup(html, "html.parser")

    listings_all = soup.select(".listing_right_section")

    data = []
    for listing in listings_all:
        business_name = listing.select_one("a.listing__name--link").text
        phone_number = listing.select_one("span[appcallback_target_phone]").text
        website_button = listing.select_one("li.mlr__item--website")
        if website_button is not None:
            redirect_link = website_button.select_one("a").get("href")
            website_url = parse_website_url(redirect_link)
        else:
            website_url = ""

        data.append(
            BusinessData(
                business_name=business_name,
                phone_number=phone_number,
                website_url=website_url,
            )
        )
    return data


if __name__ == "__main__":
    d = extract_data()
    print(d)
