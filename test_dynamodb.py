import boto3
from boto3.dynamodb.conditions import Key
from datetime import datetime

# Connect to DynamoDB
dynamodb = boto3.resource('dynamodb', region_name='ap-south-1')

print("=" * 50)
print("Testing DynamoDB Connection...")
print("=" * 50)

try:
    # Test Files Table
    files_table = dynamodb.Table('mycloud-files-metadata')
    print(f"\n✅ Files Table: {files_table.table_name}")
    print(f"   Status: {files_table.table_status}")
    print(f"   Item Count: {files_table.item_count}")
    
    # Test Logs Table
    logs_table = dynamodb.Table('mycloud-activity-logs')
    print(f"\n✅ Logs Table: {logs_table.table_name}")
    print(f"   Status: {logs_table.table_status}")
    print(f"   Item Count: {logs_table.item_count}")
    
    # Insert a test entry
    print("\n" + "=" * 50)
    print("Inserting test data...")
    print("=" * 50)
    
    test_user_id = "test-user-123"
    test_file_id = "test-file-456"
    
    files_table.put_item(
        Item={
            'user_id': test_user_id,
            'file_id': test_file_id,
            'filename': 'test-document.txt',
            'upload_time': datetime.now().isoformat(),
            'size': '1024',
            's3_key': f'{test_user_id}/{test_file_id}_test-document.txt'
        }
    )
    print("✅ Test file metadata inserted successfully!")
    
    logs_table.put_item(
        Item={
            'user_id': test_user_id,
            'timestamp': datetime.now().isoformat(),
            'action': 'test',
            'file_id': test_file_id,
            'filename': 'test-document.txt'
        }
    )
    print("✅ Test activity log inserted successfully!")
    
    # Read back the test data
    print("\n" + "=" * 50)
    print("Reading test data back...")
    print("=" * 50)
    
    response = files_table.get_item(
        Key={'user_id': test_user_id, 'file_id': test_file_id}
    )
    
    if 'Item' in response:
        print("✅ Successfully retrieved test file:")
        print(f"   Filename: {response['Item']['filename']}")
        print(f"   Size: {response['Item']['size']} bytes")
    
    # Clean up test data
    print("\n" + "=" * 50)
    print("Cleaning up test data...")
    print("=" * 50)
    
    files_table.delete_item(
        Key={'user_id': test_user_id, 'file_id': test_file_id}
    )
    logs_table.delete_item(
        Key={'user_id': test_user_id, 'timestamp': response['Item']['upload_time']}
    )
    print("✅ Test data cleaned up!")
    
    print("\n" + "=" * 50)
    print("🎉 ALL TESTS PASSED!")
    print("DynamoDB is working perfectly!")
    print("=" * 50)
    
except Exception as e:
    print(f"\n❌ Error: {str(e)}")
    print("\nPlease check:")
    print("1. AWS credentials are configured (aws configure)")
    print("2. Tables exist in DynamoDB console")
    print("3. You have internet connection")
