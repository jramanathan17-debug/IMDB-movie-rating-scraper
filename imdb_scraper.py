import csv
import re
import time

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait


# ==========================================
# IMDb Top 250 Movie Scraper
# ==========================================

URL = "https://www.imdb.com/chart/top/"


# ------------------------------------------
# Chrome setup
# ------------------------------------------

options = Options()
options.add_argument("--start-maximized")

driver = webdriver.Chrome(options=options)


try:

    # --------------------------------------
    # Open IMDb
    # --------------------------------------

    print("Opening IMDb...")

    driver.get(URL)

    time.sleep(5)

    print("PAGE TITLE:", driver.title)
    print("CURRENT URL:", driver.current_url)


    # --------------------------------------
    # Human Verification
    # --------------------------------------

    page_text = driver.find_element(
        By.TAG_NAME,
        "body"
    ).text

    if (
        "Human Verification" in driver.title
        or "Let's confirm you are human" in page_text
    ):

        print()
        print("IMDb Human Verification detected.")
        print("Please complete the verification manually in Chrome.")

        input(
            "After verification is completed, press ENTER here..."
        )

        time.sleep(5)


    # --------------------------------------
    # Wait for page
    # --------------------------------------

    time.sleep(3)


    # --------------------------------------
    # Find movie elements
    # --------------------------------------

    movie_links = driver.find_elements(
        By.CSS_SELECTOR,
        'a[href*="/title/tt"]'
    )

    print()
    print("Movie links found:", len(movie_links))


    movies = []


    # --------------------------------------
    # Extract movie information
    # --------------------------------------

    for link in movie_links:

        try:

            # Get link text
            text = link.text.strip()

            if not text:
                continue


            # --------------------------------
            # Get complete parent text
            # --------------------------------

            parent = link.find_element(
                By.XPATH,
                "./ancestor::li[1]"
            )

            row_text = parent.text.strip()

            if not row_text:
                continue


            # --------------------------------
            # Get Rank and Title
            # --------------------------------

            rank_title_match = re.search(
                r"(\d+)\.\s*(.+)",
                text
            )

            if not rank_title_match:
                continue


            rank = rank_title_match.group(1)

            title = rank_title_match.group(2).strip()


            # --------------------------------
            # Get Year
            # --------------------------------

            year_match = re.search(
                r"\b(18|19|20)\d{2}\b",
                row_text
            )

            if year_match:

                year = year_match.group(0)

            else:

                year = "N/A"


            # --------------------------------
            # Get Votes
            # --------------------------------

            vote_match = re.search(
                r"\(([0-9.,]+[KMB]?)\)",
                row_text
            )

            if vote_match:

                votes = vote_match.group(1)

            else:

                votes = "N/A"


            # --------------------------------
            # Avoid duplicate movies
            # --------------------------------

            already_exists = any(
                movie["Rank"] == rank
                for movie in movies
            )

            if already_exists:
                continue


            # --------------------------------
            # Save movie
            # --------------------------------

            movies.append({

                "Rank": rank,
                "Title": title,
                "Year": year,
                "Votes": votes

            })


            print(
                rank,
                "|",
                title,
                "|",
                year,
                "|",
                votes
            )


            # Stop at 250 movies

            if len(movies) >= 250:

                break


        except Exception as e:

            print(
                "Skipped one movie:",
                e
            )


    # --------------------------------------
    # Sort movies by Rank
    # --------------------------------------

    movies.sort(
        key=lambda x: int(x["Rank"])
    )


    # --------------------------------------
    # Final count
    # --------------------------------------

    print()
    print("--------------------------------")
    print(
        "Total movies extracted:",
        len(movies)
    )
    print("--------------------------------")


    # --------------------------------------
    # Save CSV
    # --------------------------------------

    if len(movies) > 0:

        with open(
            "imdb_top_250.csv",
            "w",
            newline="",
            encoding="utf-8-sig"
        ) as file:

            fieldnames = [
                "Rank",
                "Title",
                "Year",
                "Votes"
            ]

            writer = csv.DictWriter(
                file,
                fieldnames=fieldnames
            )

            writer.writeheader()

            writer.writerows(movies)


        print()
        print("CSV file created successfully!")
        print("File name: imdb_top_250.csv")


    else:

        print()
        print("No movie data was extracted.")
        print("Please check whether IMDb page loaded correctly.")


finally:

    input(
        "\nPress ENTER to close Chrome..."
    )

    driver.quit()