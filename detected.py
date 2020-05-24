# Author: Omar Zayed and Vanessa Lama

import os
import sys
import subprocess
from datetime import datetime, timedelta
from pydub import AudioSegment
from pydub.playback import play


def play_DetectedSound(name):

    log_file = 'logs/sound.log'
	
    #  read the log file and Check if the last sound played was within 10 seconds.
    if os.path.isfile(log_file): # First check if file exists.
        with open(log_file, 'r') as f:
            date = f.read()
            date_to_datetime = datetime.strptime(date, "%Y-%m-%d %H:%M:%S.%f")

            if datetime.now() < date_to_datetime + timedelta(seconds=10):
                return

    # Update the email log and play the audio
    with open(log_file, 'w') as f:
        f.write(str(datetime.now()))
    subprocess.call('espeak '+ name, shell=True)
    player = subprocess.Popen(["omxplayer", "audio/detected.mp3",'-o', 'local', "-ss", "30"], stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    

