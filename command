# Edit sudoers file
sudo visudo

# Add this line (replace 'pi' with your username):
Defaults secure_path="/home/pi/ledcontrol-env/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin"

sudo chmod 644 /lib/systemd/system/ledscontroller.service