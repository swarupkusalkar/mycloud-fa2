import boto3
from datetime import datetime
from botocore.client import Config
# Initialize S3 client
# Initialize AWS services with proper signature version


s3_client = boto3.client(
    's3',
    region_name='ap-south-1',
    config=Config(signature_version='s3v4')
)


BUCKET_NAME = 'mycloud-storage-swarup'

print("=" * 60)
print("Testing S3 Bucket Connection...")
print("=" * 60)

try:
    # Test 1: Check if bucket exists
    print(f"\n✅ Checking bucket: {BUCKET_NAME}")
    response = s3_client.head_bucket(Bucket=BUCKET_NAME)
    print(f"✅ Bucket exists and is accessible!")
    
    # Test 2: Upload a test file
    print("\n" + "=" * 60)
    print("Uploading test file...")
    print("=" * 60)
    
    test_content = f"Test file created at {datetime.now()}"
    test_key = "test-folder/test-file.txt"
    
    s3_client.put_object(
        Bucket=BUCKET_NAME,
        Key=test_key,
        Body=test_content.encode('utf-8')
    )
    print(f"✅ File uploaded successfully: {test_key}")
    
    # Test 3: List objects in bucket
    print("\n" + "=" * 60)
    print("Listing files in bucket...")
    print("=" * 60)
    
    response = s3_client.list_objects_v2(Bucket=BUCKET_NAME)
    
    if 'Contents' in response:
        print(f"✅ Found {len(response['Contents'])} file(s):")
        for obj in response['Contents']:
            print(f"   - {obj['Key']} ({obj['Size']} bytes)")
    else:
        print("   No files found (bucket is empty)")
    
    # Test 4: Generate presigned URL
    print("\n" + "=" * 60)
    print("Generating download URL...")
    print("=" * 60)
    
    url = s3_client.generate_presigned_url(
        'get_object',
        Params={'Bucket': BUCKET_NAME, 'Key': test_key},
        ExpiresIn=3600
    )
    print("✅ Presigned URL generated successfully!")
    print(f"   URL (valid for 1 hour): {url[:80]}...")
    
    # Test 5: Download the file
    print("\n" + "=" * 60)
    print("Downloading test file...")
    print("=" * 60)
    
    response = s3_client.get_object(Bucket=BUCKET_NAME, Key=test_key)
    content = response['Body'].read().decode('utf-8')
    print(f"✅ File downloaded successfully!")
    print(f"   Content: {content}")
    
    # Test 6: Delete test file
    print("\n" + "=" * 60)
    print("Cleaning up test file...")
    print("=" * 60)
    
    s3_client.delete_object(Bucket=BUCKET_NAME, Key=test_key)
    print(f"✅ Test file deleted!")
    
    print("\n" + "=" * 60)
    print("🎉 ALL S3 TESTS PASSED!")
    print("S3 bucket is working perfectly!")
    print("=" * 60)
    
except Exception as e:
    print(f"\n❌ Error: {str(e)}")
    print("\nPlease check:")
    print("1. Bucket name is correct: mycloud-storage-swarup")
    print("2. Bucket exists in ap-south-1 region")
    print("3. AWS credentials are configured properly")
    print("4. You have internet connection")
