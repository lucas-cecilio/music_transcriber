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
	@pip install -e .
	@echo "Setup done! ✅"

docker_run:
	@docker run --env-file .env -p 8080:8000 music_transcriber
	@echo "Don't forget http://localhost:8080/docs"

local:
	@python music_transcriber/main_local.py

api:
	@uvicorn api:app --reload --loop asyncio

streamlint:
	@streamlit run interface.py

install_all:
	@make mt3
	@make checkpoint
	@make setup

clean:
	@rm -f *.pyc

test:
	@rm -rf mt3 checkpoints
