from flask import Flask, request, jsonify, render_template, session, redirect, url_for
import boto3
from boto3.dynamodb.conditions import Key
from botocore.client import Config
import uuid
from datetime import datetime
import os


app = Flask(__name__)
app.secret_key = 'swarup-personal-file-manager-2025'  

# Initialize AWS services
# Initialize AWS services with proper signature version


s3_client = boto3.client(
    's3',
    region_name='ap-south-1',
    config=Config(signature_version='s3v4')
)

dynamodb = boto3.resource('dynamodb', region_name='ap-south-1')

# DynamoDB Tables
files_table = dynamodb.Table('mycloud-files-metadata')
logs_table = dynamodb.Table('mycloud-activity-logs')

# S3 Bucket name (we'll create this in next step)
BUCKET_NAME = 'mycloud-storage-swarup'  # Change 'youruniquename' to your name/roll number

@app.route('/')
def index():
    """Home page"""
    if 'user_id' not in session:
        session['user_id'] = str(uuid.uuid4())  # Create session for user
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_file():
    """Upload file to S3 and store metadata in DynamoDB"""
    try:
        if 'file' not in request.files:
            return jsonify({'status': 'error', 'message': 'No file uploaded'})
        
        file = request.files['file']
        if file.filename == '':
            return jsonify({'status': 'error', 'message': 'No file selected'})
        
        user_id = session.get('user_id', 'anonymous')
        file_id = str(uuid.uuid4())
        timestamp = datetime.now().isoformat()
        
        # Upload to S3
        s3_key = f'{user_id}/{file_id}_{file.filename}'
        s3_client.upload_fileobj(file, BUCKET_NAME, s3_key)
        
        # Store metadata in DynamoDB
        files_table.put_item(
            Item={
                'user_id': user_id,
                'file_id': file_id,
                'filename': file.filename,
                'upload_time': timestamp,
                'size': str(file.content_length or 0),
                's3_key': s3_key
            }
        )
        
        # Log activity in DynamoDB
        logs_table.put_item(
            Item={
                'user_id': user_id,
                'timestamp': timestamp,
                'action': 'upload',
                'file_id': file_id,
                'filename': file.filename
            }
        )
        
        return jsonify({
            'status': 'success',
            'message': f'File {file.filename} uploaded successfully',
            'file_id': file_id
        })
    
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)})

@app.route('/files')
def list_files():
    """List all files for current user"""
    try:
        user_id = session.get('user_id', 'anonymous')
        
        # Query DynamoDB for user's files
        response = files_table.query(
            KeyConditionExpression=Key('user_id').eq(user_id)
        )
        
        files = response.get('Items', [])
        return jsonify({'status': 'success', 'files': files})
    
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)})

@app.route('/download/<file_id>')
def download_file(file_id):
    """Generate download link for file"""
    try:
        user_id = session.get('user_id', 'anonymous')
        
        # Get file metadata from DynamoDB
        response = files_table.get_item(
            Key={'user_id': user_id, 'file_id': file_id}
        )
        
        if 'Item' not in response:
            return jsonify({'status': 'error', 'message': 'File not found'})
        
        item = response['Item']
        s3_key = item['s3_key']
        
        # Direct S3 URL (no signature needed since bucket policy allows public read)
        download_url = f"https://{BUCKET_NAME}.s3.ap-south-1.amazonaws.com/{s3_key}"
        
        # Log activity
        logs_table.put_item(
            Item={
                'user_id': user_id,
                'timestamp': datetime.now().isoformat(),
                'action': 'download',
                'file_id': file_id,
                'filename': item['filename']
            }
        )
        
        return jsonify({
            'status': 'success',
            'download_url': download_url,
            'filename': item['filename']
        })
    
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)})

@app.route('/logs')
def view_logs():
    """View activity logs for current user"""
    try:
        user_id = session.get('user_id', 'anonymous')
        
        # Query activity logs from DynamoDB
        response = logs_table.query(
            KeyConditionExpression=Key('user_id').eq(user_id),
            ScanIndexForward=False,  # Sort by timestamp descending
            Limit=50  # Last 50 activities
        )
        
        logs = response.get('Items', [])
        return jsonify({'status': 'success', 'logs': logs})
    
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)})

@app.route('/health')
def health_check():
    """Health check endpoint for Load Balancer"""
    return jsonify({'status': 'healthy'})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
