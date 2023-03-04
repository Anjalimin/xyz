import pytesseract
import pandas as pd
import nltk
import spacy
from PIL import Image
from datetime import datetime
from docx import Document
import os
import streamlit as st
import openai
from streamlit_chat import message
import resume_parser
import re
from io import BytesIO
import emoji

nlp = spacy.load("en_core_web_sm")


def main_page():
    st.title("#Company Name")
    st.subheader(" About Us")
    st.markdown("""


At ("#Company Name"), we're passionate about using technology to solve complex business problems. Our team of experts 
is dedicated to helping organizations of all sizes transform their operations and achieve their goals.

We offer a wide range of IT services, including software development,Data Science, system integration, 
cloud computing,  and more. Our solutions are customized to meet the unique needs of each client, and we work closely 
with them every step of the way to ensure their success.

With years of experience and a deep understanding of the latest technologies, we're committed to delivering 
high-quality results that exceed our clients' expectations. Our team is constantly learning and evolving to stay 
ahead of the curve, and we're always on the lookout for new ways to innovate and improve.

We're proud to have a track record of success and to have helped many organizations achieve their IT goals. If you're 
looking for a trusted partner to help you navigate the ever-changing world of technology, look no further than (
"#Company Name").""")


def page2():
    st.title("SMART CV EXTRACTOR")
    st.markdown("""
    <style>
    h1 {
      color: white;
    }
    </style>
    """, unsafe_allow_html=True)

    def add_bg_from_url():
        st.markdown(
            f"""
             <style>
             .stApp {{
                 background-image: url("https://cdn.pixabay.com/photo/2019/04/24/11/27/flowers-4151900_960_720.jpg");
                 background-attachment: fixed;
                 background-size: cover
             }}
             </style>
             """,
            unsafe_allow_html=True
        )

    add_bg_from_url()

    def main():
        resumes = st.file_uploader("Upload your Resumes and Images", type=["pdf", "docx", "jpg", 'jpeg'],
                                   accept_multiple_files=True)
        progress_bar = st.progress(0)  # create a progress bar widget
        for i, resume in enumerate(resumes):
            all_data = []
            for resume in resumes:
                if resume.type in ["application/pdf",
                                   "application/vnd.openxmlformats-officedocument.wordprocessingml.document"]:
                    with open(resume.name, "wb") as f:
                        f.write(resume.getbuffer())
                    # Parse the resume and display the extracted data
                    data = resume_parser.ResumeParser(resume.name).get_extracted_data()
                    all_data.append(data)
                else:
                    image = Image.open(resume)
                    text1 = pytesseract.image_to_string(image)
                    text = re.sub(r'[^\x09\x0A\x0D\x20-\x7E\x85\xA0-\uD7FF\uE000-\uFFFD]+', ' ', text1)
                    document = Document()
                    document.add_paragraph(text)
                    document.save("document.docx")
                    document = "document.docx"
                    data = resume_parser.ResumeParser(document).get_extracted_data()
                    all_data.append(data)
                progress_bar.progress((i + 1) / len(resumes))  # update the progress bar
            df = pd.DataFrame(all_data, columns=['name', 'email', 'mobile_number', 'skills', 'degree', 'experience',
                                                 'company_names'])
            df.insert(0, "TimeStamp", datetime.now())
            df.insert(0, 'New_ID', range(1, 1 + len(df)))
            # Save the CSV content as a string
            csv = df.to_csv(index=False)
            if 'download_state' not in st.session_state:
                st.session_state.download_state = False
            download = st.button("Enter")
            if download or st.session_state.download_state:
                st.session_state.download_state = True
                if os.path.isfile("oryx.csv"):
                    add_to_existing = st.radio("Do you want to add to an existing file or create a new one?",
                                               ["Add to existing", "Create new"])
                    if add_to_existing == "Add to existing":
                        existing_files = [file for file in os.listdir(".") if file.endswith(".csv")]
                        selected_files = st.multiselect("Select the files to add the resume to:", existing_files)
                        for selected_file in selected_files:
                            existing_df = pd.read_csv(selected_file)
                            last_id = existing_df["New_ID"].iloc[-1]
                            df["New_ID"] = range(last_id + 1, last_id + 1 + len(df))
                            with BytesIO() as buffer:
                                existing_df.to_csv(buffer, mode='w', header=True, index=False)
                                df.to_csv(buffer, mode='a', header=False, index=False)
                                buffer.seek(0)
                                data = buffer.getvalue()
                                st.download_button(label="Download CSV File", data=data, file_name=selected_file)
                            #df.to_csv(selected_file, mode='a', header=False, index=False)
                            #st.write("Resume added to existing CSV file")                    
                    elif add_to_existing == "Create new":
                        new_csv_name = st.text_input("Enter the name of the new CSV file with the extension ")
                        csv_path = os.path.join(".", new_csv_name)
                        if not os.path.exists(csv_path):
                            with open(csv_path, "w") as f:
                               df.to_csv(f, index=False)
                               csv_bytes = csv.encode()
                               st.download_button(label="Download CSV File", data=BytesIO(csv_bytes), file_name=new_csv_name)
                               
                        else:
                            st.warning("Enter the valid name of the new CSV file.")
                else:
                    df.to_csv("oryx.csv",index=False)
                    csv_bytes = csv.encode()
                    st.download_button(label="Download CSV File", data=BytesIO(csv_bytes), file_name="oryx.csv")
                   
            st.write(df)


            # ...
    if __name__ == '__main__':
        main()

def page3():
    # set OpenAI API key
    openai.api_key = "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"

    welcome_message = '''
                <div style="background-color: #8A2BE2; color: #FFFFFF; padding: 20px; border-radius: 10px; text-align: center;">
                  <img src="https://cdna.artstation.com/p/assets/images/images/047/673/434/original/puja-kumari-chatbot-1.gif?1648147657" alt="chatbot-avatar" width="650" height="350"">
                  <h1>Welcome to our Chatbot! &#127881;</h1>
                  <p>We're here to help answer any questions you may have. Just start typing and we'll do our best to provide a helpful response. &#x1F60A;</p>
                </div>
            '''
    st.write(welcome_message, unsafe_allow_html=True)

    # define Streamlit app
    def generate_response(prompt):
        try:
            with st.spinner(text='Processing...'):
                completions = openai.Completion.create(
                    engine="text-davinci-003",
                    prompt=prompt,
                    max_tokens=1024,
                    n=1,
                    stop=None,
                    temperature=0.5,
                )
            message = completions.choices[0].text
            timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            message = f"[{timestamp}] {message}"
            message += ' ' + emoji.emojize(':smiling_face_with_smiling_eyes:')
        except Exception as e:
            message = "Sorry, something went wrong. Please try again later."
            st.write("Error: ", e)
            st.spinner('')
        return message

    st.title("chatBot : Streamlit + openAI")

    # Storing the chat
    if 'generated' not in st.session_state:
        st.session_state['generated'] = []

    if 'past' not in st.session_state:
        st.session_state['past'] = []
        # run Streamlit app

    def get_text():
        input_text = st.text_input("Type all your Questions here...", key="input")
        return input_text

    user_input = get_text()

    if user_input:
        output = generate_response(user_input)
        # store the output
        st.session_state.past.append(user_input)
        st.session_state.generated.append(output)

    if st.session_state['generated']:
        chat_style = """
        <style>
        .chat-container {
            display: flex;
            flex-direction: column;
            max-width: 600px;
            margin: 20px auto;
        }
        .chat-bubble {
            display: inline-block;
            padding: 8px 12px;
            margin: 4px;
            border-radius: 20px;
            max-width: 70%;
            font-size: 16px;
            line-height: 1.4;
        }
        .user-bubble {
            background-color: #FFFFFF;
            color: #000000;
            border: 1px solid #CCCCCC;
            align-self: flex-start;
        }
        .bot-bubble {
            background-color: #008000;
            color: #FFFFFF;
            align-self: flex-end;
        }
        .timestamp {
            font-size: 12px;
            color: #666666;
            margin-top: 5px;
            text-align: right;
        }
        </style>
        """
        st.write(chat_style, unsafe_allow_html=True)

        for i in range(len(st.session_state['generated']) - 1, -1, -1):
            if i > 0 and st.session_state['generated'][i - 1] != '':
                st.write(
                    f'<div class="chat-bubble bot-bubble">{emoji.emojize(":robot:")} {st.session_state["generated"][i]}</div>',
                    unsafe_allow_html=True, key=str(i))
            else:
                st.write(
                    f'<div class="chat-bubble bot-bubble">{emoji.emojize(":robot:")} {st.session_state["generated"][i]}</div>',
                    unsafe_allow_html=True, key=str(i), help='The bot response')
            st.write(
                f'<div class="chat-bubble user-bubble">{emoji.emojize(":man:")} {st.session_state["past"][i]}</div>',
                unsafe_allow_html=True, is_user=True, key=str(i) + '_user', help='The user input')
    
    # add a "Clear Chat" button
    if st.button("Clear Chat"):
        st.session_state['generated'] = []
        st.session_state['past'] = []
        st.session_state['index'] = 0

page_names_to_funcs = {
    "About Us": main_page,
    "SMART CV EXTRACTOR": page2,
    "AI Chatbot": page3,

}

selected_page = st.sidebar.selectbox("Select a page", page_names_to_funcs.keys())
page_names_to_funcs[selected_page]()
