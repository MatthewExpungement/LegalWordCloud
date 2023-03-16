from os import path
from PIL import Image
from wordcloud import WordCloud, STOPWORDS, ImageColorGenerator
import matplotlib.pyplot as plt
import requests
from bs4 import BeautifulSoup
import streamlit as st
import os
import numpy as np
import time

def reset_justia_url():
    st.session_state['url_search'] = ""
def reset_select_box_option():
    st.session_state.dropdown_search = "Select"

if 'url' not in st.session_state:
    st.session_state['url'] = ''
if 'case_title' not in st.session_state:
    st.session_state['case_title'] = ''
if 'text' not in st.session_state:
    st.session_state['text'] = ''
# Generates a sidebar
with st.sidebar:
    st.title("Welcome to the Legal Opinion Word Cloud Generator")
    st.write("Enter the url from Justia of the opinion you want to word cloud .i.e. https://supreme.justia.com/cases/federal/us/388/1/")
    url = st.text_input("Enter Justia url",key='url_search',on_change=reset_select_box_option)
    if(url[0:26] != 'https://supreme.justia.com' and url != ""):
        st.error("URL Needs to start with https://supreme.justia.com")
        url = ""
    st.write("Or select from famous cases")
    famous_cases = ['Select','Loving v. Virginia, 388 U.S. 1 (1967)','Roe v. Wade, 410 U.S. 113 (1973)','Brown v. Board of Education of Topeka, 347 U.S. 483 (1954)']
    famous_case = st.selectbox("Select Famous Case",famous_cases,key='dropdown_search',on_change=reset_justia_url)
    exclude_words_basics = ["state",'footnote','page','statute','court','code ann','case','statutes','repl vol','act','v','Â','ann','F Supp']
    exclude_words_raw = st.text_area("Words to exclude",value=",".join(exclude_words_basics))
    exclude_words = exclude_words_raw.split(",")
    number_of_words = st.slider("How many words should the word cloud be capped at?",0,1000,50)
    images = ['Rectangle','Heart','Gavel']
    selected_image = st.selectbox("Select Background Image",images)
    st.text("The word cloud will generate on change of any attribute above.")
if(url != "" or famous_case != 'Select'):
    if(famous_case != 'Select'):
        #Means we have a pre-selected case.
        my_file = open("Cases//" + famous_case + ".txt")
        text = my_file.read()
        my_file.close()
        case_title = famous_case
    else:
        #Means it's a url search request
        if(url != st.session_state['url']):
            response = requests.get(url)
            #print(response.text)
            soup = BeautifulSoup(response.text,features="html.parser")
            case_title = soup.find(id = 'text-a').get_text()
            text = soup.find(id='tab-opinion').get_text()
            # print("Scraping",time.time(),st.session_state['url'])
            st.session_state['url'] = url
            st.session_state['case_title'] = case_title
            st.session_state['text'] = text
        else:
            # print("Not Scraping",time.time(),st.session_state['url'])
            url = st.session_state['url']
            case_title = st.session_state['case_title']
            text = st.session_state['text']
    st.header(case_title) #Print the title
    text = text.strip()
    opinion_text = st.text_area("Opinion Text",value=text,key='opinion_text')

    stopwords = set(STOPWORDS)
    for sword in exclude_words:
        stopwords.add(sword)

    if(selected_image == 'Rectangle'):
        #Regular word cloud
        #Use the parameter random_state=42 so that you can generate the same word cloud each time.
        wordcloud = WordCloud(background_color="white",max_words=number_of_words,stopwords=stopwords, max_font_size=40).generate(opinion_text)
        plt.imshow(wordcloud, interpolation='bilinear')
    else:
        #Create and generate a word cloud image:
        d = path.dirname(__file__) if "__file__" in locals() else os.getcwd()
        image_coloring = np.array(Image.open(path.join(d, "Images/" + selected_image + ".jpg")))
        wordcloud = WordCloud(background_color="white", max_words=number_of_words, mask=image_coloring,stopwords=stopwords, max_font_size=40).generate(opinion_text)
        image_colors = ImageColorGenerator(image_coloring)
        plt.imshow(wordcloud.recolor(color_func=image_colors), interpolation="bilinear")

    plt.axis("off")
    st.pyplot(plt)