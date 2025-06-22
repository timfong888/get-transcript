### MCP Servers

#### Context7
Remote:

{
  "mcpServers": {
    "context7": {
      "type": "http",
      "url": "https://mcp.context7.com/mcp"
    }
  }
}

Local:
{
  "servers": {
    "Context7": {
      "type": "stdio",
      "command": "npx",
      "args": ["-y", "@upstash/context7-mcp"]
    }
  }
}

### Specific Servers
These are MCP servers that are specific to our project and are not general purpose.

- Google Cloud nodejs: https://github.com/googleapis/google-cloud-node
- Firebase: https://github.com/firebase/firebase-docs
- Firebase Command Line Tools: https://github.com/firebase/firebase-tools
- Firebase Functions codebase: https://github.com/firebase/firebase-functions
- Decodo Residential proxies: https://context7.com/decodo/decodo
- Webshare Proxy: https://context7.com/context7/apidocs_webshare_io
- Youtube Transript API:  https://context7.com/jdepoix/youtube-transcript-api


