# commands used to build and run firefox in a container

docker run -it --privileged --name cliente_login --network distributedCompNetwork --rm -e DISPLAY=172.20.32.1:0.0 -p 5000:5000 -v c:/users/mike/documents/distributedComputing/SocketFinal/client:/client ubuntuc

# must have xming installed. 

once the client container is running, install python and tkinter with: 
sudo apt-get install python3
sudo apt-get install python3.tk

run the code with this command: python3 client.py
