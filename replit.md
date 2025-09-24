# Web Content Scraper

## Overview

This is an Apify actor designed for web scraping that extracts text content and media files from URLs. The scraper is specifically built for integration with automation platforms like Make.com and n8n, enabling automated content extraction workflows. The actor takes a URL as input and returns structured data containing the scraped content and associated metadata.

## User Preferences

Preferred communication style: Simple, everyday language.

## System Architecture

### Core Components

**Actor Framework**: Built on the Apify platform using their Actor framework, which provides cloud-based execution, input/output handling, and data storage capabilities.

**Input Processing**: Uses JSON schema validation for input parameters, requiring only a target URL to process. The input schema ensures proper validation and provides a clean interface for automation tools.

**Content Extraction Pipeline**: 
- Primary extraction using Trafilatura library for reliable text content extraction
- BeautifulSoup for HTML parsing and DOM manipulation
- Custom media file detection and URL resolution
- Error handling with structured error responses

**Output Format**: Structured JSON output designed for automation platform consumption, including success/failure status, extracted content, media files, and metadata with timestamps.

**Error Handling**: Comprehensive error management with categorized error types (missing_input, invalid_url, etc.) and detailed error messages for debugging automation workflows.

### Design Patterns

**Async/Await Pattern**: Uses Python's asyncio for non-blocking execution, essential for the Apify platform's concurrent processing model.

**Separation of Concerns**: URL validation, content extraction, and media processing are handled as separate logical components within the main processing pipeline.

**Structured Data Output**: Consistent JSON schema for all responses (success and error cases) to ensure reliable integration with downstream automation tools.

### Technology Stack

- **Python 3**: Core programming language
- **Apify SDK**: Platform framework for actor development and deployment
- **Trafilatura**: Primary content extraction library optimized for web article extraction
- **BeautifulSoup**: HTML parsing and DOM manipulation
- **Requests**: HTTP client for web requests

## External Dependencies

### Apify Platform
- **Apify SDK**: Core framework providing actor lifecycle management, input/output handling, and cloud execution environment
- **Apify Cloud**: Hosting and execution platform with built-in scaling and monitoring

### Content Processing Libraries
- **Trafilatura**: Advanced content extraction library that handles various website formats and content structures
- **BeautifulSoup**: HTML/XML parsing library for DOM manipulation and element extraction
- **Requests**: HTTP library for making web requests and handling responses

### Automation Platform Integration
- **Make.com**: Webhook-based automation platform integration
- **n8n**: Open-source workflow automation tool integration
- Both platforms consume the structured JSON output for further processing in automation workflows

### Runtime Environment
- **Python 3.x**: Runtime environment with standard library support
- **Memory**: Configured for 1024MB execution environment to handle large web pages and media processing