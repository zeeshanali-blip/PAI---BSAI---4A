from flask import Flask, render_template, request, jsonify

app = Flask(__name__)

# simple function to decide response for user input
def get_bot_response(user_input):
    text = user_input.lower()

    if 'admission' in text or 'apply' in text:
        return 'To apply, fill out the application form, submit your documents, and pay the application fee.'
    elif 'deadline' in text or 'when' in text:
        return 'The admission deadline is usually in late July for the fall semester and early December for spring.'
    elif 'fee' in text or 'tuition' in text:
        return 'Tuition fees depend on the program, but you can expect around $5000 per semester for most courses.'
    elif 'program' in text or 'course' in text:
        return 'We offer programs in Computer Science, Business, and Engineering. Check the website for full details.'
    elif 'requirement' in text or 'documents' in text:
        return 'You need your high school transcript, test scores, ID, and any recommendation letters.'
    elif 'hello' in text or 'hi' in text:
        return 'Hello! I am the admission bot. Ask me about admission process, deadlines, fees, programs, or requirements.'
    else:
        return 'I am not sure about that. Please ask about admission process, deadlines, fee, programs, or requirements.'

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/chat', methods=['POST'])
def chat():
    data = request.get_json()
    user_input = data.get('message', '')
    response = get_bot_response(user_input)
    return jsonify({'reply': response})

if __name__ == '__main__':
    app.run(debug=True)
