<!DOCTYPE html>
<html lang="en">

<h1>Twilio and Google Calendar Integration for WhatsApp</h1>

<p>This project demonstrates the integration of Twilio and Google Calendar for managing events through WhatsApp messages. Users can interact with their Google Calendar by sending WhatsApp messages to a Twilio phone number.</p>

<h2>Prerequisites</h2>

<ol>
  <li>
    <strong>Google Cloud Platform (GCP) Account:</strong>
    <ul>
      <li>Create a GCP account: <a href="https://console.cloud.google.com/">Google Cloud Console</a>.</li>
      <li>Set up a project and note down the Project ID.</li>
    </ul>
  </li>
  <!-- Additional Information -->
  <li>
    <strong>Deploy Flask App to Google Cloud App Engine:</strong>
    <ol>
      <li>Install Google Cloud SDK: Follow the instructions for your OS [Installing Google Cloud SDK](https://cloud.google.com/sdk/docs/install).</li>
      <li>Set Up a Google Cloud Project: Create a new project on the [Google Cloud Console](https://console.cloud.google.com/). Enable billing.</li>
      <li>Enable App Engine API: Enable the App Engine API for your project.</li>
      <li>Configure Google Cloud SDK: Run `gcloud init` and follow the instructions.</li>
      <li>Navigate to Your Flask App Directory: Open a terminal and go to your Flask app directory.</li>
      <li>Create `app.yaml` File: Create a file named `app.yaml` with the provided content in the README.</li>
      <li>Install Gunicorn: Run `pip install gunicorn` to install Gunicorn.</li>
      <li>Deploy to App Engine: Run `gcloud app deploy` to deploy your Flask app.</li>
      <li>Access Your App: After deployment, you will get a public URL for your app.</li>
    </ol>
  </li>
  <!-- End of Additional Information -->
  <li>
    <strong>Google Calendar API:</strong>
    <ul>
      <li>Enable the Google Calendar API for your project.</li>
      <li>Create credentials (OAuth client ID) for the project. Download the JSON file containing client ID and secret.</li>
    </ul>
  </li>
  <li>
    <strong>Google Cloud Storage:</strong>
    <ul>
      <li>Set up a Google Cloud Storage bucket to store OAuth tokens.</li>
      <li>Note the bucket name.</li>
    </ul>
  </li>
  <li>
    <strong>Service Account:</strong>
    <ul>
      <li>Create a service account with the necessary permissions (Google Calendar API, Google Cloud Storage).</li>
      <li>Download the JSON key file for the service account.</li>
    </ul>
  </li>
  <li>
    <strong>Twilio Account:</strong>
    <ul>
      <li>Create a Twilio account: <a href="https://www.twilio.com/console">Twilio Console</a>.</li>
      <li>Acquire a Twilio phone number configured for WhatsApp.</li>
    </ul>
  </li>
</ol>

<h2>Project Setup</h2>

<ol>
  <li>Clone the repository:</li>
</ol>

<pre><code>git clone https://github.com/your-username/your-project.git
cd your-project
</code></pre>

<ol start="2">
  <li>Install dependencies:</li>
</ol>

<pre><code>pip install -r requirements.txt
</code></pre>

<ol start="3">
  <li>Copy the Google Calendar API credentials JSON file and the service account JSON key file to the project directory.</li>
</ol>

<h2>Running the Application</h2>

<ol>
  <li>Run the Flask web application:</li>
</ol>

<p>There is no need to run the application locally, but you can run it to check if it is working.</p>

<pre><code>python app.py
</code></pre>

<p>The application will be accessible at <code>http://localhost:5000</code>.</p>

<ol start="2">
  <li>Configure your Twilio WhatsApp phone number:</li>
</ol>

<ul>
  <li>Log in to Twilio Console.</li>
  <li>Navigate to your Twilio WhatsApp phone number.</li>
  <li>Set the "Incoming Webhook" to your gcloud uri <code>https://PROJECT_ID.REGION_ID.r.appspot.com/webhook</code>.</li>
</ul>

<h2>Usage</h2>

<ol>
  <li>Send a WhatsApp message to your Twilio phone number with commands like:
    <ul>
      <li><code>next events</code>: List upcoming events.</li>
      <li><code>add event &lt;event details&gt;</code>: Add a new event to the calendar.</li>
    </ul>
  </li>
  <li>Receive WhatsApp responses with relevant information.</li>
</ol>

<h2>Troubleshooting</h2>

<ul>
  <li>If you encounter issues with Google Cloud Storage permissions, ensure that the service account has the necessary roles (e.g., Storage Object Admin) on the storage bucket.</li>
  <li>Check the Twilio WhatsApp logs for any errors related to webhook requests.</li>
</ul>
</html>
