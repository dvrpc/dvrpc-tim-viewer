## Source:
## https://wiki.postgresql.org/wiki/Apt
## ca-certificates should be preinstalled
# sudo apt-get install wget ca-certificates
wget --quiet -O - https://www.postgresql.org/media/keys/ACCC4CF8.asc | sudo apt-key add -
sudo sh -c 'echo "deb http://apt.postgresql.org/pub/repos/apt/ $(lsb_release -cs)-pgdg main" > /etc/apt/sources.list.d/pgdg.list'
# apt-cache search postgis | less
sudo apt-get update
sudo apt-get install postgresql-9.5-postgis-2.4