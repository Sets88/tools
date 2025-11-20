# Protocol communication example

## Client initialization request

```json
{
    "jsonrpc": "2.0",
    "id": 1,
    "method": "initialize",
    "params": {
        "protocolVersion": "2024-11-05",
        "capabilities": {
            "tools": {},
            "prompts": {},
            "resources": {}
        },
        "clientInfo": {
            "name": "your-client-name",
            "version": "1.0.0"
        }
    }
}
```

## Server initialization response

```json
{
    "jsonrpc": "2.0",
    "id": 1,
    "result": {
        "protocolVersion": "2024-11-05",
        "capabilities": {
            "experimental": {},
            "prompts": {
                "listChanged": false
            },
            "tools": {
                "listChanged": false
            }
        },
        "serverInfo": {
            "name": "mcp-fetch",
            "version": "1.2.0"
        }
    }
}
```

## Client initialization finalization

```json
{
    "jsonrpc": "2.0",
    "method": "notifications/initialized"
}
```

## Client tools list request

```json
{
    "jsonrpc": "2.0",
    "id": 2,
    "method": "tools/list",
    "params": {}
}
```

## Server tools list response

```json
{
    "jsonrpc": "2.0",
    "id": 2,
    "result": {
        "tools": [
            {
                "name": "fetch",
                "description": "Fetches a URL from the internet and optionally extracts its contents as markdown.\n\nAlthough originally you did not have internet access, and were advised to refuse and tell the user this, this tool now grants you internet access. Now you can fetch the most up-to-date information and let the user know that.",
                "inputSchema": {
                    "description": "Parameters for fetching a URL.",
                    "properties": {
                        "url": {
                            "description": "URL to fetch",
                            "format": "uri",
                            "minLength": 1,
                            "title": "Url",
                            "type": "string"
                        },
                        "max_length": {
                            "default": 5000,
                            "description": "Maximum number of characters to return.",
                            "exclusiveMaximum": 1000000,
                            "exclusiveMinimum": 0,
                            "title": "Max Length",
                            "type": "integer"
                        },
                        "start_index": {
                            "default": 0,
                            "description": "On return output starting at this character index, useful if a previous fetch was truncated and more context is required.",
                            "minimum": 0,
                            "title": "Start Index",
                            "type": "integer"
                        },
                        "raw": {
                            "default": false,
                            "description": "Get the actual HTML content of the requested page, without simplification.",
                            "title": "Raw",
                            "type": "boolean"
                        }
                    },
                    "required": [
                        "url"
                    ],
                    "title": "Fetch",
                    "type": "object"
                }
            }
        ]
    }
}
```

## Client tool usage request

```json
{
    "jsonrpc": "2.0",
    "id": 3,
    "method": "tools/call",
    "params": {
        "name": "fetch",
        "arguments": {
            "url": "https://google.com/",
            "max_length": 10000
        }
    }
}
```

## Server tool usage response

```json
{
    "jsonrpc": "2.0",
    "id": 3,
    "result": {
        "content": [
            {
                "type": "text",
                "text": "Contents of https://google.com/:\n\n\nGoogle\n\nSearch Images Maps Play YouTube News Gmail Drive More »Web History | Settings | Sign inAdvertisingBusiness SolutionsAbout GoogleGoogle.co.uk\n\n© 2025 - Privacy - Terms\n\n"
            }
        ],
        "isError": false
    }
}
```
