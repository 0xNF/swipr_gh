# Ensure the monitor script is executable
echo "Ensuring script is executable"
chmod +x ./sss_start.sh

# Replace the systemd service file
echo "Stopping old ssm Systemd service if it exists"
systemctl stop ssm

echo "Copying new ssm Systemd service"
cp ./ssm.service /etc/systemd/system/

echo "Reloading daemons"
systemctl daemon-reload

# Restart the systemd service
echo "Restarting ssm service"
systemctl start ssm