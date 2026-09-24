import requests
import re
import time
import mysql.connector


BASE_URL = "https://mpcore-listingsearch-prod-web.boyner.com.tr/api/v3/product/search"

TOKEN = "!!!"

PAGE_SIZE = 24

DB_HOST = "localhost"
DB_USER = "root"
DB_PASSWORD = "..."
DB_NAME = "boyner_data"
TABLE_NAME = "boyner_products"


headers = {
    "accept": "*/*",
    "accept-language": "tr-TR,tr;q=0.9,en-US;q=0.8,en;q=0.7",
    "appversion": "0.1.0",
    "ismarketplace": "true",
    "origin": "https://www.boyner.com.tr",
    "osversion": "1",
    "phonetype": "1",
    "platform": "1",
    "referer": "https://www.boyner.com.tr/",
    "storeid": "1",
    "token": TOKEN,
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                  "AppleWebKit/537.36 (KHTML, like Gecko) "
                  "Chrome/152.0.0.0 Safari/537.36",
    "x-is-web": "true"
}



def extract_perfume_type(title):

    title_lower = title.lower()

    if "extrait de parfum" in title_lower:
        return "Extrait De Parfum"

    if "eau de parfum" in title_lower:
        return "EDP"

    if "eau de toilette" in title_lower:
        return "EDT"

    if re.search(r"\bedp\b", title_lower):
        return "EDP"

    if re.search(r"\bedt\b", title_lower):
        return "EDT"

    if "parfum" in title_lower:
        return "Parfum"

    return ""


def extract_ml(title):

    match = re.search(
        r"(\d+(?:[.,]\d+)?)\s*ml\b",
        title,
        re.IGNORECASE
    )

    if match:
        return match.group(1).replace(",", ".")

    return ""



def normalize_price(price):

    if price is None:
        return None

    price = str(price).strip()

    if not price:
        return None

    price = price.replace("₺", "")
    price = price.replace("TL", "")
    price = price.replace(" ", "")

    
    if "," in price:
        price = price.split(",")[0]

   
    price = price.replace(".", "")

    return price



def get_products(page):

    params = {
        "SearchKey": "parfüm",
        "Page": page,
        "IncludeFilters": "false",
        "DropListingPageSize": PAGE_SIZE
    }

    response = requests.get(
        BASE_URL,
        params=params,
        headers=headers,
        timeout=30
    )

    response.raise_for_status()

    data = response.json()

    return data.get("Result", {}).get("Products", [])



connection = mysql.connector.connect(
    host=DB_HOST,
    user=DB_USER,
    password=DB_PASSWORD
)

cursor = connection.cursor()

cursor.execute(
    f"""
    CREATE DATABASE IF NOT EXISTS `{DB_NAME}`
    CHARACTER SET utf8mb4
    COLLATE utf8mb4_unicode_ci
    """
)

connection.commit()

cursor.close()
connection.close()



connection = mysql.connector.connect(
    host=DB_HOST,
    user=DB_USER,
    password=DB_PASSWORD,
    database=DB_NAME
)

cursor = connection.cursor()



cursor.execute(
    f"""
    CREATE TABLE IF NOT EXISTS `{TABLE_NAME}` (
        id INT AUTO_INCREMENT PRIMARY KEY,
        brand VARCHAR(255),
        product_name TEXT,
        gender VARCHAR(100),
        perfume_type VARCHAR(100),
        ml DECIMAL(10,2),
        sales_channel VARCHAR(255),
        country VARCHAR(100),
        price DECIMAL(12,2),
        currency VARCHAR(10),
        stock_status VARCHAR(50),
        product_url TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """
)

connection.commit()



cursor.execute(
    f"TRUNCATE TABLE `{TABLE_NAME}`"
)

connection.commit()



insert_query = f"""
    INSERT INTO `{TABLE_NAME}` (
        brand,
        product_name,
        gender,
        perfume_type,
        ml,
        sales_channel,
        country,
        price,
        currency,
        stock_status,
        product_url
    )
    VALUES (
        %s,
        %s,
        %s,
        %s,
        %s,
        %s,
        %s,
        %s,
        %s,
        %s,
        %s
    )
"""



page = 1
total_products = 0


while True:

    try:

        products = get_products(page)

        print(
            f"Page {page} -> "
            f"{len(products)} products"
        )

        if not products:

            print("\nNo more products.")
            break


        for product in products:

            title = product.get("Title", "")


            brand = product.get("Brand", "")


            gender = product.get("Gender", "")


            perfume_type = extract_perfume_type(title)


            ml = extract_ml(title)

            if ml == "":
                ml = None
            else:
                ml = float(ml)


            event_data = product.get("EventData") or {}

            sales_channel = event_data.get(
                "Cd_item_vendor",
                ""
            )


            price_info = product.get("PriceInfo") or {}

            price = price_info.get(
                "Price",
                None
            )

            price = normalize_price(price)


            is_out_of_stock = product.get(
                "IsOutOfStock",
                False
            )

            stock = product.get(
                "Stock",
                0
            )

            if is_out_of_stock or stock == 0:
                stock_status = "Out of Stock"
            else:
                stock_status = "In Stock"


            product_url = product.get(
                "Url",
                ""
            )

            if product_url:

                if product_url.startswith("http"):

                    full_url = product_url

                else:

                    full_url = (
                        "https://www.boyner.com.tr/"
                        + product_url.lstrip("/")
                    )

            else:

                full_url = ""

            country = ""

            currency = "TRY"


            cursor.execute(
                insert_query,
                (
                    brand,
                    title,
                    gender,
                    perfume_type,
                    ml,
                    sales_channel,
                    country,
                    price,
                    currency,
                    stock_status,
                    full_url
                )
            )

            total_products += 1



        connection.commit()

        print(
            f"Saved products: {total_products}"
        )


        page += 1

        time.sleep(0.3)



    except requests.exceptions.RequestException as e:

        print(
            f"\nPage {page} request error:"
        )

        print(e)

        print(
            "\nRetrying in 5 seconds..."
        )

        time.sleep(5)



    except Exception as e:

        print(
            f"\nUnexpected error - Page {page}:"
        )

        print(e)

        connection.rollback()

        break


cursor.close()

connection.close()


print("\n" + "=" * 60)
print("COMPLETED")
print("=" * 60)

print(f"Total products: {total_products}")
print(f"Database: {DB_NAME}")
print(f"Table: {TABLE_NAME}")