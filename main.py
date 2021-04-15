import requests
from lxml import html
import csv
import pandas as pd


def process_extract(scraped_data):
    if scraped_data:
        clean_data = scraped_data[0]

        if "LISTING BY: " in clean_data:
            data = clean_data.replace("LISTING BY: ", "")
            return data

        if "- " in clean_data:
            data = clean_data.replace("- ", "")
            return data

        return clean_data
    data = ' '.join(' '.join(scraped_data).split())
    return data


def process_listed_period(listed_period_data):
    if listed_period_data:
        listed_period = ' '.join(' '.join(listed_period_data).split())
        if "days on Zillow" not in listed_period:
            listed_period = ""
            return listed_period
        return listed_period


def process_price(price_extract):
    if price_extract:
        price_str = price_extract[0].replace("$", "").replace(",", "")
        price = int(float(price_str))
        return price

    price = ' '.join(' '.join(price_extract).split())
    return price


def process_size(size_sqft):
    if size_sqft == ["--"]:
        return None

    if size_sqft:
        size = size_sqft[0].replace(",", "")
        size = int(size)
        return size
    return ""


def scrape(url):
    header = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_2) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.96 Safari/537.36",
        "Accept-Language": "en-GB,en-US;q=0.9,en;q=0.8"
    }

    response = requests.get(url, headers=header)

    tree = html.fromstring(response.content)
    search_results = tree.xpath('//*[@id="grid-search-results"]//article')
    properties = []

    for prop in search_results:
        url_link_extract = prop.xpath(".//a[@class='list-card-link list-card-link-top-margin list-card-img']/@href")
        listed_period_extract = prop.xpath(".//div[@class='list-card-variable-text list-card-img-overlay']//text()")
        price_extract = prop.xpath(".//div[@class='list-card-price']/text()")
        beds_extract = prop.xpath(".//ul[@class='list-card-details']/li[1]/text()")
        baths_extract = prop.xpath(".//ul[@class='list-card-details']/li[2]/text()")
        size_extract = prop.xpath(".//ul[@class='list-card-details']/li[3]/text()")
        ad_type_extract = prop.xpath(".//ul[@class='list-card-details']/li[4]/text()")
        address_extract = prop.xpath(".//address//text()")
        broker_extract = prop.xpath(".//p[@class='list-card-extra-info']//text()")

        url_link = process_extract(url_link_extract)
        listed_period = process_listed_period(listed_period_extract)
        price = process_price(price_extract)
        beds = process_extract(beds_extract)
        baths = process_extract(baths_extract)
        size = process_size(size_extract)
        ad_type = process_extract(ad_type_extract)
        address = process_extract(address_extract)
        broker = process_extract(broker_extract)

        property = {
            'url link': url_link,
            'ad period': listed_period,
            'price': price,
            'no. beds': beds,
            'no. baths': baths,
            'size': size,
            'ad type': ad_type,
            'address': address,
            'broker': broker
        }

        properties.append(property)
    return properties


def convert_to_csv(properties_dict):
    columns = ['url link', 'ad period', 'price', 'no. beds', 'no. baths', 'size', 'ad type', 'address', 'broker']
    csv_filename = "zillow_properties.csv"

    try:
        with open(csv_filename, 'w') as f:
            writer = csv.DictWriter(f, fieldnames=columns)
            writer.writeheader()

            for data in properties_dict:
                writer.writerow(data)
    except IOError:
        print("I/O Error")


def get_stats(properties_dict):
    convert_to_csv(properties_dict)

    df = pd.read_csv("zillow_properties.csv")
    print(f"{len(df.index)} properties found. \n")

    mean = df['price'].mean()
    filtered_df = df[df[['price', 'size']].notnull().all(1)]
    price_total = filtered_df['price'].sum()
    size_total = filtered_df['size'].sum()
    avg_price_sqft = price_total / size_total
    print(f"Average price (total): ${mean}, Average price (per sqft): ${avg_price_sqft} \n")

    ad_type_counts = df['ad type'].value_counts()
    print(f"{ad_type_counts} \n")

    broker_counts = df['broker'].str.replace(r"\(.*\)", "").value_counts()
    print(f"{broker_counts} \n")


if __name__ == "__main__":
    url = "https://www.zillow.com/new-york-ny"
    properties = scrape(url)
    get_stats(properties)