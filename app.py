from flask  import Flask, request, render_template
import pandas as pd
import random
from flask_sqlalchemy import SQLAlchemy
from  sklearn.metrics.pairwise import cosine_similarity
from sklearn.feature_extraction.text import TfidfVectorizer


app = Flask(__name__)

## Loading files
new_data = pd.read_csv('models/main_data.csv')
trending_products = pd.read_csv('models/trending_product.csv')

# database configuration---------------------------------------
app.secret_key = "alskdjfwoeieiurlskdjfslkdjf"
app.config['SQLALCHEMY_DATABASE_URI'] = "mysql://root:@localhost/freedb_ecommerce_data"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)


# Define your model class for the 'signup' table
class Signup(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), nullable=False)
    password = db.Column(db.String(100), nullable=False)

# Define your model class for the 'signup' table
class Signin(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), nullable=False)
    password = db.Column(db.String(100), nullable=False)

# Recommendation functions
# Function to truncate product name
def truncate(text, length):
    if len(text) > length:
        return text[:length] + "......"
    else:
        return text

def content_base_recommendation_system(new_data, item_name, top_n = 10):
  
  if item_name not in new_data['Name'].values:
    print(f'Item {item_name} not found in the database')
    return pd.DataFrame()

  tfidf_vectorizer = TfidfVectorizer(stop_words = 'english')

  tfidf_matrix_content = tfidf_vectorizer.fit_transform( new_data['Tags'])

  cosine_similarity_content = cosine_similarity(tfidf_matrix_content, tfidf_matrix_content)

  item_index = new_data[new_data['Name'] == item_name].index[0]

  similar_item = list(enumerate(cosine_similarity_content[item_index]))

  sorted_similar_item = sorted(similar_item, key = lambda x: x[1], reverse = True)

  top_similar_item = sorted_similar_item[:top_n]

  recommended_similar_index = [x[0] for x in top_similar_item]

  recommended_item_details = new_data.iloc[recommended_similar_index][['Name','ReviewsCount', 'Brand', 'ImageUrl','Rating']]

  return recommended_item_details

# Routes
random_image_urls = [
    "static/img/img_1.png",
    "static/img/img_2.png",
    "static/img/img_3.png",
    "static/img/img_4.png",
    "static/img/img_5.png",
    "static/img/img_6.png",
    "static/img/img_7.png",
    "static/img/img_8.png",
]    

@app.route("/")
def index():
    random_product_image_urls = [random.choice(random_image_urls) for _ in range(len(trending_products))]
    price = [40, 50, 60, 70, 100, 122, 106, 50, 30, 50]
    return render_template('index.html', trending_products = trending_products.head(8), truncate = truncate,
                           random_product_image_urls = random_product_image_urls, random_price = random.choice(price))

@app.route("/main")
def main():
    return render_template('main.html')


@app.route("/index")
def indexredirect():
    return render_template('index.html')

@app.route("/signup",methods = ['POST','GET'])
def signup():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']


        new_signup = Signup(username = username, email = email, password = password) 
        db.session.add(new_signup)
        db.session.commit()   

        random_product_image_urls = [random.choice(random_image_urls) for _ in range(len(trending_products))]
        price = [40, 50, 60, 70, 100, 122, 106, 50, 30, 50]
        return render_template('index.html', trending_products = trending_products.head(8), truncate = truncate,
                            random_product_image_urls = random_product_image_urls, random_price = random.choice(price),
                            signup_message = 'User signed up successfully!')
    

# Route for signup page
@app.route('/signin', methods=['POST', 'GET'])
def signin():
    if request.method == 'POST':
        username = request.form['signinUsername']
        password = request.form['signinPassword']
        new_signup = Signin(username=username,password=password)
        db.session.add(new_signup)
        db.session.commit()

        # Create a list of random image URLs for each product
        random_product_image_urls = [random.choice(random_image_urls) for _ in range(len(trending_products))]
        price = [40, 50, 60, 70, 100, 122, 106, 50, 30, 50]
        return render_template('index.html', trending_products=trending_products.head(8), truncate=truncate,
                               random_product_image_urls=random_product_image_urls, random_price=random.choice(price),
                               signup_message='User signed in successfully!'
                               )


@app.route("/recommendations", methods = ['POST','GET'])
def recommendations():
    if request.method == 'POST':
        prod = request.form.get('prod')
        nbr  = int(request.form.get('nbr'))
        content_based_rec = content_base_recommendation_system(new_data, prod, top_n=nbr)

        if content_based_rec.empty:
            message = 'No recommendations avaliable for this product.'
            return render_template('main.html', message = message)
        else:
             # Create a list of random image URLs for each product
            random_product_image_urls = [random.choice(random_image_urls) for _ in range(len(trending_products))]
            print(content_based_rec)
            print(random_image_urls)

            price = [40, 50, 60, 70, 100, 122, 106, 50, 30, 50]
            return render_template('main.html', content_based_rec = content_based_rec, truncate=truncate,
                                random_product_image_urls=random_product_image_urls, random_price=random.choice(price)
                                )


if __name__ == '__main__':
    app.run(debug  = True)