import argparse
import subprocess
import os
import runpy

def sign():
  print("Sign-in/logging features not released yet")


def main():
    ascii_art= r"""
     ███          █████   █████                                            █████
    ░░░███       ░░███   ░░███                                            ░░███
      ░░░███      ░███    ░███   ██████   ████████    ██████              ███████    ██████  ████████
        ░░░███    ░███████████  ░░░░░███ ░░███░░███  ░░░░░███  ██████████░░░███░    ███░░███░░███░░███
         ███░     ░███░░░░░███   ███████  ░███ ░███   ███████ ░░░░░░░░░░   ░███    ░███ ░███ ░███ ░░░
       ███░       ░███    ░███  ███░░███  ░███ ░███  ███░░███              ░███ ███░███ ░███ ░███
     ███░         █████   █████░░████████ ████ █████░░████████             ░░█████ ░░██████  █████
    ░░░          ░░░░░   ░░░░░  ░░░░░░░░ ░░░░ ░░░░░  ░░░░░░░░               ░░░░░   ░░░░░░  ░░░░░
    """

    guidelines= f"""
    Welcome to Hana-tor, a private messaging service which aside from encryption
    provides additional anonymity by using tor network for channeling your messages
    """
    print(ascii_art)
    print("\n")
    print(guidelines)
    guidelines1=f"""
    --sign-up[to create a public identifier and make your .onion stay on a public database
    alongside your username and public_encryption key for easier messaging between users]
    Thou sign-in doesnt creates much difference except adding your tor hidden service link
    and port and public key visible, still its recommended to use '--start' if your security depends on it

    --start[immediately puts you in a .onion adress with new public and private key and nothing gets logged
    anywhere, but you have to manually send port, link and public key to the other person]

    --recv[If you want to talk to someone already running a hidden service, you will get a new private key\n but manually save the other peer's public key in .txt file in same directory]

    --login[gives you a new .onion adress but carries your username, previous public key/private key]

    --exit[Exiting the program]

    Note:-Only guest mode is currently avaiable logging is still under developement due to budget contraints
    and practical usability questions of such a public database(seems pretty useless anyways)

    Both peers can --start their own hidden service to connect to each other instead of --recv
    """
    print(guidelines1)
    usr=input("> ")
    if usr=="--recv":
      runpy.run_path("socks_tor.py")
    elif usr=="--start":
      runpy.run_path("encrypted.py")
    elif usr=="--login" or usr=="--sign-up":
      sign()
    elif usr=="--exit":
      print("Exiting...")
      return
if __name__=='__main__':
  main()
