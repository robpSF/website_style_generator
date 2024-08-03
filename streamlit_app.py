import streamlit as st
import requests
import json
from datetime import datetime
import openai
import os
import zipfile
import pandas as pd

# Load the OpenAI keys from Streamlit secrets
openai.organization = st.secrets["organization"]
openai.api_key = st.secrets["key"]

def generate_text(prompt, temp=0.7, max_tokens=1000):
    url = "https://api.openai.com/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {openai.api_key}",
        "Content-Type": "application/json"
    }
    data = {
        "model": "gpt-4o",
        "messages": [
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": prompt}
        ],
        "temperature": temp,
        "max_tokens": max_tokens,
        "top_p": 1.0,
        "frequency_penalty": 0.0,
        "presence_penalty": 0.0
    }
    response = requests.post(url, headers=headers, json=data)
    response.raise_for_status()
    return response.json()["choices"][0]["message"]["content"]

def generate_json(company_name, company_bio, header_image_url, article, title, subtitle):
    data = {
        "website_style": {
            "spoof_url": f"{company_name.replace(' ', '').lower()}.com",
            "title": company_name,
            "spoof_url_protocol": 2,
            "desc": company_bio,
            "paid_promotion": 0,
            "name": company_name,
            "open_from_start": 1,
            "ranking": 4,
            "style": {
                "comments": {
                    "past_bg_color": 16777215,
                    "past_user_text": {
                        "color": 672884,
                        "text": "",
                        "use_default_url": 1,
                        "font": "open_sansregular",
                        "url": "",
                        "size": 12
                    },
                    "past_body_text": {
                        "color": 0,
                        "text": "",
                        "use_default_url": 1,
                        "font": "open_sansregular",
                        "url": "",
                        "size": 12
                    },
                    "palceholder": "Write your comment",
                    "title": {
                        "color": 0,
                        "text": "Comments",
                        "use_default_url": 1,
                        "font": "open_sansregular",
                        "url": "",
                        "size": 16
                    },
                    "post_button": {
                        "border_color": 0,
                        "bg_img": {
                            "shown": 0,
                            "align": None,
                            "url": None
                        },
                        "border_visible": 0,
                        "label": {
                            "color": 16777215,
                            "text": "Post comment",
                            "use_default_url": 1,
                            "font": "open_sansregular",
                            "url": "",
                            "size": 12
                        },
                        "bg_color": 672884
                    },
                    "bg_color": 15921906
                },
                "content": {
                    "sub_title": {
                        "color": 6512736,
                        "text": "",
                        "use_default_url": 1,
                        "font": "open_sansregular",
                        "url": "",
                        "size": 11
                    },
                    "title": {
                        "color": 0,
                        "text": "",
                        "use_default_url": 1,
                        "font": "open_sansregular",
                        "url": "",
                        "size": 28
                    },
                    "body": {
                        "color": 0,
                        "text": "",
                        "use_default_url": 1,
                        "font": "open_sansregular",
                        "url": "",
                        "size": 14
                    },
                    "bg_color": 16777215
                },
                "header": {
                    "text": {
                        "color": 16777215,
                        "text": "",
                        "use_default_url": 1,
                        "font": "open_sansregular",
                        "url": "",
                        "size": 22
                    },
                    "bg_color": 135972,
                    "image": {
                        "shown": 1,
                        "align": "center",
                        "url": header_image_url
                    }
                },
                "sidebar": {
                    "title": {
                        "color": 0,
                        "text": "Top stories",
                        "use_default_url": 1,
                        "font": "open_sansregular",
                        "url": "",
                        "size": 16
                    },
                    "bg_color": 15921906,
                    "past_posts_text": {
                        "color": 0,
                        "text": "",
                        "use_default_url": 1,
                        "font": "open_sansregular",
                        "url": "",
                        "size": 14
                    }
                },
                "web_details": {
                    "enabled": 0,
                    "icon": {
                        "shown": 0,
                        "align": "center",
                        "url": None
                    },
                    "hacked": {
                        "shown": 0,
                        "align": "center",
                        "url": None
                    },
                    "tabs": {
                        "id_counter": 1,
                        "list": []
                    }
                }
            },
            "keywords": [],
            "active": 1,
            "past_posts": [{
                "author_id": None,
                "no_author": 0,
                "text_direction": None,
                "text": article,
                "ts": "12days",
                "attachment": [],
                "subtitle": subtitle,
                "ts_r_value": None,
                "title": title,
                "ts_r_value_type": 0,
                "ts_type": 1
            }],
            "tab_order": 1000,
            "views": 34333,
            "disable_comments": 0
        },
        "from_library_name": "MNCs",
        "from_persona_name": company_name,
        "from_persona_id": "1",
        "from_library_id": "341"
    }
    return data

def main():
    st.title('Company Profile JSON Generator')
    
    password = st.text_input("Enter a password", type="password")
    if password != st.secrets["password"]:
        st.error("Invalid password")
        return
    
    company_name = st.text_input("Company Name")
    company_bio = st.text_area("Company Bio")
    header_image_url = st.text_input("Header Image URL")
    
    if "json_data" not in st.session_state:
        st.session_state.json_data = None
    if "txws_filename" not in st.session_state:
        st.session_state.txws_filename = None
    if "csv_filename" not in st.session_state:
        st.session_state.csv_filename = None
    
    if st.button("Generate JSON"):
        if company_name and company_bio and header_image_url:
            article_prompt = f"Write a website article based on the following company bio. ###RULES 1. Don't include a title 2. keep to less than 200 words. bio=:\n\n{company_bio}\n\nArticle:"
            article = generate_text(article_prompt)
            
            title_prompt = f"Generate a title for a website article based on the following company bio. ###RULES Don't encapsulate in quotes. bio=:\n\n{company_bio}\n\nTitle:"
            title = generate_text(title_prompt, max_tokens=50).strip()
            
            subtitle_prompt = f"Generate a subtitle for a website article based on the following company bio. ###RULES Don't encapsulate in quotes. bio=:\n\n{company_bio}\n\nSubtitle:"
            subtitle = generate_text(subtitle_prompt, max_tokens=50).strip()
            
            json_data = generate_json(company_name, company_bio, header_image_url, article, title, subtitle)
            st.json(json_data)
            
            json_filename = f"{company_name.replace(' ', '_').lower()}_{datetime.now().strftime('%Y%m%d%H%M%S')}.json"
            zip_filename = f"{company_name.replace(' ', '_').lower()}.zip"
            txws_filename = f"{company_name.replace(' ', '_').lower()}.txws"
            
            with open(json_filename, 'w') as json_file:
                json.dump(json_data, json_file, indent=4)
            
            with zipfile.ZipFile(zip_filename, 'w') as zipf:
                zipf.write(json_filename)
            
            os.rename(zip_filename, txws_filename)
            
            st.session_state.json_data = json_data
            st.session_state.txws_filename = txws_filename
            
            os.remove(json_filename)
            
            # Create a CSV file with the generated article
            csv_filename = f'{company_name.replace(" ", "_").lower()}_posts.csv'
            new_post = {
                "Author": "No Author",
                "Title": title,
                "Subtitle": subtitle,
                "Message": article,
                "Attachment": "",
                "Date": "12days"
            }
            
            df = pd.DataFrame([new_post])
            df.to_csv(csv_filename, index=False)
            
            st.session_state.csv_filename = csv_filename
            
            st.success(f"JSON file has been generated and included in {txws_filename}!")
        else:
            st.error("Please fill in all fields.")
    
    if st.session_state.txws_filename:
        with open(st.session_state.txws_filename, "rb") as file:
            st.download_button(
                label="Download .txws file",
                data=file,
                file_name=st.session_state.txws_filename,
                mime="application/zip"
            )
    
    if st.session_state.csv_filename:
        with open(st.session_state.csv_filename, "rb") as file:
            st.download_button(
                label="Download CSV file",
                data=file,
                file_name=st.session_state.csv_filename,
                mime="text/csv"
            )

if __name__ == '__main__':
    main()
