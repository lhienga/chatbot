from flask import Flask, render_template, request, jsonify
from flask import Flask, flash, request, redirect, url_for, render_template
import os
#from transformers import AutoModelForCausalLM, AutoTokenizer, InstructBlipProcessor, InstructBlipForConditionalGeneration
import torch
from PIL import Image
from werkzeug.utils import secure_filename
import requests
import pandas as pd
import time

#tokenizer = AutoTokenizer.from_pretrained("microsoft/DialoGPT-medium")
#model = AutoModelForCausalLM.from_pretrained("microsoft/DialoGPT-medium")
#model = InstructBlipForConditionalGeneration.from_pretrained("Salesforce/instructblip-vicuna-7b")
#processor = InstructBlipProcessor.from_pretrained("Salesforce/instructblip-vicuna-7b")

ALLOWED_EXTENSIONS = set(['png', 'jpg', 'jpeg', 'gif'])

# Path to save the CSV file
CSV_FILE_PATH = "response.csv"

def allowed_file(filename):
	return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = "static/uploads"
@app.route("/")
def index():
    return render_template('index.html')

@app.route('/getimg', methods=['POST'])
def upload_image():
	if 'image' not in request.files:
		print('No file part')
		return redirect(request.url)
	file = request.files['image']
	if file.filename == '':
		print('No image selected for uploading')
		return redirect(request.url)
	if file and allowed_file(file.filename):
		filename = secure_filename(file.filename)
		file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
		#print('upload_image filename: ' + filename)
		print('Image successfully uploaded and displayed below')
		return render_template('upload.html', filename=filename)
	else:
		print('Allowed image types are -> png, jpg, jpeg, gif')
		return redirect(request.url)
      
@app.route("/sendfeedback", methods=["GET", "POST"])
def saveFeedback():
    global data
    global start
    fb = request.form["feedback"]
    id = int(request.form["id"])
    data.loc[start+id, 'feedback'] = fb
    data.to_csv(CSV_FILE_PATH, index=False)  # Save to CSV
    print("hiasdsaf feedback", fb)
    return "feedback saved!"

@app.route("/get", methods=["GET", "POST"])
def chat():
    global data
    id = request.form["id"]
    msg = request.form["msg"]
    url = request.form["url"]
    
    if 'image' in request.files:
        img = request.files['image']
        img.save("uploaded_image.jpg")
        print("saved image")
    print("url: ", url)
    img = Image.open(requests.get(url, stream=True).raw).convert("RGB")
    print(msg)
    input = msg
    #img = request.files["image"]
    #image_input = img
    #img = Image.open("test/20221218_205725.jpg").convert('RGB')
    print("opened img")
    #img = Image.fromarray(img).convert('RGB')
    
    ans = get_Chat_response(input, img)
    new = {"id": id, "image_url": url, "user_message": msg, "bot_message": ans, "feedback": None}
    #data = data.append(new, ignore_index = True)
    data = pd.concat([data, pd.DataFrame([new])], ignore_index=True)
    data.to_csv(CSV_FILE_PATH, index=False)  # Save to CSV
    return ans


def get_Chat_response(text, img):

    # Let's chat for 5 lines
    #for step in range(1000):
        #time.sleep(5)
        #inputs = processor(images=img, text=text, return_tensors="pt")
        print("generating output.........")
        '''
         outputs = model.generate(
                                    **inputs,
                                    do_sample=False,
                                    num_beams=5,
                                    max_length=256,
                                    min_length=1,
                                    top_p=0.9,
                                    repetition_penalty=1.5,
                                    length_penalty=1.0,
                                    temperature=1,
                                )
        '''
       
        print("generated!!!!!!!!!!")
        #generated_text = processor.batch_decode(outputs, skip_special_tokens=True)[0].strip()
    
        
        #response = model.generate({"image": image, "prompt": prompt})[0]
        # encode the new user input, add the eos_token and return a tensor in Pytorch
        #print(generated_text)
        
        
        # pretty print last ouput tokens from bot
        return "generated text"
    #generated_text


if __name__ == '__main__':
    global data
    global start
    data = pd.DataFrame(columns=["id", "image_url", "user_message", "bot_message", "feedback"])

    # Load data from existing CSV file if available
    if os.path.exists(CSV_FILE_PATH):
        data = pd.read_csv(CSV_FILE_PATH)
    start = data.shape[0] -1
    app.run()

    # Save the final data to CSV before the program ends
    data.to_csv(CSV_FILE_PATH, index=False)
