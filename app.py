from utils import move_to_reviews, get_soup, product_details, page_jumper, product_reviews, convert_to_df, sentiment
import streamlit as st
import selenium


st.title('Rakuten Product Review Sentiment')
st.subheader('Enter the product url')

url = st.text_input(label='Product link address')

st.subheader('Number of pages for reviews')
num_pages = st.text_input(label='Number of pages')

#st.session_state['nums'] = num_pages


if st.button('Start'):
    
    cus_url = move_to_reviews(url)
    cus_soup = get_soup(cus_url)

    cus_product_info = product_details(cus_soup)
    st.write(cus_product_info['product_name'])
    st.image(cus_product_info['product_image'])
    st.write(cus_product_info['product_price'])

    page_links = page_jumper(cus_url, int(num_pages))
    total_reviews = product_reviews(page_links)

    the_sentiment = sentiment(convert_to_df(total_reviews))

    st.write(the_sentiment)