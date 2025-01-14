import requests
import argparse
import os

def create_day_and_year_folder(year: str, day: str):
    current_dir = os.getcwd()
    if year in current_dir:
        full_path = f"{day}"
    else:
        if not os.path.exists(year):
            os.makedirs(year)
        full_path = f"{year}/{day}"
    
    if not os.path.exists(full_path):
        os.makedirs(full_path)
    return full_path

def get_input_data(year: str, day: str, session: str):
    input_url = f"https://adventofcode.com/{year}/day/{day}/input"
    cookies = dict(session=session)
    response = requests.get(input_url, cookies=cookies)

    if response.status_code == 200:
        input_file = response.text
        base_path = day if year in os.getcwd() else f"{year}/{day}"
        file_path = f"{base_path}/input.txt"

        if not os.path.isfile(file_path):
            with open(file_path, 'w') as file:
                file.write("")
                
        with open(file_path, 'w') as file:
            file.write(input_file)

        # Create empty example.txt file
        with open(f"{base_path}/example.txt", "w") as file:
            file.write("")
    else:
        print(f"Failed to download input data. Status code: {response.status_code}")

def main():
    parser = argparse.ArgumentParser(description="Create a folder and download input for the day and year provided.")
    parser.add_argument("-d", "--day", required=True, type=str, help="Day of the challenge from 1 - 25")
    parser.add_argument("-y", "--year", required=True, type=str, help="Year of the challenge starting from 2015")
    parser.add_argument("-s", "--session", required=True, type=str, help="Your session cookie")
    args = parser.parse_args()

    create_day_and_year_folder(args.year, args.day)
    get_input_data(args.year, args.day, args.session)

if __name__ == "__main__":
    main()