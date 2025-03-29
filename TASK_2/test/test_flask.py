from flask import Flask
app = Flask(__name__)
@app.route('/')
def hello():
	return "Flask dang hoat dong"
if __name__ == '__main__':
	app.run(debug=True,port=8000)
