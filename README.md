# Databricks Dino Game

A clone of the chromium [dino game](https://en.wikipedia.org/wiki/Dinosaur_Game) deployable as a Databricks App.

## Features
- Flask app with Chromium Dino Game in vanilla js
- Deployable locally or as a Databricks app
- Save game statistics to Databricks volume, including which object killed the player
- Delta Live Tables pipeline to process the game data
- Databricks AI/BI dashboard to analyse games and track leaderboard
- Generate synthetic game data

## Setup
There are a few things you'll need to tweak to get this working for you:
1. There are a couple of variables in the notebooks which you'll need to update based on the Volume you want to use
2. When you upload this folder to your Databricks workspace, you might have to change some of the notebook paths for the pipeline
3. Update the app.yaml file to match your catalog name etc.
4. You can deploy this pipeline with a file arrival trigger, or run it continously, up to you
5. There's also a notebook which will help you generate some sythnetic game data if you don't have many players. All the synthetic players have robot names.

### Local
1. Install python etc.
2. Configure Databricks SDK
3. Set up a virtual environment of your choosing, there's a requirements.txt to help
4. Run app.py to start the Flask app locally
5. Play game

### Databricks App
1. Upload this repo to your Databricks workspace
2. Adjust the setup.py notebook to your liking and run the cells to deploy the various assets
3. You can also follow [this guide](https://docs.databricks.com/en/dev-tools/databricks-apps/app-development.html) to deploy your app via the UI 
4. Create a Databricks workflow to orchestrate your pipeline. There's a workflow.json example to get you started.

## Roadmap
Improvements I'll likely never get around to:
- [ ] Add Databricks Asset Bundle to make deployment easier
- [ ] Create and publish dashboard, then update Leaderboard link in index.html
- [ ] Allow users to submit their own username
- [ ] Add global highscore to app from Leaderboard
- [ ] Add Databricks workflow to the assets deployed in setup.py

## Licence
This project is released into the public domain under [The Unlicense](LICENSE).
**Disclaimer**: This repo is provided as-is, with no guarantees. Bad things can happen when you copy code from strangers on the internet. Good luck, have fun!
