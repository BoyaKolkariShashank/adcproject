from flask import Flask, request, redirect, render_template
import string
import random
import boto3
from botocore.exceptions import NoCredentialsError, PartialCredentialsError

application = Flask(__name__)

# AWS configuration (consider using environment variables instead)
AWS_ACCESS_KEY_ID = 'AKIAWPPO57SMC5VZINQR'  # Replace with environment variable or secure method
AWS_SECRET_ACCESS_KEY = 'f+BefyP2F2YwVw2+w9PGeA9bzuHHckPzOUpfL2Y8'  # Replace with environment variable or secure method
AWS_REGION = 'us-east-1'

# Initialize DynamoDB
def init_dynamodb():
    try:
        dynamodb = boto3.resource(
            'dynamodb',
            aws_access_key_id=AWS_ACCESS_KEY_ID,
            aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
            region_name=AWS_REGION
        )
        return dynamodb
    except (NoCredentialsError, PartialCredentialsError) as e:
        print(f"Error initializing DynamoDB: {e}")
        return None

# Generate a random short URL
def generate_short_url(length=6):
    characters = string.ascii_letters + string.digits
    return ''.join(random.choice(characters) for _ in range(length))  # Added closing parenthesis

# Home route
@application.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        long_url = request.form['long_url']
        short_url = generate_short_url()

        # Save to DynamoDB
        dynamodb = init_dynamodb()
        if dynamodb:
            table = dynamodb.Table('urls')  # replace with your table name
            try:
                table.put_item(
                    Item={
                        'short_url': short_url,  # Assuming 'short_url' is the primary key
                        'long_url': long_url
                    }
                )
                return render_template('index.html', short_url=short_url)
            except Exception as e:
                print(f"Error saving to DynamoDB: {e}")
                return 'Failed to save to DynamoDB', 500
        else:
            return 'Failed to connect to DynamoDB', 500

    return render_template('index.html', short_url=None)

# Redirect route
@application.route('/<short_url>')
def redirect_to_url(short_url):
    dynamodb = init_dynamodb()
    if dynamodb:
        table = dynamodb.Table('urls')  # replace with your table name
        try:
            response = table.get_item(
                Key={'short_url': short_url}
            )
            if 'Item' in response:
                return redirect(response['Item']['long_url'])
        except Exception as e:
            print(f"Error retrieving from DynamoDB: {e}")
            return 'Error retrieving URL', 500
    return 'URL not found', 404

if __name__ == '__main__':
    application.run(debug=True)
