
## Windows 10 with Windows Subsystem for Linux
### Tippecanoe

1. Install Windows Subsystem for Linux - FYI: A Linux distribution is not included
Control Panel > Programs and Features > Turn Windows Features On or Off > Windows Subsystem for Linux (WSL)

2. Install a supported distribution (via Microsoft Store)
[aka.ms/wslstore](https://aka.ms/wslstore) > Microsoft Store > Ubuntu

3. Launch Bash
Run > bash.exe

4. Install Tippecanoe dependencies
`apt-get update`
`apt-get upgrade`
`apt-get install g++ make libsqlite3-0 libsqlite3-dev zlib1g zlib1g-dev`

5. Clone the repository
`git clone https://github.com/mapbox/tippecanoe`

6. Compile and install
`cd tippecanoe`
`make`
`make install`
