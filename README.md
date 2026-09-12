# YouTube Agentic AI Summarizer

This is a separate Python webpage where anyone can paste a public YouTube link and
generate a summary. It uses the Gemini API's agentic video-processing mode, so Gemini
can navigate the video timeline and inspect both spoken content and important visuals.

## Files

- `app.py`: the Streamlit webpage and Gemini API call
- `youtube_utils.py`: YouTube URL validation and summary instructions
- `requirements.txt`: Python libraries installed by the hosting service
- `.streamlit/config.toml`: webpage colors and server settings

## Run it locally

1. Install Python 3.11 or newer.
2. Open a terminal inside this folder.
3. Install the libraries:

   ```bash
   python -m pip install -r requirements.txt
   ```

4. Create `.streamlit/secrets.toml` and add:

   ```toml
   GEMINI_API_KEY = "your-real-key"
   ```

5. Start the webpage:

   ```bash
   python -m streamlit run app.py
   ```

## Put it online for anyone to use

1. Create a new GitHub repository.
2. Upload all the files in this folder. Do not upload a real `secrets.toml` file.
3. Sign in at [Streamlit Community Cloud](https://share.streamlit.io/).
4. Select **Create app**, choose the GitHub repository, and set the main file to
   `app.py`.
5. Open **Advanced settings**, then add this under **Secrets**:

   ```toml
   GEMINI_API_KEY = "your-real-key"
   ```

6. Press **Deploy**. Streamlit will give you a permanent `streamlit.app` link that
   other people can open without seeing or entering your API key.

## Important notes

- Create the API key in [Google AI Studio](https://aistudio.google.com/app/apikey).
- Only public YouTube videos are supported by Gemini's YouTube URL input.
- Every visitor uses the website owner's Gemini quota, so monitor the API usage.
- The YouTube URL feature is currently a Gemini API preview feature.
