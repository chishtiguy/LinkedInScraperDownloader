#!/usr/bin/env python3

"""
Apify actor for web scraping that extracts text content and media files from URLs.
Designed for integration with Make.com and n8n automation platforms.
"""

import json
import re
from urllib.parse import urljoin, urlparse
from typing import Dict, List, Any, Optional
from datetime import datetime

import requests
from bs4 import BeautifulSoup, Tag
import trafilatura
from apify import Actor


async def main():
    """
    Main actor function that processes URL input and extracts content.
    """
    async with Actor:
        # Get actor input
        actor_input = await Actor.get_input() or {}
        
        # Extract URL from input
        url = actor_input.get('url')
        if not url:
            error_result = {
                'url': None,
                'success': False,
                'error': 'No URL provided in input',
                'error_type': 'missing_input',
                'scraped_at': datetime.now().isoformat()
            }
            await Actor.push_data(error_result)
            Actor.log.error('No URL provided in input')
            return
        
        Actor.log.info(f'Starting to scrape URL: {url}')
        
        try:
            # Validate URL
            if not is_valid_url(url):
                error_result = {
                    'url': url,
                    'success': False,
                    'error': f'Invalid URL provided: {url}',
                    'error_type': 'validation_error',
                    'scraped_at': datetime.now().isoformat()
                }
                await Actor.push_data(error_result)
                Actor.log.error(f'Invalid URL provided: {url}')
                return
            
            # Extract content from URL
            result = scrape_url_content(url)
            
            # Push result to dataset
            await Actor.push_data(result)
            
            Actor.log.info('Successfully scraped and processed URL')
            
        except Exception as e:
            error_result = {
                'url': url if 'url' in locals() else 'unknown',
                'success': False,
                'error': f'Error processing URL: {str(e)}',
                'error_type': 'processing_error',
                'scraped_at': datetime.now().isoformat()
            }
            await Actor.push_data(error_result)
            Actor.log.error(f'Error processing URL: {str(e)}')


def is_valid_url(url: str) -> bool:
    """
    Validate if the provided string is a valid URL.
    """
    try:
        result = urlparse(url)
        return all([result.scheme, result.netloc])
    except Exception:
        return False


def scrape_url_content(url: str) -> Dict[str, Any]:
    """
    Scrape content from the given URL and return structured data.
    """
    Actor.log.info(f'Fetching content from: {url}')
    
    # Download page content
    try:
        response = requests.get(url, timeout=30, headers={
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })
        response.raise_for_status()
        html_content = response.text
    except Exception as e:
        return {
            'url': url,
            'success': False,
            'error': f'Failed to fetch URL: {str(e)}',
            'error_type': 'network_error',
            'scraped_at': datetime.now().isoformat()
        }
    
    try:
        # Extract text content using trafilatura
        Actor.log.info('Extracting text content...')
        text_content = trafilatura.extract(html_content) or ""
        
        # Parse HTML for media files
        Actor.log.info('Extracting media files...')
        soup = BeautifulSoup(html_content, 'html.parser')
        media_files = extract_media_files(soup, url)
        
        # Get page metadata
        metadata = extract_page_metadata(soup, url)
        
        # Structure the output
        result = {
            'url': url,
            'title': metadata.get('title', ''),
            'description': metadata.get('description', ''),
            'text_content': text_content,
            'word_count': len(text_content.split()) if text_content else 0,
            'media_files': media_files,
            'media_count': {
                'images': len([f for f in media_files if f['type'] == 'image']),
                'videos': len([f for f in media_files if f['type'] == 'video']),
                'documents': len([f for f in media_files if f['type'] == 'document'])
            },
            'scraped_at': datetime.now().isoformat(),
            'success': True
        }
        
        return result
        
    except Exception as e:
        return {
            'url': url,
            'success': False,
            'error': f'Error extracting content: {str(e)}',
            'error_type': 'extraction_error',
            'scraped_at': datetime.now().isoformat()
        }


def extract_media_files(soup: BeautifulSoup, base_url: str) -> List[Dict[str, Any]]:
    """
    Extract media files (images, videos, documents) from the HTML content.
    """
    media_files = []
    
    # Extract images
    for img in soup.find_all('img', src=True):
        if isinstance(img, Tag) and img.get('src'):
            img_url = urljoin(base_url, img.get('src'))
            media_files.append({
                'type': 'image',
                'url': img_url,
                'alt': img.get('alt', ''),
                'title': img.get('title', '')
            })
    
    # Extract videos
    for video in soup.find_all('video', src=True):
        if isinstance(video, Tag) and video.get('src'):
            video_url = urljoin(base_url, video.get('src'))
            media_files.append({
                'type': 'video',
                'url': video_url,
                'title': video.get('title', '')
            })
    
    # Extract video sources
    for source in soup.find_all('source', src=True):
        if isinstance(source, Tag) and source.get('src'):
            source_url = urljoin(base_url, source.get('src'))
            media_files.append({
                'type': 'video',
                'url': source_url,
                'mime_type': source.get('type', '')
            })
    
    # Extract document links (PDF, DOC, etc.)
    document_extensions = ['.pdf', '.doc', '.docx', '.xls', '.xlsx', '.ppt', '.pptx', '.txt']
    for link in soup.find_all('a', href=True):
        if isinstance(link, Tag) and link.get('href'):
            href_val = link.get('href')
            if isinstance(href_val, str):
                href = href_val.lower()
                if any(href.endswith(ext) for ext in document_extensions):
                    doc_url = urljoin(base_url, href_val)
                    media_files.append({
                        'type': 'document',
                        'url': doc_url,
                        'text': link.get_text().strip(),
                        'extension': href.split('.')[-1] if '.' in href else 'unknown'
                    })
    
    return media_files


def extract_page_metadata(soup: BeautifulSoup, url: str) -> Dict[str, str]:
    """
    Extract metadata from the HTML page.
    """
    metadata = {}
    
    # Extract title
    title_tag = soup.find('title')
    if title_tag and isinstance(title_tag, Tag):
        metadata['title'] = title_tag.get_text().strip()
    
    # Extract meta description
    desc_tag = soup.find('meta', attrs={'name': 'description'})
    if desc_tag and isinstance(desc_tag, Tag):
        content = desc_tag.get('content')
        if isinstance(content, str):
            metadata['description'] = content.strip()
    
    # Extract Open Graph title and description as fallback
    if not metadata.get('title'):
        og_title = soup.find('meta', attrs={'property': 'og:title'})
        if og_title and isinstance(og_title, Tag):
            content = og_title.get('content')
            if isinstance(content, str):
                metadata['title'] = content.strip()
    
    if not metadata.get('description'):
        og_desc = soup.find('meta', attrs={'property': 'og:description'})
        if og_desc and isinstance(og_desc, Tag):
            content = og_desc.get('content')
            if isinstance(content, str):
                metadata['description'] = content.strip()
    
    return metadata


if __name__ == '__main__':
    import asyncio
    asyncio.run(main())