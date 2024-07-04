import streamlit as st
from openai import OpenAI
import base64
from PIL import Image
import io

def encode_image(image_file):
    return base64.b64encode(image_file.getvalue()).decode('utf-8')

def analyze_image(image, tone, length, additional_context, jewelry_info, api_key):
    client = OpenAI(api_key=api_key)
    base64_image = encode_image(image)
    
    word_ranges = {
        "20-30 words": (28, 30),
        "40-50 words": (48, 50),
        "60-70 words": (68, 70)
    }
    min_words, max_words = word_ranges[length]
    
    # Check if additional context is filled
    context_filled = additional_context.strip() and additional_context != "Enter any additional context here..."
    
    # Check if any jewelry info is filled
    jewelry_filled = any(jewelry_info.values())
    
    # Increase word limits based on filled information
    if context_filled and jewelry_filled:
        min_words += 15
        max_words += 15
    elif context_filled or jewelry_filled:
        min_words += 10
        max_words += 10
    
    jewelry_info_str = "\n".join([f"{k}: {v}" for k, v in jewelry_info.items() if v])
    
    prompt = f"""
Role: You are a savvy and insightful social media manager for a popular gemstone and jewelry shopping network. Your responsibilities include setting content strategy and driving engagement on the company's website. Given an image of a jewelry product, you need to provide an enhanced description and caption.

Instructions:

Image Analysis:
Identify and describe all notable features, materials, and design elements of the jewelry piece.
Pay attention to details such as gemstone types, cuts, metal types, craftsmanship, and any unique or standout features.
Ensure the analysis is detailed and precise to provide an accurate foundation for the description.

Additional Context:
Incorporate the following context into your analysis and description where relevant: {additional_context}

Additional Jewelry Information:
Use the following user-provided information and incorporate these details into your description, CRITICAL: Prioritize this information   over conflicting image analysis information: {jewelry_info_str}

Product Description:
Craft a product description incorporating key details from the image analysis, additional context, and the provided jewelry information.
Highlight the beauty and uniqueness of the piece using varied, vivid, and engaging language.
Avoid repetitive phrases and overused words by using synonyms and descriptive terms to keep the content fresh and distinctive.
Ensure the description is SEO-friendly by including relevant keywords for better search visibility.
Reflect the selected tone by matching the language, style, and adjectives to the following tone: {tone}
Your description MUST be between {min_words} and {max_words} words. Aim for {max_words} words if possible. Count your words carefully. Do not submit a description shorter than {min_words} words or longer than {max_words} words.
If you're near the lower word limit, expand on the product's features or benefits to reach the desired length. Consider detailing the inspiration behind the design, historical significance, or specific craftsmanship techniques used.

Caption:
Create a compelling, one-liner product summary adhering strictly to a single line format.
Use different words and phrasing from the description to capture attention and interest.
Ensure the caption aligns with the brand's voice and appeals to the target audience.
Make sure each caption is unique and reflective of the specific product's characteristics and appeal.
Avoid generic phrases like "embrace the elegance" and tailor the caption specifically to the unique features of the product.

Language Variation:
Ensure that each description and caption uses different adjectives and phrasing to avoid repetition across products.
Utilize a thesaurus to find synonyms and diverse expressions for common words like "embrace", "elegance", "exquisite", "stunning", etc.

Output Format:

Image Analysis: [Your analysis here, integrating {additional_context} where relevant and prioritizing {jewelry_info_str}]
Product Description: [Your description here, strictly between {min_words} and {max_words} words, matching the {tone}]
Caption: [Your caption here]
"""
    
    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": prompt},
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:image/jpeg;base64,{base64_image}"
                        }
                    },
                ],
            }
        ],
        max_tokens=1000,
    )
    print(prompt)
    return response.choices[0].message.content

st.set_page_config(layout="wide")
st.markdown("""
    <style>
    .main {
        font-size: 0.8rem;
    }
    .stTextInput, .stSelectbox {
        font-size: 0.8rem;
    }
    </style>
    """, unsafe_allow_html=True)

st.title("Jewellery Image Analyzer", anchor=False)

# Add API key input at the top
api_key = st.text_input("Enter your OpenAI API key:", type="password")

col1, col2 = st.columns([1, 1.2])

with col1:
    uploaded_file = st.file_uploader("Choose an image...", type=["jpg", "jpeg", "png"])
    if uploaded_file is not None:
        image = Image.open(uploaded_file)
        image = image.resize((500, 500))
        buffered = io.BytesIO()
        image.save(buffered, format="PNG")
        st.image(buffered, caption='Uploaded Image', use_column_width=False, width=500)

with col2:
    tone_options = {
        "Original": "No specific tone",
        "Professional": "Business-like and competent",
        "Festive": "Celebratory and culturally rich",
        "Flowery": "Elaborate and ornate language"
    }

    length_options = {
        "Short": "20-30 words",
        "Medium": "40-50 words",
        "Long": "60-70 words",
    }

    tone = st.selectbox("Select tone:", list(tone_options.keys()), format_func=lambda x: f"{x}: {tone_options[x]}")
    length = st.selectbox("Select length:", list(length_options.keys()), format_func=lambda x: f"{x}: {length_options[x]}")

    additional_context = st.text_area("Additional Context (e.g., related festival, celebrity news):", 
                                      "Enter any additional context here...", height=80)

    st.subheader("Additional Information About Jewellery", anchor=False)
    col2_1, col2_2 = st.columns(2)
    with col2_1:
        carat = st.text_input("Carat")
        color = st.text_input("Color")
        diamond_type = st.text_input("Diamond type")
    with col2_2:
        weight = st.text_input("Weight (In gram)")
        metal = st.text_input("Metal")
        size = st.text_input("Size (In cm)")

    jewelry_info = {
        "Carat": carat,
        "Weight in grams": weight,
        "Color": color,
        "Metal": metal,
        "Diamond type": diamond_type,
        "Size in cm": size
    }
    
    analyze_button = st.button('Analyze Image')

    if uploaded_file is not None and analyze_button:
        if api_key:
            with st.spinner('Analyzing...'):
                result = analyze_image(uploaded_file, tone, length_options[length], additional_context, jewelry_info, api_key)
            st.write("Analysis Result:")
            st.write(result)
        else:
            st.error("Please enter your OpenAI API key.")