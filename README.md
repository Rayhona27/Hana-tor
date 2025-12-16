# Platform and Usage

Its a CLI only Messaging service that works over tor to ensure utmost level of anonymity.<br>
*Note:-It has only been tested on linux, as its just third alpha, but it can be used on windows pretty easily, by just running main.py in your venv, but with future versions it might not.*<br>

---

# Features

-Send and Recieve "short" messages(it will be fixed in upcomming updates with better hybrid encryption)<br>
-CLI only,minimal interface<br>
-Linux-first(May..... work on windows)<br>

---

# Installation & Usage

```bash
git clone https://github.com/Rayhona27/Hana-tor.git
cd Hana-tor
chmod +x setup.sh
./setup.sh
```
After running the setup.sh script, detailed usage will be given! But these are it in a nutshell:-<br>

```bash
--start #to start a hidden service(atleast one peer is expected to do this)
```

Then you will be prompted to generate or enter your RSA asymetric key pair(Your Private Key and your Peer's Public Key)<br>
*Note:-Preferably generate and use new keys everytime*<br>

Then save your Peer's Public RSA key into a txt file in the same directory *Generally:~"/home/you/Hana-tor"* or wherever you installed this service<br>

You will be prompted to enter name of the file where you stored it Enter it like "your_key.txt"<br>

A tor hidden service will be started on your device and after you get your .onion adress you have to share with your other peer<br>

Now theres 2 way to exchange message, either one peer runs a hidden service, and other connects to it, or both of them run their own hidden service. If you choose to follow that path run this:-<br>

```bash
/connect <replace with peer's onion>
```
and when you are done talking you can 

```bash
/quit
```

to stop the hidden service<br>

Or you if the other peer is already running a hidden service you can run<br>

```bash
--recv
```

to just connect to the other peer(This is the recommended method)<br>
the full connectivity process stays the same, but you have to enter the onion adress of the peer when prompted<br>

# Word from me
I know this isnt the most revolutionary or a new concept, but i still thought to develop it and will keep adding features and releasing updates, so keep an eye on this repo if you are interested in using it<br>

# Contact
If you have questions, feedback, or want to report any issue, feel free to reach me at: <br>
**reberuappu@proton.me**
