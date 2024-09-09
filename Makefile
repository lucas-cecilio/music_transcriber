apt:
	@sudo apt update 
	@sudo apt install libfluidsynth3 fluidsynth build-essential libasound2-dev libjack-dev gdal-bin libgdal-dev libcairo2-dev pkg-config python3-dev musescore
	@echo "Packages installed! 🎉"

mt3:
	@echo "Installing MT3 📥"
	@git clone --branch=main https://github.com/magenta/mt3
	@gsutil -m cp gs://magentadata/soundfonts/SGM-v2.01-Sal-Guit-Bass-V1.3.sf2 mt3/
	@echo "MT3 done! ✅"

checkpoint:
	@echo "Getting checkpoint 📥"
	@mkdir -p checkpoints
	@echo "This part might take a while... ⏰"
	@gsutil -m cp -r gs://mt3/checkpoints/* checkpoints/
	@echo "Checkpoints done! ✅"

setup:
	@echo "Starting setup 📥"
	@python -m pip install --upgrade pip
	@echo "Pip is now updated! 🎉"
	@cd mt3/ && pip install -e .
	@pip install -r requirements.txt
	@echo "Setup done! ✅"

run:
	@python music_transcriber/main_local.py

run_api:
	@uvicorn api:app --reload --loop asyncio

install_all:
	@make mt3
	@make checkpoint
	@make setup

clean:
	@rm -f *.pyc

test:
	@rm -rf mt3 checkpoints
