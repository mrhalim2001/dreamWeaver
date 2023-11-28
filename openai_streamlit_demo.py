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


def debug_print(label, message):
        
        print(label+": "+message)
        if debug:
            st.text_area(label=label, value=message, height=200)


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

    prompt = "In  50 to 100 words, without referencing any copyrighted entities, take the following story and give me a one-sentence prompt in English that I can use with DALLE to generate a cartoonish colorful image suitable as the cover for the story. Make sure the prompt doesn't violate DALLE user policy:\n\n"

    prompt += story_json["title"] if story_json else "No Title"
    prompt += "\n\n"

    prompt += story_json["setup"] if story_json else "Once upon a time..."
    prompt += "\n\n"

    prompt += story_json["development"] if story_json else "Then..."
    prompt += "\n\n"

    prompt += story_json["climax"] if story_json else "Suddenly..."
    prompt += "\n\n"

    prompt += story_json["resolution"] if story_json else "And they lived happily ever after."
    prompt += "\n\n"

    debug_print("prompt to make image prompt", prompt)

    client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

    if (language=="English"):
        model = "gpt-3.5-turbo"
    else:
        model = "gpt-4"

    completion = client.chat.completions.create(
         model=model,
         messages=[{"role": "user", "content": prompt}],
         max_tokens= 500,
         temperature= 0.2
    )
    image_prompt = completion.choices[0].message.content


    return "A colorful cartoonish storybook image about "+image_prompt

def invent_a_story(story_prompt):

    # story_json_str = '''{
    #     "title": "Приключения в доме с привидениями",
    #     "setup": "Однажды, Адонис и его лучший друг Бобби решили исследовать старый заброшенный дом на окраине города. Они слышали много страшных историй о привидениях, которые там обитают, но их любопытство было сильнее страха. В то же время, Нида и ее подруга Сьюзи решили прогуляться и увидели, как Адонис и Бобби входят в старый дом. Они решили следовать за ними, взяв с собой их маленького котенка Бисса.",
    #     "development": "Внутри дома было темно и страшно. Адонис и Бобби начали искать признаки привидений, а Нида и Сьюзи прятались, наблюдая за ними. Внезапно, они услышали странный шум. Это было что-то вроде стука в стену. Все они замерли от страха. Нида и Сьюзи начали плакать, а Бисс начал мяукать. Адонис и Бобби решили исследовать источник звука.",
    #     "climax": "Они подошли к стене, откуда доносился звук. Адонис, собрав все свое мужество, открыл тайную дверь в стене. Внутри была маленькая комната, где жил маленький мышонок. Он бил по стене, пытаясь пробиться наружу. Все они были облегчены, что это не привидение. Но мышонок был очень испуган и замер от страха, увидев их.",
    #     "resolution": "Нида, которая любила животных, подошла к мышонку и погладила его. Она успокоила его и обещала, что они его не обидят. Адонис и Бобби помогли ей освободить мышонка, и он быстро убежал. Все они были счастливы, что смогли помочь маленькому созданию. Они поняли, что важно быть добрыми к другим, даже если они отличаются от тебя. И с тех пор, они больше не боялись старого дома, зная, что там нет привидений."
    #     }'''

    # story_json_str = '''{ 
    #     "title": "The Adventure of Adonis and Nida", 
    #     "setup": "Once upon a time, in a land filled with magic and wonder, lived two best friends named Adonis and Nida. Adonis loved math, the color yellow, and playing video games, while Nida adored arts and crafts, unicorns, and anything pink and purple. One sunny afternoon, Adonis and Nida decided to explore a mysterious cave they had heard about from their friends.", 
    #     "development": "As they entered the dark cave, they noticed a small, playful kitten named Biss following them. Suddenly, they stumbled across a portal that transported them into the world of video games. Shocked and excited, they found themselves face to face with Kirby, a kind-hearted character they admired from their favorite Nintendo Switch game. Kirby had lost his way and needed their help to return home.", 
    #     "climax": "Together, Adonis, Nida, Bobby, Suzie, Biss, and Kirby embarked on a thrilling adventure through treacherous terrains and tricky puzzles. Along the way, they encountered strange creatures and faced their fears. They learned that kindness and teamwork were their greatest strengths.", 
    #     "resolution": "Eventually, they found the portal that led Kirby back home. Grateful and inspired, Kirby thanked them, reminding everyone that it is important to be kind to others, even if they are different. Adonis and Nida returned to their world, carrying the message of kindness in their hearts. They realized that their differences made them a stronger team and cherished their friendship even more. Adonis taught Nida some math tricks, and Nida showed Adonis how to create beautiful unicorn crafts. From that day on, they learned to appreciate and celebrate their unique interests while always being kind to others." 
    #     }'''

    client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])
    if (language=="English"):
        model = "gpt-3.5-turbo"
    else:
        model = "gpt-4"

    completion = client.chat.completions.create(
         model=model,
         messages=[{"role": "user", "content": story_prompt}],
         max_tokens= 1000,
         temperature= 0.2
    )
    story_json_str = completion.choices[0].message.content

    debug_print("story_json_str", story_json_str)

       
    try:
        story_json = json.loads(story_json_str)
    except json.JSONDecodeError as e:

        debug_print("JSON decoding failed", str(e))
        debug_print("Trying to fix the JSON string...", " ")


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
        
    image_data = base64.b64decode(image_b64_json)
    image = Image.open(BytesIO(image_data))

    return image, image_data


def get_default_image():

    # Open default image from file
    image = Image.open("sample_image.png")

    # Convert image to RGB if it's RGBA
    if image.mode == 'RGBA':
        image = image.convert('RGB')

    # Convert the image to a bytes object
    buffered = BytesIO()
    image.save(buffered, format="PNG")
    img_bytes = buffered.getvalue()

    # Encode the bytes to a base64 string
    image_data = base64.b64encode(img_bytes).decode()

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

    debug_print("story_prompt", story_prompt)

    story_json, story_title, story_setup, story_development, story_climax, story_resolution = invent_a_story(story_prompt)


    image_prompt = craft_image_prompt(story_json)

    debug_print("image_prompt", image_prompt)

    #image, image_data = get_default_image()
    try:
        image, image_data = invent_an_image(image_prompt)
    except Exception as e:
        debug_print("Image generation failed", str(e))
        debug_print("Using default image...", " ")
        image, image_data = get_default_image()


    pdf = FPDF()
    pdf.add_font('Roboto', '', 'Roboto-Thin.ttf', uni=True)
    pdf.add_font('Roboto', 'B', 'Roboto-Bold.ttf', uni=True)
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

    pdf.set_font('Roboto', 'B', 16)
    pdf.cell(200, 10, txt=story_title, ln=True, align='C')  # Centered title
    pdf.ln(10)

    # Add the image to the PDF
    image_width = 150
    image_height = 150
    pdf.image(image_path, x=pdf.l_margin+(pdf_width/2)-(image_width/2), y=pdf.get_y(), w=image_width, h=image_height)
    pdf.ln(150 + 10)  # Move below the image

    pdf.set_font('Roboto', '', 12)
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

    try:
        download_html = create_download_link(pdf.output(), "test")
    except Exception as e:
        debug_print("PDF download link generation failed", str(e))
        download_html = ""

    display_story(story_title, story_setup, story_development, story_climax, story_resolution, image, download_html)



st.set_page_config(layout="wide")

default_audience = "Adonis is an 8 year old boy who likes math, the color yellow and video games.\nNida is a 6 year old girl who likes arts and crafts, unicorns, the colors pink and purple, and is into Barbie"
default_characters = "Adonis, his best friend Bobby, Nida, her best friend Suzie, our little male kitten named Biss."
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
   disabled=False,
   #placeholder="",
)

reading_level_display = {"6 year old child": "Emerging pre-reader (6 months to 6 years)", "seven year old child": "Novice reader (6 to 7)", "9 year old child": "Decoding reader (7 to 9)", "a child 10 years or older": "Fluent child reader (9+)", "an adult": "Adult reader"}
reading_level = col1.selectbox(
   "Reading Level",
   ("6 year old child", "seven year old child", "9 year old child", "a child 10 years or older", "an adult"),
   format_func=lambda x: reading_level_display[x],
   index=1,
   disabled=False,
   #placeholder="",
)

debug = col1.toggle("Debug", value=False, help="Keep this off unless you're me")

tone = col2.text_area(label="What's the intended tone of the story", max_chars=100, height=150, placeholder=default_tone)
length = col3.text_area(label="What's the intended length of the story", max_chars=100, height=150, placeholder=default_length)

col4, col5, col6 = st.columns((1,1,1))

audience = col4.text_area(label="Who is this bedtime story for", max_chars=500, height=300, placeholder=default_audience)
characters = col5.text_area(label="Who do you want the characters to be", max_chars=500, height=300, placeholder=default_characters)
moral = col6.text_area(label="What's the intended moral of the story", max_chars=100, height=300, placeholder=default_moral)

button = st.button("Make a bedtime story!", on_click=generate_story_button_clicked)
