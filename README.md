# CEC to Sonos Adapter

This is a small hacky script capable of translating CEC (HDMI) volume changes to
a networked Sonos speaker. It requires a Raspi or other device with a
[Pulse-Eight CEC adapter](https://kodi.wiki/view/CEC#Kodi_Devices) hooked up to
an HDMI port (ideally the eARC port).

```
    ┌────────┐                 
    │        │HDMI┌─────┐      
    │   TV   ├────►Raspi│      
    │        │    └──┬──┘      
    └───┬────┘       │         
        │Optical     │Network  
┌───────▼────────┐   │         
│     Sonos      ◄───┘         
└────────────────┘             
```

This is especially helpful if your Sonos soundbar does not support HDMI eARC and
you instead hook it up to your TV over an Optical cable. The sound works fine,
but volume on an RF remote does not work. Instead you might be forced to use a
separate IR remote for the soundbar, or use a universal IR remote. With this
script running you can use the remote that you normally use for your TV.

The eARC port is not strictly necessary. But you might find that your TV warns
you that you just plugged a "receiver" into something other than the eARC port
which would normally be bad.

## Install

* Prepare any Raspberry Pi with an [up to date image](https://www.raspberrypi.com/software/operating-systems/) and install `python3`
	* Even the [very first Raspi generation](https://www.raspberrypi.com/products/raspberry-pi-1-model-b-plus/) works, and afaik every generation since
	* The Lite image is fine, a desktop is not strictly necessary
		* You *are* taking up an HDMI port though so you might consider it
* Change settings on your TV to [enable CEC and an ARC receiver](https://support.roku.com/article/360034303013)
* Edit the `cec_to_sonos.py` script to use at use the appropriate Sonos name

```
scp cec_to_sonos.py your-raspi.local:
ssh your-raspi.local
sudo install -Dm755 cec_to_sonos.py /usr/local/bin/cec_to_sonos

sudo apt install python3 python3-cec
sudo pip3 install soco

# Test it out
cec_to_sonos
(Ctrl-C)
```

To run on boot add the following to `/etc/rc.local` before the `exit 0` line:
```
nohup cec_to_sonos &
```

## Known issues

This setup works for my Roku TV, but there is a lucky caveat in that enabling
CEC and ARC on my TV does **not** disable Optical output. It's possible that's
not always the case.

This script does not handle "give audio status" requests from the TV, which may
result in weird on screen behavior. Currently the script only reports audio
status when a volume button is released. My Roku TV immediately displays a "100"
volume inidcator until I release the button at which point it displays a correct
status.

You can try adding a call to `report_audio_status` in the handling for `CEC_OPCODE_GIVE_AUDIO_STATUS`.
This could introduce additional latency, and in my case doesn't really solve much.
There is still a "100" on screen a whole lot.
I believe the problem is I can't effectively "reply" in the Python bindings for `libcec`.
If I rewrote in C linked with `libcec`, or perhaps used the [kernel cec api](https://www.kernel.org/doc/html/v4.12/media/kapi/cec-core.html) I believe I could handle it better.
But it doesn't bother me enough to solve it.
If it bothers **you** enough to solve it and you post a project somewhere let me know!
