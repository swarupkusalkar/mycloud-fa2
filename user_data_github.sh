#!/bin/bash
# User data script to deploy Personal File Manager from GitHub

# Update system
sudo yum update -y

# Install Python 3, pip, and git
sudo yum install -y python3 python3-pip git

# Clone the GitHub repository
cd /home/ec2-user
git clone https://github.com/swarupkusalkar/mycloud-fa2.git
cd mycloud-fa2

# Install Python dependencies
pip3 install -r requirements.txt

# Change ownership
sudo chown -R ec2-user:ec2-user /home/ec2-user/mycloud-fa2

# Start the application with gunicorn in background
nohup gunicorn --bind 0.0.0.0:5000 app:app --workers 2 --timeout 120 > /home/ec2-user/app.log 2>&1 &

# Create a simple startup script for auto-restart
cat > /home/ec2-user/start_app.sh << 'STARTSCRIPT'
#!/bin/bash
cd /home/ec2-user/mycloud-fa2
nohup gunicorn --bind 0.0.0.0:5000 app:app --workers 2 --timeout 120 > /home/ec2-user/app.log 2>&1 &
STARTSCRIPT

chmod +x /home/ec2-user/start_app.sh

# Add to crontab for auto-start on reboot
(crontab -l 2>/dev/null; echo "@reboot /home/ec2-user/start_app.sh") | crontab -

echo "Application deployment completed!" > /home/ec2-user/deployment_status.txt
