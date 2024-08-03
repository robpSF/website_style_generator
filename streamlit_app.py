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

def generate_text(prompt, temp=0.7):
    url = "https://api.openai.com/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {openai.api_key}",
        "Content-Type": "application/json"
    }
    data = {
        "model": "gpt-4",
        "messages": [
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": prompt}
        ],
        "temperature": temp,
        "max_tokens": 1000,
        "top_p": 1.0,
        "frequency_penalty": 0.0,
        "presence_penalty": 0.0
    }
    response = requests.post(url, headers=headers, json=data)
    response.raise_for_status()
    return response.json()["choices"][0]["message"]["content"]

def generate_json(company_name, company_bio, header_image_url, article):
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
                "ts": None,
                "attachment": ["21"],
                "subtitle": "Innovative technology and quality craftsmanship at the heart of tomorrow's electronics",
                "ts_r_value": None,
                "title": f"Pioneering the Future: {company_name} Leader Sets New Standards",
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
    
    if st.button("Generate JSON"):
        if company_name and company_bio and header_image_url:
            prompt = f"Write a website article based on the following company bio:\n\n{company_bio}\n\nArticle:"
            article = generate_text(prompt)
            data = generate_json(company_name, company_bio, header_image_url, article)
            st.json(data)
            
            json_filename = f"{company_name.replace(' ', '_').lower()}_{datetime.now().strftime('%Y%m%d%H%M%S')}.json"
            zip_filename = f"{company_name.replace(' ', '_').lower()}.zip"
            txws_filename = f"{company_name.replace(' ', '_').lower()}.txws"
            
            with open(json_filename, 'w') as json_file:
                json.dump(data, json_file, indent=4)
            
            with zipfile.ZipFile(zip_filename, 'w') as zipf:
                zipf.write(json_filename)
            
            os.rename(zip_filename, txws_filename)
            
            with open(txws_filename, "rb") as file:
                st.download_button(
                    label="Download .txws file",
                    data=file,
                    file_name=txws_filename,
                    mime="application/zip"
                )
            
            os.remove(json_filename)
            os.remove(txws_filename)
            
            # Append the generated article to a CSV file
            csv_filename = f'{company_name.replace(" ", "_").lower()}_posts.csv'
            new_post = {
                "Author": "No Author",
                "Title": f"Pioneering the Future: {company_name} Leader Sets New Standards",
                "Subtitle": "Innovative technology and quality craftsmanship at the heart of tomorrow's electronics",
                "Message": article,
                "Attachment": "21",
                "Date": datetime.now().strftime('%Y-%m-%d')
            }
            
            if os.path.exists(csv_filename):
                df = pd.read_csv(csv_filename)
                df = pd.concat([df, pd.DataFrame([new_post])], ignore_index=True)
            else:
                df = pd.DataFrame([new_post])
            
            df.to_csv(csv_filename, index=False)
            
            with open(csv_filename, "rb") as file:
                st.download_button(
                    label="Download CSV file",
                    data=file,
                    file_name=csv_filename,
                    mime="text/csv"
                )
            
            st.success(f"JSON file {json_filename} has been generated and included in {txws_filename}!")
        else:
            st.error("Please fill in all fields.")

if __name__ == '__main__':
    main()
