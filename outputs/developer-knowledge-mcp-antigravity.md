# Google Developer Knowledge MCP server in Google Antigravity 2.0, IDE, and/or CLI

**Metadata:**
- **Total Duration:** 25 minutes
- **Authors:** Pierrick Voulet
- **Last Updated:** 2026-06-03T15:35:27Z
- **Source URL:** [https://codelabs.developers.google.com/developer-knowledge-mcp-antigravity#0](https://codelabs.developers.google.com/developer-knowledge-mcp-antigravity#0)

---

## 1. Introduction
*Duration: 2 mins*

## 1. Introduction

**Note:** Are you still using the Gemini CLI? This guide covers the Antigravity CLI. More information on how to transition can be found in [this official blog post](https://developers.googleblog.com/an-important-update-transitioning-gemini-cli-to-antigravity-cli/).

[**Google Developer Knowledge**](https://developers.google.com/knowledge) is the canonical, machine-readable source of Google's public developer documentation. It's programmatically accessible via Application Programming Interface (API) and Model Context Protocol (MCP) so that developers can integrate it into applications and workflows.

Instead of relying on outdated LLM training data or manual web scraping, AI agent developers should use it for real-time access to the most accurate documentation and reduce risk of hallucinations.

In this codelab, you will learn how to install and use the **Developer Knowledge MCP** from **Antigravity 2.0, IDE, and/or CLI**. MCP is an open standard that enables AI models to securely use tools provided by remote servers. You will set up **Antigravity** to interact with the knowledge base without writing any code!

![dk_mcp_antigravity.png](https://codelabs.developers.google.com/static/developer-knowledge-mcp-antigravity/img/dk_mcp_antigravity.png)

## What you'll do

- Enable the **Developer Knowledge API** in your Google Cloud project.
- Configure **Antigravity** to access the **Developer Knowledge MCP**.
- Test the integration with a few **prompts**.

## What you'll need

- A web browser such as [Chrome](https://www.google.com/chrome/)
- A Google Cloud project (billing is **not** required).
- Antigravity 2.0, IDE, and/or CLI installed on your local machine. You can find more detail and installation guidance from [the official website](https://antigravity.google/docs/home).

## Explore more MCPs and tools

In this codelab we only cover a few basic examples of what can be done using the Google Developer Knowledge MCP server. To see the full list of Google MCP servers and tools available, refer to the [Supported Products](https://docs.cloud.google.com/mcp/supported-products).

**Note:** To go further and learn how to connect AI agents to user data, you might want to check the codelab [Google Workspace MCP servers in Google Antigravity](https://codelabs.developers.google.com/google-workspace-mcp-antigravity) that demonstrates how to set up the official Workspace MCP servers in Antigravity.

## Easy access to this codelab

![qr_code.png](https://codelabs.developers.google.com/static/developer-knowledge-mcp-antigravity/img/qr_code.png)

---

## 2. Configure Cloud project
*Duration: 5 mins*

## 2. Configure Cloud project

## Create or Select a Google Cloud project

In the [Google Cloud Console](https://console.cloud.google.com), [**select or create a Google Cloud project**](https://cloud.google.com/resource-manager/docs/creating-managing-projects).

## Enable the API

To use the Developer Knowledge MCP server, you must enable the standard Developer Knowledge API.

[Enable the Developer Knowledge API](https://console.cloud.google.com/flows/enableapi?apiid=developerknowledge.googleapis.com)

## Create the API key

To use the Developer Knowledge MCP server, you must use an API key. In the [Google Cloud Console](https://console.cloud.google.com), do the following:

1. Go to **APIs & Services** > **Credentials**.

[Go to Credentials](https://console.cloud.google.com/apis/credentials)

2. Click **+ Create credentials**, then select **API key** from the menu.
3. Set **Name** with an arbitrary name such as `Antigravity`.
4. Click the **Select API restrictions** drop-down, type `Developer Knowledge API`, check the result, then click **OK**.

   **Note:** There is a short delay before **Developer Knowledge API** appears in the list after its enablement, wait a few minutes and try again if you cannot find it.

![create_api_key.png](https://codelabs.developers.google.com/static/developer-knowledge-mcp-antigravity/img/create_api_key.png)

5. Click **Create**.
6. Your API key is now displayed on the confirmation screen. Copy it to your clipboard, you'll need it to configure **Antigravity** in the next steps.

   **Warning:** **Important:** Never share an API key publicly. The one you see in the following screenshot is fake, it was added for illustration purposes only.

![copy_api_key.png](https://codelabs.developers.google.com/static/developer-knowledge-mcp-antigravity/img/copy_api_key.png)

---

## 3. Configure Antigravity
*Duration: 10 mins*

## 3. Configure Antigravity

Now let's configure Antigravity to use the MCP endpoint. If you don't have Antigravity 2.0, IDE, and/or CLI installed, follow the instructions on the [Antigravity website](https://antigravity.google/docs/home).

## Add custom MCP servers

Antigravity 2.0, IDE, and CLI share a central MCP configuration in the file `~/.gemini/config/mcp_config.json`.

1. Open it in your preferred text editor.

   **Note:** You can access the file directly from Antigravity IDE if you have it installed by following these steps:

   1. Open **MCP Servers** via the **...** dropdown at the top of the editor's agent panel.
   2. Click **Manage MCP Servers** then **View raw config**.
2. Modify it with the following custom MCP server configuration. Before doing so, replace the **<YOUR\_API\_KEY>** placeholder with the API key you created in the previous steps:

```
{
  "mcpServers": {
    "google-developer-knowledge": {
      "headers": {
        "X-Goog-Api-Key": "<YOUR_API_KEY>"
      },
      "serverUrl": "https://developerknowledge.googleapis.com/mcp"
    }
    ...
  }
  ...
}
```

3. Save it.

   **Warning:** **Important:** Never share an API key publicly. The one you see in the following screenshot is fake, it was added for illustration purposes only.

![mcp_config.png](https://codelabs.developers.google.com/static/developer-knowledge-mcp-antigravity/img/mcp_config.png)

## Validate

You should see the MCP server that you configured as installed in Antigravity: `google-developer-knowledge`.

### Antigravity 2.0

1. Click **Settings** at the bottom left.
2. Navigate to **Customizations**.
3. Under **Installed MCP Servers**, click **Refresh**.

![configured_mcp_server_20.png](https://codelabs.developers.google.com/static/developer-knowledge-mcp-antigravity/img/configured_mcp_server_20.png)

### Antigravity IDE

1. Open **Antigravity User Settings** via the **Editor-Specific settings** menu dropdown at the top of the window.

![open_user_settings_ide.png](https://codelabs.developers.google.com/static/developer-knowledge-mcp-antigravity/img/open_user_settings_ide.png)

2. Navigate to **Customizations**.
3. Under **Installed MCP Servers**, click **Refresh**.

![configured_mcp_server_ide.png](https://codelabs.developers.google.com/static/developer-knowledge-mcp-antigravity/img/configured_mcp_server_ide.png)

### Antigravity CLI

1. Start the CLI executing the command `agy` from a terminal.
2. Type `/mcp` and press **enter**.

![configured_mcp_server_cli.png](https://codelabs.developers.google.com/static/developer-knowledge-mcp-antigravity/img/configured_mcp_server_cli.png)

---

## 4. Access Developer Knowledge
*Duration: 5 mins*

## 4. Access Developer Knowledge

Now you can interact with Google Developer Knowledge using natural language. Here are some example prompts:

- `Based on the Google Developer Knowledge, does Google Workspace support MCP servers?`
- `Give me a list of the Google Workspace and Cloud Run API names. Make it super short.`
- `Based on the Google Developer Knowledge, create a new Python script to upload a file to Google Drive`

**Note:** The first time the agent tries to use a tool from this MCP server, Antigravity will ask for your approval. You'll need to **allow** to proceed.

![mcp_allow.png](https://codelabs.developers.google.com/static/developer-knowledge-mcp-antigravity/img/mcp_allow.png)

### Antigravity 2.0

![20_test.png](https://codelabs.developers.google.com/static/developer-knowledge-mcp-antigravity/img/20_test.png)

### Antigravity IDE

![ide_test.png](https://codelabs.developers.google.com/static/developer-knowledge-mcp-antigravity/img/ide_test.png)

### Antigravity CLI

![cli_test.png](https://codelabs.developers.google.com/static/developer-knowledge-mcp-antigravity/img/cli_test.png)

---

## 5. Clean up
*Duration: 2 mins*

## 5. Clean up

To clean up your Google Cloud project without deleting it, you can disable the **Developer Knowledge API** you enabled and delete the API key you created:

1. In the Google Cloud Console, go to the [**API & Services Dashboard**](https://console.cloud.google.com/apis/dashboard).
2. Click **Developer Knowledge API** then **Disable API**.
3. In the Google Cloud Console, go to [**API & Services > Credentials**](https://console.cloud.google.com/apis/credentials).
4. Select the API key, click **Delete** then **Delete** to confirm.

---

## 6. Congratulations
*Duration: 1 mins*

## 6. Congratulations

Congratulations! You have successfully configured and tested the Google Developer Knowledge MCP server using Antigravity.

### Reference docs

- [Google Workspace MCP servers in Google Antigravity 2.0, IDE, and/or CLI](https://codelabs.developers.google.com/google-workspace-mcp-antigravity)
- [Introduction to Model Context Protocol (MCP)](https://modelcontextprotocol.io/introduction)
- [Antigravity](https://antigravity.google/docs/home)