import { authenticate } from "@google-cloud/local-auth";
import { google } from "googleapis";
import * as path from "path";
import * as fs from "fs";
import { OAuth2Client } from "google-auth-library";

// If modifying these scopes, delete token.json.
const SCOPES = ["https://www.googleapis.com/auth/gmail.readonly"];
const TOKEN_PATH = path.join(__dirname, "token.json");
const CREDENTIALS_PATH = path.join(__dirname, "credentials.json");

async function loadSavedCredentialsIfExist(): Promise<OAuth2Client | null> {
  try {
    if (fs.existsSync(TOKEN_PATH)) {
      const content = fs.readFileSync(TOKEN_PATH, "utf-8");
      const credentials = JSON.parse(content);
      return google.auth.fromJSON(credentials) as OAuth2Client;
    }
    return null;
  } catch (err) {
    return null;
  }
}

async function saveCredentials(client: OAuth2Client): Promise<void> {
  const content = fs.readFileSync(CREDENTIALS_PATH, "utf-8");
  const keys = JSON.parse(content);
  const key = keys.installed || keys.web;
  const payload = {
    type: "authorized_user",
    client_id: key.client_id,
    client_secret: key.client_secret,
    refresh_token: client.credentials.refresh_token,
  };
  fs.writeFileSync(TOKEN_PATH, JSON.stringify(payload));
}

async function authorize(): Promise<OAuth2Client> {
  let client = await loadSavedCredentialsIfExist();
  if (client) {
    return client;
  }
  client = await authenticate({
    scopes: SCOPES,
    keyfilePath: CREDENTIALS_PATH,
  });
  if (client.credentials) {
    await saveCredentials(client);
  }
  return client;
}

async function listMessages(auth: OAuth2Client) {
  const gmail = google.gmail({ version: "v1", auth });

  try {
    const response = await gmail.users.messages.list({
      userId: "me",
      maxResults: 100, // Adjust this number as needed
    });

    const messages = response.data.messages;
    if (!messages || messages.length === 0) {
      console.log("No messages found.");
      return;
    }

    console.log("Messages:");
    for (const message of messages) {
      const details = await gmail.users.messages.get({
        userId: "me",
        id: message.id!,
      });

      const subject = details.data.payload?.headers?.find(
        (header) => header.name?.toLowerCase() === "subject"
      )?.value;

      const from = details.data.payload?.headers?.find(
        (header) => header.name?.toLowerCase() === "from"
      )?.value;

      console.log(`From: ${from}`);
      console.log(`Subject: ${subject}`);
      console.log("-------------------");
    }
  } catch (error) {
    console.error("The API returned an error:", error);
  }
}

// Main execution
authorize().then(listMessages).catch(console.error);
