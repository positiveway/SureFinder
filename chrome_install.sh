if [ ! -f $HOME/Downloads/chrome.zip ]; then
  wget https://chromedriver.storage.googleapis.com/2.35/chromedriver_linux64.zip -P $HOME/Downloads -O chrome.zip
  sudo unzip $HOME/Downloads/chrome.zip -d /usr/bin
fi
