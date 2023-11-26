#We need some standard libraries
import base64
import json
from PIL import Image
from io import BytesIO
import tempfile

#These are dependencies that we need to install
import streamlit as st
from openai import OpenAI
from fpdf import FPDF

debug = False

def craft_story_prompt():
    prompt = "Write a children bedtime story in "
    prompt += language if language else default_language
    prompt += ", easily readable by a "
    prompt += reading_level if reading_level else default_reading_level
    prompt += ", following the Four Act Structure with 4 main parts roughly equal in size. "
    prompt+= "Output only a json with the following keys: [title, setup, development, climax, resolution]. "
    prompt += "The story must conform to the following characteristics:\n\n"

    prompt += "Length of the story: "
    prompt += length if length else default_length
    prompt += "\n\n"
    
    prompt += "Overall tone: "
    prompt += tone if tone else default_tone
    prompt += "\n\n"
    
    prompt += "Intended audience: "
    prompt += audience if audience else default_audience
    prompt += "\n\n"
  
    prompt += "Characters: "
    prompt += characters if characters else default_characters
    prompt += "\n\n"

    prompt += "Moral: "
    prompt += moral if moral else default_moral

    return prompt

def craft_image_prompt(story_json):

    if language != "English":
         
        prompt = "A colorful cartoonish cover image for the following story:\n\n"

        prompt += "Overall tone: "
        prompt += tone if tone else default_tone
        prompt += "\n\n"
    
        prompt += "Intended audience: "
        prompt += audience if audience else default_audience
        prompt += "\n\n"
  
        prompt += "Characters: "
        prompt += characters if characters else default_characters
        prompt += "\n\n"

        prompt += "Moral: "
        prompt += moral if moral else default_moral

    else:

        prompt = "A colorful cartoonish cover image for the following story:\n\n"

        prompt += "Title: "
        prompt += story_json["title"] if story_json else "No Title"
        prompt += "\n\n"

        #prompt += "Setup: "
        prompt += story_json["setup"] if story_json else "Once upon a time..."
        prompt += "\n\n"

        #prompt += "Development: "
        prompt += story_json["development"] if story_json else "Then..."
        prompt += "\n\n"

        #prompt += "Climax: "
        prompt += story_json["climax"] if story_json else "Suddenly..."
        prompt += "\n\n"

        #prompt += "Resolution: "
        prompt += story_json["resolution"] if story_json else "And they lived happily ever after."
        prompt += "\n\n"

    return prompt

def invent_a_story(story_prompt):

    client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])
    model = "gpt-3.5-turbo"
    completion = client.chat.completions.create(
         model=model,
         messages=[{"role": "user", "content": story_prompt}],
         max_tokens= 1000,
         temperature= 0.2
    )
    story_json_str = completion.choices[0].message.content
    #story_json_str = '{ "title": "The Adventure of Adonis and Nida", "setup": "Once upon a time, in a land filled with magic and wonder, lived two best friends named Adonis and Nida. Adonis loved math, the color yellow, and playing video games, while Nida adored arts and crafts, unicorns, and anything pink and purple. One sunny afternoon, Adonis and Nida decided to explore a mysterious cave they had heard about from their friends.", "development": "As they entered the dark cave, they noticed a small, playful kitten named Biss following them. Suddenly, they stumbled across a portal that transported them into the world of video games. Shocked and excited, they found themselves face to face with Kirby, a kind-hearted character they admired from their favorite Nintendo Switch game. Kirby had lost his way and needed their help to return home.", "climax": "Together, Adonis, Nida, Bobby, Suzie, Biss, and Kirby embarked on a thrilling adventure through treacherous terrains and tricky puzzles. Along the way, they encountered strange creatures and faced their fears. They learned that kindness and teamwork were their greatest strengths.", "resolution": "Eventually, they found the portal that led Kirby back home. Grateful and inspired, Kirby thanked them, reminding everyone that it is important to be kind to others, even if they are different. Adonis and Nida returned to their world, carrying the message of kindness in their hearts. They realized that their differences made them a stronger team and cherished their friendship even more. Adonis taught Nida some math tricks, and Nida showed Adonis how to create beautiful unicorn crafts. From that day on, they learned to appreciate and celebrate their unique interests while always being kind to others." }'

    if debug:
         st.text_area(label="story_json_str", value=story_json_str, height=200)
       
    try:
        story_json = json.loads(story_json_str)
    except json.JSONDecodeError as e:

        print("JSON decoding failed:", e)
        print("JSON string:", story_json_str)
        print("Trying to fix the JSON string...")

        # Try removing the last comma before a closing bracket or brace
        story_json_str = story_json_str[::-1].replace(',', '', 1)[::-1]
        story_json = json.loads(story_json_str)

    story_title = story_json["title"] if story_json else "No Title"
    story_setup = story_json["setup"] if story_json else "Once upon a time..."
    story_development = story_json["development"] if story_json else "Then..."
    story_climax = story_json["climax"] if story_json else "Suddenly..."
    story_resolution = story_json["resolution"] if story_json else "And they lived happily ever after."

    return story_json, story_title, story_setup, story_development, story_climax, story_resolution

def invent_an_image(image_prompt):

    client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])
    response = client.images.generate(
         model="dall-e-3",
         prompt=image_prompt,
         size="1024x1024",
         quality="standard",
         response_format="b64_json",
         n=1,
    )
    image_b64_json = response.data[0].b64_json

    #image_b64_json = open('sample_image_data.b64', 'r').read()
        
    image_data = base64.b64decode(image_b64_json)
    image = Image.open(BytesIO(image_data))

    return image, image_data

def create_download_link(val, filename):
    b64 = base64.b64encode(val) 
    return f'<a href="data:application/octet-stream;base64,{b64.decode()}" download="{filename}.pdf"><span style="text-align:center">Download the story as PDF</span></a>'

def display_story(story_title, story_setup, story_development, story_climax, story_resolution, image, download_html):

    leftMargin, middle, rightMargin = st.columns((1, 3, 1))
    with middle:
        st.markdown("<h1 style='text-align: center; color: Black;'>"+story_title+"</h1>", unsafe_allow_html=True)
        st.markdown("<div style='text-align:center'>"+download_html+"</div>", unsafe_allow_html=True)
        st.image(image, use_column_width=True)
        st.write(story_setup)
        st.write(story_development)
        st.write(story_climax)
        st.write(story_resolution)
        st.markdown("<h2 style='text-align: center; color: Black;'><i>"+"~ The End ~"+"</i></h2>", unsafe_allow_html=True)

def generate_story_button_clicked():

    story_prompt = craft_story_prompt()

    if debug:
        st.text_area(label="Story Prompt", value=story_prompt, height=200)

    story_json, story_title, story_setup, story_development, story_climax, story_resolution = invent_a_story(story_prompt)
    
    image_prompt = craft_image_prompt(story_json)

    if debug:
        st.text_area(label="Image Prompt", value=image_prompt, height=200)

    image, image_data = invent_an_image(image_prompt)

    pdf = FPDF()
    pdf.add_page()

    # Create a temporary file to save the image
    with tempfile.NamedTemporaryFile(delete=False, suffix='.jpg') as temp_image_file:
        image_path = temp_image_file.name
        image.save(temp_image_file, format='JPEG')

    # Get image dimensions to maintain aspect ratio
    width, height = image.size
    aspect_ratio = width / height
    pdf_width = pdf.w - 2 * pdf.l_margin
    pdf_height = pdf_width / aspect_ratio

    pdf.set_font('Arial', 'B', 16)
    pdf.cell(200, 10, txt=story_title, ln=True, align='C')  # Centered title
    pdf.ln(10)

    # Add the image to the PDF
    image_width = 150
    image_height = 150
    pdf.image(image_path, x=pdf.l_margin+(pdf_width/2)-(image_width/2), y=pdf.get_y(), w=image_width, h=image_height)
    pdf.ln(150 + 10)  # Move below the image

    pdf.set_font('Arial', '', 12)
    pdf.multi_cell(0, 5, story_setup)
    pdf.ln(5)
    pdf.multi_cell(0, 5, story_development)
    pdf.ln(5)
    pdf.multi_cell(0, 5, story_climax)
    pdf.ln(5)
    pdf.multi_cell(0, 5, story_resolution)
    pdf.ln(5)
    pdf.set_font('Arial', 'B', 16)
    pdf.multi_cell(0, 5, "~ The End ~", align="C")

    download_html = create_download_link(pdf.output(dest="S").encode("latin-1"), "test")    

    display_story(story_title, story_setup, story_development, story_climax, story_resolution, image, download_html)



st.set_page_config(layout="wide")

default_audience = "Adonis is an 8 year old boy who likes math, the color yellow and video games, especially Minecraft and the Kirby game series on Nintendo Switch.\nNida is a 6 year old girl who likes arts and crafts, unicorns, the colors pink and purple, and is into Barbie"
default_characters = "Adonis, his best friend Bobby, Nida, her best friend Suzie, our little male kitten named Biss, and the video game character Kirby"
default_moral = "It is important to be kind to others, even if they are different from you"
default_tone = "Scary and suspenseful, but with a happy ending"
default_length = "About 2 minutes read. No more than 1000 words"
default_language = "English"
default_reading_level = "Novice reader (6 to 7)"

story_json = None

st.title("Dream Weaver - an AI bedtime story generator")

col1, col2, col3 = st.columns((1,1,1))

language = col1.selectbox(
   "Language",
   ("English", "Russian", "Arabic"),
   index=0,
   disabled=True,
   #placeholder="",
)

reading_level_display = {"6 year old child": "Emerging pre-reader (6 months to 6 years)", "seven year old child": "Novice reader (6 to 7)", "9 year old child": "Decoding reader (7 to 9)", "a child 10 years or older": "Fluent child reader (9+)", "an adult": "Adult reader"}
reading_level = col1.selectbox(
   "Reading Level",
   ("6 year old child", "seven year old child", "9 year old child", "a child 10 years or older", "an adult"),
   format_func=lambda x: reading_level_display[x],
   index=1,
   #placeholder="",
)

tone = col2.text_area(label="What's the intended tone of the story", max_chars=100, height=150, placeholder=default_tone)
length = col3.text_area(label="What's the intended length of the story", max_chars=100, height=150, placeholder=default_length)

col4, col5, col6 = st.columns((1,1,1))

audience = col4.text_area(label="Who is this bedtime story for", max_chars=500, height=300, placeholder=default_audience)
characters = col5.text_area(label="Who do you want the characters to be", max_chars=500, height=300, placeholder=default_characters)
moral = col6.text_area(label="What's the intended moral of the story", max_chars=100, height=300, placeholder=default_moral)

button = st.button("Make a bedtime story!", on_click=generate_story_button_clicked)
