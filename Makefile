.PHONY: deploy run

TARGET:=cec.local

deploy:
	scp cec_to_sonos.py $(TARGET):/tmp/
	ssh $(TARGET) sudo install -Dm755 /tmp/cec_to_sonos.py /usr/local/bin/cec_to_sonos

run: deploy
	ssh $(TARGET) cec_to_sonos
