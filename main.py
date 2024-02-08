import streamlit as st
import requests
import pandas as pd
from openai import OpenAI

def main():
    st.title("Baby Name Generator")

    # User inputs OpenAI API key
    api_key = st.text_input("Enter your OpenAI API key:")
    client = OpenAI(api_key=api_key)

    option = st.radio("Select the method to generate baby names:", ("Nakshatra", "Zodiac"))

    if option == "Nakshatra":
        st.subheader("Nakshatra Based Name Generator")
        dob = st.date_input("Date of Birth")
        tob = st.time_input("Time of Birth")
        lat = st.number_input("Latitude")
        lon = st.number_input("Longitude")
        place = st.text_input("Place of Birth")
        gender = st.selectbox("Gender", ["Male", "Female"])

        if st.button("Generate Names"):
            nakshatra = get_nakshatra(dob, tob, lat, lon, gender, place, client)
            suggested_letters = get_suggested_letters(nakshatra)
            generated_names = generate_names(suggested_letters, gender, client)

            st.write(f"Generated Names for {nakshatra} Nakshatra:")
            for i, name in enumerate(generated_names, start=1):
                if name:  # Check if the name is not empty
                    st.write(f"{name}")

    elif option == "Zodiac":
        st.subheader("Zodiac Based Name Generator")
        day = st.number_input("Enter your birth day (1-31):", min_value=1, max_value=31)
        month = st.number_input("Enter your birth month (1-12):", min_value=1, max_value=12)
        zodiac_sign = get_zodiac_sign(day, month)
        suggested_letters = load_suggested_letters()
        gender = st.selectbox("Gender", ["Male", "Female"])
        st.write("Your zodiac sign is:", zodiac_sign)
        st.write("Suggested letters for naming a newborn baby:", suggested_letters[zodiac_sign])
            
        # Generate names and meanings based on suggested letters
        names_and_meanings = generate_names_and_meanings(suggested_letters[zodiac_sign], gender.lower(), client)
        st.write("Generated baby names and their meanings:")
        for i, name_and_meaning in enumerate(names_and_meanings, start=1):
            if name_and_meaning:  # Check if the name and meaning is not empty
                name, meaning = name_and_meaning.split(" - ")
                st.write(f"{name}: {meaning}")
                
RAPIDAPI_URL = "https://horoscope-and-panchanga.p.rapidapi.com/zodiac/PanchangaSummary"
RAPIDAPI_KEY = "695fd6e1c2mshc262e15b91a6425p13791ajsn5ca96f33ad59"

def get_nakshatra(dob, tob, lat, lon, gender, place, client):
    querystring = {
        "day": dob.day,
        "month": dob.month,
        "year": dob.year,
        "place": place,
        "lat": lat,
        "lon": lon,
        "timezoneoffset": '+5.5'
    }

    headers = {
        "X-RapidAPI-Key": RAPIDAPI_KEY,
        "X-RapidAPI-Host": "horoscope-and-panchanga.p.rapidapi.com"
    }

    response = requests.get(RAPIDAPI_URL, headers=headers, params=querystring)
    data = response.json()
    nakshatra_name_full = data['Nakshatra']['Name']
    nakshatra_name = nakshatra_name_full.split('-')[0]
    return nakshatra_name

def get_suggested_letters(birth_star):
    # Load Nakshatra dataset from Excel file
    nakshatra_data = pd.read_excel("astro.xlsx", sheet_name="Sheet1")
    
    # Check if the birth star exists in the dataset
    if birth_star in nakshatra_data['BS'].values:
        suggested_letters = nakshatra_data[nakshatra_data['BS'] == birth_star]['SL'].iloc[0]
        return suggested_letters.split(", ")
    else:
        return ["No suggested letters found for this birth star."]

def generate_names(letters, gender, client):
    messages = [
        {"role": "system", "content": f"Generate three Hindu {gender} baby names starting with '{letters}'"},
        {"role": "user", "content": ""}
    ]
    response = client.chat.completions.create(
        model="gpt-3.5-turbo-1106",
        messages=messages,
        temperature=0
    )
    response_message = response.choices[0].message.content
    
    # Extract and return the generated baby names
    baby_names = response_message.split("\n")
    return baby_names

def get_zodiac_sign(day, month):
    if (month == 12 and day >= 22) or (month == 1 and day <= 19):
        return "Capricorn"
    elif (month == 1 and day >= 20) or (month == 2 and day <= 18):
        return "Aquarius"
    elif (month == 2 and day >= 19) or (month == 3 and day <= 20):
        return "Pisces"
    elif (month == 3 and day >= 21) or (month == 4 and day <= 19):
        return "Aries"
    elif (month == 4 and day >= 20) or (month == 5 and day <= 20):
        return "Taurus"
    elif (month == 5 and day >= 21) or (month == 6 and day <= 20):
        return "Gemini"
    elif (month == 6 and day >= 21) or (month == 7 and day <= 22):
        return "Cancer"
    elif (month == 7 and day >= 23) or (month == 8 and day <= 22):
        return "Leo"
    elif (month == 8 and day >= 23) or (month == 9 and day <= 22):
        return "Virgo"
    elif (month == 9 and day >= 23) or (month == 10 and day <= 22):
        return "Libra"
    elif (month == 10 and day >= 23) or (month == 11 and day <= 21):
        return "Scorpio"
    elif (month == 11 and day >= 22) or (month == 12 and day <= 21):
        return "Sagittarius"
    else:
        return "Invalid date"

def load_suggested_letters():
    df = pd.read_excel('Rashi.xlsx')
    return df.set_index('ZS')['SL'].to_dict()

def generate_names_and_meanings(letters, gender, client):
    messages = [
        {"role": "system", "content": f"Generate three Hindu {gender} baby names starting with '{letters}' and their meanings"},
        {"role": "user", "content": ""}
    ]
    response = client.chat.completions.create(
        model="gpt-3.5-turbo-1106",
        messages=messages,
        temperature=0
    )
    response_message = response.choices[0].message.content
    
    # Extract and return the generated baby names and their meanings
    names_and_meanings = response_message.split("\n")
    return names_and_meanings

if __name__ == "__main__":
    main()
